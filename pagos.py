from flask import Blueprint,render_template,jsonify,make_response, request, send_file,url_for,redirect
from flask_login import login_required
from lib import *
import json
from con import get_con
import pandas as pd
import re
from formularios import *
import mysql.connector

pagos = Blueprint('pagos',__name__)

@pagos.route('/loterbo')
@login_required
def loterbo_():
    return render_template("pagos/loterbo.html" )


@pagos.route('/loterbo/guardarlote/<string:fecha>/<string:cobr>', methods = ['POST'])
def guardarlote(fecha,cobr):
    con = get_con()
    listarbos = json.loads(request.data.decode("UTF-8"))
    cnt = len(listarbos)
    print(listarbos)
    ins = f"insert into loterbos(fecha,cobr,cnt,procesado) values('{fecha}',{cobr},{cnt},0)"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    idlote = pgonecolumn(con, f"select max(id) from loterbos")
    for rbo in listarbos:
        ins = f"insert into rbos(idloterbos,rbo) values({idlote},{rbo})"
        cur.execute(ins)
    con.commit()
    cur.close()
    return "OK"

@pagos.route('/loterbo/obtenerlastid')
def obtenerlastid():
    con = get_con()
    idlote = str(pgonecolumn(con, f"select max(id) from loterbos"))
    return jsonify(idlote=idlote)

@pagos.route('/loterbo/imprimir/<string:fecha>/<string:cobr>/<int:idlote>', methods = ['POST'])
def loterbo_imprimir(fecha,cobr,idlote):
    con = get_con()
    listarbo = json.loads(request.data.decode("UTF-8"))
    # aca se el ast.literal entrega la lista enviada por el axios-post directamente

    loterbo(con, listarbo,fecha,cobr,idlote)
    return send_file('loterbo.pdf')

@pagos.route('/loterbo/reimprimir/<string:fecha>/<string:cobr>/<int:idlote>')
def loterbo_reimprimir(fecha,cobr,idlote):
    con = get_con()
    listarbo = pglflat(con, f"select rbo from rbos where idloterbos={idlote}")
    print(listarbo)
    loterbo(con, listarbo, fecha,cobr,idlote)
    return send_file('loterbo.pdf')


@pagos.route('/loterbo/ver')
@login_required
def loterbo_ver():
    con = get_con()
    lotesrbo = pgddict(con,f"select id,fecha,cobr,cnt from loterbos order by id desc limit 100")
    return render_template("pagos/loterbover.html", lotesrbo=lotesrbo )

@pagos.route('/loterbo/delete/<string:id>')
def loterbo_delete(id):
    con = get_con()
    cur = con.cursor()
    cur.execute("delete from loterbos where id={0}".format(id))
    con.commit()
    cur.close()
    return redirect(url_for('pagos.loterbo_ver'))

@pagos.route('/loterbo/buscanombrecobr/<int:cobr>')
def loterbo_buscanombrecobr(cobr):
    con = get_con()
    nombrecobr = pgonecolumn(con, f"select nombre from cobr where id={cobr}")
    return jsonify(nombrecobr=nombrecobr)



@pagos.route('/pagos')
@login_required
def pagos_():
    return render_template("pagos/pagosvue.html" )

@pagos.route('/pagos/planilla/<string:fechapago>/<int:cobrador>')
def pagos_planilla(fechapago,cobrador):
    con = get_con()
    planilla = pgdict(con,f"select pagos.id as id, rbo, fecha, idvta,imp as imp, rec as rec, (imp+rec) as total, nombre, calle||' '||num as direccion, zona,deuda as deuda from pagos, clientes where clientes.id=pagos.idcliente and fecha='{fechapago}' and pagos.cobr={cobrador} order by id desc")
    lote = pgonecolumn(con,f"select lote from pagos where fecha='{fechapago}' and cobr={cobrador}")
    if lote=='':
        cntrbos = 0
    else:
        cntrbos = pgonecolumn(con, f"select count(*) from (select distinct rbo from pagos where lote={lote}) as foo")
    return jsonify(planilla=planilla,lote=lote,cntrbos=cntrbos)


@pagos.route('/pagos/buscar/<string:cuenta>')
def pagos_buscar(cuenta):
    con = get_con()
    rcuenta = r'^[0-9]{5}$'
    rdni = r'^[0-9]{7,8}$'
    if (re.match(rcuenta,cuenta)):
        clientes = pgdict(con,f"select nombre,calle||' '||num as direccion,dni from clientes,ventas where clientes.id=ventas.idcliente and ventas.id={cuenta}")
    elif (re.match(rdni,cuenta)):
        clientes = pgdict(con,f"select nombre,calle||' '||num as direccion,dni from clientes where dni='{cuenta}'")
    else:
        cuenta = '%'+cuenta.replace(' ','%')+'%'
        print(cuenta)
        clientes = pgdict(con,f"select nombre,calle||' '||num as direccion,dni from clientes where nombre||calle||num||barrio ilike '{cuenta}' and deuda>0")
    return jsonify(clientes=clientes)


@pagos.route('/pagos/idvtas/<string:dni>')
def pagos_idvtas(dni):
    con = get_con()
    sel = f"select ventas.id as id,calle||' '||num from ventas,clientes where clientes.id=ventas.idcliente and dni='{dni}' and saldo>0"
    idvtas = pgdict(con,sel)
    return jsonify(idvtas=idvtas)


@pagos.route('/pagos/traerficha/<int:idvta>')
def pagos_traerficha(idvta):
    con = get_con()
    ficha = pgdict(con,f"select id,case when saldo<ic then saldo else ic end as imp,ic,saldo from ventas where id={idvta}")
    return jsonify(ficha=ficha)


@pagos.route('/pagos/pasarpagos' , methods = ['POST'])
def pagos_pasarpagos():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    idcliente = pgonecolumn(con,f"select idcliente from ventas where id={d['idvta']}")
    if(d['rec']==''):
        d['rec']=0
    ins = f"insert into pagos(idvta,fecha,imp,rec,rbo,cobr,idcliente,lote) values({d['idvta']},'{d['fecha']}',{d['imp']},{d['rec']},{d['rbo']},{d['cobr']},{idcliente},{d['lote']})"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    trigger_pago(con, d['idvta'])
    return 'ok'


@pagos.route('/pagos/borrarpago/<int:idpago>')
def pagos_borrarpago(idpago):
    con = get_con()
    stm = f"delete from pagos where id={idpago}"
    cur = con.cursor()
    idvta = pgonecolumn(con,f"select idvta from pagos where id={idpago}")
    cur.execute(stm)
    con.commit()
    trigger_pago(con, idvta)
    return 'ok'

@pagos.route('/pagos/pasarplanilla', methods = ['POST'])
def pagos_pasarplanilla():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    idplanilla = pgonecolumn(con,f"select id from planillas where fecha = '{d['fecha']}' and idcobr={d['idcobr']}")
    if(d['viatico']==""):
        d['viatico']=0
    ins = f"insert into planillas(fecha, idcobr, idlote,cobrado, comision, viatico, cntrbos) values('{d['fecha']}','{d['idcobr']}',{d['idlote']},{d['cobrado']},{d['comision']},{d['viatico']},{d['cntrbos']})"
    upd = f"update planillas set fecha='{d['fecha']}', idcobr='{d['idcobr']}',idlote={d['idlote']},cobrado={d['cobrado']},comision={d['comision']},viatico={d['viatico']},cntrbos={d['cntrbos']} where id={idplanilla}"
    cur = con.cursor()
    if(idplanilla==""):
        cur.execute(ins)
    else:
        cur.execute(upd)
    con.commit()
    return 'ok'


@pagos.route('/pagos/verplanillas')
def pagos_verplanillas():
    return render_template("pagos/planillas.html" )

@pagos.route('/pagos/getplanillas')
def pagos_getplanillas():
    con = get_con()
    planillas = pgdict(con,f"select planillas.fecha as fecha,sum(cobrado),sum(comision),sum(viatico),sum(cntrbos),(select imp from caja where comentario='global' and cuenta='cobranza' and fecha=planillas.fecha) from planillas group by planillas.fecha order by planillas.fecha desc limit 100")
    return jsonify(planillas=planillas)


@pagos.route('/pagos/getplanillas/<string:fecha>')
def pagos_getplanillashoy(fecha):
    con = get_con()
    planillas = pgdict(con,f"select fecha,idcobr,cobrado,comision,viatico,cntrbos,idlote from planillas where fecha='{fecha}'")
    return jsonify(planillas=planillas)


@pagos.route('/pagos/procesarplanilla', methods = ['POST'])
def pagos_procesarplanilla():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    fecha = d['fecha']
    ins1 = f"insert into caja(fecha,cuenta,imp,comentario) values('{fecha}','cobranza',{d['cobrado']},'global')"
    ins2 = f"insert into caja(fecha,cuenta,imp,comentario) values('{fecha}','cobranza',{-1*d['comision']},'com')"
    ins3 = f"insert into caja(fecha,cuenta,imp,comentario) values('{fecha}','cobranza',{-1*d['viatico']},'via')"
    cur = con.cursor()
    cur.execute(ins1)
    cur.execute(ins2)
    cur.execute(ins3)
    con.commit()
    cur.close()
    return "OK"

@pagos.route('/pagos/editarrbo')
@login_required
def pagos_editarrbo():
    return render_template('pagos/editarrbo.html' )


@pagos.route('/pagos/obtenerrbo/<int:id>')
def pagos_obtenerrbo(id):
    con = get_con()
    reg = pgdict(con, f"select fecha, idvta, imp, rec, rbo, cobr, id, (select nombre from clientes where clientes.id=pagos.idcliente) as nombre from pagos where id={id}")
    return jsonify (reg=reg)


@pagos.route('/pagos/obtenerregrbo/<int:buscar>')
def pagos_obtenerregrbo(buscar):
    con = get_con()
    try:
        reg = pgdict(con, f"select id, fecha, idvta, imp, rec, rbo, cobr, idcliente from pagos where rbo={buscar}")
        idcliente = pgonecolumn(con, f"select idcliente from pagos where rbo={buscar}")
        nombre = pgonecolumn(con, f"select nombre from clientes where id={idcliente}")
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        return jsonify (reg=reg, nombre=nombre)


@pagos.route('/pagos/borrarrbo/<int:id>')
def pagos_borrarrbo(id):
    con = get_con()
    stm = f"delete from pagos where id={id}"
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    cur.close()
    idvta = pgonecolumn(con,f"select idvta from pagos where id={id}")
    trigger_pago(con, idvta)
    return 'ok'

@pagos.route('/pagos/guardaredicionrbo' , methods = ['POST'])
def pagos_guardaredicionrbo():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    idcliente = pgonecolumn(con, f"select idcliente from ventas where id={d['idvta']}")
    upd = f"update pagos set fecha='{d['fecha']}', idvta={d['idvta']}, imp={d['imp']}, rec={d['rec']}, rbo={d['rbo']}, cobr={d['cobr']}, idcliente={idcliente} where id={d['id']}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    idvta = pgonecolumn(con,f"select idvta from pagos where id={d['id']}")
    trigger_pago(con, idvta)
    return 'OK'


@pagos.route('/pagos/getzonasasignadas')
def pagos_getzonasasignadas():
    con = get_con()
    zonas = pgddict(con, f"select zonas.id as id,zonas.zona as zona,asignado,(select nombre from cobr where cobr.id=asignado) as nombre, count(*) as cnt, sum(cuota) as cuota from zonas,clientes where clientes.zona=zonas.zona and pmovto>=date_sub(curdate(),interval 90 day) and zonas.zona not like '-%' group by zonas.id order by asignado")
    return jsonify(zonas=zonas)


@pagos.route('/pagos/verzona')
@login_required
def pagos_verzona():
    return render_template('pagos/verzona.html' )


@pagos.route('/pagos/editarasignado', methods = ['POST'])
def pagos_editarasignado():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    upd = f"update zonas set asignado={d['asignado']} where id={d['id']}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return 'ok'


@pagos.route('/pagos/gettotaleszonas')
def pagos_gettotaleszonas():
    con = get_con()
    totales = pgddict(con, f"select asignado,(select nombre from cobr where cobr.id=asignado) as nombre, sum(cuota) as cuota from zonas,clientes where clientes.zona=zonas.zona and pmovto>=date_sub(curdate(),interval 90 day) and zonas.zona not like '-%' group by asignado order by asignado")
    return jsonify(totales=totales)


@pagos.route('/pagos/cobrostotales')
@login_required
def pagos_cobrostotales():
    con = get_con()
    pd.options.display.float_format = '{:.0f}'.format
    sql="select date_format(fecha,'%Y-%m') as fp,imp+rec as cuota,cobr from pagos where fecha >date_sub(curdate(),interval 365 day)"
    sql1="select date_format(fecha,'%Y-%m') as fp,imp+rec as cuota,pagos.cobr as cobr,zona,(select asignado from zonas where zona=clientes.zona) as asignado from pagos,clientes where clientes.id=pagos.idcliente and fecha >date_sub(curdate(),interval 365 day) and zona not like '-%'"
    dat = pd.read_sql_query(sql, con)
    dat1= pd.read_sql_query(sql1,con)
    df = pd.DataFrame(dat)
    df1 = pd.DataFrame(dat1)
    tbl = pd.pivot_table(df, values=['cuota'],index='cobr',columns='fp',aggfunc='sum').sort_index(1, 'fp',False)
    tbl1 = pd.pivot_table(df1, values=['cuota'],index=['asignado','zona'],columns='fp',aggfunc='sum').sort_index(1, 'fp',False)
    tbl = tbl.fillna("")
    tbl1 = tbl1.fillna("")
    tbl = tbl.to_html(table_id="totales",classes="table")
    tbl1 = tbl1.to_html(table_id="totaleszona",classes="table")
    return render_template("pagos/totales.html", tbl=tbl, tbl1=tbl1 )


@pagos.route('/pagos/estimados')
@login_required
def pagos_estimados():
    con = get_con()
    pd.options.display.float_format = '{:.0f}'.format
    sql="select date_format(pmovto,'%Y-%m') as pmovto,cuota,asignado,clientes.zona as zona from clientes,zonas where clientes.zona=zonas.zona and pmovto>date_sub(curdate(),interval 180 day)  and zonas.zona not like '-%'"
    sql1="select date_format(pmovto,'%Y-%m') as pmovto,cuota,asignado,clientes.zona as zona from clientes,zonas where clientes.zona=zonas.zona and pmovto>date_sub(curdate(),interval 180 day)  and zonas.zona not like '-%'"
    dat = pd.read_sql_query(sql, con)
    dat1= pd.read_sql_query(sql1,con)
    df = pd.DataFrame(dat)
    df1 = pd.DataFrame(dat1)
    tbl = pd.pivot_table(df, values=['cuota'],index='asignado',columns='pmovto',aggfunc='sum').sort_index(1, 'pmovto',False)
    tbl1 = pd.pivot_table(df1, values=['cuota'],index=['asignado','zona'],columns='pmovto',aggfunc='sum').sort_index(1, 'pmovto',False)
    tbl = tbl.fillna("")
    tbl1 = tbl1.fillna("")
    tbl = tbl.to_html(table_id="totales",classes="table")
    tbl1 = tbl1.to_html(table_id="totaleszona",classes="table")
    return render_template("pagos/estimados.html", tbl=tbl, tbl1=tbl1 ) 


@pagos.route('/pagos/comisiones')
@login_required
def pagos_comisiones():
    con = get_con()
    pd.options.display.float_format = '${:.0f}'.format
    sql="select date_format(fecha,'%Y-%m') as fecha,imp+rec as cobranza,(imp+rec)*0.15 as comision,cobr from pagos where cobr in (750,815,796,800,816) and fecha>'2018-07-31'"
    dat = pd.read_sql_query(sql, con)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values=['comision','cobranza'],index='fecha',columns='cobr',aggfunc='sum').sort_index(0, 'fecha',False)
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="tablecomisiones",classes="table")
    return render_template("pagos/comisiones.html", tbl=tbl )


@pagos.route('/pivot/pagos_cobr')
def pivot_pagos_cobr():
    con = get_con()
    sql="select date_format(fecha,'%Y-%m') as fecha,imp+rec as cobranza,(imp+rec)*0.15 as comision,cobr from pagos where cobr in (750,815,796,800,816) and fecha>'2018-07-31'"
    dat = pd.read_sql_query(sql, con)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values=['comision','cobranza'],index='fecha',columns='cobr',aggfunc='sum')
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="table",classes="table table-sm")
    return render_template("pivot_cobr.html", tbl=tbl)


@pagos.route('/pivot/retiros')
def pivot_retiros():
    con = get_con()
    sql="select date_format(fecha,'%Y-%m') as fecha, cuenta, imp from caja where cuenta like 'retiro%'"
    dat = pd.read_sql_query(sql, con)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values='imp',index='fecha',columns='cuenta',aggfunc='sum')
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="table",classes="table  table-sm")
    return render_template("pivot_retiros.html", tbl=tbl)


@pagos.route('/pivot/retiros/excel')
def pivot_retiros_excel():
    con = get_con()
    sql="select date_format(fecha,'%Y-%m') as fecha, cuenta, imp from caja where cuenta like 'retiro%'"
    dat = pd.read_sql_query(sql, con)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values='imp',index='fecha',columns='cuenta',aggfunc='sum')
    tbl = tbl.fillna("")
    tbl = tbl.to_excel('retiros.xlsx', index=False)
    return send_file('retiros.xlsx')