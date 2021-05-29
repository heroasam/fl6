from flask import Blueprint,render_template,jsonify,make_response, request
from flask_login import login_required
from lib import *
import ast
from con import con
import pandas as pd

ventas = Blueprint('ventas',__name__)

@ventas.route('/ventas/pasarventas')
@login_required
def ventas_pasarventas():
    return render_template('ventas/pasarventas.html')


@ventas.route('/ventas/getcalles')
def ventas_getcalles():
    calles = pglflat(con, f"select calle from calles order by calle")
    return jsonify(calles= calles)


@ventas.route('/ventas/getbarrios')
def ventas_getbarrios():
    barrios = pglflat(con, f"select barrio from barrios order by barrio")
    return jsonify(barrios= barrios)


@ventas.route('/ventas/getzonas')
def ventas_getzonas():
    zonas = pglflat(con, f"select zona from zonas order by zona")
    return jsonify(zonas= zonas)


@ventas.route('/ventas/getcuentapordni/<string:dni>')
def ventas_getcuentaspordni(dni):
    try:
        clientes = pgdict(con,f"select sex,dni,nombre,calle,num,barrio,zona,tel,wapp,acla,horario,mjecobr,infoseven,id from clientes where dni='{dni}'")
    except psycopg2.Error as e:
        con.rollback()
        error = e.pgerror
        return make_response(error,400)
    else:
        return jsonify(clientes=clientes)


@ventas.route('/ventas/guardarcliente', methods=['POST'])
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
        if d['id']=="":
            id = pgonecolumn(con,f"select id from clientes order by id desc limit 1")
        else:
            id = d['id']
        return jsonify(id=id)


@ventas.route('/ventas/guardarventa', methods=['POST'])
def ventas_guardarventa():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    per = d['p']
    if per=='mensual':
        p=1
    elif per=='semanal':
        p=3
    else:
        p=2
    ins = f"insert into ventas(fecha,idvdor,cc,ic,p,primera,idcliente) values('{d['fecha']}',{d['idvdor']},{d['cc']},{d['ic']},{p},'{d['primera']}',{d['idcliente']})"
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
        idvta = pgonecolumn(con,f"select id from ventas order by id desc limit 1")
        venta_trigger(con,idvta)
        return jsonify(idvta=idvta)

@ventas.route('/ventas/guardardetvta', methods=['POST'])
def ventas_guardardetvta():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    costo = pgonecolumn(con, f"select costo from articulos where art='{d['art']}'")
    ins = f"insert into detvta(idvta,cnt,art,cc,ic,costo) values({d['idvta']},{d['cnt']},'{d['art']}',{d['cc']},{d['ic']},{costo})"
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
        detvta = pgdict(con,f"select id,cnt,art,cc,ic::integer from detvta where idvta={d['idvta']}")
        sumic = pgonecolumn(con,f"select sum(ic::integer) from detvta where idvta={d['idvta']}")
        return jsonify(detvta=detvta,sumic=sumic)


@ventas.route('/ventas/borrardetvta/<int:id>')
def ventas_borrardetvta(id):
    idvta= pgonecolumn(con,f"select idvta from detvta where id={id}")
    stm = f"delete from detvta where id={id}"
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
        detvta = pgdict(con,f"select id,cnt,art,cc,ic::integer from detvta where idvta={idvta}")
        sumic = pgonecolumn(con,f"select sum(ic::integer) from detvta where idvta={idvta}")
        if sumic is None:
            sumic=0
        return jsonify(detvta=detvta,sumic=sumic)



@ventas.route('/ventas/getarticulos')
def ventas_getarticulos():
    articulos = pglflat(con, f"select art from articulos where activo=1")
    return jsonify(articulos=articulos)


@ventas.route('/ventas/getlistado')
def ventas_getlistado():
    listado = pgdict(con,f"select id, fecha, cc, ic::integer, p, pmovto  , comprado::integer, idvdor, primera, (select sum(cnt) from detvta where idvta= ventas.id) as cnt, (select string_agg(art,' | ')  from detvta where idvta=ventas.id) as art, (select count(id) from ventas as b where b.idcliente=ventas.idcliente and saldo>0 and pmovto<now() - interval '4 month') as count from ventas order by id desc limit 200")
    return jsonify(listado=listado)


@ventas.route('/ventas/listado')
def ventas_listado():
    return render_template("ventas/listado.html")


@ventas.route('/ventas/borrarventa/<int:id>')
def ventas_borrarventa(id):
    stm = f"delete from ventas where id={id}"
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

@ventas.route('/ventas/datosventa/<int:id>')
def ventas_datosventa(id):
    venta = pgdict(con, f"select fecha,cc,ic::integer,p,pmovto,idvdor,primera from ventas where id={id}")
    return jsonify(venta=venta)


@ventas.route('/ventas/guardaredicionventa', methods=['POST'])
def ventas_guardaredicionvta():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    upd = f"update ventas set fecha='{d['fecha']}',cc={d['cc']},ic={d['ic']},p={d['p']},pmovto='{d['pmovto']}',idvdor={d['idvdor']},primera='{d['primera']}' where id={d['id']}"
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

@ventas.route('/ventas/clientes')
def ventas_clientes():
    return render_template('ventas/clientes.html')


@ventas.route('/ventas/getclientes')
def ventas_getclientes():
    clientes = pgdict(con, f"select ventas.id, nombre, calle,num, zona, gestion, mudo, incobrable,acla from ventas, clientes where ventas.idcliente=clientes.id order by ventas.id desc limit 200")
    return jsonify(clientes=clientes)


@ventas.route('/ventas/calles')
def ventas_calles():
    return render_template('ventas/calles.html')


@ventas.route('/ventas/barrios')
def barrios_calles():
    return render_template('ventas/barrios.html')


@ventas.route('/ventas/zonas')
def zonas_calles():
    return render_template('ventas/zonas.html')


@ventas.route('/ventas/getcallesconid')
def ventas_getcallesconid():
    calles = pgdict(con, f"select id,calle from calles order by calle")
    return jsonify(calles= calles)


@ventas.route('/ventas/getbarriosconid')
def ventas_getbarriosconid():
    barrios = pgdict(con, f"select id,barrio from barrios order by barrio")
    return jsonify(barrios= barrios)


@ventas.route('/ventas/getzonasconid')
def ventas_getzonasconid():
    zonas = pgdict(con, f"select id,zona from zonas order by zona")
    return jsonify(zonas= zonas)


@ventas.route('/ventas/guardaredicioncalle', methods=['POST'])
def ventas_guardaredicioncalle():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    upd = f"update calles set calle='{d['calle']}' where id={d['id']}"
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



@ventas.route('/ventas/guardaredicionbarrio', methods=['POST'])
def ventas_guardaredicionbarrio():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    upd = f"update barrios set barrio='{d['barrio']}' where id={d['id']}"
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


@ventas.route('/ventas/guardaredicionzona', methods=['POST'])
def ventas_guardaredicionzona():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    upd = f"update zonas set zona='{d['zona']}' where id={d['id']}"
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


@ventas.route('/ventas/borrarcalle/<int:id>')  
def ventas_borrarcalle(id):
    stm = f"delete from calles where id={id}"
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



@ventas.route('/ventas/borrarbarrio/<int:id>')  
def ventas_borrarbarrio(id):
    stm = f"delete from barrios where id={id}"
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


@ventas.route('/ventas/borrarzona/<int:id>')  
def ventas_borrarzona(id):
    stm = f"delete from zonas where id={id}"
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

@ventas.route('/ventas/guardarcallenueva', methods=['POST'])
def ventas_guardarcallenueva():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    ins = f"insert into calles(calle) values('{d['calle']}')"
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



@ventas.route('/ventas/guardarbarrionueva', methods=['POST'])
def ventas_guardarbarrionueva():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    ins = f"insert into barrios(barrio) values('{d['barrio']}')"
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


@ventas.route('/ventas/guardarzonanueva', methods=['POST'])
def ventas_guardarzonanueva():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    ins = f"insert into zonas(zona) values('{d['zona']}')"
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


@ventas.route('/ventas/estadisticas')
@login_required
def ventas_estadisticas():
    return render_template('ventas/estadisticas.html')


@ventas.route('/ventas/estadisticasanuales')
@login_required
def ventas_estadisticasanuales():
    est_anuales = pgdict(con,f"select y(fecha) as y, sum(comprado::integer), sum(saldo::integer), sum(saldo::float)/sum(comprado::float) as inc,sum(cnt) from ventas group by y order by y desc")
    return jsonify(est_anuales=est_anuales)


@ventas.route('/ventas/estadisticasmensuales/<string:year>')
@login_required
def ventas_estadisticasmensuales(year):
    est_mensuales = pgdict(con,f"select ym(fecha) as ym, sum(comprado::integer), sum(saldo::integer), sum(saldo::float)/sum(comprado::float) as inc,sum(cnt) from ventas where y(fecha)='{year}' group by ym order by ym")
    return jsonify(est_mensuales=est_mensuales)