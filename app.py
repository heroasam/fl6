from flask import Flask
from flask import render_template,url_for,request,redirect, send_file,jsonify
import psycopg2
import psycopg2.extras
from lib import *
import pandas as pd
import numpy as np
import re
import ast




app = Flask(__name__)
PORT = 5000
DEBUG = False
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'


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
    return render_template("pagosvue.html")

@app.route('/pagos/planilla/<string:fechapago>/<int:cobrador>')
def pagos_planilla(fechapago,cobrador):
    planilla = pgdict(con,f"select pagos.id as id, rbo, fecha, idvta,imp::INTEGER as imp, rec::INTEGER as rec, (imp+rec)::INTEGER as total, nombre, calle||' '||num as direccion, zona,deuda::INTEGER as deuda from pagos, clientes where clientes.id=pagos.idcliente and fecha='{fechapago}' and pagos.cobr={cobrador} order by id desc")
    lote = pgonecolumn(con,f"select lote from pagos where fecha='{fechapago}' and cobr={cobrador}") 
    return jsonify(planilla=planilla,lote=lote)


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
        clientes = pgdict(con,f"select nombre,calle||' '||num as direccion,dni from clientes where nombre||calle||num||barrio like '{cuenta}' and deuda>0")
    print(clientes)
    return jsonify(clientes=clientes)


@app.route('/pagos/idvtas/<string:dni>')
def pagos_idvtas(dni):
    sel = f"select ventas.id as id,calle||' '||num from ventas,clientes where clientes.id=ventas.idcliente and dni='{dni}' and saldo>0"
    print(sel)
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
    print(ins)
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
    return render_template("planillas.html")

@app.route('/pagos/getplanillas')
def pagos_getplanillas():
    planillas = pgdict(con,f"select planillas.fecha as fecha,sum(cobrado::integer),sum(comision::integer),sum(viatico::integer),sum(cntrbos),(select imp::integer from caja where comentario='global' and cuenta='cobranza' and fecha=planillas.fecha) from planillas group by planillas.fecha order by planillas.fecha desc limit 100")
    return jsonify(planillas=planillas)


@app.route('/pagos/getplanillas/<string:fecha>')
def pagos_getplanillashoy(fecha):
    planillas = pgdict(con,f"select fecha,idcobr,cobrado::integer,comision::integer,viatico::integer,cntrbos,idlote from planillas where fecha='{fecha}'")
    return jsonify(planillas=planillas)


@app.route('/buscador')
def buscador():
    return render_template("buscador.html")


@app.route('/buscador/<string:buscar>')
def buscar_cuenta(buscar):
    rcuenta = r'^[0-9]{5}$'
    rdni = r'^[0-9]{7,8}$'
    if (re.match(rcuenta,buscar)):
        clientes = pgdict(con,f"select dni,nombre,calle||' '||num,barrio,tel,wapp,clientes.zona,clientes.pmovto,deuda::integer,sev,incobrable,gestion,subirseven,novendermas,seguir from clientes,ventas where clientes.id=ventas.idcliente and ventas.id={buscar}")
    elif (re.match(rdni,buscar)):
        clientes = pgdict(con,f"select dni,nombre,calle||' '||num,barrio,tel,wapp,zona,pmovto,deuda::integer,sev,incobrable,gestion,subirseven,novendermas,seguir from clientes where dni='{buscar}'")
    else:
        buscar = '%'+buscar.replace(' ','%')+'%'
        clientes = pgdict(con,f"select dni,nombre,calle||' '||num from clientes where nombre||calle||num||barrio ilike '{buscar}'")
    return jsonify(clientes=clientes) 


@app.route('/buscador/pedirventas/<string:dni>')
def buscar_ventas(dni):
    idcliente = pgonecolumn(con,f"select id from clientes where dni='{dni}'")
    ventas = pgdict(con,f"select id,fecha,cc,ic::integer,p,idvdor,saldo::integer,pp,pcc,pic::integer,pper from ventas where idcliente={idcliente}")
    return jsonify(ventas=ventas)


@app.route('/buscador/pedirarticulos/<int:idvta>')
def buscar_articulos(idvta):
    articulos = pgdict(con,f"select cnt,art,cc||' '||'x$'||ic from detvta where idvta={idvta}")
    return jsonify(articulos=articulos)