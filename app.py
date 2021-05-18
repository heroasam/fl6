from flask import Flask, json
from flask import render_template,url_for,request,redirect, send_file,jsonify, make_response
from flask_wtf.csrf import CSRFProtect
import psycopg2
import psycopg2.extras
from lib import *
from formularios import *
import pandas as pd
import numpy as np
import re
import ast
import os




app = Flask(__name__)
PORT = 5000
DEBUG = False
app.config['SECRET_KEY'] = os.urandom(24)
#print(app.config['SECRET_KEY'])
#'7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'

csrf = CSRFProtect(app)

#con = psycopg2.connect(dbname='daq6n3vvmrg79o', user='ynpqvlqqsidhga', host='ec2-3-95-87-221.compute-1.amazonaws.com', password='4bded69478ac502d5223655094cbc2241ed5aaf025f0b31fd19494c5aa35d6f0',sslmode='require')
con = psycopg2.connect(dbname='hero', user='hero', host='localhost', password='ata', port=5432)


@app.route('/pivot/pagos_cobr')
def pivot_pagos_cobr():
    sql="select ym(fecha) as fecha,imp+rec as cobranza,(imp+rec)*0.15 as comision,cobr from pagos where cobr in (750,815,796,800,816) and fecha>'2018-07-31'"
    dat = pd.read_sql_query(sql, con)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values=['comision','cobranza'],index='fecha',columns='cobr',aggfunc='sum')
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="table",classes="table table-sm")
    return render_template("pivot_cobr.html", tbl=tbl)


@app.route('/pivot/retiros')
def pivot_retiros():
    sql="select ym(fecha) as fecha, cuenta, imp from caja where cuenta like 'retiro%'"
    dat = pd.read_sql_query(sql, con)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values='imp',index='fecha',columns='cuenta',aggfunc='sum')
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="table",classes="table  table-sm")
    return render_template("pivot_retiros.html", tbl=tbl)


@app.route('/pivot/retiros/excel')
def pivot_retiros_excel():
    sql="select ym(fecha) as fecha, cuenta, imp from caja where cuenta like 'retiro%'"
    dat = pd.read_sql_query(sql, con)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values='imp',index='fecha',columns='cuenta',aggfunc='sum')
    tbl = tbl.fillna("")
    tbl = tbl.to_excel('retiros.xlsx', index=False)
    return send_file('retiros.xlsx')


@app.template_filter()
def cur(monto):
    if monto==None:
        return None
    else:
        return f"${int(monto)}"


@app.route('/pagos')
def pagos():
    return render_template("pagos/pagosvue.html")

@app.route('/pagos/planilla/<string:fechapago>/<int:cobrador>')
def pagos_planilla(fechapago,cobrador):
    planilla = pgdict(con,f"select pagos.id as id, rbo, fecha, idvta,imp::INTEGER as imp, rec::INTEGER as rec, (imp+rec)::INTEGER as total, nombre, calle||' '||num as direccion, zona,deuda::INTEGER as deuda from pagos, clientes where clientes.id=pagos.idcliente and fecha='{fechapago}' and pagos.cobr={cobrador} order by id desc")
    lote = pgonecolumn(con,f"select lote from pagos where fecha='{fechapago}' and cobr={cobrador}")
    if lote=='':
        cntrbos = 0
    else:
        cntrbos = pgonecolumn(con, f"select count(*) from (select distinct rbo from pagos where lote={lote}) as foo")
    return jsonify(planilla=planilla,lote=lote,cntrbos=cntrbos)


@app.route('/pagos/buscar/<string:cuenta>')
def pagos_buscar(cuenta):
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


@app.route('/pagos/idvtas/<string:dni>')
def pagos_idvtas(dni):
    sel = f"select ventas.id as id,calle||' '||num from ventas,clientes where clientes.id=ventas.idcliente and dni='{dni}' and saldo>0"
    idvtas = pgdict(con,sel)
    return jsonify(idvtas=idvtas)


@app.route('/pagos/traerficha/<int:idvta>')
def pagos_traerficha(idvta):
    ficha = pgdict(con,f"select id,case when saldo::integer<ic::integer then saldo::integer else ic::integer end as imp,ic::integer,saldo::integer from ventas where id={idvta}")
    return jsonify(ficha=ficha)


@app.route('/pagos/pasarpagos' , methods = ['POST'])
def pagos_pasarpagos():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    idcliente = pgonecolumn(con,f"select idcliente from ventas where id={d['idvta']}")
    if(d['rec']==''):
        d['rec']=0
    ins = f"insert into pagos(idvta,fecha,imp,rec,rbo,cobr,idcliente,lote) values({d['idvta']},'{d['fecha']}',{d['imp']},{d['rec']},{d['rbo']},{d['cobr']},{idcliente},{d['lote']})"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    trigger_pago(con, d['idvta'])
    return 'ok'


@app.route('/pagos/borrarpago/<int:idpago>')
def pagos_borrarpago(idpago):
    stm = f"delete from pagos where id={idpago}"
    cur = con.cursor()
    idvta = pgonecolumn(con,f"select idvta from pagos where id={idpago}")
    cur.execute(stm)
    con.commit()
    trigger_pago(con, idvta)
    return 'ok'

@app.route('/pagos/pasarplanilla', methods = ['POST'])
def pagos_pasarplanilla():
    d = ast.literal_eval(request.data.decode("UTF-8"))
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


@app.route('/pagos/verplanillas')
def pagos_verplanillas():
    return render_template("pagos/planillas.html")

@app.route('/pagos/getplanillas')
def pagos_getplanillas():
    planillas = pgdict(con,f"select planillas.fecha as fecha,sum(cobrado::integer),sum(comision::integer),sum(viatico::integer),sum(cntrbos),(select imp::integer from caja where comentario='global' and cuenta='cobranza' and fecha=planillas.fecha) from planillas group by planillas.fecha order by planillas.fecha desc limit 100")
    return jsonify(planillas=planillas)


@app.route('/pagos/getplanillas/<string:fecha>')
def pagos_getplanillashoy(fecha):
    planillas = pgdict(con,f"select fecha,idcobr,cobrado::integer,comision::integer,viatico::integer,cntrbos,idlote from planillas where fecha='{fecha}'")
    return jsonify(planillas=planillas)


@app.route('/pagos/procesarplanilla', methods = ['POST'])
def pagos_procesarplanilla():
    d = ast.literal_eval(request.data.decode("UTF-8"))
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

@app.route('/pagos/editarrbo')
def pagos_editarrbo():
    return render_template('pagos/editarrbo.html')


@app.route('/pagos/obtenerrbo/<int:id>')
def pagos_obtenerrbo(id):
    reg = pgdict(con, f"select fecha, idvta, imp::integer, rec::integer, rbo, cobr, id, (select nombre from clientes where clientes.id=pagos.idcliente) as nombre from pagos where id={id}")
    return jsonify (reg=reg)


@app.route('/pagos/obtenerregrbo/<int:buscar>')
def pagos_obtenerregrbo(buscar):
    try:
        reg = pgdict(con, f"select id, fecha, idvta, imp::integer, rec::integer, rbo, cobr, idcliente from pagos where rbo={buscar}")
        idcliente = pgonecolumn(con, f"select idcliente from pagos where rbo={buscar}")
        nombre = pgonecolumn(con, f"select nombre from clientes where id={idcliente}")
    except psycopg2.Error as e:
        con.rollback()
        error = e.pgerror
        return make_response(error,400)
    else:
        return jsonify (reg=reg, nombre=nombre)


@app.route('/pagos/borrarrbo/<int:id>')
def pagos_borrarrbo(id):
    stm = f"delete from pagos where id={id}"
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    cur.close()
    return 'ok'

@app.route('/pagos/guardaredicionrbo' , methods = ['POST'])
def pagos_guardaredicionrbo():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    idcliente = pgonecolumn(con, f"select idcliente from ventas where id={d['idvta']}")
    upd = f"update pagos set fecha='{d['fecha']}', idvta={d['idvta']}, imp={d['imp']}, rec={d['rec']}, rbo={d['rbo']}, cobr={d['cobr']}, idcliente={idcliente} where id={d['id']}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return 'OK'


@app.route('/pagos/getzonasasignadas')
def pagos_getzonasasignadas():
    zonas = pgddict(con, f"select zonas.id as id,zonas.zona as zona,asignado,(select nombre from cobr where cobr.id=asignado) as nombre, count(*) as cnt, sum(cuota::integer) as cuota from zonas,clientes where clientes.zona=zonas.zona and pmovto>=now()-interval '3 month' and zonas.zona not like '-%' group by zonas.id order by asignado")
    return jsonify(zonas=zonas)


@app.route('/pagos/verzona')
def pagos_verzona():
    return render_template('pagos/verzona.html')


@app.route('/pagos/editarasignado', methods = ['POST'])
def pagos_editarasignado():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    upd = f"update zonas set asignado={d['asignado']} where id={d['id']}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return 'ok'


@app.route('/pagos/gettotaleszonas')
def pagos_gettotaleszonas():
    totales = pgddict(con, f"select asignado,(select nombre from cobr where cobr.id=asignado) as nombre, sum(cuota::integer) as cuota from zonas,clientes where clientes.zona=zonas.zona and pmovto>=now()-interval '3 month' and zonas.zona not like '-%' group by asignado order by asignado")
    return jsonify(totales=totales)


@app.route('/pagos/cobrostotales')
def pagos_cobrostotales():
    pd.options.display.float_format = '{:.0f}'.format
    sql="select ym(fecha) as fp,imp+rec as cuota,cobr from pagos where fecha >now() -interval '12 months'"
    sql1="select ym(fecha) as fp,imp+rec as cuota,pagos.cobr as cobr,zona,(select asignado from zonas where zona=clientes.zona) as asignado from pagos,clientes where clientes.id=pagos.idcliente and fecha >now()- interval '12 months' and zona not like '-%'"
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
    return render_template("pagos/totales.html", tbl=tbl, tbl1=tbl1)


@app.route('/pagos/estimados')
def pagos_estimados():
    pd.options.display.float_format = '{:.0f}'.format
    sql="select ym(pmovto) as pmovto,cuota,asignado,clientes.zona as zona from clientes,zonas where clientes.zona=zonas.zona and pmovto>now()- interval '6 months'  and zonas.zona not like '-%'"
    sql1="select ym(pmovto) as pmovto,cuota,asignado,clientes.zona as zona from clientes,zonas where clientes.zona=zonas.zona and pmovto>now()-interval '6 months'  and zonas.zona not like '-%'"
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
    return render_template("pagos/estimados.html", tbl=tbl, tbl1=tbl1)


@app.route('/pagos/comisiones')
def pagos_comisiones():
    pd.options.display.float_format = '${:.0f}'.format
    sql="select ym(fecha) as fecha,imp+rec as cobranza,(imp+rec)*0.15 as comision,cobr from pagos where cobr in (750,815,796,800,816) and fecha>'2018-07-31'"
    dat = pd.read_sql_query(sql, con)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values=['comision','cobranza'],index='fecha',columns='cobr',aggfunc='sum').sort_index(0, 'fecha',False)
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="table",classes="table table-sm")
    return render_template("pagos/comisiones.html", tbl=tbl)


@app.route('/')
@app.route('/buscador')
def buscador():
    return render_template("buscador.html")


@app.route('/buscador/<string:buscar>')
def buscar_cuenta(buscar):
    rcuenta = r'^[0-9]{5}$'
    rdni = r'^[0-9]{7,8}$'
    if (re.match(rcuenta,buscar)):
        clientes = pgdict(con,f"select dni,nombre,calle||' '||num,barrio,tel,wapp,clientes.zona,clientes.pmovto,deuda::integer,sev,incobrable,gestion,subirseven,novendermas,seguir,mudo,llamar,acla,horario,mjecobr,infoseven,sex from clientes,ventas where clientes.id=ventas.idcliente and ventas.id={buscar}")
    elif (re.match(rdni,buscar)):
        clientes = pgdict(con,f"select dni,nombre,calle,num,barrio,tel,wapp,zona,pmovto,deuda::integer,sev,incobrable,gestion,subirseven,novendermas,seguir,mudo,llamar,acla,horario,mjecobr,infoseven,sex from clientes where dni='{buscar}'")
    else:
        buscar = '%'+buscar.replace(' ','%')+'%'
        clientes = pgdict(con,f"select dni,nombre,calle||' '||num from clientes where nombre||calle||num||barrio ilike '{buscar}'")
    if len(clientes)==0:
        print('No hay respuesta')
        return make_response("No existe ese DNI en Romitex",400)
    return jsonify(clientes=clientes)


@app.route('/buscador/pedirventas/<string:dni>')
def buscar_ventas(dni):
    idcliente = pgonecolumn(con,f"select id from clientes where dni='{dni}'")
    ventas = pgdict(con,f"select id,fecha,cc,ic::integer,p,idvdor,saldo::integer,comprado::integer,pp,pcc,pic::integer,pper,devuelta,condonada from ventas where idcliente={idcliente}")
    return jsonify(ventas=ventas)


@app.route('/buscador/pedirarticulos/<int:idvta>')
def buscar_articulos(idvta):
    articulos = pgdict(con,f"select cnt,art,cc||' '||'x$'||ic from detvta where idvta={idvta}")
    return jsonify(articulos=articulos)


@app.route('/buscador/pedircuotas/<string:dni>')
def buscar_cuotas(dni):
    idcliente = pgonecolumn(con,f"select id from clientes where dni='{dni}'")
    ventas = pgdict(con,f"select id from ventas where idcliente={idcliente} and saldo>0")
    cur = con.cursor()
    for v in ventas:
        cur.execute(f"select gc({v[0]})")
    cur.close()
    cuotas = pgdict(con, f"select nc,vto,ic::integer,idvta from cuotas where debe>0 and idcliente={idcliente} order by vto")
    pagadas = pgdict(con, f"select fecha,rbo,imp::integer,rec::integer,cobr from pagos where idcliente={idcliente} and \
             idvta in (select id from ventas where saldo>0) order by fecha desc")
    return jsonify(cuotas=cuotas,pagadas=pagadas)


@app.route('/buscador/fecharpmovto/<string:dni>/<string:pmovto>')
def buscar_fecharpmovto(dni,pmovto):
    upd = f"update clientes set pmovto='{pmovto}' where dni='{dni}'"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return 'ok'


@app.route('/buscador/imprimirficha' , methods = ['POST'])
def buscar_imprimirficha():
    dni = ast.literal_eval(request.data.decode("UTF-8"))
    ficha(con,dni)
    return send_file('ficha.pdf')


@app.route('/buscador/datosultvta/<string:dni>')
def buscar_datosultvta(dni):
    idcliente = pgonecolumn(con,f"select id from clientes where dni='{dni}'")
    ultvta = pgdict(con,f"select fecha, (select max(art) from detvta where idvta=ventas.id) from ventas where idcliente={idcliente} order by id desc")
    return jsonify(ultvta=ultvta)


@app.route('/buscador/togglesube/<string:dni>')
def buscar_togglesube(dni):
    sube = pgonecolumn(con,f"select subirseven from clientes where dni='{dni}'")
    sev = pgonecolumn(con,f"select sev from clientes where dni='{dni}'")
    if sev==0:
        if sube:
            upd = f"update clientes set subirseven=0 where dni='{dni}'"
            msg = "Registro desmarcado para subir seven"
        else:
            upd = f"update clientes set subirseven=1 where dni='{dni}'"
            msg = "Registro marcado para subir seven"
        cur = con.cursor()
        cur.execute(upd)
        con.commit()
        cur.close()
        return msg
    else:
        return 'No se sube pq ya esta en el seven'


@app.route('/buscador/togglegestion/<string:dni>')
def buscar_togglegestion(dni):
    sube = pgonecolumn(con,f"select gestion from clientes where dni='{dni}'")
    if sube:
        upd = f"update clientes set gestion=0 where dni='{dni}'"
        msg = "Registro desmarcado como Gestion"
    else:
        upd = f"update clientes set gestion=1 where dni='{dni}'"
        msg = "Registro marcado como Gestion"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return msg


@app.route('/buscador/togglemudado/<string:dni>')
def buscar_togglemudado(dni):
    sube = pgonecolumn(con,f"select mudo from clientes where dni='{dni}'")
    if sube:
        upd = f"update clientes set mudo=0 where dni='{dni}'"
        msg = "Registro desmarcado como Mudado"
    else:
        upd = f"update clientes set mudo=1 where dni='{dni}'"
        msg = "Registro marcado como Mudado"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return msg


@app.route('/buscador/toggleinc/<string:dni>')
def buscar_toggleinc(dni):
    sube = pgonecolumn(con,f"select incobrable from clientes where dni='{dni}'")
    if sube:
        upd = f"update clientes set incobrable=0 where dni='{dni}'"
        msg = "Registro desmarcado como Incobrable"
    else:
        upd = f"update clientes set incobrable=1 where dni='{dni}'"
        msg = "Registro marcado como Incobrable"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return msg


@app.route('/buscador/toggleln/<string:dni>')
def buscar_toggleln(dni):
    sube = pgonecolumn(con,f"select novendermas from clientes where dni='{dni}'")
    if sube:
        upd = f"update clientes set novendermas=0 where dni='{dni}'"
        msg = "Registro desmarcado como No Vender Mas"
    else:
        upd = f"update clientes set novendermas=1 where dni='{dni}'"
        msg = "Registro marcado como No Vender Mas"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return msg


@app.route('/buscador/togglellamar/<string:dni>')
def buscar_togglellamar(dni):
    sube = pgonecolumn(con,f"select llamar from clientes where dni='{dni}'")
    if sube:
        upd = f"update clientes set llamar=0 where dni='{dni}'"
    else:
        upd = f"update clientes set llamar=1 where dni='{dni}'"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return 'ok'


@app.route('/buscador/toggleseguir/<string:dni>')
def buscar_toggleseguir(dni):
    sube = pgonecolumn(con,f"select seguir from clientes where dni='{dni}'")
    if sube:
        upd = f"update clientes set seguir=0 where dni='{dni}'"
    else:
        upd = f"update clientes set seguir=1 where dni='{dni}'"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return 'ok'


@app.route('/buscador/gettablas')
def buscar_gettablas():
    calles = pgdict(con,f"select calle from calles order by calle")
    barrios = pgdict(con,f"select barrio from barrios order by barrio")
    zonas = pgdict(con,f"select zona from zonas order by zona")
    return jsonify(calles=calles,barrios=barrios,zonas=zonas)


@app.route('/buscador/getzonas')
def buscar_getzonas():
    zonas = pgdict(con,f"select zona from zonas order by zona")
    return jsonify(zonas=zonas)


@app.route('/buscador/editardatos/<string:dni>' , methods = ['POST'])
def busca_editardatos(dni):
    d = ast.literal_eval(request.data.decode("UTF-8"))
    upd = f"update clientes set sex='{d['sex']}', dni='{d['dni']}', nombre='{d['nombre']}', calle='{d['calle']}', num={d['num']}, barrio='{d['barrio']}', zona='{d['zona']}', tel='{d['tel']}', wapp={d['wapp']}, acla='{d['acla']}', mjecobr='{d['mjecobr']}', horario='{d['horario']}', infoseven='{d['infoseven']}' where dni='{dni}'"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return 'ok'


@app.route('/buscador/pedircomentarios/<string:dni>')
def buscar_pedircomentarios(dni):
    idcliente = pgonecolumn(con,f"select id from clientes where dni='{dni}'")
    comentarios=pgdict(con,f"select fechahora,comentario from comentarios where idcliente={idcliente}")
    return jsonify(comentarios=comentarios)



@app.route('/fichaje')
def fichaje():
    return render_template("fichaje.html")


@app.route('/fichaje/getcobradores')
def fichaje_getcobradores():
    cobradores = pgdict(con,f"select id from cobr where activo=1 and prom=0 and id>15")
    return jsonify(cobradores=cobradores)


@app.route('/fichaje/muestrazonas/<int:cobr>')
def fichaje_muestrazona(cobr):
    zonas = pgdict(con,f"select zona from zonas where asignado={cobr}")
    return jsonify(zonas=zonas)


@app.route('/fichaje/muestraclientes/<string:tipo>/<string:zona>')
def fichaje_muestraclientes(tipo,zona):
    if tipo=='normales':
        clientes = pgdict(con,f"select nombre,calle,num,ultpago,pmovto,sev,novendermas,gestion,mudo,incobrable,dni,subirseven,comprado::integer,deuda::integer,zona,barrio from clientes where zona='{zona}' and ultpago>now()-interval '12 month' and deuda>0  and gestion=0 and incobrable=0 and mudo=0 order by pmovto")
    elif tipo=='gestion':
        clientes = pgdict(con,f"select nombre,calle,num,ultpago,pmovto,sev,novendermas,gestion,mudo,incobrable,dni,subirseven,comprado::integer,deuda::integer,zona,barrio from clientes where zona='{zona}' and ultpago>now()-interval '12 month' and deuda>0  and (gestion=1 or incobrable=1 or mudo=1) order by pmovto")
    elif tipo=='antiguos':
        clientes = pgdict(con,f"select nombre,calle,num,ultpago,pmovto,sev,novendermas,gestion,mudo,incobrable,dni,subirseven,comprado::integer,deuda::integer,zona,barrio from clientes where zona='{zona}' and ultpago<=now()-interval '12 month' and deuda>0  order by ultpago desc")
    return jsonify(clientes=clientes)


@app.route('/fichaje/imprimir', methods = ['POST'])
def fichaje_imprimir():
    listadni = ast.literal_eval(request.data.decode("UTF-8"))
    # aca se el ast.literal entrega la lista enviada por el axios-post directamente

    ficha(con, listadni)
    return send_file('ficha.pdf')

@app.route('/loterbo')
def loterbo_():
    return render_template("pagos/loterbo.html")

@app.route('/loterbo/guardarlote/<string:fecha>/<string:cobr>', methods = ['POST'])
def guardarlote(fecha,cobr):
    listarbos = ast.literal_eval(request.data.decode("UTF-8"))
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

@app.route('/loterbo/obtenerlastid')
def obtenerlastid():
    idlote = str(pgonecolumn(con, f"select max(id) from loterbos"))
    return jsonify(idlote=idlote)

@app.route('/loterbo/imprimir/<string:fecha>/<string:cobr>/<int:idlote>', methods = ['POST'])
def loterbo_imprimir(fecha,cobr,idlote):
    listarbo = ast.literal_eval(request.data.decode("UTF-8"))
    # aca se el ast.literal entrega la lista enviada por el axios-post directamente

    loterbo(con, listarbo,fecha,cobr,idlote)
    return send_file('loterbo.pdf')

@app.route('/loterbo/reimprimir/<string:fecha>/<string:cobr>/<int:idlote>')
def loterbo_reimprimir(fecha,cobr,idlote):
    listarbo = pglflat(con, f"select rbo from rbos where idloterbos={idlote}")
    print(listarbo)
    loterbo(con, listarbo, fecha,cobr,idlote)
    return send_file('loterbo.pdf')


@app.route('/loterbo/ver')
def loterbo_ver():
    lotesrbo = pgddict(con,f"select id,fecha,cobr,cnt from loterbos order by id desc limit 100")
    return render_template("pagos/loterbover.html", lotesrbo=lotesrbo)

@app.route('/loterbo/delete/<string:id>')
def loterbo_delete(id):
    cur = con.cursor()
    cur.execute("delete from loterbos where id={0}".format(id))
    con.commit()
    cur.close()
    return redirect(url_for('loterbo_ver'))

@app.route('/loterbo/buscanombrecobr/<int:cobr>')
def loterbo_buscanombrecobr(cobr):
    nombrecobr = pgonecolumn(con, f"select nombre from cobr where id={cobr}")
    return jsonify(nombrecobr=nombrecobr)



@app.route('/stock/asientos')
def stock_asientos():
    return render_template('stock/asientos.html')


@app.route('/stock/getasientos')
def stock_getasientos():
    asientos=pgddict(con, f"select id,fecha, cuenta, imp::integer, comentario from caja order by id desc limit 100")
    saldo = pgonecolumn(con, f"select sum(imp::int) from caja")
    return jsonify(asientos=asientos,saldo=saldo)


@app.route('/stock/deleteasiento/<int:id>')
def stock_deleteasiento(id):
    stm=f'delete from caja where id={id}'
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    cur.close()
    return 'el registro ha sido borrado'


@app.route('/stock/getcuentas')
def stock_getcuentas():
    cuentas = pglflat(con, f"select cuenta from ctas order by cuenta")
    print(cuentas)
    return jsonify(cuentas=cuentas)


@app.route('/stock/guardarasiento' , methods = ['POST'])
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


@app.route('/stock/mayor')
def stock_mayor():
    return render_template('stock/mayor.html')


@app.route('/stock/getmayor/<string:cuenta>')
def stock_getmayor(cuenta):
    asientos=pgddict(con, f"select id,fecha, cuenta, imp::integer, comentario from caja where cuenta='{cuenta}' order by id desc")
    return jsonify(asientos=asientos)


@app.route('/stock/pivotcuentas')
def stock_pivotcuentas():
    sql="select ym(fecha) as fecha,cuenta,imp from caja order by id desc"
    pd.options.display.float_format = '{:20.0f}'.format
    dat = pd.read_sql_query(sql, con)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values=['imp'],index='cuenta',columns='fecha',aggfunc='sum').sort_index(1, 'fecha',False)
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="table",classes="table table-sm")
    return render_template("stock/pivot_cuentas.html", tbl=tbl)


@app.route('/stock/retiros')
def stock_retiros():
    sql="select ym(fecha) as fecha,cuenta,imp from caja where cuenta in ('retiro papi', 'retiro fede') order by id desc"
    pd.options.display.float_format = '{:20.0f}'.format
    dat = pd.read_sql_query(sql, con)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values=['imp'],index='fecha',columns='cuenta',aggfunc='sum')
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="table",classes="table table-sm")
    return render_template("stock/retiros.html", tbl=tbl)


@app.route('/stock/getcompras')
def stock_getcompras():
    compras=pgddict(con, f"select id,fecha,art,cnt::integer, costo::integer,total::integer,proveedor from artcomprado order by id desc limit 200")
    return jsonify(compras=compras)


@app.route('/stock/getarticulos')
def stock_getarticulos():
    articulos=pglflat(con, f"select art from articulos")
    return jsonify(articulos=articulos)


@app.route('/stock/compras')
def stock_compras():
    return render_template('stock/compras.html')


@app.route('/stock/deletecompra/<int:id>')
def stock_deletecompra(id):
    stm=f'delete from artcomprado where id={id}'
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    cur.close()
    return 'el registro ha sido borrado'


@app.route('/stock/guardarcompra' , methods = ['POST'])
def stock_guardarcompra():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    ins = f"insert into artcomprado(fecha,cnt,art,costo,total,proveedor) values('{d['fecha']}',{d['cnt']},'{d['art']}',{d['costo']},{d['total']},'{d['proveedor']}')"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    cur.close()
    return 'OK'


@app.route('/stock/saldosorpresa')
def stock_saldosorpresa():
    pagado = pgonecolumn(con, f"select sum(imp::integer) from caja where cuenta = 'depositos sorpresa'")
    comprado = pgonecolumn(con, f"select sum(total::integer) from artcomprado where proveedor ilike 'Sorpresa' and fecha>'2015-09-20'")
    saldosorpresa = 122031 + comprado + pagado
    return jsonify(saldosorpresa=saldosorpresa)


@app.route('/stock/getdepositos')
def stock_getdepositos():
    depositos=pgddict(con, f"select fecha,imp::integer from caja where cuenta='depositos sorpresa' order by id desc")
    return jsonify(depositos=depositos)


@app.route('/stock/generarstock')
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


@app.route('/stock/verstock')
def stock_verstock():
    return render_template('stock/verstock.html')


@app.route('/stock/salidas')
def stock_salidas():
    return render_template('stock/salidas.html')


@app.route('/stock/getsalidas')
def stock_getsalidas():
    salidas=pgddict(con, f"select id,fecha,cnt,art,costo::integer,comentario from detsalida order by id desc limit 200")
    return jsonify(salidas=salidas)


@app.route('/stock/deletesalida/<int:id>')
def stock_deletesalida(id):
    stm=f'delete from detsalida where id={id}'
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    cur.close()
    return 'el registro ha sido borrado'


@app.route('/stock/guardarsalida' , methods = ['POST'])
def stock_guardarsalida():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    ins = f"insert into detsalida(fecha,cnt,art,costo,comentario) values('{d['fecha']}',{d['cnt']},'{d['art']}',{d['costo']},'{d['comentario']}')"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    cur.close()
    return 'OK'


@app.route('/stock/getlistaarticulos')
def stock_getlistaarticulos():
    articulos=pgddict(con, f"select id,art,costo::integer,activo from articulos order by id desc" )
    return jsonify(articulos=articulos)


@app.route('/stock/articulos')
def stock_articulos():
    return render_template('stock/articulos.html')


@app.route('/stock/guardararticulo' , methods = ['POST'])
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


@app.route('/stock/deletearticulo/<int:id>')
def stock_deletearticulo(id):
    stm=f'delete from articulos where id={id}'
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    cur.close()
    return 'el registro ha sido borrado'


@app.route('/stock/articulotoggleactivo/<int:id>')
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


@app.route('/stock/guardaredicionarticulo' , methods = ['POST'])
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


@app.route('/ventas/pasarventas')
def ventas_pasarventas():
    return render_template('ventas/pasarventas.html')


@app.route('/ventas/getcalles')
def ventas_getcalles():
    calles = pglflat(con, f"select calle from calles order by calle")
    return jsonify(calles= calles)


@app.route('/ventas/getbarrios')
def ventas_getbarrios():
    barrios = pglflat(con, f"select barrio from barrios order by barrio")
    return jsonify(barrios= barrios)


@app.route('/ventas/getzonas')
def ventas_getzonas():
    zonas = pglflat(con, f"select zona from zonas order by zona")
    return jsonify(zonas= zonas)


@app.route('/ventas/getcuentapordni/<string:dni>')
def ventas_getcuentaspordni(dni):
    try:
        clientes = pgdict(con,f"select sex,dni,nombre,calle,num,barrio,zona,tel,wapp,acla,horario,mjecobr,infoseven,id from clientes where dni='{dni}'")
    except psycopg2.Error as e:
        con.rollback()
        error = e.pgerror
        return make_response(error,400)
    else:
        return jsonify(clientes=clientes)


@app.route('/ventas/guardarcliente', methods=['POST'])
def ventas_guardarcliente():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    if d['id']=="":
        stm = f"insert into clientes(sex,dni,nombre,calle,num,barrio,zona,tel,wapp,acla,horario,mjecobr,infoseven) values('{d['sex']}','{d['dni']}','{d['nombre']}','{d['calle']}','{d['num']}','{d['barrio']}','{d['zona']}','{d['tel']}','{d['wapp']}','{d['acla']}','{d['horario']}','{d['mjecobr']}','{d['infoseven']}')"
    else:
        stm = f"update clientes set sex='{d['sex']}', dni='{d['dni']}', nombre='{d['nombre']}',calle='{d['calle']}',num='{d['num']}',barrio='{d['barrio']}', zona='{d['zona']}',tel='{d['tel']}', wapp='{d['wapp']}', acla='{d['acla']}', horario='{d['horario']}', mjecobr='{d['mjecobr']}', infoseven='{d['infoseven']}' where id={d['id']}"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except psycopg2.Error as e:
        con.rollback()
        error = e.pgerror
        return make_response(error,400)
    else:
        con.commit()
        cur.close()
        return 'OK'
