"""Modulo que responde a todo lo relativo a pagos."""
import re
from flask import Blueprint, render_template, jsonify, make_response,\
     request, send_file, url_for, redirect
from flask_login import login_required
import pandas as pd
import simplejson as json
import mysql.connector
from lib import *
from con import get_con, log, engine, check_roles
from formularios import *

pagos = Blueprint('pagos',__name__)

@pagos.route('/loterbo')
@login_required
@check_roles(['dev','gerente','admin','cobrador'])
def loterbo_():
    return render_template("pagos/loterbo.html" )


@pagos.route('/loterbo/guardarlote/<string:fecha>/<string:cobr>',\
             methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def guardarlote(fecha, cobr):
    """Guarda lote de recibos."""
    con = get_con()
    listarbos = json.loads(request.data.decode("UTF-8"))
    cnt = len(listarbos)
    ins = f"insert into loterbos(fecha,cobr,cnt,procesado) values('{fecha}',{cobr},{cnt},0)"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    idlote = pgonecolumn(con, "select max(id) from loterbos")
    for rbo in listarbos:
        ins = f"insert into rbos(idloterbos,rbo) values({idlote},{rbo})"
        cur.execute(ins)
    con.commit()
    cur.close()
    con.close()
    return jsonify(idlote=idlote)


@pagos.route('/loterbo/imprimir/<string:fecha>/<string:cobr>/<int:idlote>',\
             methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def loterbo_imprimir(fecha,cobr,idlote):
    con = get_con()
    listarbo = json.loads(request.data.decode("UTF-8"))
    # aca se el ast.literal entrega la lista enviada por el axios-post directamente

    estimado = pgdict(con, f"select sum(monto) as cuotas from estimados where cobr={cobr} and mes=date_format(curdate(),'%Y%m')")
    cobrado = pgonecolumn(con, f"select sum(imp+rec) from pagos where cobr={cobr} and date_format(fecha,'%Y-%m')=date_format(curdate(),'%Y-%m')")
    if cobrado is None:
        cobrado = 0
    loterbo(con, listarbo,fecha,cobr,idlote, estimado['cuotas'], cobrado)
    con.close()
    return send_file('/home/hero/loterbo.pdf')

@pagos.route('/loterbo/reimprimir/<string:fecha>/<string:cobr>/<int:idlote>')
@login_required
@check_roles(['dev','gerente','admin'])
def loterbo_reimprimir(fecha,cobr,idlote):
    con = get_con()
    listarbo = pglist(con, f"select rbo from rbos where idloterbos={idlote}")
    estimado = pglistdict(con, f"select date_format(pmovto,'%Y-%m') as periodo,sum(cuota) as cuotas from clientes,zonas where clientes.zona=zonas.zona and pmovto>date_sub(curdate(),interval 180 day)  and zonas.zona not like '-%' and asignado={cobr} group by periodo having periodo=date_format(curdate(),'%Y-%m')")[0]
    cobrado = pgonecolumn(con, f"select sum(imp+rec) from pagos where cobr={cobr} and date_format(fecha,'%Y-%m')=date_format(curdate(),'%Y-%m')")
    if cobrado is None:
        cobrado = 0
    loterbo(con, listarbo, fecha,cobr,idlote,estimado['cuotas'],cobrado)
    con.close()
    return send_file('/home/hero/loterbo.pdf')


@pagos.route('/loterbo/ver')
@login_required
@check_roles(['dev','gerente','admin'])
def loterbo_ver():
    return render_template("pagos/loterbover.html")


@pagos.route('/loterbo/getlistalotesrbo')
@login_required
@check_roles(['dev','gerente','admin'])
def loterbo_getlistalotesrbo():
    con = get_con()
    lotesrbo = pglistdict(con,f"select id,fecha,cobr,cnt from loterbos order by id desc limit 100")
    con.close()
    return jsonify(listalotesrbo=lotesrbo)


@pagos.route('/loterbo/delete/<string:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def loterbo_delete(id):
    con = get_con()
    cur = con.cursor()
    cur.execute("delete from loterbos where id={0}".format(id))
    con.commit()
    cur.close()
    con.close()
    return redirect(url_for('pagos.loterbo_ver'))

@pagos.route('/loterbo/buscanombrecobr/<int:cobr>')
@login_required
@check_roles(['dev','gerente','admin'])
def loterbo_buscanombrecobr(cobr):
    con = get_con()
    nombrecobr = pgonecolumn(con, f"select nombre from cobr where id={cobr} and activo=1 and prom=0")
    con.close()
    if len(nombrecobr)>0:
        return jsonify(nombrecobr=nombrecobr)
    else:
        return make_response("error", 404)


@pagos.route('/loterbo/getidcobradores')
@login_required
@check_roles(['dev','gerente','admin'])
def loterbo_getidcobradores():
    con = get_con()
    idcobradores = pglist(con, "select id from cobr where activo=1 and prom=0 and id>500")
    return jsonify(idcobradores=idcobradores)


@pagos.route('/pagos')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_():
    return render_template("pagos/pagos.html")


@pagos.route('/pagos/listado/<string:fechapago>/<int:cobrador>')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_listado(fechapago, cobrador):
    con = get_con()
    listado = pglistdict(con, f"select pagos.id as id, rbo, fecha, idvta,imp as imp, rec as rec, (imp+rec) as total, nombre, concat(calle,' ',num) as direccion, zona,deuda as deuda from pagos, clientes where clientes.id=pagos.idcliente and fecha='{fechapago}' and pagos.cobr={cobrador} order by id desc")
    planilla = pglistdict(con, f"select * from planillas where fecha='{fechapago}' and idcobr={cobrador}")
    con.close()
    return jsonify(listado=listado, planilla=planilla)


@pagos.route('/pagos/buscar/<string:cuenta>')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_buscar(cuenta):
    con = get_con()
    rcuenta = r'^[0-9]{5}$'
    rdni = r'^[0-9]{7,8}$'
    if (re.match(rcuenta,cuenta)):
        sql = f"select nombre,concat(calle,' ',num) as direccion,dni from clientes,ventas where clientes.id=ventas.idcliente and ventas.id={cuenta}"
    elif (re.match(rdni,cuenta)):
        sql = f"select nombre,concat(calle,' ',num) as direccion,dni from clientes where dni='{cuenta}'"
    else:
        cuenta = '%'+cuenta.replace(' ','%')+'%'
        sql = f"select nombre,concat(calle,' ',num) as direccion,dni from clientes where lower(concat(nombre,calle,num,barrio)) like lower('{cuenta}') and deuda>0"
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    clientes = cur.fetchall()
    con.close()
    return jsonify(clientes=clientes)


@pagos.route('/pagos/idvtas/<string:dni>')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_idvtas(dni):
    con = get_con()
    sel = f"select ventas.id as id,concat(calle,' ',num) from ventas,clientes where clientes.id=ventas.idcliente and dni='{dni}' and saldo>0"
    idvtas = pglistdict(con,sel)
    con.close()
    return jsonify(idvtas=idvtas)


@pagos.route('/pagos/traerficha/<int:idvta>')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_traerficha(idvta):
    con = get_con()
    sql = f"select id,case when saldo<ic then saldo else ic end as imp,ic,saldo,idcliente from ventas where id={idvta}"
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    ficha = cur.fetchone()
    con.close()
    return jsonify(ficha=ficha)


@pagos.route('/pagos/pasarpagos' , methods = ['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_pasarpagos():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    if(d['rec']==''):
        d['rec']=0
    ins = f"insert into pagos(idvta,fecha,imp,rec,rbo,cobr,idcliente) values({d['idvta']},'{d['fecha']}',{d['imp']},{d['rec']},{d['rbo']},{d['cobr']},{d['idcliente']})"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    con.close()
    log(ins)
    return 'ok'


@pagos.route('/pagos/borrarpago/<int:idpago>')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_borrarpago(idpago):
    con = get_con()
    stm = f"delete from pagos where id={idpago}"
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    log(stm)
    con.close()
    return 'ok'

@pagos.route('/pagos/pasarplanilla', methods = ['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_pasarplanilla():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    idplanilla = pgonecolumn(con,f"select id from planillas where fecha = '{d['fecha']}' and idcobr={d['idcobr']}")
    if(d['viatico']==""):
        d['viatico']=0
    ins = f"insert into planillas(fecha, idcobr, idlote,cobrado, comision, viatico, cntrbos) values('{d['fecha']}','{d['idcobr']}',0,{d['cobrado']},{d['comision']},{d['viatico']},{d['cntrbos']})"
    upd = f"update planillas set fecha='{d['fecha']}', idcobr='{d['idcobr']}',idlote=0,cobrado={d['cobrado']},comision={d['comision']},viatico={d['viatico']},cntrbos={d['cntrbos']} where id={idplanilla}"
    cur = con.cursor()
    if(idplanilla==""):
        cur.execute(ins)
        log(ins)
    else:
        cur.execute(upd)
        log(upd)
    con.commit()
    con.close()
    return 'ok'


@pagos.route('/pagos/corregirplanillacobrador', methods = ['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_corregirplanillascobradores():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    upd = f"update pagos set cobr={d['cobr2']} where fecha='{d['fecha']}' and cobr={d['cobr']}"
    stm = f"delete from planillas where fecha='{d['fecha']}' and idcobr={d['cobr']}"
    cur = con.cursor()
    try:
        cur.execute(upd)
        cur.execute(stm)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        log(upd)
        log(stm)
        con.close()
        return 'ok'


@pagos.route('/pagos/corregirplanillacobradorseleccionados', methods = ['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_corregirplanillascobradoresseleccionados():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    lpg ='('
    for idpago in d['ids']:
        lpg+=str(idpago)+','
        lpg = lpg[0:-1]+')'
    upd = f"update pagos set cobr={d['cobr2']} where id in {lpg}"
    stm = f"delete from planillas where fecha='{d['fecha']}' and idcobr={d['cobr']}"
    cur = con.cursor()
    try:
        cur.execute(upd)
        cur.execute(stm)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        log(upd)
        log(stm)
        con.close()
        return 'ok'


@pagos.route('/pagos/verplanillas')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_verplanillas():
    return render_template("pagos/planillas.html" )

@pagos.route('/pagos/getplanillas')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_getplanillas():
    con = get_con()
    planillas = pglistdict(con,f"select planillas.fecha as fecha,sum(cobrado) as cobrado,sum(comision) as comision,sum(viatico) as viatico,sum(cntrbos) as cntrbos,(select imp from caja where comentario='global' and cuenta='cobranza' and fecha=planillas.fecha) as cobradocaja, (-1)*(select imp from caja where comentario='via' and cuenta='cobranza' and fecha=planillas.fecha) as viaticocaja from planillas  where planillas.fecha>date_sub(curdate(), interval 60 day) group by planillas.fecha order by planillas.fecha desc")
    con.close()
    return jsonify(planillas=planillas)


@pagos.route('/pagos/getplanillas/<string:fecha>')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_getplanillashoy(fecha):
    con = get_con()
    planillas = pglistdict(con,f"select fecha,idcobr,cobrado,comision,viatico,cntrbos,idlote from planillas where fecha='{fecha}'")
    con.close()
    return jsonify(planillas=planillas)


@pagos.route('/pagos/getplanillascobr')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_getplanillascobr():
    con = get_con()
    planillascobr = pglistdict(con, f"select fecha,idcobr,cobrado,comision,viatico,cntrbos from planillas order by fecha desc limit 100")
    con.close()
    return jsonify(planillascobr=planillascobr)


@pagos.route('/pagos/procesarplanilla', methods = ['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_procesarplanilla():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    fecha = d['fecha']
    stmdel = f"delete from caja where cuenta='cobranza' and fecha='{fecha}'"
    ins1 = f"insert into caja(fecha,cuenta,imp,comentario) values('{fecha}','cobranza',{d['cobrado']},'global')"
    ins2 = f"insert into caja(fecha,cuenta,imp,comentario) values('{fecha}','cobranza',{-1*int(d['comision'])},'com')"
    ins3 = f"insert into caja(fecha,cuenta,imp,comentario) values('{fecha}','cobranza',{-1*int(d['viatico'])},'via')"
    cur = con.cursor()
    cur.execute(stmdel)
    con.commit()
    cur.execute(ins1)
    cur.execute(ins2)
    cur.execute(ins3)
    log(ins1)
    log(ins2)
    log(ins3)
    con.commit()
    cur.close()
    con.close()
    return "OK"

@pagos.route('/pagos/editarrbo')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_editarrbo():
    return render_template('pagos/editarrbo.html' )


@pagos.route('/pagos/obtenerrbo/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_obtenerrbo(id):
    con = get_con()
    reg = pglistdict(con, f"select fecha, idvta, imp, rec, rbo, cobr, id, (select nombre from clientes where clientes.id=pagos.idcliente) as nombre from pagos where id={id}")
    con.close()
    return jsonify (reg=reg)


@pagos.route('/pagos/obtenernuevonombre/<int:idvta>')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_obtenernuevonombre(idvta):
    con = get_con()
    idcliente = pgonecolumn(con, f"select idcliente from ventas where id={idvta}")
    nombre = pgonecolumn(con, f"select nombre from clientes where id={idcliente}")
    return jsonify(nombre=nombre)


@pagos.route('/pagos/obtenerregrbo/<int:buscar>')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_obtenerregrbo(buscar):
    con = get_con()
    try:
        reg = pglistdict(con, f"select pagos.id as id, fecha, idvta, imp, rec, rbo, cobr, idcliente, nombre from pagos,clientes where clientes.id=pagos.idcliente and  rbo={buscar}")
        # idcliente = pgonecolumn(con, f"select idcliente from pagos where rbo={buscar}")
        # nombre = pgonecolumn(con, f"select nombre from clientes where id={idcliente}")
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.close()
        return jsonify (reg=reg)


@pagos.route('/pagos/borrarrbo/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_borrarrbo(id):
    con = get_con()
    stm = f"delete from pagos where id={id}"
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    log(stm)
    cur.close()
    idvta = pgonecolumn(con,f"select idvta from pagos where id={id}")
    con.close()
    return 'ok'

@pagos.route('/pagos/guardaredicionrbo' , methods = ['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_guardaredicionrbo():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    idcliente = pgonecolumn(con, f"select idcliente from ventas where id={d['idvta']}")
    upd = f"update pagos set fecha='{d['fecha']}', idvta={d['idvta']}, imp={d['imp']}, rec={d['rec']}, rbo={d['rbo']}, cobr={d['cobr']}, idcliente={idcliente} where id={d['id']}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    log(upd)
    cur.close()
    idvta = pgonecolumn(con,f"select idvta from pagos where id={d['id']}")
    con.close()
    return 'OK'


@pagos.route('/pagos/getzonasasignadas')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_getzonasasignadas():
    con = get_con()
    zonas = pglistdict(con, f"select zonas.id as id,zonas.zona as zona,asignado as cobr,(select nombre from cobr where cobr.id=asignado) as nombre, count(*) as cnt, sum(cuota) as cuotas from zonas,clientes where clientes.zona=zonas.zona and pmovto>=date_sub(curdate(),interval 90 day) and zonas.zona not like '-%' group by zonas.id order by asignado")
    con.close()
    return jsonify(zonas=zonas)


@pagos.route('/pagos/verzona')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_verzona():
    return render_template('pagos/verzona.html' )


@pagos.route('/pagos/editarasignado', methods = ['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_editarasignado():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    upd = f"update zonas set asignado={d['cobr']} where id={d['id']}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    log(upd)
    cur.close()
    con.close()
    return 'ok'


@pagos.route('/pagos/gettotaleszonas')
@login_required
@check_roles(['dev','gerente'])
def pagos_gettotaleszonas():
    con = get_con()
    totales = pglistdict(con, f"select asignado as cobr,(select nombre from cobr where cobr.id=asignado) as nombre, sum(cuota) as total from zonas,clientes where clientes.zona=zonas.zona and pmovto>=date_sub(curdate(),interval 90 day) and zonas.zona not like '-%' group by asignado order by asignado")
    con.close()
    return jsonify(totales=totales)


@pagos.route('/pagos/cobrostotales')
@login_required
@check_roles(['dev','gerente'])
def pagos_cobrostotales():
    pd.options.display.float_format = '${:.0f}'.format
    sql="select date_format(fecha,'%Y-%m') as fp,imp+rec as cuota,cobr from pagos where fecha >date_sub(curdate(),interval 365 day)"
    sql1="select date_format(fecha,'%Y-%m') as fp,imp+rec as cuota,pagos.cobr as cobr,zona,(select asignado from zonas where zona=clientes.zona) as asignado from pagos,clientes where clientes.id=pagos.idcliente and fecha >date_sub(curdate(),interval 365 day) and zona not like '-%'"
    dat = pd.read_sql_query(sql, engine)
    dat1= pd.read_sql_query(sql1,engine)
    df = pd.DataFrame(dat)
    df1 = pd.DataFrame(dat1)
    tbl = pd.pivot_table(df, values=['cuota'],index='cobr',columns='fp',aggfunc='sum').sort_index(axis=1, level='fp',ascending=False)
    tbl1 = pd.pivot_table(df1, values=['cuota'],index=['asignado','zona'],columns='fp',aggfunc='sum').sort_index(axis=1, level='fp',ascending=False)
    tbl = tbl.fillna("")
    tbl1 = tbl1.fillna("")
    index = tbl.columns.tolist()
    tbl = tbl.to_html(table_id="totales",classes="table")
    tbl1 = tbl1.to_html(table_id="totaleszona",classes="table")
    return render_template("pagos/totales.html", tbl=tbl, tbl1=tbl1, index=index )


@pagos.route('/pagos/estimados')
@login_required
@check_roles(['dev','gerente'])
def pagos_estimados():
    pd.options.display.float_format = '${:.0f}'.format
    sql="select date_format(pmovto,'%Y-%m') as pmovto,cuota,asignado,clientes.zona as zona from clientes,zonas where clientes.zona=zonas.zona and pmovto>date_sub(curdate(),interval 180 day)  and zonas.zona not like '-%'"
    sql1="select date_format(pmovto,'%Y-%m') as pmovto,cuota,asignado,clientes.zona as zona from clientes,zonas where clientes.zona=zonas.zona and pmovto>date_sub(curdate(),interval 180 day)  and zonas.zona not like '-%'"
    dat = pd.read_sql_query(sql, engine)
    dat1= pd.read_sql_query(sql1,engine)
    df = pd.DataFrame(dat)
    df1 = pd.DataFrame(dat1)
    tbl = pd.pivot_table(df, values=['cuota'],index='asignado',columns='pmovto',aggfunc='sum').sort_index(axis=1, level='pmovto',ascending=False)
    tbl1 = pd.pivot_table(df1, values=['cuota'],index=['asignado','zona'],columns='pmovto',aggfunc='sum').sort_index(axis=1, level='pmovto',ascending=False)
    tbl = tbl.fillna("")
    index = tbl.columns.values.tolist()
    # aca entregamos el valor de las columnas como indice
    tbl1 = tbl1.fillna("")
    tbl = tbl.to_html(table_id="estimados",classes="table")
    tbl1 = tbl1.to_html(table_id="estimadoszona",classes="table")
    return render_template("pagos/estimados.html", tbl=tbl, tbl1=tbl1, index=index )


@pagos.route('/pagos/estimadosmes')
@login_required
@check_roles(['dev','gerente'])
def pagos_estimadosmes():
    con = get_con()
    pd.options.display.float_format = '${:.0f}'.format
    sql="select date_format(pmovto,'%Y-%m') as pmovto,cuota,asignado,clientes.zona as zona from clientes,zonas where clientes.zona=zonas.zona and date_format(pmovto,'%Y%m')=date_format(curdate(),'%Y%m')  and zonas.zona not like '-%'"
    dat = pd.read_sql_query(sql, engine)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values=['cuota'],index='asignado',columns='pmovto',aggfunc='sum')
    tbl = tbl.fillna("")
    tbl1 = pd.pivot_table(df, values=['cuota'],index='zona',columns='pmovto',aggfunc='sum')
    tbl1 = tbl1.fillna("")
    #index = tbl.columns.values.tolist()
    # aca entregamos el valor de las columnas como indice
    tbl = tbl.to_json()
    tbl1 = tbl1.to_json()
    tbl = tbl.split(')":')[1][:-1]
    tbl1 = tbl1.split(')":')[1][:-1]
    d = tbl1[1:-1]
    d = d.split(',')

    for item in d:
        k,v = item.split(':')
        k = k[1:-1]
        cobr = pgonecolumn(con, f"select asignado from zonas where zona='{k}'")
        ins = f"insert into estimados(mes,zona,monto,cobr) values(\
        date_format(curdate(),'%Y%m'),'{k}',{v},{cobr})"
        pgexec(con, ins)
    return 'ok'


@pagos.route('/pagos/comisiones')
@login_required
@check_roles(['dev','gerente'])
def pagos_comisiones():
    pd.options.display.float_format = '${:.0f}'.format
    sql="select date_format(fecha,'%Y-%m') as fecha,imp+rec as cobranza,(imp+rec)*0.15 as comision,cobr from pagos where cobr in (750,815,796,800,802) and fecha>date_sub(curdate(), interval 1 year)"
    dat = pd.read_sql_query(sql, engine)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values=['comision'],index='fecha',columns='cobr',aggfunc='sum').sort_index(axis=0, level='fecha',ascending=False)
    tbl = tbl.fillna("")
    c750 = tbl.iloc[:,0][:12].tolist()
    c796 = tbl.iloc[:,1][:12].tolist()
    c800 = tbl.iloc[:,2][:12].tolist()
    c802 = tbl.iloc[:,3][:12].tolist()
    c815 = tbl.iloc[:,4][:12].tolist()
    index = tbl.index[:12].tolist()
    tbl = tbl.to_html(table_id="tablecomisiones",classes="table")
    return render_template("pagos/comisiones.html", tbl=tbl,c750=c750,c796=c796,c800=c800,c802=c802,c815=c815,index=index )


@pagos.route('/pivot/pagos_cobr')
@login_required
@check_roles(['dev','gerente','admin'])
def pivot_pagos_cobr():
    sql="select date_format(fecha,'%Y-%m') as fecha,imp+rec as cobranza,(imp+rec)*0.15 as comision,cobr from pagos where cobr in (750,815,796,800,816) and fecha>'2018-07-31'"
    dat = pd.read_sql_query(sql, engine)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values=['comision','cobranza'],index='fecha',columns='cobr',aggfunc='sum')
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="table",classes="table table-sm")
    return render_template("pivot_cobr.html", tbl=tbl)


@pagos.route('/pivot/retiros')
@login_required
@check_roles(['dev','gerente'])
def pivot_retiros():
    sql="select date_format(fecha,'%Y-%m') as fecha, cuenta, imp from caja where cuenta like 'retiro%' and not like '%capital%' order by fecha desc"
    dat = pd.read_sql_query(sql, engine)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values='imp',index='fecha',columns='cuenta',aggfunc='sum').sort_index(axis=1, level='fecha',ascending=False)
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="table",classes="table  table-sm")
    return render_template("pivot_retiros.html", tbl=tbl)


@pagos.route('/pivot/retiros/excel')
@login_required
@check_roles(['dev','gerente'])
def pivot_retiros_excel():
    sql="select date_format(fecha,'%Y-%m') as fecha, cuenta, imp from caja where cuenta like 'retiro%'"
    dat = pd.read_sql_query(sql, engine)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values='imp',index='fecha',columns='cuenta',aggfunc='sum')
    tbl = tbl.fillna("")
    tbl = tbl.to_excel('retiros.xlsx', index=False)
    return send_file('retiros.xlsx')


@pagos.route('/pagos/altas')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_altas():
    return render_template('pagos/altas.html')

@pagos.route('/pagos/loadaltas')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_loadaltas():
    con = get_con()
    listaltas = pglistdict(con, f"select id,nombre,dni,sex, calle,num,deuda,ultpago,subirseven from clientes where subirseven=1 and alta is null order by deuda")
    con.close()
    return jsonify(listaltas=listaltas)


@pagos.route('/pagos/togglesube/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_togglesube(id):
    con = get_con()
    subir = pgonecolumn(con, f"select subirseven from clientes where id={id}")
    if subir==1:
        upd = f"update clientes set subirseven=0 where id={id}"
    else:
        upd = f"update clientes set subirseven=1 where id={id}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    log(upd)
    cur.close()
    con.close()
    return 'OK'


@pagos.route('/pagos/sevenaltas')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_sevenaltas():
    con = get_con()
    sevenaltas = pglisttuples(con, f"select 2210,dni,dni,3,sex,'','',nombre,concat(calle,' ',num),5000,barrio,'Cordoba','Cordoba','M', date_format(current_date(),'%Y-%m-%d'),0,'01','',wapp from clientes where subirseven=1 and alta is null")
    con.close()
    return jsonify(sevenaltas=sevenaltas)


@pagos.route('/pagos/marcarsubidos', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_marcarsubidos():
    con = get_con()
    listadni = json.loads(request.data.decode("UTF-8"))
    lpg ='('
    for dni in listadni:
        lpg+=str(dni)+','
    lpg = lpg[0:-1]+')'
    upd = f"update clientes set subirseven=0,sev=1,alta=date_format(current_date(),'%Y-%m-%d') where dni in {lpg}"
    cur = con.cursor()
    try:
        cur.execute(upd)
        log(upd)
        for dni in listadni:
            idcliente = pgonecolumn(con, f"select id from clientes where dni={dni}")
            ins = f"insert into seven(idcliente,codigo,fecha) values({idcliente},'A',date_format(current_date(),'%Y-%m-%d'))"
            cur.execute(ins)
            log(ins)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        cur.close()
        con.close()
        return 'OK'


@pagos.route('/pagos/loadbajas')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_loadbajas():
    con = get_con()
    listbajas = pglistdict(con, f"select dni,nombre,dni, 'Cancelado' as canc, ultpago from clientes where sev=1 and deuda=0")
    print(listbajas)
    con.close()
    return jsonify(listbajas=listbajas)


@pagos.route('/pagos/sevenbajas')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_sevenbajas():
    con = get_con()
    sevenbajas = pglisttuples(con, f"select dni,nombre,dni,'Cancelado' as canc,ultpago from clientes where sev=1 and deuda=0")
    print(sevenbajas)
    return jsonify(sevenbajas=sevenbajas)


@pagos.route('/pagos/bajas')
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_bajas():
    return render_template('pagos/bajas.html')


@pagos.route('/pagos/prestamos')
@login_required
@check_roles(['dev','gerente'])
def pagos_prestamos():
    return render_template('pagos/prestamos.html')


@pagos.route('/pagos/marcarbajados', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def pagos_marcarbajados():
    con = get_con()
    listadni = json.loads(request.data.decode("UTF-8"))
    lpg ='('
    for dni in listadni:
        lpg+=str(dni)+','
    lpg = lpg[0:-1]+')'
    upd = f"update clientes set sev=0,baja=date_format(current_date(),'%Y-%m-%d') where dni in {lpg}"
    cur = con.cursor()
    try:
        cur.execute(upd)
        log(upd)
        for dni in listadni:
            idcliente = pgonecolumn(con, f"select id from clientes where dni={dni}")
            ins = f"insert into seven(idcliente,codigo,fecha) values({idcliente},'B',date_format(current_date(),'%Y-%m-%d'))"
            cur.execute(ins)
            log(ins)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        cur.close()
        con.close()
        return 'OK'


@pagos.route('/pagos/getvdorcondeuda')
@login_required
@check_roles(['dev','gerente'])
def pagos_getvdorcondeuda():
    con = get_con()
    vendedores = pglist(con, "select distinct codigo from caja where cuenta \
    in ('prestamos empleados','recupero prestamos') and fecha>'2022-01-01'")
    return jsonify(vendedores=vendedores)


@pagos.route('/pagos/getprestamosvdor/<int:vdor>')
@login_required
@check_roles(['dev','gerente'])
def pagos_getprestamosvdor(vdor):
    con = get_con()
    prestamos = pglistdict(con, f"select fecha, imp, cuenta from caja \
    where cuenta in ('prestamos empleados','recupero prestamos') \
    and fecha>'2022-01-01' and codigo like '%{vdor}%' order by fecha desc")
    return jsonify(prestamos=prestamos)


@pagos.route('/pagos/pivotcobros')
@login_required
@check_roles(['dev','gerente'])
def pagos_pivotcobros():
    return render_template('pagos/pivotcobros.html' )


@pagos.route('/pagos/getcobroscobrador')
@login_required
@check_roles(['dev','gerente'])
def pagos_getcobroscobrador():
    con = get_con()
    listacobros = pglistdict(con, f"select id , (select sum(imp+\
    rec) from pagos where cobr=cobr.id and date_format(fecha,'%Y%m')=\
    date_format(curdate(),'%Y%m')) as cobrado, (select sum(monto) from \
    estimados where cobr=cobr.id and \
    mes = date_format(curdate(),'%Y%m') group by cobr) as estimado \
    from cobr where activo=1 and prom=0 and id not in (10,816,835,820)")
    return jsonify(listacobros=listacobros)


@pagos.route('/pagos/getcobroszonas/<int:cobr>')
@login_required
@check_roles(['dev','gerente'])
def pagos_getcobroszonas(cobr):
    con = get_con()
    listacobroszonas = pglistdict(con, f"select clientes.zona , (select \
    sum(imp+rec) from pagos where cobr={cobr} and date_format(fecha,'%Y%m')=\
    date_format(curdate(),'%Y%m') and idcliente in (select id from clientes \
    as clientes1 where clientes1.zona=clientes.zona)) as cobrado,  (select monto from estimados where cobr={cobr} and \
    mes = date_format(curdate(),'%Y%m') and zona=clientes.zona) as estimado from clientes,zonas where \
    clientes.zona=zonas.zona and asignado={cobr} group by clientes.zona")
    return jsonify(listacobroszonas=listacobroszonas)


@pagos.route('/pagos/acumulativo')
@login_required
@check_roles(['dev','gerente'])
def pagos_acumulativo():
    return render_template('pagos/acumulativo.html' )


@pagos.route('/pagos/getpagosacumulativos')
@login_required
@check_roles(['dev','gerente'])
def pagos_getpagosacumulativos():
    con = get_con()
    mesactual = pgonecolumn(con, "select date_format(curdate(),'%Y-%m')")
    mespasado = pgonecolumn(con, "select date_format(date_sub(curdate(),\
    interval 1 month), '%Y-%m')")
    antepenultimo = pgonecolumn(con, "select date_format(date_sub(curdate(),\
    interval 2 month), '%Y-%m')")
    pagosestemes = pglist(con, f"select sum(imp+rec) from pagos where \
    date_format(fecha,'%Y-%m')='{mesactual}' and cobr>15 and cobr!=816 and \
    cobr != 835 group by fecha")
    pagosmespasado = pglist(con, f"select sum(imp+rec) from pagos where \
    date_format(fecha,'%Y-%m')='{mespasado}' and cobr>15 and cobr!=816 and \
    cobr != 835 group by fecha")
    pagosantepenultimo = pglist(con, f"select sum(imp+rec) from pagos where \
    date_format(fecha,'%Y-%m')='{antepenultimo}' and cobr>15 and cobr!=816 and \
    cobr != 835 group by fecha")
    return jsonify(pagosestemes=pagosestemes,pagosmespasado=pagosmespasado,\
                   pagosantepenultimo=pagosantepenultimo)
