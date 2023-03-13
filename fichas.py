from flask import Blueprint,render_template,jsonify,make_response, request, send_file
from flask_login import login_required, current_user
from lib import *
import simplejson as json
from con import get_con, log, check_roles
from formularios import *
import mysql.connector
import time
from datetime import date

fichas = Blueprint('fichas',__name__)

@fichas.route('/fichas')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_():
    return render_template("fichas/fichaje.html")


@fichas.route('/fichas/getcobradores')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_getcobradores():
    con = get_con()
    cobradores = pglistdict(con,"select id from cobr where activo=1 and prom=0 and id>15")
    con.close()
    return jsonify(cobradores=cobradores)


@fichas.route('/fichas/muestrazonas/<int:cobr>')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_muestrazona(cobr):
    con = get_con()
    zonas = pglistdict(con,f"select zona from zonas where asignado={cobr}")
    con.close()
    return jsonify(zonas=zonas)


@fichas.route('/fichas/muestraclientes/<string:tipo>/<string:zona>')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_muestraclientes(tipo,zona):
    con = get_con()
    if tipo=='normales':
        clientes = pglistdict(con,f"select * from clientes where zona='{zona}' and pmovto>date_sub(curdate(),interval 210 day) and deuda>0  and gestion=0 and incobrable=0 and mudo=0 order by pmovto")
    elif tipo=='gestion':
        clientes = pglistdict(con,f"select * from clientes where zona like '{zona}' and pmovto>date_sub(curdate(),interval 210 day) and deuda>0  and (gestion=1 or incobrable=1 or mudo=1) order by pmovto")
    elif tipo=='antiguos':
        clientes = pglistdict(con,f"select * from clientes where zona like '{zona}' and pmovto<=date_sub(curdate(),interval 210 day) and deuda>0  order by ultpago desc")
    elif tipo=='nuevomoroso':
        clientes = pglistdict(con,f"select * from clientes where zona like '{zona}' and pmovto<=date_sub(curdate(),interval 5 day) and deuda>0 and ultcompra>date_sub(curdate(),interval 30 day)  order by pmovto")
    elif tipo=='morosos':
        clientes = pglistdict(con,f"select * from clientes where zona like '{zona}' and pmovto<=date_sub(curdate(),interval 60 day) and pmovto>date_sub(curdate(),interval 210 day) and deuda>0  order by pmovto")
    elif tipo=='vender':
        clientes = pglistdict(con,f"select * from clientes where zona like '{zona}' and ultpago>=date_sub(curdate(),interval 40 day) and deuda>0 and deuda<=cuota and sev=0 and novendermas=0 and gestion=0 and mudo=0 and incobrable=0  order by zona,calle,num")
    elif tipo=='cancelados':
        clientes = pglistdict(con,f"select * from clientes where zona like '{zona}' and deuda=0  order by ultpago desc")
    elif tipo=='ppagos':
        clientes = pglistdict(con,f"select * from clientes where zona like '{zona}' and deuda>0 and planvigente=1  order by ultpago desc")
    elif tipo=='garantizado':
        clientes = pglistdict(con,f"select * from clientes where zona like '{zona}' and deuda>0 and garantizado=1  order by ultpago desc")
    con.close()
    return jsonify(clientes=clientes)


@fichas.route('/fichas/imprimir', methods = ['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_imprimir():
    con = get_con()
    # aca se el ast.literal entrega la lista enviada por el axios-post directamente
    listadni = json.loads(request.data.decode("UTF-8"))
    zona,cobr = pgtuple(con, f"select clientes.zona as zona, asignado from \
    clientes, zonas where clientes.zona=zonas.zona and \
    clientes.dni={listadni[0]}")
    total_cobrable = pgonecolumn(con, f"select monto from estimados where \
                 zona='{zona}' and mes=date_format(curdate(),'%Y%m')")
    total_cobrado = pgonecolumn(con, f"select sum(imp+rec) from pagos,clientes \
    where pagos.idcliente=clientes.id and zona='{zona}' and cobr={cobr} and \
                     date_format(fecha,'%Y%m')=date_format(curdate(),'%Y%m')")

    ficha(con, listadni, total_cobrable, total_cobrado)
    con.close()
    return send_file('/home/hero/ficha.pdf')


@fichas.route('/fichas/intimar', methods = ['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_intimar():
    con = get_con()
    listadni = json.loads(request.data.decode("UTF-8"))
    # aca se el ast.literal entrega la lista enviada por el axios-post directamente
    intimacion(con, listadni)
    con.close()
    return send_file('/home/hero/intimacion_global.pdf')


@fichas.route('/fichas/intimarpdf', methods=["POST"])
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_intimarpdf():
    con = get_con()
    listadni = json.loads(request.data.decode("UTF-8"))
    for dni in listadni:
        wapp = pgonecolumn(con, f"select wapp from clientes where dni={dni}")
        if wapp:
            idcliente = pgonecolumn(con, f"select id from clientes where dni={dni}")
            intimacion(con, [dni])
            response = send_file_whatsapp(idcliente,f'https://www.fedesal.lol/pdf/intimacion{dni}.pdf', wapp)
            if response == 'success':
                upd = f"update clientes set fechaintimacion=curdate() where dni={dni}"
                cur = con.cursor()
                cur.execute(upd)
                con.commit()
    con.close()
    return 'ok'

def msg_intimacion(dni):
    con = get_con()
    sev, nombre, idcliente,calle,num = pgtuple(con, f"select sev, nombre, id, calle, num from clientes where dni={dni}")
    # nombre = pgonecolumn(con, f"select nombre from clientes where dni={dni}")
    fecha, articulos = pgtuple(con, f"select fecha,art from ventas where idcliente={idcliente} order by fecha desc limit 1")
    direccion = f"{calle} {num}"
    if sev:
        text="Nos comunicamos de la empresa ROMITEX por una deuda que usted tiene con la firma. Usted fue subido al SEVEN hasta regularizar su cuenta. Puede hacer un plan de pagos. Consulte por Wapp. Una vez cancelado en 48hs se lo elimina del SEVEN. De no desmostrar interes nos vemos obligados a cobrar su pagare por via JUDICIAL. Atte. *Departamento de cobranzas de ROMITEX*"
    else:
        text="Nos comunicamos de la empresa ROMITEX por una deuda que usted tiene con la firma. En los proximos dias deberemos informar al SEVEN el atraso de su cuenta. Le proponemos un plan de pagos que podemos realizar por este medio."
    messaje = f"{nombre.upper()}: {text}  \n(Por compra de {articulos} realizada en {direccion} el dia {fecha})."
    messaje = messaje.replace(' ','%20')
    return messaje, idcliente


@fichas.route('/fichas/intimarwhatsapp', methods=["POST"])
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_intimarwhatsapp():
    con = get_con()
    listadni = json.loads(request.data.decode("UTF-8"))
    for dni in listadni:
        wapp = pgonecolumn(con, f"select wapp from clientes where dni={dni}")
        if wapp:
            msg, idcliente = msg_intimacion(dni)
            send_msg_whatsapp(idcliente, wapp, msg)
            # espero 10 segundos por requerimientos de la  whatsapp api
            #time.sleep(10)
            # registro la intimacion
            upd = f"update clientes set fechaintimacion=curdate() where dni={dni}"
            cur = con.cursor()
            cur.execute(upd)
            con.commit()
    con.close()
    return 'ok'


@fichas.route('/fichas/recordatorioswapp', methods=["POST"])
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_recordatorioswapp():
    clientes = json.loads(request.data.decode("UTF-8"))
    for cliente in clientes:
        if cliente['wapp']:
            msgRecordatorio = f"{('Estimado ' if cliente['sex']=='M' else 'Estimada ')}{cliente['nombre'].upper()}: Buenos dias, le escribimos de ROMITEX para recordarle el vencimiento de su cuota. Le pedimos que nos envie por este medio el comprobante de la transferencia, asi le enviamos el recibo correspondiente. Gracias!"
            send_msg_whatsapp(cliente['id'], cliente['wapp'], msgRecordatorio)
            #time.sleep(10)
    return 'ok'


@fichas.route('/fichas/msgprogramado', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_msgprogramado():
    d = json.loads(request.data.decode("UTF-8"))
    clientes = d['listaclientes']
    msg = d['msg']
    for cliente in clientes:
        if cliente['wapp']:
            send_msg_whatsapp(cliente['id'], cliente['wapp'], msg)
    return 'ok'


@fichas.route('/fichas/cambiarzona/<string:zona>',methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_cambiarzona(zona):
    con = get_con()
    listadni = json.loads(request.data.decode("UTF-8"))
    lpg ='('
    for dni in listadni:
        lpg+="'"+dni+"'"+","
    lpg = lpg[0:-1]+")"
    upd = f"update clientes set zona='{zona}' where dni in {lpg}"
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


@fichas.route('/fichas/cobradores')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_cobradores():
    return render_template('fichas/cobr.html')


@fichas.route('/fichas/programar')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_programar():
    return render_template('fichas/programar.html')


@fichas.route('/fichas/getfullcobradores')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_getfullcobradores():
    con = get_con()
    cobradores = pglistdict(con,f"select * from cobr order by id desc")
    con.close()
    return jsonify(cobradores=cobradores)


@fichas.route('/fichas/toggleactivo/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_toggleactivo(id):
    con = get_con()
    activo = pgonecolumn(con, f"select activo from cobr where id={id}")
    if activo:
        upd = f"update cobr set activo=0 where id={id}"
    else:
        upd = f"update cobr set activo=1 where id={id}"
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


@fichas.route('/fichas/toggleprom/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_toggleprom(id):
    con = get_con()
    prom = pgonecolumn(con, f"select prom from cobr where id={id}")
    if prom:
        upd = f"update cobr set prom=0 where id={id}"
    else:
        upd = f"update cobr set prom=1 where id={id}"
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


@fichas.route('/fichas/togglevdor/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_togglevdor(id):
    con = get_con()
    vdor = pgonecolumn(con, f"select vdor from cobr where id={id}")
    if vdor:
        upd = f"update cobr set vdor=0 where id={id}"
    else:
        upd = f"update cobr set vdor=1 where id={id}"
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


@fichas.route('/fichas/borrarcobrador/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_borrarcobrador(id):
    con = get_con()
    stm = f"delete from cobr where id={id}"
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


@fichas.route('/fichas/getcobradorbyid/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_getcobradorbyid(id):
    con = get_con()
    cobrador = pglistdict(con, f"select id,dni,nombre,direccion,telefono,fechanac, desde, activo,prom from cobr where id={id}")[0]
    con.close()
    return jsonify(cobrador=cobrador)


@fichas.route('/fichas/guardarcobrador' , methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_guardarcobrador():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    if d['id']!='':
        stm = f"update cobr set dni='{d['dni']}', nombre='{d['nombre']}', direccion='{d['direccion']}', telefono='{d['telefono']}', fechanac='{d['fechanac']}', desde='{d['desde']}', activo={d['activo']}, prom={d['prom']} where id= {d['id']}"
    else:
        stm = f"insert into cobr(dni,nombre, direccion, telefono, fechanac,desde,activo,prom) values('{d['dni']}','{d['nombre']}','{d['direccion']}','{d['telefono']}','{d['fechanac']}', '{d['desde']}', {d['activo']}, {d['prom']})"
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


@fichas.route('/fichas/fechador')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_fechador():
    return render_template('fichas/fechador.html')


@fichas.route('/fichas/buscacuenta/<int:idvta>')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_buscacuenta(idvta):
    con = get_con()
    cuenta = pglistdict(con, f"select nombre, clientes.pmovto as pmovto,asignado \
    from clientes, ventas,zonas where clientes.id=ventas.idcliente and \
    clientes.zona=zonas.zona and ventas.id={idvta}")
    if cuenta:
        cuenta = cuenta[0]
    con.close()
    return jsonify(cuenta=cuenta)


@fichas.route('/fichas/guardarfechado/<int:idvta>/<string:pmovto>/<int:cobr>')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_guardarfechado(idvta,pmovto,cobr):
    con = get_con()
    idcliente = pgonecolumn(con, f"select idcliente from ventas where id={idvta}")
    expmovto = pgonecolumn(con, f"select pmovto from clientes where id={idcliente}")
    upd = f"update clientes set pmovto='{pmovto}' where id = {idcliente}"
    ins = f"insert into fechados(fecha,idcliente,expmovto,pmovto,cobr) values(current_date(),{idcliente},'{expmovto}','{pmovto}',{cobr})"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as e:
        con.rollback()
        error = e.msg
        return make_response(error,400)
    else:
        cur.execute(ins)
        con.commit()
        log(upd)
        cur.close()
        con.close()
        return 'OK'


@fichas.route('/fichas/listado')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_listado():
    return render_template('fichas/listado.html')


@fichas.route('/fichas/getzonas')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_getzonas():
    con = get_con()
    zonas = pglist(con,f"select zona from zonas where asignado>700 and asignado !=820 order by zona")
    vdores = pglist(con, "select id from cobr where activo=1 and vdor=1 and id>500")
    con.close()
    return jsonify(zonas=zonas, vdores=vdores)


@fichas.route('/fichas/getmsgs')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_getmsgs():
    con = get_con()
    msgs = pglistdict(con, f"select * from msgs")
    con.close()
    return jsonify(msgs=msgs)


@fichas.route('/fichas/getlistado/<string:zona>')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_getlistado(zona):
    con = get_con()
    direcciones_deudoras = listsql(pglist(con, "select concat(calle,num) from \
    clientes where deuda>2000 and pmovto<date_sub(curdate(),interval 90 day) \
                                           and incobrable=0"))
    dire_deudoras_con_inc = listsql(pglist(con, "select concat(calle,num) \
    from clientes where deuda>2000 and pmovto<date_sub(curdate(),interval 90 \
    day) and incobrable=1"))
    listado = pglistdict(con, f"select date_format(ultpago,'%Y') as year, ultpago, \
    dni,nombre, concat(calle,' ',num) as direccion from clientes where zona=\
    '{zona}' and deuda=0 and incobrable=0 and mudo=0 and gestion=0 and \
    novendermas=0 and comprado>0 and ultpago>'2010-01-01' and \
    concat(calle,num) not in {direcciones_deudoras} and  \
    (fechadato is null or fechadato<ultcompra or datediff(now(),fechadato)>45) order by ultpago desc")
    noexceptuados =  pglistdict(con, f"select date_format(ultpago,'%Y') as year, ultpago, \
    dni,nombre, concat(calle,' ',num) as direccion from clientes where zona=\
    '{zona}' and deuda=0 and incobrable=0 and mudo=0 and gestion=0 and \
    novendermas=0 and comprado>0 and ultpago>'2010-01-01' and \
    concat(calle,num) in {dire_deudoras_con_inc} and  \
    (fechadato is null or fechadato<ultcompra or datediff(now(),fechadato)>45) order by ultpago desc")
    exceptuados =  pglistdict(con, f"select date_format(ultpago,'%Y') as year, ultpago, \
    dni,nombre, concat(calle,' ',num) as direccion from clientes where zona=\
    '{zona}' and deuda=0 and incobrable=0 and mudo=0 and gestion=0 and \
    novendermas=0 and comprado>0 and ultpago>'2010-01-01' and \
    concat(calle,num) in {direcciones_deudoras} and  \
    (fechadato is null or fechadato<ultcompra or datediff(now(),fechadato)>45) order by ultpago desc")
    con.close()
    return jsonify(listado=listado, exceptuados=exceptuados, noexceptuados=noexceptuados)


@fichas.route('/fichas/getresumen/<string:zona>')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_getresumen(zona):
    con = get_con()
    resumen = pglistdict(con, f"select date_format(ultpago,'%Y') as y, count(*) as cnt from clientes where zona='{zona}' and deuda=0 and incobrable=0 and mudo=0 and gestion=0 and novendermas=0 and ultpago>'2010-01-01' group by y order by y")
    con.close()
    return jsonify(resumen=resumen)


@fichas.route('/fichas/imprimirlistado', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_imprimirlistado():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    listadni = d['lista']
    formato = d['formato']
    listado(con, listadni, formato)
    con.close()
    return send_file('/home/hero/listado.pdf')


@fichas.route('/fichas/obtenerlistadofechados')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_obtenerlistadofechados():
    con = get_con()
    listado = pglistdict(con, f"select fechados.id as id,nombre,expmovto,fechados.pmovto as pmovto,cobr from fechados,clientes where clientes.id=fechados.idcliente and fecha=current_date() order by fechados.id desc")
    con.close()
    return jsonify(listado=listado)


@fichas.route('/fichas/borrarfechado/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_borrarfechado(id):
    con = get_con()
    fechado = pglistdict(con, f"select * from fechados where id={id}")[0]
    stm = f"delete from fechados where id={id}"
    upd = f"update clientes set pmovto = '{fechado['expmovto']}' where id={fechado['idcliente']}"
    cur = con.cursor()
    cur.execute(stm)
    cur.execute(upd)
    log(stm)
    log(upd)
    con.commit()
    con.close()
    return 'OK'


@fichas.route('/fichas/asuntos')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_asuntos():
    return render_template("/fichas/asuntos.html")


@fichas.route('/fichas/getasuntos')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_getasuntos():
    con = get_con()
    asuntos = pglistdict(con, f"select asuntos.id as id, idcliente, tipo, fecha, vdor, asunto,nombre,completado from asuntos,clientes where clientes.id=asuntos.idcliente")
    con.close()
    return jsonify(asuntos=asuntos)


@fichas.route('/fichas/deleteasunto/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_deleteasunto(id):
    con = get_con()
    stm = f"delete from asuntos where id={id}"
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    log(stm)
    con.close()
    return 'ok'


@fichas.route('/fichas/editarasunto', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_editarasunto():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    upd = f"update asuntos set fecha='{d['fecha']}',tipo='{d['tipo']}',vdor={d['vdor']},asunto='{d['asunto']}' where id={d['id']}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    log(upd)
    con.close()
    return 'ok'


@fichas.route('/fichas/toggleasuntocompletado/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_toggleasuntocompletado(id):
    con = get_con()
    estado = pgonecolumn(con, f"select completado from asuntos where id={id}")
    if estado:
        upd = f"update asuntos set completado=0 where id={id}"
    else:
        upd = f"update asuntos set completado=1 where id={id}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    log(upd)
    con.close()
    return 'ok'


@fichas.route('/fichas/imprimirasunto' , methods = ['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_imprimirasunto():
    con = get_con()
    ids = json.loads(request.data.decode("UTF-8"))
    # aca se el ast.literal entrega la lista enviada por el axios-post directamente

    asuntos(con, ids)
    con.close()
    return send_file('/home/hero/asuntos.pdf')


@fichas.route('/fichas/cancelados')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_cancelado():
    return render_template("fichas/cancelados.html")


@fichas.route('/fichas/getcancelados')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_getcancelados():
    con = get_con()
    direcciones_deudoras = listsql(pglist(con, "select concat(calle,num) from \
    clientes where deuda>2000 and pmovto<date_sub(curdate(),interval 90 day) \
                                           and incobrable=0"))
    dire_deudoras_con_inc = listsql(pglist(con, "select concat(calle,num) from \
    clientes where deuda>2000 and pmovto<date_sub(curdate(),interval 90 day) \
    and incobrable=1"))
    cancelados = pglistdict(con, f"select ultpago, nombre, calle, num, zona, tel, \
    wapp, dni from clientes where deuda=0 and incobrable=0 and mudo=0 and \
    gestion=0 and novendermas=0 and ultpago>date_sub(curdate(),interval 30 \
    day) and (fechadato is null or fechadato<ultcompra or datediff(now(),fechadato)>45) and concat(calle,num) \
    not in {direcciones_deudoras}  order by ultpago desc")
    noexceptuados = pglistdict(con, f"select ultpago,nombre,calle,num,zona,tel, \
    wapp, dni from clientes where deuda=0 and incobrable=0 and mudo=0 and \
    gestion=0 and novendermas=0 and ultpago>date_sub(curdate(),interval 30 \
    day) and (fechadato is null or fechadato<ultcompra or datediff(now(),fechadato)>45) and concat(calle,num) \
    in {dire_deudoras_con_inc}  order by ultpago desc")
    exceptuados = pglistdict(con, f"select ultpago,nombre,calle,num,zona,tel, \
    wapp, dni from clientes where deuda=0 and incobrable=0 and mudo=0 and \
    gestion=0 and novendermas=0 and ultpago>date_sub(curdate(),interval 30 \
    day) and (fechadato is null or fechadato<ultcompra or datediff(now(),fechadato)>45) and concat(calle,num) \
    in {direcciones_deudoras}  order by ultpago desc")
    max_ultpago = pgonecolumn(con, f"select max(ultpago) from clientes where \
    deuda=0  and ultpago>date_sub(curdate(),interval 30 day)")
    vdores = pglist(con, "select id from cobr where vdor=1 and activo=1")
    return jsonify(cancelados=cancelados, max_ultpago=max_ultpago,vdores=\
                   vdores,exceptuados=exceptuados,noexceptuados=\
                   noexceptuados)


@fichas.route('/fichas/mudados')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_mudados():
    return render_template("fichas/mudados.html")


@fichas.route('/fichas/getmudados')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_getmudados():
    con = get_con()
    mudados = pglistdict(con, f"select nombre, calle, num, zona, tel, wapp, dni from clientes where deuda=0 and  mudo=1 and mudado_llamado=0 and novendermas=0 and ultpago>date_sub(curdate(), interval 4 year) order by ultpago desc")
    return jsonify(mudados=mudados)


@fichas.route('/fichas/imprimircancelados', methods = ['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_imprimircancelados():
    con = get_con()
    listadni = json.loads(request.data.decode("UTF-8"))
    # aca se el ast.literal entrega la lista enviada por el axios-post directamente

    cancelados(con, listadni)
    con.close()
    return send_file('/home/hero/cancelados.pdf')


@fichas.route('/fichas/toggleMudadoLlamado/<string:dni>')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_togglemudadollamado(dni):
    con = get_con()
    upd = f"update clientes set mudado_llamado=1 where dni={dni}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    log(upd)
    con.close()
    return 'ok'


@fichas.route('/fichas/programarboton', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_programarboton():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    id = d['id']
    nombre = d['nombre']
    msg = d['msg']
    file = d['file']
    upd = f"update msgs set nombre = '{nombre}', msg='{msg}',file='{file}' \
    where id={id}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    log(upd)
    con.close()
    return 'ok'


@fichas.route('/fichas/procesarlistado', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_procesarlistado():
    """Proceso la planilla de clientes a visitar."""
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    cobr = d['vdor']
    zona = d['zona']
    clientes = d['clientes']
    cnt_cl = len(clientes)
    user = current_user.email

    ins = f"insert into listavisitar(fecha,cobr,zona,cntclientes,\
           user) values(curdate(),{cobr},'{zona}',{cnt_cl},'{user}')"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    log(ins)
    idlistavisitar = pgonecolumn(con, "SELECT LAST_INSERT_ID()")

    for dni in clientes:
        cliente = pglistdict(con, f"select id, year(ultcompra) as yultcompra from\
                  clientes where dni={dni}")[0]
        if not cliente['yultcompra']:
            cliente['yultcompra'] = date.today().year
        ins = f"insert into prospectos(idlistavisitar,idcliente,yultcompra,\
              fecha,vdor,zona) values({idlistavisitar},{cliente['id']},\
              {cliente['yultcompra']},curdate(),{cobr},'{zona}')"
        cur.execute(ins)
    con.commit()
    con.close()
    return 'ok'

@fichas.route('/fichas/listavisitar')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_listavisitar():
    return render_template('/fichas/listavisitar.html')


@fichas.route('/fichas/getlistalistados')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_getlistalistados():
    con = get_con()
    listalistados = pglistdict(con, "select * from listavisitar order by id desc")
    return jsonify(listalistados=listalistados)


@fichas.route('/fichas/borrarlistavisitar/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def fichas_borrarlistavisitar(id):
    con = get_con()
    stm = f"delete from listavisitar where id={id}"
    cur = con.cursor()
    cur.execute(stm)
    con.commit()
    con.close()
    log(stm)
    return 'ok', 200
