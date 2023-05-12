"""Modulo que dirige todo lo relativo a la busqueda de clientes."""
import re
import logging
import simplejson as json
import mysql.connector
from flask import Blueprint, render_template, jsonify, make_response, request,\
    send_file
from flask_login import login_required, current_user
from lib import pgonecolumn, pglistdict, send_msg_whatsapp, send_file_whatsapp, \
    pglist, log_busqueda, listsql, actualizar, send_img_whatsapp, pgexec
from formularios import intimacion, libredeuda, ficha, recibotransferencia
from con import get_con, log, check_roles


buscador = Blueprint('buscador', __name__)


def obtenerdni(idcliente):
    """Simple funcion que retorn el dni dado el idcliente."""
    con = get_con()
    dni = pgonecolumn(con, f"select dni from clientes where id={idcliente}")
    return dni


@buscador.route('/buscador', methods=['GET', 'POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_():
    """Muestra pagina buscador."""
    return render_template("buscador/buscar.html")


@buscador.route('/buscador/clientenuevo')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_clientenuevo():
    """Pantalla generar cliente nuevo."""
    return render_template("buscador/clientenuevo.html")


@buscador.route('/buscador/clientenuevovdor')
@login_required
@check_roles(['dev','gerente'])
def buscador_clientenuevovdor():
    """Pantalla ver los clientes ingresados por los vendedores."""
    return render_template("buscador/clientenuevovdor.html")


@buscador.route('/buscador/verdatos')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_verdatos():
    """Pantalla generar vista de datos."""
    return render_template("buscador/verdatos.html")


@buscador.route('/buscador/enviardatos')
@login_required
@check_roles(['dev','gerente'])
def buscador_autorizardatos():
    """Pantalla generar vista de enviar datos."""
    return render_template("buscador/enviardatos.html")


@buscador.route('/buscador/reautorizardatos')
@login_required
@check_roles(['dev','gerente'])
def buscador_reautorizardatos():
    """Pantalla generar vista de reautorizar datos."""
    return render_template("buscador/reautorizardatos.html")


@buscador.route('/buscador/listaautorizados')
@login_required
@check_roles(['dev','gerente'])
def buscador_listaautorizados():
    """Pantalla generar vista de reautorizar datos."""
    return render_template("buscador/listaautorizados.html")


@buscador.route('/buscador/revisardatos')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_revisardatos():
    """Pantalla generar vista de revision de datos enviados."""
    return render_template("buscador/revisardatos.html")


@buscador.route('/pdf/<pdf>')
#@login_required
#@check_roles(['dev','gerente','admin'])
def buscador_pdf(pdf):
    """Reenvia un pdf por una ruta."""
    return send_file('/home/hero/'+pdf)


@buscador.route('/img/<img>')
#@login_required
#@check_roles(['dev','gerente','admin'])
def buscador_img(img):
    """Reenvia una imagen por una ruta."""
    return send_file('/home/hero/'+img)


@buscador.route('/log')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_log():
    """Muestra pagina log."""
    return render_template('buscador/log.html')


@buscador.route('/buscador/interno/<dni>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_interno_buscar(dni):
    """Anexo buscador para ver-cuenta desde otra pagina."""
    if len(str(dni))<7:
        dni = obtenerdni(dni)
    return render_template('/buscador/buscar.html', dnilistado=dni)


@buscador.route('/buscador/<string:buscar>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_cuenta(buscar):
    """Funcion principal de buscar cuenta."""
    con = get_con()
    rcuenta = r'^[0-9]{5}$'
    rdni = r'^[0-9]{6,8}$'
    rid = r'^id[0-9]{4,5}$'
    rwapp = r'^[0-9]{10,15}$'
    if buscar == "-":
        sql = "select * from clientes where id=0"
        error_msg = "ingrese algo para buscar"
    elif re.match(rcuenta, buscar):
        cur = con.cursor()
        try:
            cur.execute(f'select idcliente from ventas where id={buscar}')
            idcliente = cur.fetchone()[0]
            sql = f"select * from clientes where id={idcliente}"
        except:
            sql = "select * from clientes where id=0"
            error_msg = "Cuenta no encontrada"
    elif re.match(rdni, buscar):
        sql = f"select * from clientes where dni='{buscar}'"
        error_msg = "DNI no encontrado"
    elif re.match(rwapp, buscar):
        sql = f"select * from clientes where wapp='{buscar}'"
        error_msg = "Whatsapp no encontrado"
    elif re.match(rid, buscar):
        sql = f"select * from clientes where id={buscar[2:]}"
        error_msg = "idcliente no encontrado"
    else:
        buscar = re.sub(r'^(\w)', '%'+r'\1', buscar)
        buscar = re.sub(r'(\s)(\D)', '%'+r'\2', buscar)
        buscar = re.sub(r'(\s)(\d)', '% '+r'\2', buscar)
        buscar = re.sub(r'\*', '%', buscar)
        buscar = re.sub(r'(\D)$', r'\1'+'%', buscar)
        sql = f"select * from clientes where lower(concat(nombre,calle,acla,\
        ' ' ,num)) like lower('{buscar}') order by calle,num"
        error_msg = "no hay respuesta para esa busqueda"
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    clientes = cur.fetchall()
    if len(clientes) == 0:
        return make_response(error_msg, 400)
    con.close()
    log_busqueda(buscar)
    return jsonify(clientes=clientes)


@buscador.route('/buscador/getasignado/<zona>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_getasignado(zona):
    con = get_con()
    asignado = pgonecolumn(con, f"select asignado from zonas where \
    zona='{zona}'")
    return jsonify(asignado=asignado)


@buscador.route('/buscador/clientesdireccion/<string:calle>/<string:num>')
@login_required
@check_roles(['dev','gerente','admin'])
def clientesdireccion(calle, num):
    """Entrega lista de clientes en la direccion."""
    con = get_con()
    cur = con.cursor(dictionary=True)
    sql = f"select * from clientes where calle='{calle}' and num='{num}'"
    cur.execute(sql)
    clientes = cur.fetchall()
    con.close()
    return jsonify(clientes=clientes)


@buscador.route('/buscador/pedirpagadasporidcliente/<int:idcliente>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_pedirpagadasporidcliente(idcliente):
    """Entrega lista de cuotas pagadas por idcliente."""
    sql = f"select * from pagos where idcliente={idcliente} order by id desc"
    con = get_con()
    pagadas = pglistdict(con, sql)
    con.close()
    return jsonify(pagadas=pagadas)


@buscador.route('/buscador/obtenerventasporidcliente/<int:idcliente>')
@login_required
@check_roles(['dev','gerente','admin','cobrador'])
def buscar_obtenerventasporidcliente(idcliente):
    """Entrega lista de ventas por idcliente."""
    sql = f"select * from ventas where idcliente={idcliente} and saldo>0 order \
    by id desc"
    con = get_con()
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    ventas = cur.fetchall()
    con.close()
    return jsonify(ventas=ventas)


@buscador.route('/buscador/pedircomentarios/<int:idcliente>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_pedircomentarios(idcliente):
    """Entrega lista de comentarios por idcliente."""
    sql = f"select * from comentarios where idcliente={idcliente}"
    con = get_con()
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    comentarios = cur.fetchall()
    con.close()
    return jsonify(comentarios=comentarios)


@buscador.route('/buscador/guardarcomentario/<int:idcliente>', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_guardarcomentario(idcliente):
    """Guarda comentario ingresado."""
    d = json.loads(request.data.decode("UTF-8"))
    ins = f"insert into comentarios(idcliente,fechahora,comentario,ingreso) \
    values({idcliente},'{d['fechahora']}','{d['comentario']}','{d['ingreso']}')"
    con = get_con()
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    log(ins)
    con.close()
    return 'ok'


@buscador.route('/buscador/deletecomentario/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_deletecomentario(id):
    con = get_con()
    stm = f"delete from comentarios where id={id}"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error,400)
    else:
        con.commit()
        con.close()
        log(stm)
        return 'ok'


@buscador.route('/buscador/pedirlogcambiodireccion/<int:idcliente>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_logcambiodireccion(idcliente):
    """Entrega lista de logcambiodireccion."""
    sql = f"select fecha,calle,num,wapp,acla from logcambiodireccion where idcliente={idcliente}"
    con = get_con()
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    logcambiodireccion = cur.fetchall()
    con.close()
    return jsonify(logcambiodireccion=logcambiodireccion)


@buscador.route('/buscador/obtenerventascanceladasporidcliente/<int:idcliente>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_obtenerventascanceladasporidcliente(idcliente):
    """Entrega lista de ventas canceladas por idcliente."""
    sql = f"select * from ventas where idcliente={idcliente} and saldo<=0 order by id desc"
    con = get_con()
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    ventascanceladas = cur.fetchall()
    con.close()
    return jsonify(ventascanceladas=ventascanceladas)


@buscador.route('/buscador/guardarpmovto/<int:idcliente>/<string:pmovto>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_guardarpmovto(idcliente, pmovto):
    """Guarda el pmovto editado del cliente."""
    con = get_con()
    sql = f"update clientes set pmovto='{pmovto}' where id={idcliente}"
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    log(sql)
    con.close()
    return 'ok'


@buscador.route('/buscador/imprimirficha', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_imprimirficha():
    """Funcion para imprimir ficha de cliente."""
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    dni = d['dni']
    wapp = d['whatsapp']
    idcliente = d['idcliente']
    ficha(con, [dni])
    con.close()
    pattern = re.compile("\D")
    not_valid_wapp = pattern.search(wapp)
    logging.warning(f"/buscador/imprimirficha wapp:{wapp} idcliente:{idcliente} not_valid_wapp:{not_valid_wapp}")
    if wapp and not not_valid_wapp:
        response = send_file_whatsapp(
            idcliente, "https://www.fedesal.lol/pdf/ficha.pdf", wapp)
        return jsonify(response=response)
    else:
        return 'error',400


@buscador.route('/buscador/imprimirfichanowapp', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_imprimirfichanowapp():
    """Funcion para imprimir ficha de cliente en pantalla."""
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    dni = d['dni']
    ficha(con, [dni])
    con.close()
    return send_file('/home/hero/ficha.pdf')


@buscador.route('/buscador/togglesube/<string:dni>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_togglesube(dni):
    """Funcion para marcar subir al seven."""
    con = get_con()
    selsube = f"select subirseven from clientes where dni='{dni}'"
    selsev = f"select sev from clientes where dni='{dni}'"
    sube = pgonecolumn(con, selsube)
    sev = pgonecolumn(con, selsev)
    if sev == 0:
        if sube:
            upd = f"update clientes set subirseven=0 where dni='{dni}'"
            msg = "Registro desmarcado para subir seven"
        else:
            upd = f"update clientes set subirseven=1 where dni='{dni}'"
            msg = "Registro marcado para subir seven"
        cur = con.cursor()
        cur.execute(upd)
        con.commit()
        log(upd)
        cur.close()
        return jsonify(msg=msg)
    else:
        con.close()
        msg = 'No se sube pq ya esta en el seven'
        return jsonify(msg=msg)


@buscador.route('/buscador/togglegestion/<string:dni>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_togglegestion(dni):
    """Funcion para marcar subir a gestion."""
    con = get_con()
    sel = f"select gestion from clientes where dni='{dni}'"
    sube = pgonecolumn(con, sel)
    if sube:
        upd = f"update clientes set gestion=0 where dni='{dni}'"
        msg = "Registro desmarcado como Gestion"
    else:
        upd = f"update clientes set gestion=1 where dni='{dni}'"
        msg = "Registro marcado como Gestion"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    log(upd)
    cur.close()
    con.close()
    return jsonify(msg=msg)


@buscador.route('/buscador/togglemudo/<string:dni>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_togglemudado(dni):
    """Funcion para marcar mudado."""
    con = get_con()
    sel = f"select mudo from clientes where dni='{dni}'"
    sube = pgonecolumn(con, sel)
    if sube:
        upd = f"update clientes set mudo=0 where dni='{dni}'"
        msg = "Registro desmarcado como Mudado"
    else:
        upd = f"update clientes set mudo=1 where dni='{dni}'"
        msg = "Registro marcado como Mudado"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except:
        return make_response("un error se ha producido", 400)
    else:
        con.commit()
        log(upd)
        cur.close()
        con.close()
        return jsonify(msg=msg)


@buscador.route('/buscador/toggleinc/<string:dni>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_toggleinc(dni):
    """Funcion para marcar incobrable."""
    con = get_con()
    sel = f"select incobrable from clientes where dni='{dni}'"
    sube = pgonecolumn(con, sel)
    if sube:
        upd = f"update clientes set incobrable=0 where dni='{dni}'"
        msg = "Registro desmarcado como Incobrable"
    else:
        upd = f"update clientes set incobrable=1 where dni='{dni}'"
        msg = "Registro marcado como Incobrable"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    log(upd)
    cur.close()
    con.close()
    return jsonify(msg=msg)


@buscador.route('/buscador/togglenvm/<string:dni>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_togglenvm(dni):
    """Funcion para marcar lista negra."""
    con = get_con()
    sel = f"select novendermas from clientes where dni='{dni}'"
    sube = pgonecolumn(con, sel)
    if sube:
        upd = f"update clientes set novendermas=0 where dni='{dni}'"
        msg = "Registro desmarcado como No Vender Mas"
    else:
        upd = f"update clientes set novendermas=1 where dni='{dni}'"
        msg = "Registro marcado como No Vender Mas"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    log(upd)
    cur.close()
    con.close()
    return jsonify(msg=msg)


@buscador.route('/buscador/togglellamar/<string:dni>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_togglellamar(dni):
    """Funcion para marcar cliente a llamar."""
    con = get_con()
    sel = f"select llamar from clientes where dni='{dni}'"
    sube = pgonecolumn(con, sel)
    if sube:
        upd = f"update clientes set llamar=0 where dni='{dni}'"
        msg = "Registro desmarcado para Llamar"
    else:
        upd = f"update clientes set llamar=1 where dni='{dni}'"
        msg = "Registro marcado para Llamar"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    log(upd)
    cur.close()
    con.close()
    return jsonify(msg=msg)


@buscador.route('/buscador/toggleseguir/<string:dni>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_toggleseguir(dni):
    """Funcion para marcar cliente a seguir."""
    con = get_con()
    sel = f"select seguir from clientes where dni='{dni}'"
    sube = pgonecolumn(con, sel)
    if sube:
        upd = f"update clientes set seguir=0 where dni='{dni}'"
        msg = "Registro desmarcado para Seguir"
    else:
        upd = f"update clientes set seguir=1 where dni='{dni}'"
        msg = "Registro marcado para Seguir"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    log(upd)
    cur.close()
    con.close()
    return jsonify(msg=msg)


@buscador.route('/buscador/guardaredicioncliente/<int:idcliente>',\
                methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def busca_guardaredicioncliente(idcliente):
    """Funcion para guardar edicion cliente."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    cliente_viejo = pglistdict(con, f"select * from clientes where id=\
    {d_data['id']}")[0]
    upd = f"update clientes set sex='{d_data['sex']}', dni='{d_data['dni']}',\
    nombre='{d_data['nombre']}', calle='{d_data['calle']}', num={d_data['num']}\
    , barrio='{d_data['barrio']}', zona='{d_data['zona']}', tel=\
    '{d_data['tel']}', wapp='{d_data['wapp']}',acla='{d_data['acla']}', \
    mjecobr='{d_data['mjecobr']}', horario='{d_data['horario']}',\
    infoseven='{d_data['infoseven']}' where id={idcliente}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error,400)
    else:
        log(upd)
        con.commit()
        ins = f"insert into logcambiodireccion(idcliente,calle,num,barrio,\
        tel,acla,fecha,nombre,dni,wapp) values({cliente_viejo['id']},\
        '{cliente_viejo['calle']}','{cliente_viejo['num']}',\
        '{cliente_viejo['barrio']}','{cliente_viejo['tel']}',\
        '{cliente_viejo['acla']}',curdate(),'{cliente_viejo['nombre']}',\
        '{cliente_viejo['dni']}','{cliente_viejo['wapp']}')"
        if cliente_viejo['calle'] != d_data['calle'] or cliente_viejo['num'] !=\
           d_data['num'] or cliente_viejo['acla'] != d_data['acla'] or \
               cliente_viejo['wapp'] != d_data['wapp']:
            cur.execute(ins)
            con.commit()
            log(ins)
        return 'ok'
    finally:
        con.close()


@buscador.route('/buscador/obtenerlistadocalles')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_obtenerlistadocalles():
    """Funcion que entrega listado de calles."""
    con = get_con()
    calles = pglist(con, "select calle from calles order by calle")
    con.close()
    return jsonify(result=calles)


@buscador.route('/buscador/obtenerlistabarrios')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_obtenerlistabarrios():
    """Funcion que entrega listado de barrios."""
    con = get_con()
    barrios = pglist(con,"select barrio from barrios order by barrio")
    con.close()
    return jsonify(result=barrios)


@buscador.route('/buscador/obtenerlistazonas')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_obtenerlistazonas():
    """Funcion que entrega listado de zonas."""
    con = get_con()
    zonas = pglist(con,"select zona from zonas order by zona")
    con.close()
    return jsonify(result=zonas)


@buscador.route('/buscador/obtenercobradores')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_obtenercobradores():
    """Funcion que entrega lista cobradores.

    activo=1, prom=0, id>100 para evitar 10,15 y id!=820 que es romitex."""
    con = get_con()
    cobradores = pglist(con,"select id from cobr where activo=1 and prom=0 \
    and id>100 and id!=820 order by id")
    con.close()
    return jsonify(cobradores=cobradores)


@buscador.route('/buscador/pedirwappcobrador/<cobr>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_pedirwappcobrador(cobr):
    "Simple funcion que obtiene el wapp de un cobrador dado."""
    con = get_con()
    wapp = pgonecolumn(con, f"select telefono from cobr where id={cobr}")
    con.close()
    return jsonify(wapp=wapp)


def buscar_buscarplandepagos_muerto(idcliente):
    """Funcion que busca planes de pago muertos del cliente.

    En el caso que tenga mas de un idvta con pp=1 por error del ultimo tiempo
    pedimos el ultimo con max(id), en caso que exista buscamos si tiene pagos
    asociados. Si no tiene pagos asociados se puede borrar tranquilamente y
    devuelvo True o sea el plan de pagos esta muerto, y en otro caso ya sea que
    no exista una idvta con pp=1 o si existe tenga pagos hechos devuelvo False
    o sea el plan de pagos no esta muerto.
    """
    con = get_con()
    # pongo max(id) pq hay casos no muchos que tienen planes superpuestos
    idplan = pgonecolumn(con, f"select max(id) from ventas where pp=1 and \
        idcliente={idcliente}")
    # ahora averiguo de ese idvta hizo pagos
    if idplan is not None:
        pagos = pglist(con, f"select id from pagos where idvta={idplan}")
        if len(pagos)==0:
            return True
    return False


@buscador.route('/buscador/generarplandepagos', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_generarplandepagos():
    """Proceso para generar un plan de pagos."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    idcliente = d_data['idcliente']
    stm = None
    if buscar_buscarplandepagos_muerto(idcliente):
        idplanmuerto = pgonecolumn(con, f"select max(id) from ventas where \
            pp=1 and idcliente={idcliente}")
        stm = f"delete from ventas where id={idplanmuerto}"
    upd = f"update ventas set saldo=0, pcondo=1, pp=0 where idcliente=\
        {idcliente} and saldo>0"
    ins = f"insert into ventas(fecha,cc,ic,p,primera,pp,idvdor,idcliente,cnt,\
                               art)values('{d_data['fecha']}',{d_data['cc']},\
                                          {d_data['ic']},{d_data['p']},\
                                          '{d_data['primera']}',1,10,\
                                          {idcliente},1,'Plan de Pagos')"
    cur = con.cursor()
    deuda = pgonecolumn(con, f"select deuda from clientes where id={idcliente}")
    pmovto = pgonecolumn(con, f"select date_format(pmovto,'%Y%c') from \
        clientes where id={idcliente}")
    saldoact = actualizar(deuda,pmovto)
    try:
        if stm is not None:
            cur.execute(stm)
        cur.execute(upd)
        cur.execute(ins)
        idvta = pgonecolumn(con,  "SELECT LAST_INSERT_ID()")
        insplan = f"insert into planes(fecha,idcliente,user,cc,ic,p,primera,\
        saldoact,saldo,idvta) values(current_date(),{idcliente},\
        '{current_user.email}',{d_data['cc']},{d_data['ic']},{d_data['p']},\
        '{d_data['primera']}',{saldoact},{int(d_data['cc'])*int(d_data['ic'])},\
                                     {idvta})"
        cur.execute(insplan)
    except mysql.connector.Error as _error:
        if stm is not None:
            logging.warning(stm)
        logging.warning(ins)
        logging.warning(upd)
        logging.warning(insplan)
        con.rollback()
        error = _error.msg
        logging.warning(error)
        return make_response(error, 400)
    else:
        con.commit()
        log(upd)
        log(ins)
        log(insplan)
        if stm is not None:
            log(stm)
        return 'ok'
    finally:
        con.close()


@buscador.route('/buscador/imagenes', methods=["POST"])
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_imagenes():
    """Proceso intimar cliente."""
    d_data = json.loads(request.data.decode("UTF-8"))
    dni = d_data['dni']
    wapp = d_data['wapp']
    idcliente = d_data['id']
    con = get_con()
    pattern = re.compile("\D")
    not_valid_wapp = pattern.search(wapp)
    logging.warning(f"/buscador/imagenes wapp:{wapp} idcliente:{idcliente} \
        not_valid_wapp:{not_valid_wapp}")
    if wapp and not not_valid_wapp:
        response = send_img_whatsapp(
            idcliente, f"https://www.fedesal.lol/img/cortinas.jpeg", wapp)
        if response == 'success':
            upd = f"update clientes set fechaintimacion=curdate() where \
                dni={dni}"
            cur = con.cursor()
            cur.execute(upd)
            con.commit()
    else:
        response = 'invalid'
    con.close()
    return jsonify(response=response)


@buscador.route('/buscador/intimar', methods=["POST"])
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_intimar():
    """Proceso intimar cliente."""
    d_data = json.loads(request.data.decode("UTF-8"))
    dni = d_data['dni']
    wapp = d_data['wapp']
    idcliente = d_data['id']
    con = get_con()
    intimacion(con, [dni])
    pattern = re.compile("\D")
    not_valid_wapp = pattern.search(wapp)
    logging.warning(f"/buscador/intimar wapp:{wapp} idcliente:{idcliente} \
        not_valid_wapp:{not_valid_wapp}")
    if wapp and not not_valid_wapp:
        response = send_file_whatsapp(
            idcliente, f"https://www.fedesal.lol/pdf/intimacion{dni}.pdf", wapp)
        if response == 'success':
            upd = f"update clientes set fechaintimacion=curdate() where \
                dni={dni}"
            cur = con.cursor()
            cur.execute(upd)
            con.commit()
    else:
        response = 'invalid'
    con.close()
    return jsonify(response=response)


@buscador.route('/buscador/intimar/nowapp/<dni>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_intimar_nowapp(dni):
    """Proceso de intimar cuando no hay wapp, imprimiendo en pantalla."""
    con = get_con()
    intimacion(con, dni)
    return send_file(f'/home/hero/intimacion{dni}.pdf')


@buscador.route('/buscador/libredeuda', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_libredeuda():
    """Proceso de emision de libre deuda."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    dni = d_data['dni']
    wapp = d_data['wapp']
    deuda = d_data['deuda']
    idcliente = d_data['idcliente']
    libredeuda(con, dni)
    pattern = re.compile("\D")
    not_valid_wapp = pattern.search(wapp)
    logging.warning(f"/buscador/libredeuda wapp:{wapp} idcliente:{idcliente} \
        not_valid_wapp:{not_valid_wapp}")
    if wapp and not not_valid_wapp and deuda<=0:
        response = send_file_whatsapp(
            idcliente, f"https://www.fedesal.lol/pdf/libredeuda{dni}.pdf", wapp)
        return jsonify(response)
    return 'invalid',400


@buscador.route('/buscador/libredeuda/nowapp', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_libredeuda_nowapp():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    dni = d['dni']
    libredeuda(con, dni)
    return send_file(f'/home/hero/libredeuda{dni}.pdf')


@buscador.route('/buscador/obtenerlogs')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_obtenerlogs():
    con = get_con()
    logs = pglistdict(con, "select * from log order by id desc limit 1000")
    con.close()
    return jsonify(logs=logs)


@buscador.route('/buscador/cargarasunto', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_cargarasunto():
    d = json.loads(request.data.decode("UTF-8"))
    con = get_con()
    ins = f"insert into asuntos(idcliente, fecha, vdor, tipo, asunto) values ({d['idcliente']}, '{d['fecha']}','{d['vdor']}','{d['tipo']}','{d['asunto']}') "
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    log(ins)
    con.close()
    return 'ok'


@buscador.route('/buscador/obtenerlistacalles')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_obtenerlistacalles():
    con = get_con()
    calles = pglist(con, 'select calle from calles order by calle')
    return jsonify(result=calles)


@buscador.route('/buscador/mostrarcalle/<string:calle>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_mostrarcalle(calle):
    con = get_con()
    calle = pglistdict(
        con, f"select num,nombre,deuda,dni, coalesce(datediff(now(), ultpago),0) as atraso from clientes where calle='{calle}' and comprado>0 order by num")
    return jsonify(calle=calle)


@buscador.route('/buscador/generarrbotransferencia', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_generarrbotransferencia():
    d = json.loads(request.data.decode("UTF-8"))
    con = get_con()
    fecha = d['fecha']
    ic = d['ic']
    cuenta = d['cuenta']
    cobr = d['cobr']
    idcliente = d['idcliente']
    rbo = pgonecolumn(con, "select max(id) from pagos")+1
    ins = f"insert into pagos(idvta,fecha,imp,rec,rbo,cobr,idcliente) values({cuenta},'{fecha}',{ic},0,{rbo},{cobr},{idcliente})"
    cur = con.cursor()
    try:
        cur.execute(ins)
        con.commit()
    except:
        return make_response("No se registro el Recibo, hay un error", 400)
    else:
        log(ins)
        con.close()
        return jsonify(rbo=rbo)


@buscador.route('/buscador/enviarrbotransferencia', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_enviarrbotransferencia():
    d = json.loads(request.data.decode("UTF-8"))
    con = get_con()
    recibotransferencia(con, 'd[fecha]', d['cuenta'], d['nc'],
                        d['ic'], d['cobr'], d['rbo'], d['idcliente'])
    wapp = d['wapp']
    cuenta = d['cuenta']
    idcliente = d['idcliente']
    con.close()
    pattern = re.compile("\D")
    not_valid_wapp = pattern.search(wapp)
    logging.warning(f"/buscador/enviarrbotransferencia wapp:{wapp} idcliente:{idcliente} not_valid_wapp:{not_valid_wapp}")
    if wapp and not not_valid_wapp:
        response = send_file_whatsapp(
            idcliente, f"https://www.fedesal.lol/pdf/recibotransferencia{cuenta}.pdf", wapp)
        return jsonify(response=response)
    else:
        return 'error',400


@buscador.route('/buscador/enviarrbotransferencia/nowapp', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_enviarrbotransferencia_nowapp():
    d = json.loads(request.data.decode("UTF-8"))
    con = get_con()
    recibotransferencia(con, 'd[fecha]', d['cuenta'], d['nc'],
                        d['ic'], d['cobr'], d['rbo'], d['idcliente'])
    cuenta = d['cuenta']
    con.close()
    return send_file(f"/home/hero/recibotransferencia{cuenta}.pdf")


@buscador.route('/buscador/wapp', methods=["POST"])
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_wapp():
    d = json.loads(request.data.decode("UTF-8"))
    idcliente = d['idcliente']
    wapp = d['wapp']
    msg = d['msg']
    pattern = re.compile("\D")
    not_valid_wapp = pattern.search(wapp)
    logging.warning(f"/buscador/wapp wapp:{wapp} idcliente:{idcliente} not_valid_wapp:{not_valid_wapp}")
    if wapp and not not_valid_wapp:
        response = send_msg_whatsapp(idcliente, wapp, msg)
        if response == 'success' and ('seven' in msg.lower()):
            con = get_con()
            upd = f"update clientes set fechaintimacion=curdate() where id={idcliente}"
            cur = con.cursor()
            cur.execute(upd)
            con.commit()
            con.close()
        if response is None:
            response = 'Rejected'
        return response
    else:
        return 'error', 400


@buscador.route('/buscador/registrarwapp', methods=["POST"])
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_registrarwapp():
    d = json.loads(request.data.decode("UTF-8"))
    wapp = d['wapp']
    msg = d['msg']
    con = get_con()
    ins = f"insert into wappsenviados(wapp,msg,user) values('{wapp}','{msg}',\
                                                    '{current_user.email}')"
    pgexec(con, ins)
    con.close()
    return 'ok'


@buscador.route('/buscador/obtenerwapps/<wapp>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscar_obtenerwapps(wapp):
    con = get_con()
    recibidos = pglistdict(con, f"select fecha,msg,'rec' as dir from wappsrecibidos \
        where wapp='549{wapp}'")
    enviados = pglistdict(con, f"select fecha,msg,'env' as  dir, user from wappsenviados \
        where wapp='{wapp}'")
    con.close()
    return jsonify(recibidos=recibidos, enviados=enviados)


@buscador.route('/buscador/callesprueba')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_callesprueba():
    con = get_con()
    result = pglistdict(con, "select id, calle as text from calles order by id")
    return jsonify(result=result)


@buscador.route('/buscador/bajaindividualseven/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_bajaindividualseven(id):
    upd = f"update clientes set sev=0, baja=current_date() where id={id}"
    con = get_con()
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cliente = pglistdict(con, f"select * from clientes where id={id}")
    con.close()
    log(upd)
    return jsonify(cliente=cliente)


@buscador.route('/buscador/tablainflacion')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_tablainflacion():
    con = get_con()
    inflacion = pglistdict(con, "select year,month,indice from inflacion")
    ultimo_valor = pgonecolumn(con, "select indice from inflacion order by id desc limit 1")
    dict_inflacion = {}
    for row in inflacion:
        dict_inflacion[str(row['year'])+str(row['month'])] = ultimo_valor/row['indice']
    return jsonify(inflacion=dict_inflacion)


@buscador.route('/buscador/pedirlistagarantizados/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_pedirlistagarantizados(id):
    con = get_con()
    dni = pgonecolumn(con, f"select dni from clientes where id={id}")
    listagarantizados = pglistdict(con, f"select * from clientes where dnigarante={dni} and garantizado=1")
    return jsonify(listagarantizados=listagarantizados)


@buscador.route('/buscador/pedirlistadevoluciones/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_pedirlistadevoluciones(id):
    con = get_con()
    idvtas = pglist(con, f"select id from ventas where idcliente={id}")
    if idvtas:
        listadevoluciones = pglistdict(con, f"select * from devoluciones where idvta in {listsql(idvtas)}")
    else:
        listadevoluciones = []
    return jsonify(listadevoluciones=listadevoluciones)


@buscador.route('/buscador/pedirlistavisitas/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_pedirlistavisitas(id):
    con = get_con()
    listavisitas = pglistdict(con, f"select concat(visitas.fecha,'    ',\
    visitas.hora) as fecha, vdor,\
                    case result when 1 then 'venta' \
                                when 2 then 'anulado' \
                                when 3 then 'no estaba' \
                                when 4 then 'fechado' \
                                when 5 then 'mudo' \
                                when 6 then 'fallecio' \
                                when 7 then 'devolucion' \
                                when 8 then 'rechazado' end as result \
    from visitas,datos where datos.id=visitas.iddato and idcliente = {id}")
    return jsonify(listavisitas=listavisitas)


@buscador.route('/buscador/pedirlistaplanes/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_pedirlistaplanes(id):
    con = get_con()
    listaplanes = pglistdict(con, f"select * from planes where idcliente={id}")
    return jsonify(listaplanes=listaplanes)


@buscador.route('/buscador/pedirasignado/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_pedirasignado(id):
    con = get_con()
    asignado = pgonecolumn(con, f"select asignado from clientes,zonas where \
        clientes.zona=zonas.zona and clientes.id={id}")
    return jsonify(asignado=asignado)


@buscador.route('/buscador/toggleeditado/<int:id>')
@login_required
@check_roles(['dev','gerente','vendedor'])
def buscador_toggleeditado(id):
    con = get_con()
    upd = f"update clientes set modif_vdor=0 where id={id}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as _error:
       con.rollback()
       error = _error.msg
       return make_response(error,400)
    else:
        log(upd)
        con.commit()
        con.close()
        return 'ok'


@buscador.route('/buscador/markquieredevolver/<int:idvta>')
@login_required
@check_roles(['dev','gerente','admin'])
def buscador_quieredevolver(idvta):
    con = get_con()
    idcliente = pgonecolumn(con, f"select idcliente from ventas where id=\
        {idvta}")
    status_devolucion = pgonecolumn(con, f"select proceso_devolucion from \
        clientes where id={idcliente}")
    if status_devolucion:
        upd = f"update clientes set proceso_devolucion=0, pmovto=COALESCE((\
                select max(pmovto) from ventas where idcliente={idcliente} and \
                devuelta=0),NULL) where id={idcliente}"
        upddato = f"update datos set quiere_devolver=0 where idvta={idvta}"
    else:
        upd = f"update clientes set proceso_devolucion=1 , pmovto=date_add(\
                curdate(),interval 1 month) where id={idcliente}"
        upddato = f"update datos set quiere_devolver=1 where idvta={idvta}"
    pgexec(con, upd)
    pgexec(con, upddato)
    con.close()
    return 'ok'
