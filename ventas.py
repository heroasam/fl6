from flask import Blueprint,render_template,jsonify,make_response, request
from flask_login import login_required
from lib import *
import ast
from con import con

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