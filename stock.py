"""Modulo unificado para manejar lo relativo a stock."""
from flask import Blueprint,render_template,jsonify,make_response, request,\
           send_file
from flask_login import login_required
import simplejson as json

import pandas as pd
import mysql.connector
from lib import pgdict, pgonecolumn, pglflat
from con import get_con, log, engine
from formularios import listaprecios, imprimir_stock

stock = Blueprint('stock',__name__)

@stock.route('/stock/asientos')
@login_required
def stock_asientos():
    """Inicializo la pagina asientos."""
    return render_template('stock/asientos.html')


@stock.route('/stock/proveedores')
@login_required
def stock_proveedores():
    """Inicializo la pagina proveedores."""
    return render_template('stock/proveedores.html')


@stock.route('/stock/getasientos')
def stock_getasientos():
    """Proveo lista de asientos."""
    con = get_con()
    asientos=pgdict(con, "select id,fecha, cuenta, imp, comentario from caja \
            order by id desc limit 100")
    saldo = pgonecolumn(con, "select sum(imp) from caja,ctas where \
            caja.cuenta=ctas.cuenta and tipo in (0,1)")
    saldosantander = pgonecolumn(con, "select sum(imp) from caja,ctas where \
            caja.cuenta=ctas.cuenta and tipo in (2,3)")
    con.close()
    return jsonify(asientos=asientos,saldo=saldo,saldosantander=saldosantander)


@stock.route('/stock/deleteasiento/<int:id_asiento>')
def stock_deleteasiento(id_asiento):
    """Borrado de asiento."""
    con = get_con()
    stm=f'delete from caja where id={id_asiento}'
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    log(stm)
    cur.close()
    con.close()
    return 'OK'


@stock.route('/stock/getcuentas')
def stock_getcuentas():
    """Proveo lista de cuentas."""
    con = get_con()
    cuentas = pglflat(con, "select cuenta from ctas order by cuenta")
    con.close()
    return jsonify(result=cuentas)


@stock.route('/stock/guardarasiento' , methods = ['POST'])
def stock_guardarasiento():
    """Guardar Asiento."""
    con = get_con()
    d_dato = json.loads(request.data.decode("UTF-8"))
    tipo = pgonecolumn(con, f"select tipo from ctas where cuenta='{d_dato['cuenta']}'")
    if tipo in [0, 3]:
        importe = int(d_dato['imp'])*(-1)
    else:
        importe = int(d_dato['imp'])

    ins = f"insert into caja(fecha,cuenta,imp,comentario) values\
    ('{d_dato['fecha']}','{d_dato['cuenta']}',{importe},'{d_dato['comentario']}')"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    log(ins)
    cur.close()
    con.close()
    return 'OK'


@stock.route('/stock/editarcomentarioasiento', methods=['POST'])
def stock_editarcomentarioasiento():
    """Editar comentarios en asientos."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    upd = f"update caja set comentario='{d_data['comentario']}' where id=\
            {d_data['id']}"
    cur = con.cursor()
    cur.execute(upd)
    log(upd)
    con.commit()
    con.close()
    return 'ok'


@stock.route('/stock/mayor')
def stock_mayor():
    """Muestro pagina Mayor."""
    return render_template('stock/mayor.html')


@stock.route('/stock/getmayor/<string:cuenta>')
def stock_getmayor(cuenta):
    """Obtengo asientos por cuenta (mayorizo)."""
    con = get_con()
    asientos=pgdict(con, f"select id,fecha, cuenta, imp, comentario from caja \
                          where cuenta='{cuenta}' order by id desc")
    con.close()
    return jsonify(asientos=asientos)


@stock.route('/stock/pivotcuentas')
def stock_pivotcuentas():
    """Pivot Cuentas."""
    sql="select date_format(fecha,'%Y-%m') as fecha,cuenta,imp from caja \
         order by id desc"
    pd.options.display.float_format = '{:20.0f}'.format
    dat = pd.read_sql_query(sql, engine)
    dframe = pd.DataFrame(dat)
    tbl = pd.pivot_table(dframe, values=['imp'],index='cuenta',columns='fecha',\
          aggfunc='sum').sort_index(axis=1, level='fecha',ascending=False)
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="table",classes="table table-sm")
    return render_template("stock/pivot_cuentas.html", tbl=tbl)


@stock.route('/stock/retiros')
def stock_retiros():
    """Pandas de retiro socios."""
    sql="select date_format(fecha,'%Y-%m') as fecha,cuenta,imp from caja \
            where cuenta like '%retiro%' and cuenta not like '%capital%' \
            order by id desc"
    pd.options.display.float_format = '{:20.0f}'.format
    dat = pd.read_sql_query(sql, engine)
    dframe = pd.DataFrame(dat)
    print(dframe)
    tbl = pd.pivot_table(dframe, values=['imp'],index='fecha',columns='cuenta'\
        ,aggfunc='sum').sort_index(axis=0,level='fecha',ascending=False)
    col0 = tbl.iloc[:,0]
    col1 = tbl.iloc[:,1]
    diff1 = col0.sub(col1,axis=0)
    col2 = tbl.iloc[:,2]
    col3 = tbl.iloc[:,3]
    diff2 = col2.sub(col3,axis=0)
    tbl.insert(4,'diff1', diff1)
    tbl.insert(5,'diff2', diff2)
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="retiros",classes="table is-narrow")
    return render_template("stock/retiros.html", tbl=tbl)


@stock.route('/stock/getcompras')
def stock_getcompras():
    """Obtengo lista compras."""
    con = get_con()
    compras=pgdict(con, "select id,fecha,art,cnt, costo,total,proveedor from \
                          artcomprado order by id desc limit 200")
    proveedores = pglflat(con, "select distinct proveedor from artcomprado")
    con.close()
    return jsonify(compras=compras, proveedores=proveedores)


@stock.route('/stock/getarticulos')
def stock_getarticulos():
    """Obtengo lista de articulos."""
    con = get_con()
    articulos=pglflat(con, "select art from articulos")
    con.close()
    return jsonify(result=articulos)


@stock.route('/stock/compras')
def stock_compras():
    """Muestro pagina de compras."""
    return render_template('stock/compras.html')


@stock.route('/stock/deletecompra/<int:id_compra>')
def stock_deletecompra(id_compra):
    """Borrar compra."""
    con = get_con()
    stm=f'delete from artcomprado where id={id_compra}'
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    log(stm)
    cur.close()
    con.close()
    return 'el registro ha sido borrado'


@stock.route('/stock/guardarcompra' , methods = ['POST'])
def stock_guardarcompra():
    """Guardar compra."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    total = int(d_data['cnt']) * int(d_data['costo'])
    ins = f"insert into artcomprado(fecha,cnt,art,costo,total,proveedor) \
            values('{d_data['fecha']}',{d_data['cnt']},'{d_data['art']}',{d_data['costo']},\
            {total},'{d_data['proveedor']}')"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    log(ins)
    cur.close()
    con.close()
    return 'OK'


@stock.route('/stock/saldosorpresa')
def stock_saldosorpresa():
    """Obtengo saldo cuenta corriente Sorpresa."""
    con = get_con()
    pagado = pgonecolumn(con, "select sum(imp) from caja where cuenta = \
                               'depositos sorpresa'")
    comprado = pgonecolumn(con, "select sum(total) from artcomprado where \
             lower(proveedor) like lower('Sorpresa') and fecha>'2015-09-20'")
    saldosorpresa = 122031 + comprado + pagado
    con.close()
    return jsonify(saldosorpresa=saldosorpresa)


@stock.route('/stock/getdepositos')
def stock_getdepositos():
    """Obtengo lista depositos."""
    con = get_con()
    depositos=pgdict(con, "select fecha,imp from caja where cuenta=\
    'depositos sorpresa' order by id desc")
    con.close()
    return jsonify(depositos=depositos)


@stock.route('/stock/generarstock')
def stock_generarstock():
    """Genero stock."""
    con = get_con()
    cur = con.cursor()
    cur.execute('drop table if exists detalles')
    cur.execute("create temporary table if not exists detalles as select cnt,\
    art from detvta where idvta>55203 and devuelta=0 UNION ALL select cnt,art \
    from detallesalida")
    cur.execute('drop table if exists stockactual')
    cur.execute("create temporary table if not exists stockactual as select \
    art,sum(cnt) as ingreso,(select sum(cnt) from detalles where art=\
    artcomprado.art) as egreso from artcomprado where  fecha>'2015-09-15' \
    group by art")
    con.commit()
    cur.close()
    listastock = pgdict(con, "select stockactual.art, ingreso, IFNULL(egreso,\
    0) as egreso, ingreso-IFNULL(egreso, 0) as stock, costo, cuota from \
    stockactual,articulos where articulos.art=stockactual.art order by stock \
    desc")
    con.close()
    return jsonify(stock=listastock)


@stock.route('/stock/verstock')
def stock_verstock():
    """Muestro pagina verstock."""
    return render_template('stock/verstock.html')


@stock.route('/stock/salidas')
def stock_salidas():
    """Muestro pagina salidas."""
    return render_template('stock/salidas.html')


@stock.route('/stock/getsalidas')
def stock_getsalidas():
    """Obtengo lista de salidas."""
    con = get_con()
    salidas=pgdict(con, "select id,fecha,cnt,art,costo,comentario from \
    detallesalida order by id desc limit 200")
    con.close()
    return jsonify(salidas=salidas)


@stock.route('/stock/deletesalida/<int:id_salida>')
def stock_deletesalida(id_salida):
    """Borro salida."""
    con = get_con()
    stm=f'delete from detallesalida where id={id_salida}'
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    log(stm)
    cur.close()
    con.close()
    return 'el registro ha sido borrado'


@stock.route('/stock/guardarsalida' , methods = ['POST'])
def stock_guardarsalida():
    """Guardo salida."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    ins = f"insert into detallesalida(fecha,cnt,art,costo,comentario) values\
    ('{d_data['fecha']}',{d_data['cnt']},'{d_data['art']}',{d_data['costo']},\
    '{d_data['comentario']}')"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    log(ins)
    cur.close()
    con.close()
    return 'OK'


@stock.route('/stock/getlistaarticulos')
def stock_getlistaarticulos():
    """Obtengo lista de articulos."""
    con = get_con()
    articulos=pgdict(con, "select * from articulos order by activo desc,art" )
    grupos = pglflat(con, "select distinct grupo from articulos where grupo \
    is not null")
    con.close()
    return jsonify(articulos=articulos, grupos=grupos)


@stock.route('/stock/articulos')
def stock_articulos():
    """Muestro pagina de articulos."""
    return render_template('stock/articulos.html')


@stock.route('/stock/guardararticulo' , methods = ['POST'])
def stock_guardararticulo():
    """Guardo articulo."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    ins = f"insert into articulos(art, costo, activo,cuota,grupo,codigo) \
    values('{d_data['art']}',{d_data['costo']},{d_data['activo']},\
    {d_data['cuota']},'{d_data['grupo']}','{d_data['codigo']}')"
    cur = con.cursor()
    try:
        cur.execute(ins)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error,400)
    else:
        con.commit()
        log(ins)
        cur.close()
        con.close()
        return 'OK'


@stock.route('/stock/deletearticulo/<int:id_articulo>')
def stock_deletearticulo(id_articulo):
    """Borrar articulo."""
    con = get_con()
    stm=f'delete from articulos where id={id_articulo}'
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    log(stm)
    cur.close()
    con.close()
    return 'el registro ha sido borrado'


@stock.route('/stock/articulotoggleactivo/<int:id_articulo>')
def stock_articulotoggleactivo(id_articulo):
    """Toggle activo para articulos."""
    con = get_con()
    activo = pgonecolumn(con, f"select activo from articulos where id=\
    {id_articulo}")
    if activo==1:
        stm = f"update articulos set activo=0 where id={id_articulo}"
    else:
        stm = f"update articulos set activo=1 where id={id_articulo}"
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    log(stm)
    cur.close()
    con.close()
    return 'OK'


@stock.route('/stock/guardaredicionarticulo' , methods = ['POST'])
def stock_guardaredicionarticulo():
    """Guardar edicion de articulo."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    upd = f"update articulos set art='{d_data['art']}', costo= \
    {d_data['costo']}, activo= {d_data['activo']}, cuota= {d_data['cuota']},\
    grupo='{d_data['grupo']}',codigo='{d_data['codigo']}' where id=\
    {d_data['id']}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error,400)
    else:
        con.commit()
        log(upd)
        cur.close()
        con.close()
        return 'OK'


@stock.route('/stock/getproveedores')
def stock_getproveedores():
    """Obtengo proveedores."""
    con = get_con()
    proveedores = pgdict(con, "select * from proveedores order by empresa")
    return jsonify(proveedores=proveedores)


@stock.route('/stock/agregarproveedor', methods=["POST"])
def stock_agregarproveedor():
    """Agrego proveedores."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    ins = f"insert into proveedores(empresa,direccion,wapp,alias,cbu,contacto,\
    transporte,descripcion) values('{d_data['empresa']}',\
    '{d_data['direccion']}','{d_data['wapp']}','{d_data['alias']}',\
    '{d_data['cbu']}','{d_data['contacto']}','{d_data['transporte']}',\
    '{d_data['descripcion']}')"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    log(ins)
    con.close()
    return 'ok'


@stock.route('/stock/editarproveedor', methods=["POST"])
def stock_editarproveedor():
    """Edito proveedor."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    upd = f"update proveedores set empresa='{d_data['empresa']}',direccion=\
    '{d_data['direccion']}',wapp='{d_data['wapp']}',alias='{d_data['alias']}'\
    ,cbu='{d_data['cbu']}',contacto='{d_data['contacto']}',transporte=\
    '{d_data['transporte']}',descripcion='{d_data['descripcion']}' where \
    id={d_data['id']}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    log(upd)
    con.close()
    return 'ok'


@stock.route('/stock/borrarproveedor/<int:id_proveedor>')
def stock_borrarproveedor(id_proveedor):
    """Borrar proveedor."""
    con = get_con()
    stm = f"delete from proveedores where id={id_proveedor}"
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    log(stm)
    con.close()
    return 'ok'


@stock.route('/stock/listawapp')
def stock_listawapp():
    """Lista whatsapps."""
    con = get_con()
    wapps = pgdict(con, "select wapp,fecha,msg,file,id,idcliente,user,timein,\
    timeout,enviado,response from logwhatsapp order by id desc")
    return jsonify(wapps=wapps)


@stock.route('/wapp')
def stock_wapp():
    """Muestro pagina wapp."""
    return render_template('/stock/wapp.html')


@stock.route('/stock/generarlistaprecios')
def stock_generarlistaprecios():
    """Genero lista de precios."""
    con = get_con()
    lista = pgdict(con, "select * from articulos where activo=1 order by grupo\
    ,codigo")
    grupos = pglflat(con, "select distinct grupo from articulos where activo=1\
                           and grupo is not null order by grupo")
    listaprecios(lista,grupos)
    return 'ok'

@stock.route('/stock/cuentas')
def stock_cuentas():
    """Muestro pagina cuentas."""
    return render_template('stock/cuentas.html')


@stock.route('/stock/getdictcuentas')
def stock_getdictcuentas():
    """Obtengo lista cuentas."""
    con = get_con()
    cuentas = pgdict(con, "select * from ctas")
    return jsonify(cuentas=cuentas)


@stock.route('/stock/editarcuenta', methods=['POST'])
def stock_editarcuenta():
    """Editar Cuentas."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    upd = f"update ctas set cuenta='{d_data['cuenta']}',tipo={d_data['tipo']} \
    where id={d_data['id']}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    log(upd)
    con.close()
    return 'ok'


@stock.route('/stock/agregarcuenta', methods=['POST'])
def stock_agregarcuenta():
    """Agregar cuenta."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    ins = f"insert into ctas(cuenta,tipo) values('{d_data['cuenta']}',\
    {d_data['tipo']})"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    log(ins)
    con.close()
    return 'ok'


@stock.route('/stock/borrarcuenta/<int:id_cuenta>')
def stock_borrarcuenta(id_cuenta):
    """Borrar cuenta."""
    con = get_con()
    stm = f"delete from ctas where id={id_cuenta}"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        log(stm)
        con.close()
        return 'ok',200


@stock.route('/stock/cuadro')
def stock_cuadro():
    """Muestro pagina cuadro."""
    return render_template('/stock/cuadro.html')


@stock.route('/stock/obtenerresumenmensual/<mes>')
def stock_obtenerresumenmensual(mes):
    """Obtengo resumen mensual."""
    con = get_con()
    resumen = pgdict(con, f"select caja.cuenta as cuenta,sum(imp) as imp,tipo \
    from caja,ctas where date_format(fecha,'%Y-%m')='{mes}' and caja.cuenta=\
    ctas.cuenta group by caja.cuenta")
    return jsonify(resumen=resumen)


@stock.route('/stock/imprimirstock', methods = ['POST'])
def stock_imprimirstock():
    """Imprimo stock."""
    con = get_con()
    listastock = json.loads(request.data.decode("UTF-8"))
    imprimir_stock(con,listastock)
    return send_file('/home/hero/stock.pdf')
