from flask import Blueprint,render_template,jsonify,make_response, request
from flask_login import login_required, current_user
from .lib import *
from .con import get_con, log
import pandas as pd
import simplejson as json
import mysql.connector

ventas = Blueprint('ventas',__name__)

@ventas.route('/ventas/pasarventas')
@login_required
def ventas_pasarventas():
    return render_template('ventas/pasarventas.html')


@ventas.route('/ventas/getcalles')
def ventas_getcalles():
    con = get_con()
    calles = pglflat(con, f"select calle from calles order by calle")
    con.close()
    return jsonify(calles= calles)


@ventas.route('/ventas/getbarrios')
def ventas_getbarrios():
    con = get_con()
    barrios = pglflat(con, f"select barrio from barrios order by barrio")
    con.close()
    return jsonify(barrios= barrios)


@ventas.route('/ventas/getzonas')
def ventas_getzonas():
    con = get_con()
    zonas = pglflat(con, f"select zona from zonas order by zona")
    con.close()
    return jsonify(zonas= zonas)


@ventas.route('/ventas/getcuentapordni/<string:dni>')
def ventas_getcuentaspordni(dni):
    con = get_con()
    try:
        clientes = pgdict(con,f"select sex,dni,nombre,calle,num,barrio,zona,tel,wapp,acla,horario,mjecobr,infoseven,id from clientes where dni='{dni}'")
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
def ventas_guardarcliente():
    con = get_con()
    # d = json.loads(request.data.decode("UTF-8"))
    d = json.loads(request.data.decode("UTF-8"))
    # print(d)
    if d['id']=="":
        stm = f"insert into clientes(sex,dni,nombre,calle,num,barrio,zona,tel,wapp,acla,horario,mjecobr,infoseven) values('{d['sex']}','{d['dni']}','{d['nombre']}','{d['calle']}','{d['num']}','{d['barrio']}','{d['zona']}','{d['tel']}','{d['wapp']}','{d['acla']}','{d['horario']}','{d['mjecobr']}','{d['infoseven']}')"
    else:
        stm = f"update clientes set sex='{d['sex']}', dni='{d['dni']}', nombre='{d['nombre']}',calle='{d['calle']}',num='{d['num']}',barrio='{d['barrio']}', zona='{d['zona']}',tel='{d['tel']}', wapp='{d['wapp']}', acla='{d['acla']}', horario='{d['horario']}', mjecobr='{d['mjecobr']}', infoseven='{d['infoseven']}' where id={d['id']}"
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
        if d['id']=="":
            id = pgonecolumn(con,f"select id from clientes order by id desc limit 1")
        else:
            id = d['id']
            ins = f"insert into logcambiodireccion(idcliente,calle,num,barrio,tel,acla,fecha,nombre,dni,wapp) values({d['id']},'{d['calle']}','{d['num']}','{d['barrio']}','{d['tel']}','{d['acla']}',curdate(),'{d['nombre']}','{d['dni']}','{d['wapp']}')"
            cur = con.cursor()
            cur.execute(ins)
            con.commit()
            log(ins)
            cur.close()
        con.close()
        return jsonify(id=id)


@ventas.route('/ventas/guardarventa', methods=['POST'])
def ventas_guardarventa():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
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
def ventas_guardardetvta():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    costo = pgonecolumn(con, f"select costo from articulos where art='{d['art']}'")
    ins = f"insert into detvta(idvta,cnt,art,cc,ic,costo) values({d['idvta']},{d['cnt']},'{d['art']}',{d['cc']},{d['ic']},{costo})"
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
        detvta = pgdict(con,f"select id,cnt,art,cc,ic from detvta where idvta={d['idvta']}")
        sumic = pgonecolumn(con,f"select sum(ic) from detvta where idvta={d['idvta']}")
        con.close()
        return jsonify(detvta=detvta,sumic=sumic)


@ventas.route('/ventas/borrardetvta/<int:id>')
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
        detvta = pgdict(con,f"select id,cnt,art,cc,ic from detvta where idvta={idvta}")
        sumic = pgonecolumn(con,f"select sum(ic) from detvta where idvta={idvta}")
        if sumic is None:
            sumic=0
        con.close()
        return jsonify(detvta=detvta,sumic=sumic)



@ventas.route('/ventas/getarticulos')
def ventas_getarticulos():
    con = get_con()
    articulos = pglflat(con, f"select art from articulos where activo=1")
    con.close()
    return jsonify(articulos=articulos)


@ventas.route('/ventas/getlistado')
def ventas_getlistado():
    con = get_con()
    listado = pgdict(con,f"select id, fecha, cc, ic, p, pmovto  , comprado, idvdor, primera, cnt, art, (select count(id) from ventas as b where b.idcliente=ventas.idcliente and saldo>0 and pmovto<date_sub(curdate(), interval 120 day)) as count from ventas order by id desc limit 200")
    con.close()
    return jsonify(listado=listado)


@ventas.route('/ventas/listado')
def ventas_listado():
    return render_template("ventas/listado.html")


@ventas.route('/ventas/borrarventa/<int:id>')
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
def ventas_datosventa(id):
    con = get_con()
    venta = pgdict(con, f"select fecha,cc,ic,p,pmovto,idvdor,primera from ventas where id={id}")[0]
    con.close()
    return jsonify(venta=venta)


@ventas.route('/ventas/guardaredicionventa', methods=['POST'])
def ventas_guardaredicionvta():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    upd = f"update ventas set fecha='{d['fecha']}',cc={d['cc']},ic={d['ic']},p={d['p']},pmovto='{d['pmovto']}',idvdor={d['idvdor']},primera='{d['primera']}' where id={d['id']}"
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
def ventas_clientes():
    return render_template('ventas/clientes.html')


@ventas.route('/ventas/getclientes')
def ventas_getclientes():
    con = get_con()
    clientes = pgdict(con, f"select ventas.id as idvta, nombre, calle,num, zona, gestion, mudo, incobrable,acla from ventas, clientes where ventas.idcliente=clientes.id order by ventas.id desc limit 200")
    con.close()
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
    con = get_con()
    calles = pgdict(con, f"select id,calle from calles order by calle")
    con.close()
    return jsonify(calles= calles)


@ventas.route('/ventas/getbarriosconid')
def ventas_getbarriosconid():
    con = get_con()
    barrios = pgdict(con, f"select id,barrio from barrios order by barrio")
    con.close()
    return jsonify(barrios= barrios)


@ventas.route('/ventas/getzonasconid')
def ventas_getzonasconid():
    con = get_con()
    zonas = pgdict(con, f"select id,zona from zonas order by zona")
    con.close()
    return jsonify(zonas= zonas)


@ventas.route('/ventas/guardaredicioncalle', methods=['POST'])
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
def ventas_guardaredicionzona():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    upd = f"update zonas set zona='{d['zona']}' where id={d['id']}"
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

@ventas.route('/ventas/guardarcallenueva', methods=['POST'])
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
def ventas_estadisticas():
    return render_template('ventas/estadisticas.html')


@ventas.route('/ventas/estadisticasanuales')
@login_required
def ventas_estadisticasanuales():
    con = get_con()
    est_anuales = pgdict(con,f"select date_format(fecha,'%Y') as y, sum(comprado) as comprado, sum(saldo) as saldo, sum(saldo)/sum(comprado) as inc,sum(cnt) as cnt from ventas group by y order by y desc")
    # print(est_anuales)
    con.close()
    return jsonify(est_anuales=est_anuales)


@ventas.route('/ventas/estadisticasmensuales/<string:year>')
@login_required
def ventas_estadisticasmensuales(year):
    con = get_con()
    est_mensuales = pgdict(con,f"select date_format(fecha,'%Y-%m') as ym, sum(comprado) as comprado, sum(saldo) as saldo, sum(saldo)/sum(comprado) as inc,sum(cnt) as cnt from ventas where date_format(fecha,'%Y')='{year}' group by ym order by ym")
    print(est_mensuales)
    con.close()
    return jsonify(est_mensuales=est_mensuales)


@ventas.route('/ventas/filtracalles/<string:buscar>')
def ventas_filtracalles(buscar):
    con = get_con()
    buscar = '%'+buscar.replace(' ','%')+'%'
    listacalles = pgdict(con,f"select id,calle from calles where lower(calle) like lower('{buscar}')")
    return jsonify(listacalles=listacalles)

@ventas.route('/ventas/getmorosidadprimercuota')
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
def ventas_morosidad():
    return render_template('ventas/morosidad.html')


@ventas.route('/ventas/devolucion')
def ventas_devoluciones():
    return render_template('ventas/devolucion.html')

@ventas.route('/ventas/devolucion/buscarcliente/<int:idvta>')
def ventas_devolucion_buscarcliente(idvta):
    con = get_con()
    idcliente = pgonecolumn(con, f"select idcliente from ventas where id={idvta}")
    nombre = pgonecolumn(con, f"select nombre from clientes where id={idcliente}")
    arts = pgdict(con, f"select * from detvta where idvta={idvta}")
    return jsonify(nombre=nombre, arts=arts)


@ventas.route('/ventas/devolucion/borrararticulo/<int:id>')
def ventas_devolucion_borrararticulo(id):
    con = get_con()
    stm = f"delete from detvta where id={id}"
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    con.close()
    log(stm)
    return 'ok'


@ventas.route('/ventas/devolucion/obtenerlistaarticulos')
def ventas_devolucion_obtenerlistaarticulos():
    con = get_con()
    arts = pglflat(con, f"select art from articulos where activo=1")
    con.close()
    return jsonify(arts=arts)


@ventas.route('/ventas/devolucion/procesar', methods=['POST'])
def ventas_devolucion_procesar():
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

    cnt = pgonecolumn(con, f"select sum(cnt) from detvta where idvta={idvta}")
    art = pgonecolumn(con, f"select group_concat(art,'|') from detvta where idvta={idvta}")
    
    # update ventas cc/ic/cnt/art para una devolucion parcial
    # update ventas devuelta=1, saldo=0 para una devolucion total
    cur = con.cursor(buffered=True)
    if totparc=='Parcial':
        updvta = f"update ventas set cc={cc},ic={ic},cnt={cnt},art='{art}' where id={idvta}"
        cur.execute(updvta)
        con.commit()
        log(updvta)
    else:   # totparc=='Total'
        updvta = f"update ventas set devuelta=1, saldo=0 where id={idvta}"
        cur.execute(updvta)
        con.commit()
        log(updvta)
    #   update detvta poner devuelta=1 a los articulos devueltos en una devolucion total
        upddetvta = f"update detvta set devuelta=1 where idvta={idvta}"
        cur.execute(upddetvta)
        con.commit()
        log(upddetvta)
    #  update ventas novendermas segun el valor de dicha variable
    if novendermas:
        updnvm = f"update clientes set novendermas=1 where id={idcliente}"
        cur.execute(updnvm)
        con.commit()
        log(updnvm)
        
    # insert devoluciones con todos los datos de la devolucion
    ins = f"insert into devoluciones(idvta,fechadev,cobr,comprdejado,rboN,totparc,novendermas,vdor,mesvta,montodev,registro) values({idvta},'{fechadev}',{cobr},'{comprdejado}','{rboN}','{totparc}',{novendermas}, {vdor}, '{mesvta}', {montodev},'{registro}')" 
    print(ins)
    cur.execute(ins)
    con.commit()
    log(ins)
    con.close()

    return 'ok'
