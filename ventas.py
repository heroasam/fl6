from flask import Blueprint,render_template,jsonify,make_response, request
from flask_login import login_required, current_user
import re
import pandas as pd
import simplejson as json
import mysql.connector
import logging
from con import get_con, log, engine, check_roles
from lib import *

ventas = Blueprint('ventas',__name__)

@ventas.route('/ventas/ventas')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_pasarventas():
    return render_template('ventas/ventas.html')


@ventas.route('/CZI6X7BC6wNtseAN22HiXsmqc')
@ventas.route('/ventas/getcalles')
@login_required
@check_roles(['dev','gerente','admin','vendedor'])
def ventas_getcalles():
    con = get_con()
    calles = pglist(con, f"select calle from calles order by calle")
    con.close()
    return jsonify(result=calles)


@ventas.route('/w98LuAaWBax9c6rENQ2TjO3PR')
@ventas.route('/ventas/getbarrios')
@login_required
@check_roles(['dev','gerente','admin','vendedor'])
def ventas_getbarrios():
    con = get_con()
    barrios = pglist(con, f"select barrio from barrios order by barrio")
    con.close()
    return jsonify(result=barrios)


@ventas.route('/ventas/getzonas')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_getzonas():
    con = get_con()
    zonas = pglist(con, f"select zona from zonas order by zona")
    con.close()
    return jsonify(result=zonas)


@ventas.route('/ventas/getperiodicidad')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_getperiodicidad():
    periodicidad=['mensual','quincenal','semanal']
    return jsonify(result=periodicidad)


@ventas.route('/ventas/getcuentapordni/<string:dni>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_getcuentaspordni(dni):
    con = get_con()
    try:
        clientes = pglistdict(con,f"select sex,dni,nombre,calle,num,barrio,zona,tel,wapp,acla,horario,mjecobr,infoseven,id from clientes where dni='{dni}'")
        if len(clientes)==1:
            clientes = clientes[0]
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.close()
        return jsonify(clientes=clientes)


@ventas.route('/ventas/guardarcliente', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_guardarcliente():
    con = get_con()
    cur = con.cursor()
    d = json.loads(request.data.decode("UTF-8"))
    if d['id']: # o sea existe el id, es decir es un update
        cliente_viejo = pglistdict(con, f"select * from clientes where id={d['id']}")[0]
    if d['id']=="":
        stm = f"insert into clientes(sex,dni,nombre,calle,num,barrio,zona,tel,wapp,acla,horario,mjecobr,infoseven) values('{d['sex']}','{d['dni']}','{d['nombre']}','{d['calle']}','{d['num']}','{d['barrio']}','{d['zona']}','{d['tel']}','{d['wapp']}','{d['acla']}','{d['horario']}','{d['mjecobr']}','{d['infoseven']}')"
    else:
        stm = f"update clientes set sex='{d['sex']}', dni='{d['dni']}', nombre='{d['nombre']}',calle='{d['calle']}',num='{d['num']}',barrio='{d['barrio']}', zona='{d['zona']}',tel='{d['tel']}', wapp='{d['wapp']}', acla='{d['acla']}', horario='{d['horario']}', mjecobr='{d['mjecobr']}', infoseven='{d['infoseven']}' where id={d['id']}"
    try:
        cur.execute(stm)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(stm)
        cur.close()
        if d['id']=="":
            id = pgonecolumn(con,f"select id from clientes order by id desc limit 1")
        else:
            id = d['id']
            ins = f"insert into logcambiodireccion(idcliente,calle,num,barrio,tel,acla,fecha,nombre,dni,wapp) values({cliente_viejo['id']},'{cliente_viejo['calle']}','{cliente_viejo['num']}','{cliente_viejo['barrio']}','{cliente_viejo['tel']}','{cliente_viejo['acla']}',curdate(),'{cliente_viejo['nombre']}','{cliente_viejo['dni']}','{cliente_viejo['wapp']}')"
            cur = con.cursor()
            if cliente_viejo['calle']!=d['calle'] or cliente_viejo['num']!=d['num'] or cliente_viejo['acla']!=d['acla'] or cliente_viejo['wapp']!=d['wapp']:
                cur.execute(ins)
                con.commit()
                log(ins)
                cur.close()
                con.close()
        return jsonify(id=id)


@ventas.route('/ventas/guardarventa', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_guardarventa():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    ant = d['ant'] or 0

    per = d['p']
    if per=='mensual':
        p=1
    elif per=='semanal':
        p=3
    else:
        p=2
    if d['dnigarante']:
        garantizado = 1
        dnigarante = d['dnigarante']
    else:
        garantizado = 0
        dnigarante = 0
    ins = f"insert into ventas(fecha,idvdor,ant,cc,ic,p,primera,idcliente,garantizado,dnigarante) values('{d['fecha']}',{d['idvdor']},{ant},{d['cc']},{d['ic']},{p},'{d['primera']}',{d['idcliente']},{garantizado},{dnigarante})"
    cur = con.cursor()
    try:
        cur.execute(ins)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(ins)
        cur.close()
        idvta = pgonecolumn(con,f"select id from ventas order by id desc limit 1")
        con.close()
        return jsonify(idvta=idvta)


@ventas.route('/ventas/guardardetvta', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_guardardetvta():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    costo = pgonecolumn(con, f"select costo from articulos where art='{d['art']}'")
    ins = f"insert into detvta(idvta,cnt,art,cc,ic,costo,devuelta) values({d['idvta']},{d['cnt']},'{d['art']}',{d['cc']},{d['ic']},{costo},0)"
    cur = con.cursor()
    try:
        cur.execute(ins)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(ins)
        cur.close()
        detvta = pglistdict(con,f"select id,cnt,art,cc,ic from detvta where idvta={d['idvta']}")
        sumic = pgonecolumn(con,f"select sum(ic) from detvta where idvta={d['idvta']}")
        con.close()
        return jsonify(detvta=detvta,sumic=sumic)


@ventas.route('/ventas/borrardetvta/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_borrardetvta(id):
    con = get_con()
    idvta= pgonecolumn(con,f"select idvta from detvta where id={id}")
    stm = f"delete from detvta where id={id}"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(stm)
        cur.close()
        detvta = pglistdict(con,f"select id,cnt,art,cc,ic from detvta where idvta={idvta}")
        sumic = pgonecolumn(con,f"select sum(ic) from detvta where idvta={idvta}")
        if sumic is None:
            sumic=0
            con.close()
        return jsonify(detvta=detvta,sumic=sumic)



@ventas.route('/ventas/getarticulos')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_getarticulos():
    con = get_con()
    articulos = pglist(con, f"select concat(codigo,'-',art) as art from articulos where activo=1 and codigo is not null")
    con.close()
    return jsonify(result=articulos)


@ventas.route('/ventas/getlistado')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_getlistado():
    con = get_con()
    listado = pglistdict(con,f"select id, fecha, cc, ic, p, pmovto  , comprado, idvdor, primera, cnt, art, (select count(id) from ventas as b where b.idcliente=ventas.idcliente and saldo>0 and pmovto<date_sub(curdate(), interval 120 day)) as count, dnigarante,devuelta,parcial,cambio,idcliente,(select dni from clientes where id=idcliente) as dni from ventas where pp=0 order by id desc limit 100")
    con.close()
    return jsonify(listado=listado)


@ventas.route('/ventas/getlistadocuenta/<int:cuenta>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_getlistadocuenta(cuenta):
    con = get_con()
    listado = pglistdict(con,f"select id, fecha, cc, ic, p, pmovto  , comprado, idvdor, primera, cnt, art, (select count(id) from ventas as b where b.idcliente=ventas.idcliente and saldo>0 and pmovto<date_sub(curdate(), interval 120 day)) as count from ventas where id={cuenta}")
    con.close()
    return jsonify(listado=listado)


@ventas.route('/ventas/listado')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_listado():
    return render_template("ventas/listado.html")


@ventas.route('/ventas/borrarventa/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_borrarventa(id):
    con = get_con()
    stm = f"delete from ventas where id={id}"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(stm)
        cur.close()
        con.close()
        return 'OK'


@ventas.route('/ventas/datosventa/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_datosventa(id):
    con = get_con()
    venta = pglistdict(con, f"select fecha,cc,ic,p,pmovto,idvdor,primera from ventas where id={id}")[0]
    con.close()
    return jsonify(venta=venta)


@ventas.route('/ventas/guardaredicionventa', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_guardaredicionvta():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    if d['dnigarante']:
        garantizado = 1
        dnigarante = d['dnigarante']
    else:
        garantizado = 0
        dnigarante = 0
    upd = f"update ventas set fecha='{d['fecha']}',cc={d['cc']},ic={d['ic']},p={d['p']},pmovto='{d['pmovto']}',idvdor={d['idvdor']},primera='{d['primera']}',garantizado={garantizado},dnigarante={dnigarante} where id={d['id']}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(upd)
        cur.close()
        con.close()
        return 'OK'

@ventas.route('/ventas/clientes')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_clientes():
    return render_template('ventas/clientes.html')


@ventas.route('/ventas/getclientes/<tipo>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_getclientes(tipo):
    """Entrego lista de cliente segun tipo pedido."""
    con = get_con()
    if tipo=='idvta':
        clientes = pglistdict(con, "select ventas.id as idvta,dni, nombre, \
        calle,num,zona, gestion, mudo, incobrable,acla,wapp,sendwapp from \
        ventas, clientes where ventas.idcliente=clientes.id and pp=0 and \
        devuelta=0 order by ventas.id desc limit 500")
    else:
        clientes = pglistdict(con, "select id,dni, nombre, calle,num, zona, \
        gestion,mudo, incobrable,acla from  clientes  order by id desc \
        limit 500")

    con.close()
    return jsonify(clientes=clientes)


@ventas.route('/ventas/calles')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_calles():
    return render_template('ventas/calles.html')


@ventas.route('/ventas/barrios')
@login_required
@check_roles(['dev','gerente','admin'])
def barrios_calles():
    return render_template('ventas/barrios.html')


@ventas.route('/ventas/zonas')
@login_required
@check_roles(['dev','gerente','admin'])
def zonas_calles():
    return render_template('ventas/zonas.html')


@ventas.route('/ventas/getcallesconid')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_getcallesconid():
    con = get_con()
    calles = pglistdict(con, f"select id,calle from calles order by calle")
    con.close()
    return jsonify(calles= calles)


@ventas.route('/ventas/getbarriosconid')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_getbarriosconid():
    con = get_con()
    barrios = pglistdict(con, f"select id,barrio from barrios order by barrio")
    con.close()
    return jsonify(barrios= barrios)


@ventas.route('/ventas/getzonasconid')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_getzonasconid():
    con = get_con()
    zonas = pglistdict(con, f"select id,zona,asignado from zonas order by zona")
    con.close()
    return jsonify(zonas= zonas)


@ventas.route('/ventas/guardaredicioncalle', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_guardaredicioncalle():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    if d['id']=='':
        stm = f"insert into calles(calle) values('{d['calle']}')"
    else:
        stm = f"update calles set calle='{d['calle']}' where id={d['id']}"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(stm)
        cur.close()
        con.close()
        if d['id']=='':
            return 'Se creo una calle con exito'
        else:
            return 'Se edito la calle con exito'



@ventas.route('/ventas/guardaredicionbarrio', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_guardaredicionbarrio():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    upd = f"update barrios set barrio='{d['barrio']}' where id={d['id']}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(upd)
        cur.close()
        con.close()
        return 'OK'


@ventas.route('/ventas/guardaredicionzona', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_guardaredicionzona():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    upd = f"update zonas set zona='{d['zona']}',asignado={d['asignado']} \
    where id={d['id']}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(upd)
        cur.close()
        con.close()
        return 'OK'


@ventas.route('/ventas/borrarcalle/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_borrarcalle(id):
    con = get_con()
    stm = f"delete from calles where id={id}"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(stm)
        cur.close()
        con.close()
        return 'OK'



@ventas.route('/ventas/borrarbarrio/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_borrarbarrio(id):
    con = get_con()
    stm = f"delete from barrios where id={id}"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(stm)
        cur.close()
        con.close()
        return 'OK'


@ventas.route('/ventas/borrarzona/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_borrarzona(id):
    con = get_con()
    stm = f"delete from zonas where id={id}"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(stm)
        cur.close()
        con.close()
        return 'OK'


@ventas.route('/ventas/borrarzonapornombre/<zona>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_borrarzonapornombre(zona):
    con = get_con()
    stm = f"delete from zonas where zona='{zona}'"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(stm)
        cur.close()
        con.close()
        return 'OK'


@ventas.route('/ventas/borrarcallepornombre/<calle>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_borrarcallepornombre(calle):
    con = get_con()
    stm = f"delete from calles where calle='{calle}'"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(stm)
        cur.close()
        con.close()
        return 'OK'


@ventas.route('/ventas/borrarcliente/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_borrarcliente(id):
    con = get_con()
    stm = f"delete from clientes where id={id}"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(stm)
        cur.close()
        con.close()
        return 'OK'


@ventas.route('/ventas/guardarcallenueva', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_guardarcallenueva():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    ins = f"insert into calles(calle) values('{d['calle']}')"
    cur = con.cursor()
    try:
        cur.execute(ins)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(ins)
        cur.close()
        con.close()
        return 'OK'



@ventas.route('/ventas/guardarbarrionueva', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_guardarbarrionueva():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    ins = f"insert into barrios(barrio) values('{d['barrio']}')"
    cur = con.cursor()
    try:
        cur.execute(ins)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(ins)
        cur.close()
        con.close()
        return 'OK'


@ventas.route('/ventas/guardarzonanueva', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_guardarzonanueva():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    ins = f"insert into zonas(zona) values('{d['zona']}')"
    cur = con.cursor()
    try:
        cur.execute(ins)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(ins)
        cur.close()
        con.close()
        return 'OK'


@ventas.route('/ventas/estadisticas')
@login_required
@check_roles(['dev','gerente'])
def ventas_estadisticas():
    return render_template('ventas/estadisticas.html')


@ventas.route('/ventas/estadisticasanuales')
@login_required
@check_roles(['dev','gerente'])
def ventas_estadisticasanuales():
    con = get_con()
    est_anuales = pglistdict(con,f"select date_format(fecha,'%Y') as y, sum(comprado) as comprado, sum(saldo) as saldo, sum(saldo)/sum(comprado) as inc,sum(cnt) as cnt from ventas where devuelta=0 and pp=0 group by y order by y desc")
    con.close()
    return jsonify(est_anuales=est_anuales)


@ventas.route('/ventas/estadisticasmensuales/<string:year>')
@login_required
@check_roles(['dev','gerente'])
def ventas_estadisticasmensuales(year):
    con = get_con()
    est_mensuales = pglistdict(con,f"select date_format(fecha,'%Y-%m') as ym, sum(comprado) as comprado, sum(saldo) as saldo, sum(saldo)/sum(comprado) as inc,sum(cnt) as cnt from ventas where devuelta=0 and pp=0 and date_format(fecha,'%Y')='{year}' group by ym order by ym")
    con.close()
    return jsonify(est_mensuales=est_mensuales)


@ventas.route('/ventas/filtracalles/<string:buscar>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_filtracalles(buscar):
    con = get_con()
    buscar = '%'+buscar.replace(' ','%')+'%'
    listacalles = pglistdict(con,f"select id,calle from calles where lower(calle) like lower('{buscar}')")
    return jsonify(listacalles=listacalles)

@ventas.route('/ventas/getmorosidadprimercuota')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_getmorosidadprimercuota():
    con = get_con()
    upd = "update ventas set vencido=(truncate(datediff(now(),primera)/30,0)+1)*ic where primera < now() and id>79999"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    sel = "select ventas.id as id,fecha,ic,vencido,ventas.pagado as pagado,ventas.pmovto as pmovto,vencido-ventas.pagado as mora, nombre,asignado,EXTRACT(YEAR_MONTH FROM fecha) as ym from ventas,clientes,zonas where ventas.idcliente=clientes.id and clientes.zona=zonas.zona and ventas.id>79999 and primera<now() and cc>1 and devuelta=0 order by mora desc"
    cur.execute(sel)
    morosidad = cur.fetchall()
    con.close()
    return jsonify(morosidad=morosidad)


@ventas.route('/ventas/morosidad')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_morosidad():
    return render_template('ventas/morosidad.html')


@ventas.route('/ventas/devolucion')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_devoluciones():
    return render_template('ventas/devolucion.html')


@ventas.route('/ventas/devolucion/buscarcliente/<int:idvta>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_devolucion_buscarcliente(idvta):
    con = get_con()
    venta = pglistdict(con, f"select * from ventas where id={idvta}")[0]
    nombre = pgonecolumn(con, f"select nombre from clientes where id={venta['idcliente']}")
    arts = pglistdict(con, f"select * from detvta where idvta={idvta} and devuelta=0")
    ic = venta['ic']
    cc = venta['cc']
    return jsonify(nombre=nombre, arts=arts, ic=ic, cc=cc)


@ventas.route('/ventas/devolucion/borrararticulo/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_devolucion_borrararticulo(id):
    """Cuando se hace un cambio o una devolucion parcial,
    le ponemos devuelta=1 al detvta.
    Si cargado=1 hacemos ademas cnt=cnt*(-1) y cargado=0,
    porque al ser un art viejo ya cargado, cuando lo devuelven
    el vendedor debe traerlo a la empresa, por eso el negativo
    y el cargado=0 que se pone.
    Si cargado=0 significa que el art vendido no se cargo todavia,
    y ahora se recupero, o sea se compensa, por eso se pone
    cargado=1 para que no impacte."""
    con = get_con()
    item = pglistdict(con,f"select * from detvta where id={id}")[0]
    cargado = item['cargado']
    cnt = item['cnt']
    art = item['art']
    idvta = item['idvta']
    if cargado==0:
        upd = f"update detvta set devuelta=1, cargado=1 where id={id}"
    else:
        upd = f"update detvta set devuelta=1,cargado=0,cnt=cnt*(-1) where id={id}"
    # en este momento puede que haya un registro en tabla devolucion. Por lo que hay
    # que hacer una verificacion primero para ver si hay que hacer un upd o ins.
    iddev = pgonecolumn(con,f"select id from devoluciones where idvta={idvta}")
    if iddev:
        stmlog = f"update devoluciones set log=concat(log,' devuelto:{cnt}-{art}') where id={iddev}"
    else: # no hay un registro todavia de devoluciones
        stmlog = f"insert into devoluciones(idvta,log) values({idvta},'devuelto:{cnt}-{art}')"
    cur = con.cursor()
    cur.execute(upd)
    cur.execute(stmlog)
    con.commit()
    con.close()
    log(upd)
    return 'ok'


@ventas.route('/ventas/devolucion/agregararticulo', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_agregararticulo():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    ins = f"insert into detvta(cnt,art,ic,cc,idvta) values({d['cnt']},'{d['art']}',{d['ic']},{d['cc']},{d['idvta']})"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    id =  pgonecolumn(con, "SELECT LAST_INSERT_ID()")
    item = pglistdict(con,f"select * from detvta where id={id}")[0]
    cnt = item['cnt']
    art = item['art']
    idvta = item['idvta']
    # en este momento puede que haya un registro en tabla devolucion. Por lo que hay
    # que hacer una verificacion primero para ver si hay que hacer un upd o ins.
    iddev = pgonecolumn(con,f"select id from devoluciones where idvta={idvta}")
    if iddev:
        stmlog = f"update devoluciones set log=concat(log,' agrego:{cnt}-{art}') where id={iddev}"
    else: # no hay un registro todavia de devoluciones
        stmlog = f"insert into devoluciones(idvta,log) values({idvta},'agrego:{cnt}-{art}')"
    cur.execute(stmlog)
    con.commit()
    log(ins)
    con.close()
    return 'ok'

@ventas.route('/ventas/devolucion/obtenerlistaarticulos')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_devolucion_obtenerlistaarticulos():
    con = get_con()
    arts = pglist(con, f"select art from articulos where activo=1")
    con.close()
    return jsonify(arts=arts)


@ventas.route('/ventas/devolucion/procesar', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_devolucion_procesar():
    """Cuando se hace un cambio o una devolucion parcial,
    le ponemos devuelta=1 al detvta.
    Si cargado=1 hacemos ademas cnt=cnt*(-1) y cargado=0,
    porque al ser un art viejo ya cargado, cuando lo devuelven
    el vendedor debe traerlo a la empresa, por eso el negativo
    y el cargado=0 que se pone.
    Si cargado=0 significa que el art vendido no se cargo todavia,
    y ahora se recupero, o sea se compensa, por eso se pone
    cargado=1 para que no impacte."""
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    idvta = d['idvta']
    idcliente = pgonecolumn(con, f"select idcliente from ventas where id={idvta}")
    comprado = pgonecolumn(con, f"select comprado from ventas where id={idvta}")
    cc = int(d['cc'])
    ic = int(d['imp'])
    fechadev = d['fechadev']
    cobr = d['cobr']
    comprdejado = d['comprdejado']
    rboN = d['rbon'] or 0
    totparc = d['totparcial']
    novendermas = d['novendermas'] or 0
    vdor = pgonecolumn(con, f"select idvdor from ventas where id={idvta}")
    mesvta = pgonecolumn(con, f"select date_format(fecha, '%Y-%m') from ventas where id={idvta}")
    if totparc=='Total':
        montodev=comprado
    else:
        montodev = comprado - (cc*ic)
    registro = current_user.email

    cnt = pgonecolumn(con, f"select sum(cnt) from detvta where idvta={idvta} and devuelta=0")
    art = pgonecolumn(con, f"select group_concat(art,'|') from detvta where idvta={idvta} and devuelta=0")

    # update ventas cc/ic/cnt/art para una devolucion parcial
    # update ventas devuelta=1, saldo=0 para una devolucion total
    cur = con.cursor(buffered=True)
    if totparc in ('Parcial','Cambio'):
        if totparc=='Parcial':
            updvta = f"update ventas set cc={cc},ic={ic},cnt={cnt},art='{art}',parcial=1 where id={idvta}"
        else: # osea totparc=='Cambio'
            updvta = f"update ventas set cc={cc},ic={ic},cnt={cnt},art='{art}',cambio=1 where id={idvta}"
        cur.execute(updvta)
        con.commit()
        log(updvta)
    else:   # totparc=='Total'
        updvta = f"update ventas set devuelta=1, saldo=0 where id={idvta}"
        cur.execute(updvta)
        con.commit()
        log(updvta)
    #   update detvta poner devuelta=1 a los articulos devueltos en una devolucion total
        ids_detvta = pglist(con, f"select id from detvta where idvta={idvta}")
        logging.warning(f"ids_detvta {ids_detvta}")
        for id in ids_detvta:
            cargado = pgonecolumn(con, f"select cargado from detvta where id={id}")
            if cargado==0:
                upddetvta = f"update detvta set devuelta=1,cargado=1 where id={id}"
            else: # osea cargado==1 articulo viejo pongo cargado=0 y cnt=cnt*(-1)
                upddetvta = f"update detvta set devuelta=1, cargado=0, cnt=cnt*(-1) where id={id}"
            cur.execute(upddetvta)
            log(upddetvta)
            item = pglistdict(con,f"select * from detvta where id={id}")[0]
            cnt = item['cnt']
            art = item['art']
            idvta = item['idvta']
            iddev = pgonecolumn(con,f"select id from devoluciones where idvta={idvta}")
            logging.warning(f"iddev cuando procesa art por art {iddev}")
            if iddev:
                stmlog = f"update devoluciones set log=concat(log,' devolvio:{cnt}-{art}') where id={iddev}"
            else: # no hay un registro todavia de devoluciones
                stmlog = f"insert into devoluciones(idvta,log) values({idvta},'devolvio:{cnt}-{art}')"
            cur.execute(stmlog)
        con.commit()
    #  update ventas novendermas segun el valor de dicha variable
    if novendermas:
        updnvm = f"update clientes set novendermas=1 where id={idcliente}"
        cur.execute(updnvm)
        con.commit()
        log(updnvm)

    # update devoluciones con todos los datos de la devolucion
    iddev = pgonecolumn(con,f"select id from devoluciones where idvta={idvta}")
    logging.warning(f"iddev {iddev}")
    upd = f"update devoluciones set fechadev='{fechadev}',cobr={cobr},comprdejado='{comprdejado}',rboN='{rboN}',totparc='{totparc}',novendermas={novendermas},vdor={vdor},mesvta='{mesvta}',montodev={montodev},registro='{registro}' where id={iddev}"
    logging.warning(upd)
    cur.execute(upd)
    # se pone el campo clientes.proceso_devolucion=0
    upd_proceso = f"update clientes set proceso_devolucion=0 where id={idcliente}"
    # se pone el campo datos.quiere_devolver=0
    upd_dato = f"update datos set quiere_devolver=0 where idcliente={idcliente}"
    cur.execute(upd_proceso)
    cur.execute(upd_dato)
    con.commit()
    log(upd)
    con.close()

    return 'ok'





@ventas.route('/ventas/condonar/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_condonar(id):
    con = get_con()
    condonada = pgonecolumn(con, f"select condonada from ventas where id={id}")
    condonada = 1 if condonada == 0 or condonada is None else 0
    upd = f"update ventas set condonada={condonada} where id={id}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    log(upd)
    con.close()
    return 'ok'


@ventas.route('/ventas/pordia')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_pordia():
    """Pandas ventas por dia para controlar entradas."""
    pd.options.display.float_format = '{:.0f}'.format
    sql = "select fecha,comprado,idvdor from ventas where devuelta=0 and pp=0 \
    and fecha>date_sub(curdate(),interval 1 month) and idvdor>15 \
    order by id desc"
    dat = pd.read_sql_query(sql, engine)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values=['comprado'],index='fecha',\
                         columns='idvdor',aggfunc='sum').sort_index(axis=0,\
                                            level='fecha',ascending=False)
    tot = tbl.iloc[:,0].add(tbl.iloc[:,1],axis=0,fill_value=0).tolist()
    tbl.insert(2,'total',tot)
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="tableventas",classes="table")
    return render_template("ventas/pordia.html", tbl=tbl)


@ventas.route('/ventas/pormes')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_pormes():
    """Pandas de ventas por mes, presente año."""
    pd.options.display.float_format = '${:.0f}'.format
    sql = "select date_format(fecha,'%Y-%m') as mes,comprado,idvdor from \
    ventas where devuelta=0 and pp=0 and year(fecha)=year(curdate()) and \
    idvdor>15 order by id desc"
    dat = pd.read_sql_query(sql, engine)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values=['comprado'],index='mes',columns='idvdor',\
                         aggfunc='sum').sort_index(axis=0, level='mes',\
                                                   ascending=True)
    tot = tbl.iloc[:,0].add(tbl.iloc[:,1],axis=0,fill_value=0).tolist()
    tbl.insert(2,'total',tot)
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="tableventas",classes="table")
    return render_template("ventas/pormes.html", tbl=tbl, tot=tot)


@ventas.route('/ventas/artyear')
@login_required
@check_roles(['dev','gerente'])
def ventas_artyear():
    """Pandas de venta articulos por año."""
    pd.options.display.float_format = '{:.0f}'.format
    sql = "select year(fecha) as año,detvta.cnt as cnt,detvta.art as art \
    from ventas,detvta where ventas.devuelta=0 and fecha>'2017-12-31' \
    and ventas.id=detvta.idvta order by ventas.id desc"
    dat = pd.read_sql_query(sql, engine)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values=['cnt'],index='art',columns='año',\
                         aggfunc='sum').sort_index(axis=0, level='art',\
                                                   ascending=False)
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="tableartyear",classes="table")
    return render_template("ventas/artyear.html", tbl=tbl)


@ventas.route('/ventas/pivotdevoluciones')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_pivotdevoluciones():
    """Pandas de devoluciones."""
    pd.options.display.float_format = '${:.0f}'.format
    sql = "select montodev,vdor,mesvta from devoluciones where \
    fechadev>date_sub(curdate(),interval 1 year)"
    dat = pd.read_sql_query(sql, engine)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values=['montodev'],index='mesvta',columns='vdor',aggfunc='sum').sort_index(axis=0, level='mesvta',ascending=False)
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="pivotdevoluciones",classes="table")
    return render_template("ventas/pivotdevoluciones.html", tbl=tbl )


@ventas.route('/ventas/obtenerwappcliente/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_obtenerwappcliente(id):
    con = get_con()
    wapp = pgonecolumn(con, f"select wapp from clientes where id={id}")
    return jsonify(wapp=wapp)


@ventas.route('/ventas/obtenerventasultyear')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_obtenerventasultyear():
    """Entrega lista de ventas ultimo ano."""
    con = get_con()
    listventas = []
    result = pglistdict(con, "select date_format(fecha,'%Y-%m') as ym, \
    sum(comprado) as vta from ventas where fecha>date_sub(curdate(),\
    interval 1 year)  group by ym")
    for row in result:
        listventas.append(row['vta'])
    return jsonify(ventas=listventas)


@ventas.route('/ventas/buscarcliente/<string:buscar>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_buscarcliente(buscar):
    con = get_con()
    rdni = r'^[0-9]{7,8}$'
    sql = f"select * from clientes where dni='{buscar}'"
    if (re.match(rdni, buscar)):
        clientes = pglistdict(con, sql)
        error_msg = "DNI no encontrado"
    else:
        error_msg = "Ponga un formato valido de DNI"
        clientes = []
    if len(clientes) == 0:
        return make_response(error_msg, 400)
    con.close()
    return jsonify(clientes=clientes)


@ventas.route('/ventas/cambiazonas')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_cambiazonas():
    return render_template('ventas/rezonificar.html')


@ventas.route('/ventas/cambiacalles')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_cambiacalles():
    return render_template('ventas/recallificar.html')


@ventas.route('/ventas/getclienteszona/<zona>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_getclienteszona(zona):
    con = get_con()
    clientes = pglistdict(con, f"select * from clientes where zona='{zona}' order by barrio")
    return jsonify(clientes=clientes)


@ventas.route('/ventas/getclientescalle/<calle>')
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_getclientescalle(calle):
    con = get_con()
    clientes = pglistdict(con, f"select * from clientes where calle='{calle}' order by num")
    return jsonify(clientes=clientes)


@ventas.route('/ventas/cambiarzona/<string:zona>',methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_cambiarzona(zona):
    con = get_con()
    listaid = json.loads(request.data.decode("UTF-8"))
    lpg ='('
    for id in listaid:
        lpg+="'"+id+"'"+","
    lpg = lpg[0:-1]+")"
    upd = f"update clientes set zona='{zona}' where id in {lpg}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(upd)
        cur.close()
        con.close()
        return 'OK'


@ventas.route('/ventas/cambiarcalle/<string:calle>',methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def ventas_cambiarcalle(calle):
    con = get_con()
    listaid = json.loads(request.data.decode("UTF-8"))
    lpg ='('
    for id in listaid:
        lpg+="'"+id+"'"+","
    lpg = lpg[0:-1]+")"
    upd = f"update clientes set calle='{calle}' where id in {lpg}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        con.commit()
        log(upd)
        cur.close()
        con.close()
        return 'OK'


@ventas.route('/3ibzPLLq53RuFgIqkq6G3bSzO/<dni>')
@ventas.route('/ventas/obtenerdatosgarante/<dni>')
@login_required
@check_roles(['dev','gerente','admin','vendedor'])
def ventas_obtenerdatosgarante(dni):
    con = get_con()
    garante = pglistdict(con, f"select nombre, concat(calle, ' ', num) as direccion from clientes where dni={dni}")
    if len(garante)>0:
        return jsonify(garante=garante)
    else:
        return make_response('dni no existe', 404)



@ventas.route('/ventas/ingresoventas')
@login_required
@check_roles(['dev','gerente'])
def ventas_ingresoventas():
    return render_template("/ventas/ingresoventas.html")


@ventas.route('/ventas/visitas')
@login_required
@check_roles(['dev', 'gerente'])
def ventas_visitas():
    return render_template('/ventas/visitas.html')


@ventas.route('/ventas/cargarartvdor')
@login_required
@check_roles(['dev', 'gerente','admin'])
def ventas_cargarartvdores():
    return render_template('/ventas/cargarartvdor.html')


@ventas.route('/ventas/comisiones')
@login_required
@check_roles(['dev', 'gerente'])
def ventas_comisiones():
    return render_template('/ventas/comisiones.html')

@ventas.route('/ventas/comisionesprom')
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def ventas_comisionesprom():
    return render_template('/ventas/comisionesprom.html')

@ventas.route('/ventas/yearcompra')
@login_required
@check_roles(['dev', 'gerente'])
def ventas_yearcompra():
    """Pandas de ventas por año."""
    pd.options.display.float_format = '${:.0f}'.format
    sql="select id,EXTRACT(YEAR_MONTH FROM fechacompra) as ym, yultcompra from prospectos where compro=1"
    dat = pd.read_sql_query(sql, engine)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values=['id'],index='yultcompra',columns='ym',aggfunc='count').sort_index(axis=1, level='ym',ascending=False)
    tbl = tbl.fillna("")
    tbl = tbl.to_html(table_id="yultcompra",classes="table")
    return render_template("ventas/yearcompra.html", tbl=tbl)


@ventas.route('/ventas/vtalistadozonas')
@login_required
@check_roles(['dev', 'gerente'])
def ventas_vtalistadozonas():
    """Pandas de ventas de listado por zonas."""
    pd.options.display.float_format = '${:.0f}'.format
    sql="select date_format(fecha,'%Y-%m') as fp,ventas.comprado as venta, zona from ventas,clientes where clientes.id=ventas.idcliente and fecha >date_sub(curdate(),interval 365 day) and idvdor=835"
    dat = pd.read_sql_query(sql, engine)
    df = pd.DataFrame(dat)
    tbl = pd.pivot_table(df, values=['venta'],index='zona',columns='fp',aggfunc='sum').sort_index(axis=1, level='fp',ascending=False)
    tbl = tbl.fillna("")
    index = tbl.columns.tolist()
    tbl = tbl.to_html(table_id="vtazonas",classes="table")
    return render_template("ventas/vtalistadozona.html", tbl=tbl, index=index )


@ventas.route('/ventas/isindevolucion/<int:idvta>')
@login_required
@check_roles(['dev', 'gerente'])
def ventas_isindevolucion(idvta):
    con = get_con()
    is_in_dev = pgonecolumn(con, f"select id from devoluciones where idvta={idvta}")
    if is_in_dev:
        isindevolucion = 1
    else:
        isindevolucion = 0
    return jsonify(isindevolucion=isindevolucion)


@ventas.route('/pDfkNKQMQvgp8Zbqa0C6ETYAh/<int:idvta>')
@ventas.route('/ventas/marksendwapp/<int:idvta>')
@login_required
@check_roles(['dev','gerente','vendedor'])
def ventas_marksendwapp(idvta):
    con = get_con()
    upd = f"update ventas set sendwapp=1 where id={idvta} and pp=0"
    # pp=0 asegura que no se marcaran los planes de pago
    pgexec(con, upd)
    con.close()
    return 'ok'


@ventas.route('/ventas/resendwapp/<int:idvta>')
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def ventas_resendwapp(idvta):
    con = get_con()
    (idcliente,cc,ic,primera,arts) = pgtuple(con, f"select idcliente,cc,ic,\
    primera,art from ventas where id={idvta}")
    (nombre,wapp) = pgtuple(con, f"select nombre,wapp from clientes where \
    id={idcliente}")
    arts = arts.replace('|',' ')
    msg = f"""Estimado cliente: {nombre}, agradecemos su compra de {arts}.
Le recordamos que el plan de pagos elegido es de {cc} cuotas mensuales de ${ic} y la primer cuota vence el dia {primera:%d-%m-%Y} para cualquier consulta no dude en contactarnos, estamos a su disposición!."""
    response = send_msg_whatsapp(idcliente, wapp, msg)
    print('response',response)
    if response == 'success':
        pgexec(con, f"update ventas set sendwapp=1 where id={idvta}")
    send_file_whatsapp(
            idcliente,f"https://www.fedesal.lol/pdf/informacion-importante.pdf", wapp)
    con.close()
    return response
