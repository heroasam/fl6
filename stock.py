from flask import Blueprint,render_template,jsonify,make_response, request
from flask_login import login_required
from lib import *
import ast
from con import con
import pandas as pd

stock = Blueprint('stock',__name__)

@stock.route('/stock/asientos')
def stock_asientos():
    return render_template('stock/asientos.html')


@stock.route('/stock/getasientos')
def stock_getasientos():
    asientos=pgddict(con, f"select id,fecha, cuenta, imp::integer, comentario from caja order by id desc limit 100")
    saldo = pgonecolumn(con, f"select sum(imp::int) from caja")
    return jsonify(asientos=asientos,saldo=saldo)


@stock.route('/stock/deleteasiento/<int:id>')
def stock_deleteasiento(id):
    stm=f'delete from caja where id={id}'
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    cur.close()
    return 'el registro ha sido borrado'


@stock.route('/stock/getcuentas')
def stock_getcuentas():
    cuentas = pglflat(con, f"select cuenta from ctas order by cuenta")
    print(cuentas)
    return jsonify(cuentas=cuentas)


@stock.route('/stock/guardarasiento' , methods = ['POST'])
def stock_guardarasiento():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    tipo = pgonecolumn(con, f"select tipo from ctas where cuenta='{d['cuenta']}'")
    print('tipo',tipo)
    if tipo==0:
        importe = int(d['imp'])*(-1)
    else:
        importe = int(d['imp'])

    ins = f"insert into caja(fecha,cuenta,imp,comentario) values('{d['fecha']}','{d['cuenta']}',{importe},'{d['comentario']}')"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    cur.close()
    return 'OK'


@stock.route('/stock/mayor')
def stock_mayor():
    return render_template('stock/mayor.html')


@stock.route('/stock/getmayor/<string:cuenta>')
def stock_getmayor(cuenta):
    asientos=pgddict(con, f"select id,fecha, cuenta, imp::integer, comentario from caja where cuenta='{cuenta}' order by id desc")
    return jsonify(asientos=asientos)


@stock.route('/stock/pivotcuentas')
def stock_pivotcuentas():
    sql="select ym(fecha) as fecha,cuenta,imp from caja order by id desc"
    pd.options.display.float_format = '{:20.0f}'.format
    dat = pd.read_sql_query(sql, con)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values=['imp'],index='cuenta',columns='fecha',aggfunc='sum').sort_index(1, 'fecha',False)
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="table",classes="table table-sm")
    return render_template("stock/pivot_cuentas.html", tbl=tbl)


@stock.route('/stock/retiros')
def stock_retiros():
    sql="select ym(fecha) as fecha,cuenta,imp from caja where cuenta in ('retiro papi', 'retiro fede') order by id desc"
    pd.options.display.float_format = '{:20.0f}'.format
    dat = pd.read_sql_query(sql, con)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values=['imp'],index='fecha',columns='cuenta',aggfunc='sum')
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="table",classes="table table-sm")
    return render_template("stock/retiros.html", tbl=tbl)


@stock.route('/stock/getcompras')
def stock_getcompras():
    compras=pgddict(con, f"select id,fecha,art,cnt::integer, costo::integer,total::integer,proveedor from artcomprado order by id desc limit 200")
    return jsonify(compras=compras)


@stock.route('/stock/getarticulos')
def stock_getarticulos():
    articulos=pglflat(con, f"select art from articulos")
    return jsonify(articulos=articulos)


@stock.route('/stock/compras')
def stock_compras():
    return render_template('stock/compras.html')


@stock.route('/stock/deletecompra/<int:id>')
def stock_deletecompra(id):
    stm=f'delete from artcomprado where id={id}'
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    cur.close()
    return 'el registro ha sido borrado'


@stock.route('/stock/guardarcompra' , methods = ['POST'])
def stock_guardarcompra():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    ins = f"insert into artcomprado(fecha,cnt,art,costo,total,proveedor) values('{d['fecha']}',{d['cnt']},'{d['art']}',{d['costo']},{d['total']},'{d['proveedor']}')"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    cur.close()
    return 'OK'


@stock.route('/stock/saldosorpresa')
def stock_saldosorpresa():
    pagado = pgonecolumn(con, f"select sum(imp::integer) from caja where cuenta = 'depositos sorpresa'")
    comprado = pgonecolumn(con, f"select sum(total::integer) from artcomprado where proveedor ilike 'Sorpresa' and fecha>'2015-09-20'")
    saldosorpresa = 122031 + comprado + pagado
    return jsonify(saldosorpresa=saldosorpresa)


@stock.route('/stock/getdepositos')
def stock_getdepositos():
    depositos=pgddict(con, f"select fecha,imp::integer from caja where cuenta='depositos sorpresa' order by id desc")
    return jsonify(depositos=depositos)


@stock.route('/stock/generarstock')
def stock_generarstock():
    cur = con.cursor()
    cur.execute('drop table if exists detalles')
    cur.execute("create temp table if not exists detalles as select cnt,art from detvta where idvta>55203 and devuelta=0 UNION ALL select cnt,art from detsalida")
    cur.execute('drop table if exists stockactual')
    cur.execute("create temp table if not exists stockactual as select art,sum(cnt) as ingreso,(select sum(cnt) from detalles where art=artcomprado.art) as egreso from artcomprado where  fecha>'2015-09-15' group by art order by art")
    con.commit()
    cur.close()
    stock = pgddict(con, f"select art, ingreso, egreso, ingreso-egreso as stock from stockactual")
    return jsonify(stock=stock)


@stock.route('/stock/verstock')
def stock_verstock():
    return render_template('stock/verstock.html')


@stock.route('/stock/salidas')
def stock_salidas():
    return render_template('stock/salidas.html')


@stock.route('/stock/getsalidas')
def stock_getsalidas():
    salidas=pgddict(con, f"select id,fecha,cnt,art,costo::integer,comentario from detsalida order by id desc limit 200")
    return jsonify(salidas=salidas)


@stock.route('/stock/deletesalida/<int:id>')
def stock_deletesalida(id):
    stm=f'delete from detsalida where id={id}'
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    cur.close()
    return 'el registro ha sido borrado'


@stock.route('/stock/guardarsalida' , methods = ['POST'])
def stock_guardarsalida():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    ins = f"insert into detsalida(fecha,cnt,art,costo,comentario) values('{d['fecha']}',{d['cnt']},'{d['art']}',{d['costo']},'{d['comentario']}')"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    cur.close()
    return 'OK'


@stock.route('/stock/getlistaarticulos')
def stock_getlistaarticulos():
    articulos=pgddict(con, f"select id,art,costo::integer,activo from articulos order by id desc" )
    return jsonify(articulos=articulos)


@stock.route('/stock/articulos')
def stock_articulos():
    return render_template('stock/articulos.html')


@stock.route('/stock/guardararticulo' , methods = ['POST'])
def stock_guardararticulo():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    ins = f"insert into articulos(art, costo, activo) values('{d['art']}',{d['costo']},{d['activo']})"
    cur = con.cursor()
    try:
        cur.execute(ins)
    except psycopg2.Error as e:
        con.rollback()
        error = e.pgerror
        return make_response(error,400)
    else:
        con.commit()
        cur.close()
        return 'OK'


@stock.route('/stock/deletearticulo/<int:id>')
def stock_deletearticulo(id):
    stm=f'delete from articulos where id={id}'
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    cur.close()
    return 'el registro ha sido borrado'


@stock.route('/stock/articulotoggleactivo/<int:id>')
def stock_articulotoggleactivo(id):
    activo = pgonecolumn(con, f"select activo from articulos where id={id}")
    if activo==1:
        stm = f"update articulos set activo=0 where id={id}"
    else:
        stm = f"update articulos set activo=1 where id={id}"
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    cur.close()
    return 'OK'


@stock.route('/stock/guardaredicionarticulo' , methods = ['POST'])
def stock_guardaredicionarticulo():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    upd = f"update articulos set art='{d['arted']}', costo= {d['costoed']}, activo= {d['activoed']} where id={d['ided']}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except psycopg2.Error as e:
        con.rollback()
        error = e.pgerror
        return make_response(error,400)
    else:
        con.commit()
        cur.close()
        return 'OK'