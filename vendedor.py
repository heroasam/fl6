# -*- coding: utf-8 -*-
"""Modulo que concentra la mayoria de las funciones del sistema vendedor."""

import logging
import time
from flask_login import login_required, current_user
import mysql.connector
from flask import Blueprint, render_template, jsonify, make_response, request, \
    send_file
import simplejson as json
from lib import pgonecolumn, pglistdict, send_msg_whatsapp, \
    send_file_whatsapp, pglist,  listsql, pgdict, pgexec, pgtuple
from con import get_con, log, check_roles
from formularios import ficha
import re

vendedor = Blueprint('vendedor', __name__)


var_sistema = {}
hay_venta = 0
hay_auth = 0

def leer_variables():
    """Funcion para leer variables de sistema.

    Las variables estan ubicadas en la tabla variables con los campos clave,
    valor.
    Y seran incorporados en una variable  que es un dict."""

    con = get_con()
    try:
        variables = pglistdict(con, "select clave,valor from variables")
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        for row in variables:
            var_sistema[row['clave']] = row['valor']
        return 1
    finally:
        con.close()


leer_variables()


def calculo_cuota_maxima(idcliente):
    """Funcion que calcula la cuota maxima vendible del cliente.

    Busca la cuota maxima de los ultimos tres años y la actualiza por inflacion
    le disminuye 5% por cada mes de atraso que haya tenido
    le aumenta 5% por cada compra que haya tenido en los ultimos tres años.
    Esto ultimo se suspende pq aumenta mucho la cuota por la gran inflacion que
    hay.
    Cambios: se saco el incremento por cantidad de ventas.
    Se toman las ventas de los ultimos tres años canceladas o no, y se
    actualizan luego se pone la cuota actualizada mas alta.
    Tambien se tiene en cuenta el monto total de la venta/6 para el calculo de
    la cuota para evitar distorsion si el plan fue en 4 o 5 cuotas.
    """
    con = get_con()
    cuotas = pglistdict(con, f"select comprado as monto,\
    date_format(fecha,'%Y%c') as fecha from ventas where idcliente={idcliente} \
    and fecha>date_sub(curdate(),interval 3 year) and devuelta=0 and pp=0")
    cuota_actualizada = 0
    try:
        if cuotas:
            ultimo_valor = pgonecolumn(con, "select indice from inflacion \
            order by id desc limit 1")
            cuotas_actualizadas = []
            for venta in cuotas:
                cuota = venta['monto']/6
                fecha = venta['fecha']
                indice = pgonecolumn(con, f"select indice from inflacion \
                where concat(year,month)='{fecha}'")
                if not indice:  # esto sucede si es un mes sin indice cargado aun
                    indice = ultimo_valor
                actualizada = ultimo_valor/indice * cuota
                cuotas_actualizadas.append(actualizada)
            cuota_actualizada = max(cuotas_actualizadas)

            atraso = pgonecolumn(con, f"select atraso from clientes where \
            id={idcliente}")
            if atraso is None:
                atraso = 0
            if atraso > 0:
                cuota_actualizada = cuota_actualizada * (1-(atraso/30)*0.05)
                cuota_actualizada = max(cuota_actualizada, 0)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        return cuota_actualizada
    finally:
        con.close()


def calculo_sin_extension(idcliente):
    """Determina si a un cliente se le puede ofrecer automaticamente extension.

    de la cuota_maxima. Toma los parametros: cantidad de ventas: 1 venta no,
    atrasos>60 en ultimos 3 años no.
    Return 1 negativo sin_extension. 0 positivo se puede ofrecer extension."""

    con = get_con()
    try:
        cnt_vtas = pgonecolumn(con, f"select count(*) from ventas where \
        saldo=0 and idcliente = {idcliente}")
        if cnt_vtas == 1:
            return 1
        atraso = pgonecolumn(con, f"select atraso from clientes where \
        id={idcliente}")
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        if atraso and atraso > 60:
            return 1
        return 0
    finally:
        con.close()


def editar_cntwapp(wapp):
    """Funcion que edita el campo cnt_wapp de tabla clientes cuando se edita
    el wapp de un cliente."""
    con = get_con()
    if wapp != 'INVALIDO' and wapp != '' and wapp is not None:
        updcntwapp = f"update clientes set cnt_wapp=(select count(*) from \
            clientes as a where a.wapp='{wapp}') where wapp=\
                '{wapp}'"
        cnt_wapp = pgonecolumn(con, f"select count(*) from \
            clientes as a where a.wapp='{wapp}'")
        try:
            cur = con.cursor()
            cur.execute(updcntwapp)
            con.commit()
        except mysql.connector.Error as _error:
            con.rollback()
            logging.warning(
                f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        finally:
            con.close()


def es_dni_valido(dni):
    patron = r'^\d{7,8}$'
    if dni is None:
        return False
    dni = str(dni)
    if re.match(patron, dni):
        return True
    else:
        return False


@vendedor.route('/vendedor/getcuotamaxima/<int:idcliente>')
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_getcuotamaxima(idcliente):
    """Funcion que pide la cuota maxima del cliente.

    Si es menor a la cuota basica del sistema, pone esta ultima."""
    cuotamaxima = int(calculo_cuota_maxima(idcliente))
    if int(cuotamaxima) < int(var_sistema['cuota_basica']):
        cuotamaxima = int(var_sistema['cuota_basica'])
    return jsonify(cuotamaxima=cuotamaxima)


@vendedor.route('/vendedor/guardardato', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_guardardato():
    """Funcion que procesa el guardado de un dato del cliente.

    Primero calcula la cuota_maxima y sin_extension. "sin_extension" significa
    que no puede autorizar una cuota mas alta.
    Calcula tambien la deuda en la casa, primero obteniendo la direccion del
    cliente.
    Calcula si es garante, en cuyo caso calcula el monto garantizado.
    Luego hace la insersion en la tabla datos y hace update en tabla clientes
    en el campo fechadato para que el mismo cliente no salga en listados."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    cuota_maxima = calculo_cuota_maxima(d_data['idcliente'])
    sin_extension = calculo_sin_extension(d_data['idcliente'])
    if cuota_maxima < float(var_sistema['cuota_basica']):
        cuota_maxima = var_sistema['cuota_basica']
    direccion_cliente = pgonecolumn(con, f"select concat(calle,num) from \
    clientes where id={d_data['idcliente']}")
    deuda_en_la_casa = pgonecolumn(con, f"select sum(deuda) from clientes \
    where concat(calle,num)='{direccion_cliente}' and id!={d_data['idcliente']}")
    es_garante = pgonecolumn(con, f"select esgarante from clientes where id=\
    {d_data['idcliente']}")
    zona = pgonecolumn(con, f"select zona from clientes where id=\
    {d_data['idcliente']}")
    if es_garante:
        dni = pgonecolumn(con, f"select dni from clientes where id=\
        {d_data['idcliente']}")
        monto_garantizado = pgonecolumn(con, f"select sum(saldo) from ventas \
        where garantizado=1 and dnigarante={dni}")
    else:
        monto_garantizado = 0
    if deuda_en_la_casa is None:
        deuda_en_la_casa = 0
    ins = f"insert into datos(fecha, user, idcliente, fecha_visitar, art,\
    horarios, comentarios, cuota_maxima,deuda_en_la_casa,sin_extension,\
    monto_garantizado,zona) values ('{d_data['fecha']}', '{d_data['user']}',\
    {d_data['idcliente']},'{d_data['fecha_visitar']}','{d_data['art']}',\
    '{d_data['horarios']}','{d_data['comentarios']}', {cuota_maxima}, \
    '{deuda_en_la_casa}',{sin_extension},{monto_garantizado},'{zona}')"
    cur = con.cursor()
    upd = f"update clientes set fechadato=curdate() where \
                id={d_data['idcliente']}"
    try:
        pgexec(con, upd)
        pgexec(con, ins)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        log(ins)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/vendedor/togglerechazardato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_togglerechazardato(iddato):
    """Funcion que hace un toggle en el campo rechazado.

    Tambien actualiza el campo resultado y la tabla autorizacion."""
    con = get_con()
    resultado = pgonecolumn(con, f"select resultado from datos where \
    id={iddato}")
    if resultado == 8:  # o sea ya esta rechazado
        upd = f"update datos set resultado=NULL, rechazado=0 where id={iddato}"
        updaut = f"update autorizacion set rechazado=0,autorizado=0 where \
        iddato={iddato}"
    elif resultado is None:  # o sea se puede rechazar
        upd = f"update datos set resultado=8,rechazado=1 where id={iddato}"
        updaut = f"update autorizacion set rechazado=1,autorizado=0 where \
        iddato={iddato}"
    else:
        return make_response("error", 400)
    cur = con.cursor()
    try:
        cur.execute(upd)
        cur.execute(updaut)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(upd)
        log(updaut)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/vendedor/getlistadodatos')
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_getlistadodatos():
    """Entrega lista de datos, cuota basica y lista de vendedores."""
    con = get_con()
    listadodatos = pglistdict(
        con, "select datos.id, fecha, user,fecha_visitar,\
    art, horarios, comentarios,  dni, nombre, resultado,monto_vendido, \
    cuota_maxima, novendermas, incobrable, sev, baja, deuda_en_la_casa, \
    sin_extension,nosabana, autorizado, datos.zona as zona from datos, \
    clientes where clientes.id =datos.idcliente order by id desc")
    cuotabasica = var_sistema['cuota_basica']
    vdores = pglist(con, "select id from cobr where vdor=1 and activo=1")
    return jsonify(listadodatos=listadodatos, cuotabasica=cuotabasica,
                   vdores=vdores)


@vendedor.route('/vendedor/getlistadodatosenviar')
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_getlistadodatosenviar():
    """Funcion que entrega lista de datos a enviar.

    enviado_vdor=0, rechazado=0."""
    #
    con = get_con()
    listadodatos = pglistdict(
        con, "select datos.id, fecha, user,fecha_visitar,\
    art, horarios, comentarios,  dni, nombre, resultado,monto_vendido, \
    cuota_maxima, novendermas, incobrable, sev, baja, deuda_en_la_casa, \
    sin_extension,nosabana, autorizado, monto_garantizado,datos.zona as zona \
    from datos, clientes where clientes.id = datos.idcliente and \
    enviado_vdor=0 and rechazado=0 and resultado is null order by id desc")
    # enviado_vdor=0 filtra los datos no enviados aun.
    cuotabasica = var_sistema['cuota_basica']
    vdores = pglist(con, "select id from cobr where vdor=1 and activo=1")
    return jsonify(listadodatos=listadodatos, cuotabasica=cuotabasica,
                   vdores=vdores)


@vendedor.route('/vendedor/getlistadodatosenviados')
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_getlistadodatosenviados():
    """Funcion que entrega una lista de los datos ya enviados.

    campo enviado_vdor=1."""

    con = get_con()
    listadodatos = pglistdict(
        con, "select datos.id, fecha, user,fecha_visitar,idcliente,\
    art, horarios, comentarios,  dni, nombre, resultado,monto_vendido,\
    autorizado, cuota_maxima, novendermas, incobrable, sev, baja,\
    deuda_en_la_casa, vendedor, autorizado,datos.zona as zona,nosabana,\
    sin_extension from datos, clientes where clientes.id = \
    datos.idcliente and enviado_vdor=1 order by edited desc")
    # enviado_vdor=1 filtra los datos enviados
    cuotabasica = var_sistema['cuota_basica']
    vdores = pglist(con, "select id from cobr where vdor=1 and activo=1")
    return jsonify(listadodatos=listadodatos, cuotabasica=cuotabasica,
                   vdores=vdores)


@vendedor.route('/vendedor/asignardatosvendedor', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente','admin'])
def vendedor_asignardatosvendedor():
    """Funcion que asigna datos a un vendedor dado.

    Pone el codigo de vendedor y enviado_vdor=1."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    ids = listsql(d_data['ids'])
    upd = f"update datos set vendedor = {d_data['vendedor']},enviado_vdor=1 \
    where id in {ids}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        return 'ok'
    finally:
        con.close()


@vendedor.route('/vendedor/desafectardatos', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente','admin'])
def vendedor_desafectardatos():
    """Funcion que desafecta datos asignados a un vendedor.

    Pone el enviado_vdor=0 y resultado=10 (que significa descartado)."""
    con = get_con()
    lista_ids = json.loads(request.data.decode("UTF-8"))
    ids = listsql(lista_ids)
    upd = f"update datos set enviado_vdor=0, resultado=10 where id in {ids}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        return 'ok'
    finally:
        con.close()


@vendedor.route('/vendedor/ingresardatoyasignardatosvendedor',
                methods=['POST'])
@login_required
@check_roles(['dev', 'gerente','admin'])
def vendedor_ingresardatoyasignardatosvendedor():
    """Funcion que ingresa el dato y automaticamente asigna el vendedor.

    Se usa en asignacion de listado."""

    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    ids = d_data['ids']
    cur = con.cursor()
    try:
        for dni in ids:
            idcliente = pgonecolumn(con, f"select id from clientes where dni=\
            {dni}")
            cuota_maxima = calculo_cuota_maxima(idcliente)
            sin_extension = calculo_sin_extension(idcliente)
            cuotabasica = var_sistema['cuota_basica']
            if cuota_maxima == 0 or int(cuota_maxima) < int(cuotabasica):
                cuota_maxima = cuotabasica
            direccion_cliente = pgonecolumn(con, f"select concat(calle,num) \
            from clientes where id={idcliente}")
            deuda_en_la_casa = pgonecolumn(con, f"select sum(deuda) from \
            clientes where concat(calle,num)='{direccion_cliente}' \
            and id!={idcliente} and ultpago<date_sub(curdate(), \
            interval 120 day)")
            zona = pgonecolumn(con, f"select zona from clientes where id=\
            {idcliente}")
            if deuda_en_la_casa is None:
                deuda_en_la_casa = 0
            existe_dato_ya = pgonecolumn(con, f"select id from datos where \
            resultado is null and idcliente={idcliente}")
            if not existe_dato_ya:
                ins = f"insert into datos(fecha, user, idcliente, \
                fecha_visitar,art,horarios, comentarios, cuota_maxima,\
                deuda_en_la_casa, sin_extension,vendedor,listado,\
                enviado_vdor,zona) values (curdate(), \
                '{current_user.email}',{idcliente},curdate(),'','','', \
                {cuota_maxima},'{deuda_en_la_casa}',{sin_extension},\
                {d_data['vendedor']},1,1,'{zona}')"
                upd = f"update clientes set fechadato=curdate() where \
                id={idcliente}"
                cur.execute(ins)
                cur.execute(upd)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        return 'ok'
    finally:
        con.close()


@vendedor.route('/vendedor/getcuotabasica')
@login_required
@check_roles(['dev', 'gerente','admin'])
def vendedor_getcuotabasica():
    """Simple funcion para leer la cuota basica desde la variable."""
    cuotabasica = var_sistema['cuota_basica']
    return jsonify(cuotabasica=cuotabasica)


@vendedor.route('/vendedor/borrardato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_borrardato(iddato):
    """Simple proceso para borrar un dato dado su iddato."""
    con = get_con()
    stm = f"delete from datos where id={iddato}"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(stm)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/vendedor/borrarvisita/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_borrarvisita(iddato):
    """Simple proceso para borrar visita de un dato restaurado."""
    con = get_con()
    stm = f"delete from visitas where iddato={iddato}"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(stm)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/vendedor/editardato', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_editardato():
    """Funcion para editar dato."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    if d_data['nosabana']:
        nosabana = 1
    else:
        nosabana = 0
    if d_data['sin_extension']:
        sin_extension = 1
    else:
        sin_extension = 0
    if d_data['resultado'] == None:
        resultado = 'NULL'
    else:
        resultado = d_data['resultado']
    upd = f"update datos set fecha='{d_data['fecha']}',user='{d_data['user']}',\
    fecha_visitar='{d_data['fecha_visitar']}', horarios='{d_data['horarios']}',\
    art='{d_data['art']}', comentarios='{d_data['comentarios']}', cuota_maxima=\
    {d_data['cuota_maxima']},nosabana={nosabana},sin_extension={sin_extension},\
    resultado={resultado} where id={d_data['id']}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(upd)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/vendedor/verificarqueyaesdato/<int:idcliente>')
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_verificarqueyaesdato(idcliente):
    """Simple funcion para verificar que un cliente tiene un dato pendiente."""
    con = get_con()
    dato = pgonecolumn(con, f"select idcliente from datos where \
    idcliente={idcliente} and resultado is null")
    if dato:
        return make_response("error", 400)
    return make_response("ok", 200)


@vendedor.route('/vendedor/guardarcuotabasica/<int:cuota>')
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_guardarcuotabasica(cuota):
    """Simple funcion para actualizar la cuota basica."""
    con = get_con()
    upd = f"update variables set valor={cuota} where clave='cuota_basica'"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(upd)
        leer_variables()
        return 'ok'
    finally:
        con.close()


@vendedor.route('/2xxXix5cnz7IKcYegqs6qf0R6')
# @vendedor.route('/vendedor/listadatos')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_listadatos():
    """Ruta para render pagina listadatos."""
    return render_template('/vendedor/listadatos.html')


@vendedor.route('/Hb0IQfDEnbLV4eyWZeg5kbcff')
@vendedor.route('/vendedor/agregarcliente')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_agregarcliente():
    """Ruta para render pagina agregarcliente."""
    return render_template('/vendedor/agregarcliente.html')


@vendedor.route('/pEmPj7NAUn0Odsru4aL2BhlOu', methods=['POST'])
@vendedor.route('/vendedor/envioclientenuevo', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_envioclientenuevo():
    """Proceso para agregar cliente nuevo por el vendedor."""
    logging.warning("envioclientenuevo %s", current_user.email)
    global hay_auth
    hay_auth = 1
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    cliente_viejo = {}
    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    dni = d_data['dni']
    cur = con.cursor()
    cliente = pglistdict(con, f"select * from clientes where dni={dni}")
    if cliente:  # o sea esta en la base de Romitex
        cliente = cliente[0]
        sin_extension = calculo_sin_extension(d_data['id'])
        cuota_maxima = calculo_cuota_maxima(d_data['id'])
        cuota_basica = var_sistema['cuota_basica']
        if cuota_maxima == 0 or cuota_maxima < float(cuota_basica):
            cuota_maxima = cuota_basica
        direccion_cliente = pgonecolumn(con, f"select concat(calle,num) from \
        clientes where id={d_data['id']}")
        deuda_en_la_casa = pgonecolumn(con, f"select sum(deuda) from clientes \
        where concat(calle,num)='{direccion_cliente}' and id!={d_data['id']}")
        es_garante = pgonecolumn(con, f"select esgarante from clientes where \
        id={d_data['id']}")
        zona = pgonecolumn(con, f"select zona from clientes where id=\
        {d_data['id']}")
        if es_garante:
            dni = pgonecolumn(con, f"select dni from clientes where id=\
            {d_data['id']}")
            monto_garantizado = pgonecolumn(con, f"select sum(saldo) from \
            ventas where garantizado=1 and dnigarante={dni}")
        else:
            monto_garantizado = 0
        if deuda_en_la_casa is None:
            deuda_en_la_casa = 0
        # consulta para ver si el dato ha sido asignado a otro vendedor
        # aca primero buscamos un dato cargado no definido.
        iddato = pgonecolumn(con, f"select id from datos where idcliente =\
        {d_data['id']} and resultado is null")
        if iddato:  # o sea hay ya un dato sin definir de ese cliente
            ins = None
        else:
            ins = f"insert into datos(fecha, user, idcliente, fecha_visitar, \
            art,horarios, comentarios, cuota_maxima,deuda_en_la_casa,\
            sin_extension,monto_garantizado,vendedor,dnigarante,enviado_vdor,\
            zona) values (curdate(),'{current_user.email}',{d_data['id']},\
            curdate(),'','','cliente enviado por vendedor', {cuota_maxima}, \
            '{deuda_en_la_casa}', {sin_extension}, {monto_garantizado},\
            {vdor},{d_data['dnigarante']},0,'{zona}')"
        # Testeo si hay cambios en los datos del cliente que envia el vendedor
        upd = None
        inslog = None
        cliente_nuevo = [cliente['calle'], cliente['num'], cliente['barrio'],
                         cliente['wapp'], cliente['tel'], cliente['acla']]
        cliente_viejo = [d_data['calle'], d_data['num'], d_data['barrio'],
                         d_data['wapp'], d_data['tel'], d_data['acla']]
        if cliente_nuevo != cliente_viejo:
            upd = f"update clientes set calle='{d_data['calle']}', \
            num={d_data['num']},barrio='{d_data['barrio']}',\
            wapp='{d_data['wapp']}',tel='{d_data['tel']}', \
            modif_vdor=1,acla='{d_data['acla']}' where id={d_data['id']}"
            inslog = f"insert into logcambiodireccion(idcliente,calle,\
            num,barrio,tel,acla,fecha,nombre,dni,wapp) values({cliente['id']},\
            '{cliente['calle']}','{cliente['num']}','{cliente['barrio']}',\
            '{cliente['tel']}','{cliente['acla']}',curdate(),\
            '{cliente['nombre']}','{cliente['dni']}','{cliente['wapp']}')"
        try:
            if ins:
                cur.execute(ins)
                iddato = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
                insaut = f"insert into autorizacion(fecha,vdor,iddato,\
                idcliente,cuota_requerida,cuota_maxima,arts) \
                values(current_timestamp(),{vdor},{iddato},{d_data['id']},\
                {d_data['cuota_requerida']},{cuota_maxima},'{d_data['arts']}')"
                cur.execute(insaut)
                idautorizacion = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
                vdorasignado = vdor
            else:  # dato repetido inserto auth con iddato que ya tenia de antes
                # busco el vdorasignado al dato si es que existe.
                vdorasignado = pgonecolumn(con, f"select vendedor from datos \
                where id={iddato}")
                # si el dato era del vdor inserto la autorizacion.
                if vdorasignado == vdor:
                    insaut = f"insert into autorizacion(fecha,vdor,iddato,\
                    idcliente,cuota_requerida,cuota_maxima,arts) \
                    values(current_timestamp(),{vdor},{iddato},{d_data['id']},\
                    {d_data['cuota_requerida']},{cuota_maxima},\
                    '{d_data['arts']}')"
                    cur.execute(insaut)
                    idautorizacion = pgonecolumn(
                        con, "SELECT LAST_INSERT_ID()")
                # si no hay vdorasignado- Se asigna dato y crea la auth.
                else:
                    upddato = f"update datos set vendedor={vdor} where id=\
                        {iddato}"
                    insauth = f"insert into autorizacion(fecha,vdor,iddato,\
                    idcliente,cuota_requerida,cuota_maxima,arts) \
                    values(current_timestamp(),{vdor},{iddato},{d_data['id']},\
                    {d_data['cuota_requerida']},{cuota_maxima},\
                    '{d_data['arts']}')"

                    cur.execute(upddato)
                    cur.execute(insauth)
            if upd:
                cur.execute(upd)
            if inslog:
                cur.execute(inslog)
        except mysql.connector.Error as _error:
            con.rollback()
            error = _error.msg
            logging.warning(
                f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
            return make_response(error, 400)
        else:
            con.commit()
            log(ins)
            # if 'wapp' in d_data:
            #     editar_cntwapp(d_data['wapp'])
            # if 'wapp' in cliente_viejo:
            #     editar_cntwapp(cliente_viejo['wapp'])
            if ins:
                log(insaut)
            if upd:
                log(upd)
            if inslog:
                log(inslog)
            if vdor != vdorasignado:
                otroasignado = 1
                if vdorasignado is None:
                    otroasignado = 0
                return jsonify(idautorizacion=idautorizacion,
                               otroasignado=otroasignado)
            return jsonify(idautorizacion=idautorizacion, otroasignado=0)
        finally:
            con.close()

    else:  # o sea es un cliente nuevo
        sin_extension = 1
        cuota_maxima = var_sistema['cuota_basica']
        direccion_cliente = d_data['calle']+d_data['num']
        deuda_en_la_casa = pgonecolumn(con, f"select sum(deuda) from clientes \
        where concat(calle,num)='{direccion_cliente}'")
        es_garante = 0
        monto_garantizado = 0
        # el cliente recien ingresado no tiene zona
        zona = ''
        if deuda_en_la_casa is None:
            deuda_en_la_casa = 0
        if d_data['dnigarante'] == '':
            dnigarante = 0
        else:
            dnigarante = d_data['dnigarante']
        inscliente = f"insert into clientes(sex,dni, nombre,calle,num,barrio,\
        tel,wapp,zona,modif_vdor,acla,horario,mjecobr,infoseven) values('F',\
        {d_data['dni']},'{d_data['nombre']}','{d_data['calle']}',\
        {d_data['num']},'{d_data['barrio']}','{d_data['tel']}',\
        '{d_data['wapp']}','-CAMBIAR',1,'{d_data['acla']}','','','')"
        try:
            cur.execute(inscliente)
            idcliente = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
            ins = f"insert into datos(fecha, user, idcliente, fecha_visitar, \
            art,horarios, comentarios, cuota_maxima,deuda_en_la_casa,\
            sin_extension,monto_garantizado,vendedor,dnigarante,zona) values \
            (curdate(), '{current_user.email}',{idcliente},curdate(),'','',\
            'cliente enviado por vendedor', {cuota_maxima}, \
            '{deuda_en_la_casa}',{sin_extension}, {monto_garantizado},{vdor},\
            {dnigarante},'{zona}')"
            cur.execute(ins)
            iddato = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
            insaut = f"insert into autorizacion(fecha,vdor,iddato,idcliente,\
            cuota_requerida,cuota_maxima,arts) values(current_timestamp(),\
            {vdor},{iddato},{idcliente},{d_data['cuota_requerida']},\
            {cuota_maxima},'{d_data['arts']}')"
            cur.execute(insaut)
            idautorizacion = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
        except mysql.connector.Error as _error:
            con.rollback()
            error = _error.msg
            logging.warning(
                f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
            return make_response(error, 400)
        else:
            con.commit()
            # if 'wapp' in d_data:
            #     editar_cntwapp(d_data['wapp'])
            # if 'wapp' in cliente_viejo:
            #     editar_cntwapp(cliente_viejo['wapp'])
            log(ins)
            log(insaut)
            return jsonify(idautorizacion=idautorizacion)
        finally:
            con.close()


@vendedor.route('/4mY6khlmZKUzDRZDJkakr75iH')
@vendedor.route('/vendedor/listavisitasvdor')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_visitasvdor():
    """Ruta que render pagina listavisitasvdor."""
    return render_template('/vendedor/listavisitasvdor.html')


@vendedor.route('/VGIdj7tUnI1hWCX3N7W7WAXgU')
@vendedor.route('/vendedor/getlistadodatosvendedor')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getlistadodatosvendedor():
    """Funcion que obtiene la lista de datos de un vendedor en particular."""
    logging.warning("GETLISTADODATOSVENDEDOR, %s", current_user.email)

    con = get_con()
    if current_user.email == var_sistema['816']:
        vdor = 816
    if current_user.email == var_sistema['835']:
        vdor = 835
    agrupar = var_sistema["agrupar"+str(vdor)]
    listadodatos = pglistdict(con, f"select datos.id, fecha, fecha_visitar,\
    art, horarios, comentarios,  dni, nombre,calle,num,acla,wapp,tel,barrio, \
    clientes.zona as zona, cuota_maxima,idcliente, sin_extension,idvta,\
    resultado,datos.dnigarante as dnigarante,quiere_devolver,vendedor,\
    wapp_verificado from  datos,clientes where clientes.id = datos.idcliente \
    and vendedor={vdor} and (resultado is null or resultado=7 or (resultado=1 \
    and quiere_devolver=1) or (resultado=1 and date(fecha_definido)=\
    curdate())) and fecha_visitar <=curdate() and enviado_vdor=1 order by id \
                              desc")
    return jsonify(listadodatos=listadodatos, agrupar=agrupar)


@vendedor.route('/pnZWxv9Nicwt6TQ6zxohzvats/<int:iddato>')
@vendedor.route('/vendedor/getdato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getdato(iddato):
    """Simple funcion que levanta un dato dado su id."""
    con = get_con()
    dato = pgdict(con, f"select datos.id, fecha, fecha_visitar,\
    art, horarios, comentarios,  dni, nombre,calle,num,acla,wapp,tel,barrio, \
    clientes.zona as zona, cuota_maxima,idcliente, sin_extension,vendedor, \
    datos.dnigarante as dnigarante,idvta,monto_vendido,nosabana,\
    wapp_verificado, auth_sinwapp_verificado from datos, clientes where \
                  clientes.id = datos.idcliente and datos.id={iddato}")
    return jsonify(dato=dato)


@vendedor.route('/kHEhacFNmI2vflFHBbaT1AQ1Z')
@vendedor.route('/vendedor/getlistadoarticulos')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getlistadoarticulos():
    """Simple funcion que levanta la lista de articulos activos."""
    con = get_con()
    articulos = pglistdict(
        con,
        "select art,cuota from articulos where activo=1 \
    order by art")
    return jsonify(articulos=articulos)


@vendedor.route('/uQ3gisetQ8v0n6tw81ORnpL1s', methods=['POST'])
@vendedor.route('/vendedor/editarwapp', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor', 'cobrador'])
def vendedor_editarwapp():
    """Proceso para editar el wapp del cliente."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    wapp = d_data['wapp']
    if wapp!='' and wapp is not None and wapp != 'INVALIDO':
        try:
            comprueba_si_wapp_en_uso = pglist(con, f"select id from clientes \
                        where wapp={wapp} and id!={d_data['idcliente']}")
            if len(comprueba_si_wapp_en_uso)>0:
                return make_response("ese wapp ya esta en uso",400)
        except mysql.connector.Error as _error:
            con.rollback()
            error = _error.msg
            logging.warning(
                f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
            return make_response(error, 400)
    wapp_viejo = pgonecolumn(con, f"select wapp from clientes where id= \
    {d_data['idcliente']}")
    upd = f"update clientes set wapp='{d_data['wapp']}' where \
    id={d_data['idcliente']}"
    if wapp_viejo and wapp_viejo != 'INVALIDO':
        inslogcambio = f"insert into logcambiodireccion(idcliente,wapp,fecha) \
        values ({d_data['idcliente']},'{wapp_viejo}', current_date())"
    else:
        inslogcambio = None
    cur = con.cursor()
    try:
        cur.execute(upd)
        if inslogcambio is not None:
            cur.execute(inslogcambio)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        # editar_cntwapp(d_data['wapp'])
        # editar_cntwapp(wapp_viejo)
        log(upd)
        # editar_cntwapp(d_data['wapp'])
        return 'ok'
    finally:
        con.close()


@vendedor.route('/HvjJNtFgF71pRYafzcTC74nUt', methods=['POST'])
@vendedor.route('/vendedor/guardardatofechado', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_guardardatofechado():
    """Proceso para el fechado de un dato."""
    logging.warning("guardardatofechado, %s", current_user.email)

    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    upd = f"update datos set fecha_visitar='{d_data['fecha_visitar']}' where \
    id = {d_data['id']}"
    ins = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{vdor},{d_data['id']},4,0)"
    cur = con.cursor()
    try:
        cur.execute(upd)
        cur.execute(ins)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(upd)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/UtVc3f6y5hfxu2dPmcrV9Y7mc/<int:iddato>')
@vendedor.route('/vendedor/anulardato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_anulardato(iddato):
    """Proceso para anular un dato."""
    global hay_venta
    hay_venta = 1
    logging.warning("anulardato, %s", current_user.email)

    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    con = get_con()
    upd = f"update datos set resultado=2, fecha_definido=current_timestamp()\
    where id = {iddato}"
    ins = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{vdor},{iddato},2,0)"
    cur = con.cursor()
    try:
        cur.execute(upd)
        cur.execute(ins)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(upd)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/gJUmonE8slTFGZqSKXSVwqPJ1/<int:iddato>')
@vendedor.route('/vendedor/mudodato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_mudodato(iddato):
    """Proceso para registrar la mudanza de un cliente."""
    logging.warning("mudodato, %s", current_user.email)

    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    con = get_con()
    idcliente = pgonecolumn(con, f"select idcliente from datos where \
    id={iddato}")
    upd = f"update datos set resultado=5, fecha_definido=current_timestamp()\
    where id = {iddato}"
    ins = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{vdor},{iddato},5,0)"
    updcliente = f"update clientes set mudo=1 where id={idcliente}"
    inscomentario = f"insert into comentarios(idcliente, ingreso, comentario) \
    values({idcliente},'{current_user.email}','puesto como mudado por \
    vendedor {vdor}')"
    cur = con.cursor()
    try:
        cur.execute(upd)
        cur.execute(ins)
        cur.execute(updcliente)
        cur.execute(inscomentario)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(upd)
        log(updcliente)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/sLTFCMArYAdVsrEgwsz7utyRi/<int:iddato>')
@vendedor.route('/vendedor/falleciodato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_falleciodato(iddato):
    """Proceso para registrar el fallecimiento de un cliente."""
    logging.warning("falleciodato, %s", current_user.email)

    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    con = get_con()
    idcliente = pgonecolumn(con, f"select idcliente from datos where id=\
    {iddato}")
    upd = f"update datos set resultado=6, fecha_definido=current_timestamp()\
    where id = {iddato}"
    ins = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{vdor},{iddato},6,0)"
    updcli = f"update clientes set zona='-FALLECIDOS', modif_vdor=1 where id=\
    {idcliente}"
    inscomentario = f"insert into comentarios(idcliente, ingreso, comentario) \
    values({idcliente},'{current_user.email}','puesto como fallecido por \
    vendedor {vdor}')"
    cur = con.cursor()
    try:
        cur.execute(upd)
        cur.execute(ins)
        cur.execute(updcli)
        cur.execute(inscomentario)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(upd)
        log(updcli)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/fc3vpQG6SzEH95Ya7kTJPZ48M', methods=['POST'])
@vendedor.route('/vendedor/validardni', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_validardni():
    """Proceso para validar un DNI."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    logging.warning(d_data)
    dni = pgonecolumn(con, f"select dni from clientes where id={d_data['id']}")
    if d_data['dni'] != '' and dni == int(d_data['dni']):
        return make_response('aprobado', 200)
    return make_response('error', 400)


@vendedor.route('/vaHQ2gFYLW2pIWSr5I0ogCL0k', methods=['POST'])
@vendedor.route('/vendedor/registrarautorizacion', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_registrarautorizacion():
    """Proceso para registrar un pedido de autorizacion."""
    logging.warning("registrarautorizacion, %s", current_user.email)
    global hay_auth
    hay_auth = 1
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    vdor = var_sistema[current_user.email]
    if 'dnigarante' in d_data:
        dnigarante_propuesto = d_data['dnigarante']
    else:
        dnigarante_propuesto = ''
    ins = f"insert into autorizacion(fecha,vdor,iddato,idcliente,\
    cuota_requerida,cuota_maxima,arts,dnigarante_propuesto) values\
        (current_timestamp(),\
    {vdor},{d_data['id']},{d_data['idcliente']},{d_data['cuota_requerida']},\
    {d_data['cuota_maxima']},'{d_data['arts']}','{dnigarante_propuesto}')"
    logging.warning(ins)
    cur = con.cursor()
    try:
        if len(str(dnigarante_propuesto)) > 0:
            upddato = f"update datos set dnigarante='{dnigarante_propuesto}' \
                where id={d_data['id']}"
            logging.warning(upddato)
            cur.execute(upddato)
        cur.execute(ins)
        idautorizacion = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(ins)
        return jsonify(idautorizacion=idautorizacion)
    finally:
        con.close()


@vendedor.route('/vendedor/getlistadoautorizados')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getlistadoautorizados():
    """Funcion que entrega lista de autorizaciones pendientes."""

    con = get_con()
    listadoautorizados = pglistdict(con, "select autorizacion.id as id,\
    datos.id as iddato,datos.fecha as fecha, datos.user as user, nombre, \
    datos.resultado as resultado, datos.art as art, datos.cuota_maxima as \
    cuota_maxima, datos.sin_extension as sin_extension,datos.nosabana as \
    nosabana, datos.deuda_en_la_casa as deuda_en_la_casa,datos.vendedor as \
    vendedor, clientes.novendermas as novendermas, clientes.incobrable as \
    incobrable,clientes.sev as sev, clientes.baja as baja, autorizacion.fecha \
    as fechahora, autorizacion.cuota_requerida as cuota_requerida,\
    autorizacion.tomado as tomado, autorizacion.arts as arts,horarios,\
    comentarios,(select count(*) from autorizacion where \
    autorizacion.idcliente=clientes.id) as cnt,autorizacion.idcliente, \
    autorizacion.dnigarante_propuesto as dnigarante from \
    datos, autorizacion,clientes  where datos.idcliente=clientes.id and \
    autorizacion.iddato=datos.id and autorizacion.autorizado=0 and \
    autorizacion.rechazado=0 and autorizacion.sigueigual=0 and datos.resultado \
    is null")
    cuotabasica = var_sistema['cuota_basica']
    return jsonify(listadoautorizados=listadoautorizados,
                   cuotabasica=cuotabasica)


@vendedor.route('/vendedor/getlistadoautorizadosporid/<int:idcliente>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getlistadoautorizadosporid(idcliente):
    """Funcion que entrega la lista de autorizaciones que tuvo un cliente."""
    con = get_con()
    listadoautorizadosporid = pglistdict(con, f"select datos.id as id,\
    datos.fecha as fecha, datos.user as user, nombre, datos.resultado as \
    resultado, datos.art as art, datos.cuota_maxima as cuota_maxima, \
    datos.sin_extension as sin_extension,datos.nosabana as nosabana, \
    datos.deuda_en_la_casa as deuda_en_la_casa,datos.vendedor as vendedor, \
    clientes.novendermas as novendermas, clientes.incobrable as incobrable,\
    clientes.sev as sev,clientes.baja as baja, autorizacion.fecha as fechahora,\
    autorizacion.cuota_requerida as cuota_requerida, autorizacion.arts as arts,\
    horarios,comentarios,(select count(*) from autorizacion where \
    autorizacion.idcliente=clientes.id) as cnt from datos,autorizacion,\
    clientes  where datos.idcliente=clientes.id and autorizacion.iddato=\
    datos.id and autorizacion.idcliente={idcliente}")
    return jsonify(listadoautorizadosporid=listadoautorizadosporid)


@vendedor.route('/vendedor/getlistaautorizados')
@login_required
@check_roles(['dev', 'gerente','admin'])
def vendedor_getlistaautorizados():
    """Funcion que entrega lista de autorizaciones."""

    con = get_con()
    listaautorizados = pglistdict(con, "select id,fecha,vdor,idcliente,\
    (select nombre from clientes where id=autorizacion.idcliente) as nombre,\
    cuota_requerida,cuota_maxima,autorizado,user,rechazado,sigueigual,\
    motivo,comentario from autorizacion order by id desc")
    return jsonify(listaautorizados=listaautorizados)


@vendedor.route('/vendedor/autorizardato/<int:idauth>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_autorizardato(idauth):
    """Proceso para autorizar un dato."""
    con = get_con()
    cuota_requerida = pgonecolumn(con, f"select cuota_requerida from \
    autorizacion where id={idauth}")
    upd_aut = f"update autorizacion set autorizado=1,rechazado=0,sigueigual=0,\
    user = '{current_user.email}' where id={idauth}"
    iddato = pgonecolumn(con, f"select iddato from autorizacion where \
    id={idauth}")
    upd_dat = f"update datos set cuota_maxima = {cuota_requerida}, \
    autorizado=1,rechazado=0,sigueigual=0,enviado_vdor=1, fecha_visitar=\
         curdate() where id={iddato}"
    con = get_con()
    cur = con.cursor()
    try:
        cur.execute(upd_aut)
        cur.execute(upd_dat)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(upd_dat)
        log(upd_aut)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/vendedor/noautorizardato/<int:idauth>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_noautorizardato(idauth):
    """Proceso para NO autorizar un dato, y que siga igual, venda la basica."""
    con = get_con()
    upd_aut = f"update autorizacion set autorizado=0, user = \
    '{current_user.email}',rechazado=0,sigueigual=1 where id={idauth}"
    iddato = pgonecolumn(con, f"select iddato from autorizacion where \
    id={idauth}")
    upddato = f"update datos set rechazado=0, autorizado=0,sigueigual=1, \
    resultado=null, enviado_vdor=1 where id={iddato}"
    con = get_con()
    cur = con.cursor()
    try:
        cur.execute(upd_aut)
        cur.execute(upddato)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(upd_aut)
        log(upddato)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/vendedor/rechazardato/<int:idauth>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_rechazardato(idauth):
    """Proceso para rechazar dato, no se puede vender alli."""
    con = get_con()
    upd_aut = f"update autorizacion set autorizado=0, user = \
    '{current_user.email}',rechazado=1,sigueigual=0 where id={idauth}"
    iddato = pgonecolumn(con, f"select iddato from autorizacion where \
    id={idauth}")
    upddato = f"update datos set rechazado=1, autorizado=0, sigueigual=0, \
    resultado=8 where id={iddato}"
    con = get_con()
    cur = con.cursor()
    try:
        cur.execute(upd_aut)
        cur.execute(upddato)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(upd_aut)
        log(upddato)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/xuNzBi4bvtSugd5KbxSQzD0Ey', methods=['POST'])
@vendedor.route('/vendedor/pasarventa', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_pasarventa():
    """Proceso para pasar una venta por el vendedor."""
    global hay_venta
    hay_venta = 1
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    vdor = var_sistema[current_user.email]
    ant = 0
    cant_cuotas = 6
    imp_cuota = d_data['cuota']
    per = 1
    if d_data['dnigarante']:
        garantizado = 1
    else:
        garantizado = 0
    if es_dni_valido(d_data['dnigarante']):
        dnigarante = d_data['dnigarante']
    else:
        dnigarante = 0

    insvta = f"insert into ventas(fecha,idvdor,ant,cc,ic,p,primera,idcliente,\
    garantizado,dnigarante) values(curdate(),{vdor},{ant},{cant_cuotas},{imp_cuota},{per},\
    '{d_data['primera']}',{d_data['idcliente']},{garantizado},{dnigarante})"
    insvis = f"insert into visitas(fecha,hora,vdor,iddato,result,\
    monto_vendido) values(curdate(),curtime(),{vdor},{d_data['id']},1,{imp_cuota*cant_cuotas})"
    try:
        ultinsvta = pgonecolumn(con, "select valor from variables where id=13")
        listart = ''
        for item in d_data['arts']:
            listart += item['cnt']
            listart += item['art']
        if str(ultinsvta) != f"{cant_cuotas}{imp_cuota}{per}{d_data['primera']}{d_data['idcliente']}\
        {d_data['id']}{listart}":
            pgexec(con, insvis)
            pgexec(con, insvta)

            idvta = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
            # lo siguiente ha sido trasladado al trigger ventas_ins_clientes
            # upd = f"update datos set resultado=1, monto_vendido={imp_cuota*6}, \
            # fecha_definido=# current_timestamp(), idvta={idvta} where \
            #     id={d_data['id']}"
            # cur.execute(upd)
            listart = ''
            for item in d_data['arts']:
                listart += item['cnt']
                listart += item['art']
                cnt = item['cnt']
                art = item['art']
                imp_cuota = item['cuota']
                costo = pgonecolumn(con, f"select costo from articulos where \
                art='{art}'")
                ins = f"insert into detvta(idvta,cnt,art,cc,ic,costo,devuelta) \
                values({idvta},{cnt},'{art}',6,{imp_cuota},{costo},0)"
                pgexec(con, ins)
                log(ins)
            inslog = f"update variables set valor='{cant_cuotas}{imp_cuota}{per}{d_data['primera']}\
            {d_data['idcliente']}{d_data['id']}{listart}' where id=13"
            pgexec(con, inslog)
            con.commit()  # pruebo con hacer commit instantaneo de la variable
            # que quizas no sea leida pq no se hizo el commit.
        else:
            logging.warning("duplicacion de venta %s Dara cod 401", ultinsvta)
            return make_response('error de duplicacion de venta', 401)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        logging.warning(insvta, insvis)
        return make_response(error, 400)
    else:
        log(insvta)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/G9S85pbqWVEX17nNQuOOnpxvn/<int:iddato>')
@vendedor.route('/vendedor/noestabadato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_noestabadato(iddato):
    """Proceso de noestaba. Vendedor visita y no esta el cliente."""
    logging.warning("noestabadato, %s", current_user.email)

    con = get_con()
    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    ins = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{vdor},{iddato},3,0)"
    cur = con.cursor()
    try:
        cur.execute(ins)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        return 'ok'
    finally:
        con.close()


@vendedor.route('/vendedor/getvisitasvendedor')
@login_required
@check_roles(['dev', 'gerente','admin'])
def vendedor_getvisitasvendedor():
    """Funcion que entrega lista de visitas hechas por el vendedor."""
    con = get_con()
    visitasvendedor = pglistdict(con, "select visitas.fecha as fecha,\
    cast(hora as char) as hora, visitas.vdor as vdor, result, \
    visitas.monto_vendido as monto_vendido, idcliente,nombre,calle,num,\
    clientes.zona as zona from visitas,datos,clientes where visitas.iddato=\
    datos.id and clientes.id=datos.idcliente order by visitas.fecha desc,hora")

    fechasvisitas = pglistdict(
        con, "select visitas.fecha as fecha, visitas.vdor \
    as vdor, count(*) as cnt, sum(visitas.monto_vendido) as monto_vendido \
    from visitas,datos where visitas.iddato=datos.id group by visitas.fecha,\
    visitas.vdor order by visitas.fecha,visitas.vdor desc")
    return jsonify(visitasvendedor=visitasvendedor,
                   fechasvisitas=fechasvisitas)


@vendedor.route('/F8cq9GzHJIG9hENBo0Xq7hdH7')
@vendedor.route('/vendedor/getvisitasvdor')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getvisitasvdor():
    """Funcion que entrega la lista de visitas hechas por un vendedor."""
    logging.warning("getvisitasvdor, %s", current_user.email)

    con = get_con()
    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    visitasvendedor = pglistdict(con, f"select visitas.fecha as fecha,\
    cast(hora as char) as hora, visitas.vdor as vdor, result, \
    visitas.monto_vendido as monto_vendido, idcliente,nombre,calle,num,\
    clientes.zona as zona from visitas,datos,clientes where visitas.iddato=\
    datos.id and clientes.id=datos.idcliente and visitas.vdor={vdor} and \
    visitas.fecha>date_sub(curdate(),interval 6 day) order by \
    visitas.fecha desc,hora")

    fechasvisitas = pglistdict(
        con, f"select visitas.fecha as fecha, visitas.vdor \
    as vdor, count(*) as cnt, sum(visitas.monto_vendido) as monto_vendido \
    from visitas,datos where visitas.iddato=datos.id and visitas.vdor={vdor} \
    and visitas.fecha>date_sub(curdate(),interval 6 day) \
    group by visitas.fecha,visitas.vdor order by visitas.fecha,visitas.vdor \
    desc")
    return jsonify(visitasvendedor=visitasvendedor,
                   fechasvisitas=fechasvisitas)


@vendedor.route('/vendedor/getclientesingresadosporvdor')
@login_required
@check_roles(['dev', 'gerente','admin'])
def vendedor_getclientesingresadosporvdor():
    """Funcion entrega lista de clientes ingresados o alterados por el vdor."""
    con = get_con()
    clientes = pglistdict(con, "select * from clientes where modif_vdor=1")
    return jsonify(clientes=clientes)


@vendedor.route('/vendedor/getventashoy')
@login_required
@check_roles(['dev', 'gerente','admin'])
def vendedor_getventashoy():
    """Funcion que entrega lista de las ventas del dia para el vendedor."""
    con = get_con()
    devol_pend_registrar = pglistdict(con, "select ventas.id as id,\
                                      comentario_retirado,\
                                      dni from ventas,clientes where \
                                      clientes.id = ventas.idcliente and \
                                      retirado=1 and devol_procesada=0")
    ventashoy = pglistdict(con, "select fecha_definido,\
    nombre,concat(calle,' ',num) as direccion,clientes.zona as zona, monto_vendido,\
    vendedor,dni,wapp_verificado from datos,clientes where datos.idcliente = clientes.id and \
    date(fecha_definido)=curdate() and resultado=1 order by fecha_definido")
    vendedores = pglist(con, "select id from cobr where activo=1 and vdor=1")
    wappnoenviados = pglistdict(con, "SELECT DISTINCT clientes.id as id, \
                                nombre,CONCAT(calle, ' ', num) AS direccion, \
                                ventas.id as idvta,wapp,wapp_verificado,dni, \
                                auth_sinwapp_verificado \
                                FROM clientes \
                                JOIN ventas ON clientes.id = ventas.idcliente \
                                WHERE fecha > CURDATE() - INTERVAL 3 DAY \
                                AND sendwapp = 0 and pp= 0 and devuelta = 0 \
                                and wapp!= '' and wapp is not null and \
                                      idcliente not in (select id from \
                                      clientes where auth_sinwapp_verificado=\
                                      1)")
    return jsonify(ventashoy=ventashoy, vendedores=vendedores,
                   wappnoenviados=wappnoenviados,devolpendregistrar=\
                    devol_pend_registrar)


@vendedor.route('/vendedor/getvisitashoy')
@login_required
@check_roles(['dev', 'gerente','admin'])
def vendedor_getvisitashoy():
    """Funcion que entrega lista de las visitas del dia para el vendedor."""
    con = get_con()
    visitashoy = pglistdict(con, "select concat(fecha,' ',hora) as fechahora,\
    vdor,result,(select concat(calle,' ',num) from clientes where id=(select \
    idcliente from datos where id=iddato)) as direccion from visitas \
    where fecha=curdate() order by hora")
    return jsonify(visitashoy=visitashoy)


@vendedor.route('/3ZbXanrRQalY6JL5eOBi49Nyc', methods=["POST"])
@vendedor.route('/vendedor/wappaut', methods=["POST"])
@login_required
@check_roles(['dev', 'gerente', 'admin', 'vendedor'])
def vendedor_wappaut():
    """Funcion que procesa el wapp de autorizacion.

    Si el tipo = 'retiro de zona' aparte de enviar wapp al wapp_auth envia un
    segundo wapp a mi."""

    logging.warning("wappaut, %s", current_user.email)
    vdor = var_sistema[current_user.email]
    _ = json.loads(request.data.decode("UTF-8"))
    msg = f"Autorizacion para el vdor {vdor}"
    wapp1 = var_sistema['wapp_auth']
    wapp2 = var_sistema['wapp_auth2']
    wapp3 = '3512411963'
    try:
        if wapp1:
            send_msg_whatsapp(0, wapp1, msg)
        if wapp2:
            send_msg_whatsapp(0, wapp2, msg)
        send_msg_whatsapp(0,wapp3,msg)
    except mysql.connector.Error as _error:
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        return 'ok'


@vendedor.route('/vendedor/wapprespauth', methods=["POST"])
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_wapprespaut():
    """Funcion que procesa la respuesta a la autorizacion."""

    d_data = json.loads(request.data.decode("UTF-8"))
    vdor = 'wapp'+str(d_data['vdor'])
    wappvdor = var_sistema[vdor]
    msg = d_data['msg']
    if wappvdor:
        time.sleep(15)
        response = send_msg_whatsapp(0, wappvdor, msg)
        return response
    return 'error', 400


@vendedor.route('/hX53695XAOpaLY9itLgmghkhH', methods=["POST"])
@vendedor.route('/vendedor/wapp', methods=["POST"])
@login_required
@check_roles(['dev', 'gerente', 'admin', 'vendedor'])
def vendedor_wapp():
    """Funcion que procesa wapp enviados por el vendedor."""
    d_data = json.loads(request.data.decode("UTF-8"))
    idcliente = d_data['idcliente']
    wapp = d_data['wapp']
    msg = d_data['msg']
    # devel = var_sistema['devel']
    # if devel=='1':
    #     prod=0
    # else:
    #     prod=1
    if wapp:
        response = send_msg_whatsapp(idcliente, wapp, msg)
        if response is None:
            response = 'Encolado'
        return response
    return 'error', 400


@vendedor.route('/4qUK6eNZnCYjIiGTt3HSj2YDp', methods=['POST'])
@vendedor.route('/vendedor/filewapp', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'admin', 'vendedor'])
def vendedor_filewapp():
    """Funcion que procesa el envio de pdf por el vendedor."""

    d_data = json.loads(request.data.decode("UTF-8"))
    wapp = d_data['wapp']
    idcliente = d_data['idcliente']
    file = d_data['file']
    # devel = var_sistema['devel']
    # if devel=='1':
    #     prod=0
    # else:
    #     prod=1
    if wapp:
        response = send_file_whatsapp(
            idcliente, f"https://fedesal.lol/pdf/{file}.pdf", wapp)
        return jsonify(response=response)
    return 'error', 400


@vendedor.route('/vendedor/getcomisionesvendedor/<int:vdor>')
@login_required
@check_roles(['dev', 'gerente','admin'])
def vendedor_getcomisionesvendedor(vdor):
    """Funcion que entrega lista de comisiones por vendedor."""

    com = 'com'+str(vdor)
    comision = var_sistema[com]
    con = get_con()
    comisiones = pglistdict(con, f"select date(fecha_definido) as fecha,\
    monto_vendido*{comision} as com,idvta as id from datos where vendedor=\
    {vdor} and com_pagada=0 and monto_vendido>0 order by date(fecha_definido)")
    devoluciones = pglistdict(con, f"select date(fecha_definido) as fecha,\
    monto_devuelto*{comision}*(-1) as com, idvta as id from datos where \
    vendedor={vdor} and com_pagada_dev=0 and monto_devuelto!=0 order by \
    date(fecha_definido)")
    fechascomisiones = pglistdict(
        con, f"select date(fecha_definido) as fecha,  \
    count(*) as cnt,sum(case when com_pagada=0 then monto_vendido*{comision} \
    when com_pagada=1 then 0 end)+sum(monto_devuelto*{comision}*(-1)) as \
    comision from datos where ((resultado=1 and com_pagada=0) or \
    (monto_devuelto>0 and com_pagada_dev=0)) and vendedor={vdor} group by \
    date(fecha_definido) order by date(fecha_definido) desc")
    if devoluciones:
        comisiones = comisiones+devoluciones
    return jsonify(comisiones=comisiones, fechascomisiones=fechascomisiones)


@vendedor.route('/vendedor/getcomisionesprom')
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_getcomisionesprom():
    """Funcion que entrega la lista de comisiones de las administrativas."""
    con = get_con()
    comisiones = pglistdict(con, "select date(fecha_definido) as fecha,\
    monto_vendido*0.04 as com,idvta as id from datos where user in \
    ('isabelheredie@gmail.com','n.dryon@gmail.com') and com_pagada_prom=0 \
    and monto_vendido>0 order by date(fecha_definido)")
    fechascomisiones = pglistdict(
        con, "select date(fecha_definido) as fecha,  \
    count(*) as cnt,sum(monto_vendido*0.04) as comision from datos where \
    resultado=1 and com_pagada_prom=0 and user in ('isabelheredie@gmail.com',\
    'n.dryon@gmail.com') group by date(fecha_definido) order by \
    date(fecha_definido) desc")
    return jsonify(comisiones=comisiones, fechascomisiones=fechascomisiones)


@vendedor.route('/MeHzAqFYsbb78KAVFAGTlZRW9/<dni>')
@vendedor.route('/vendedor/buscaclientepordni/<dni>')
@login_required
@check_roles(['dev', 'gerente', 'admin', 'vendedor'])
def vendedor_buscaclientepordni(dni):
    """Simple funcion que levanta datos del cliente por dni."""
    con = get_con()
    cliente = pgdict(con, f"select * from clientes where dni={dni}")
    if cliente:
        return jsonify(cliente=cliente)
    return make_response("error", 401)


@vendedor.route('/vendedor/getartvendedor/<int:vdor>')
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_getartvendedor(vdor):
    """Funcion que entrega lista de articulos a cargar por vendedor."""
    con = get_con()
    artvendedor = pglistdict(con, f"select sum(detvta.cnt) as cnt,\
    detvta.art as art from detvta,ventas where detvta.idvta=ventas.id and \
    cargado=0 and idvdor={vdor} group by detvta.art")
    # no se filtra mas por devuelta=0, solo por cargado=0
    return jsonify(artvendedor=artvendedor)


@vendedor.route('/vendedor/getvendedores')
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_getvendedores():
    """Simple funcion que entrega lista de vendedores."""
    con = get_con()
    vendedores = pglist(con, "select id from cobr where activo=1 and vdor=1")
    return jsonify(vendedores=vendedores)


@vendedor.route('/vendedor/marcarcargado/<int:vdor>')
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_marcarcargado(vdor):
    """Proceso que marca que los articulos pendientes fueron cargados."""
    con = get_con()
    upd = f"update detvta set cargado=1 where idvta in (select id from ventas \
    where idvdor={vdor})"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(upd)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/vendedor/marcarpagadas/<int:vdor>')
@login_required
@check_roles(['dev', 'gerente'])
def vendedor_marcarpagadas(vdor):
    """Proceso que marca como pagadas las comisiones pendientes de un vdor."""
    con = get_con()
    upd = f"update datos set com_pagada=1, fechapagocom=current_date() where \
    idvta in (select idvta from datos where vendedor={vdor} and com_pagada=0 \
    and monto_vendido>0)"
    upddev = f"update datos set com_pagada_dev=1, fechapagocomdev=\
    current_date() where idvta in (select idvta from datos where vendedor=\
    {vdor} and com_pagada_dev=0 and monto_devuelto!=0)"
    cur = con.cursor()
    try:
        cur.execute(upd)
        cur.execute(upddev)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(upd)
        log(upddev)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/vendedor/marcarpagadasseleccionados', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente'])
def vendedor_marcarpagadasseleccionados():
    """Proceso que marca pagadas las comisiones de un vdor en ciertos dias."""
    d_data = json.loads(request.data.decode("UTF-8"))
    vdor = d_data['vdor']
    fechas = d_data['fechas']
    lpg = '('
    for fecha in fechas:
        lpg += f"'{str(fecha)}',"
    lpg = lpg[0:-1]+')'
    con = get_con()
    upd = f"update datos set com_pagada=1, fechapagocom=current_date() where \
    idvta in (select idvta from datos where vendedor={vdor} and com_pagada=0 \
    and monto_vendido>0 and date(fecha_definido) in {lpg})"
    upddev = f"update datos set com_pagada_dev=1, fechapagocomdev=\
    current_date() where idvta in (select idvta from datos where vendedor=\
    {vdor} and com_pagada_dev=0 and monto_devuelto>0 and date(fecha_definido) \
    in {lpg})"
    cur = con.cursor()
    try:
        cur.execute(upd)
        cur.execute(upddev)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(upd)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/vendedor/marcarpagadascomprom')
@login_required
@check_roles(['dev', 'gerente'])
def vendedor_marcarpagadascomprom():
    """Proceso que marca pagadas comisiones promotoras pendientes."""
    con = get_con()
    upd = "update datos set com_pagada_prom=1, fechapagocom_prom=\
    current_date() where idvta in (select idvta from datos where user in \
    ('isabelheredie@gmail.com','n.dryon@gmail.com') and com_pagada_prom=0 \
    and monto_vendido>0)"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(upd)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/vendedor/marcarpagadascompromseleccionados',
                methods=['POST'])
@login_required
@check_roles(['dev', 'gerente'])
def vendedor_marcarpagadascompromseleccionados():
    """Proceso que marca pagadas comisiones promotoras en ciertos dias."""
    d_data = json.loads(request.data.decode("UTF-8"))
    fechas = d_data['fechas']
    lpg = '('
    for fecha in fechas:
        lpg += f"'{str(fecha)}',"
    lpg = lpg[0:-1]+')'
    con = get_con()
    upd = f"update datos set com_pagada_prom=1, fechapagocom_prom=\
    current_date() where idvta in (select idvta from datos where user in \
    ('isabelheredie@gmail.com','n.dryon@gmail.com') and com_pagada_prom=0 \
    and monto_vendido>0 and date(fecha_definido) in {lpg})"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        con.commit()
        log(upd)
        return 'ok'
    finally:
        con.close()


@vendedor.route('/k8E5hsVs4be3jsJJaob6OQmAX')
@vendedor.route('/vendedor/getcargavendedor')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getcargavendedor():
    """Funcion entrega lista de articulos a cargar para el vendedor."""
    logging.warning("getcargavendedor, %s", current_user.email)

    con = get_con()
    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    artvendedor = pglistdict(con, f"select sum(detvta.cnt) as cnt,\
    detvta.art as art from detvta,ventas where detvta.idvta=ventas.id and \
    cargado=0 and idvdor={vdor} group by detvta.art")
    # no se filtra mas por devuelta=0, solo por cargado=0
    return jsonify(artvendedor=artvendedor)


@vendedor.route('/TWGQV0TM0p7Oa9tMPvrNWIHyd')
@vendedor.route('/vendedor/cargararticulos')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_cargararticulos():
    """Ruta que renderiza la pagina cargarart."""
    return render_template('/vendedor/cargarart.html')


@vendedor.route('/DDFEwfGEDYv5UHTVgcDPFUWm1')
@vendedor.route('/vendedor/comisionesvdor')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_comisionesvdor():
    """Ruta que renderiza la pagina comisionesvdor."""
    return render_template('/vendedor/comisionesvdor.html')


@vendedor.route('/IrV7gmqz4Wu8Q8rwmXMftphaB')
@vendedor.route('/vendedor/getcomisionesparavendedor')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getcomisionesparavendedor():
    """Funcion que entrega lista de comisiones pendiente para el vendedor."""
    logging.warning("getcomisionesparavendedor, %s", current_user.email)

    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    com = 'com'+str(vdor)
    comision = var_sistema[com]
    con = get_con()
    comisiones = pglistdict(con, f"select date(fecha_definido) as fecha,\
    monto_vendido*{comision} as com, idvta as id from datos where \
    vendedor={vdor} and com_pagada=0 and monto_vendido>0 order by \
    date(fecha_definido)")
    devoluciones = pglistdict(
        con, f"select fecha,monto_devuelto*{comision}*(-1) \
    as com, idvta as id from datos where vendedor={vdor} and com_pagada_dev=0 \
    and monto_devuelto!=0 order by fecha")
    fechascomisiones = pglistdict(
        con, f"select date(fecha_definido) as fecha,  \
    count(*) as cnt,sum(case when com_pagada=0 then monto_vendido*{comision} \
    when com_pagada=1 then 0 end)+sum(monto_devuelto*{comision}*(-1)) as \
    comision from datos where ((resultado=1 and com_pagada=0) or \
    (monto_devuelto>0 and com_pagada_dev=0)) and vendedor={vdor} group by \
    date(fecha_definido) order by date(fecha_definido) desc")
    if devoluciones:
        comisiones = comisiones+devoluciones
    return jsonify(comisiones=comisiones, fechascomisiones=fechascomisiones)


@vendedor.route('/vendedor/obtenerdni/<int:idcliente>')
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_obtenerdni(idcliente):
    """Simple funcion que busca el dni de un cliente dado su idcliente."""
    con = get_con()
    dni = pgonecolumn(con, f"select dni from clientes where id={idcliente}")
    return jsonify(dni=dni)


@vendedor.route('/vendedor/tomardato/<int:idauth>')
@login_required
@check_roles(['dev', 'gerente', 'admin'])
def vendedor_tomardato(idauth):
    """Simple proceso que marca que una autorizacion fue atendida."""
    con = get_con()
    upd = f"update autorizacion set tomado=1 where id={idauth}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    con.close()
    return 'ok'


@vendedor.route('/u0IEJT3i1INZpKoNKbyezlfRy/<int:auth>')
@vendedor.route('/vendedor/isatendido/<int:auth>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_isatendido(auth):
    """Simple funcion que marca si una autorizacion ya esta atendida."""
    con = get_con()
    tomado = pgonecolumn(con, f"select tomado from autorizacion where id=\
    {auth}")
    return jsonify(tomado=tomado)


@vendedor.route('/ymIVWKdjgnCeJvo2zcodwRTQM/<int:auth>')
@vendedor.route('/vendedor/isrespondidoauth/<int:auth>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_isrespondidoauth(auth):
    """Funcion que entrega la respuesta que tuvo la autorizacion."""
    con = get_con()
    respuesta, motivo = pgtuple(con, f" select \
                            case when autorizado=1 then 'autorizado' \
                                 when rechazado=1 then 'rechazado' \
                                 when sigueigual=1 then 'sigueigual' end \
                            as respuesta, motivo \
    from autorizacion where id={auth}")
    if motivo is None:
        motivo = ''
    logging.warning(f"respuesta{respuesta}, motivo:{motivo}")
    return jsonify(respuesta=respuesta, motivo=motivo)


@vendedor.route('/vendedor/motivoautorizacion/<motivo>/<int:idauth>')
@login_required
@check_roles(['dev', 'gerente','admin'])
def vendedor_motivoautorizacion(motivo, idauth):
    """Proceso para registrar el motivo del rechazo de una autorizacion."""
    con = get_con()
    upd = f"update autorizacion set motivo='{motivo}' where id={idauth}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    con.close()
    return 'ok'


@vendedor.route('/vendedor/comentarioautorizacion/<comentario>/<int:idauth>')
@login_required
@check_roles(['dev', 'gerente','admin'])
def vendedor_comentarioautorizacion(comentario, idauth):
    """Proceso para registrar el comentario del rechazo de una autorizacion."""
    con = get_con()
    upd = f"update autorizacion set comentario='{comentario}' where id={idauth}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    con.close()
    return 'ok'


@vendedor.route('/quBXVVWkNijghkJ4JpwSgluJQ', methods=['POST'])
@vendedor.route('/vendedor/imprimirfichapantalla', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_imprimirfichapantalla():
    """Funcion para imprimir ficha de cliente en pantalla a vendedor."""
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    idcliente = d['idcliente']
    dni = pgonecolumn(con, f"select dni from clientes where id={idcliente}")
    ficha(con, [dni])
    con.close()
    return send_file('/home/hero/ficha.pdf')


@vendedor.route('/S0rjYKB35QIcHunPmebg2tmr1', methods=['POST'])
@vendedor.route('/vendedor/visitadevolucion', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_visitadevolucion():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    iddato = pgonecolumn(con, f"select id from datos where idvta={d['idvta']}")
    updvta = f"update ventas set retirado=1,comentario_retirado='{d['msg']}' where id={d['idvta']}"
    ins = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{d['vendedor']},{iddato},7,0)"
    try:
        pgexec(con, ins)
        pgexec(con, updvta)
    except mysql.connector.Error as _error:
            con.rollback()
            error = _error.msg
            logging.warning(
                f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
            return make_response(error, 400)
    else:
        con.close()
        return 'ok'


@vendedor.route('/vendedor/asignawappacliente/<string:wapp>/<int:idcliente>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_asignawappacliente(wapp,idcliente):
    con = get_con()
    clientes_con_ese_wapp = pglist(con, f"select id from clientes where \
                                   wapp='{wapp}'")
    if clientes_con_ese_wapp!='':
        clientes_con_ese_wapp = listsql(clientes_con_ese_wapp)
        updborrar = f"update clientes set wapp='' where id in \
            {clientes_con_ese_wapp}"
        updasignar = f"update clientes set wapp='{wapp}' where id={idcliente}"
        insverificables = f"insert into verificables(wapp,idcliente) values(\
            '{wapp}',{idcliente})"
        try:
            pgexec(con, updborrar)
            pgexec(con, updasignar)
            pgexec(con, insverificables)
        except mysql.connector.Error as _error:
            con.rollback()
            error = _error.msg
            logging.warning(
                f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
            return make_response(error, 400)
        else:
            con.commit()
            return 'ok'
        finally:
            con.close()
    else:
        return make_response('ese idcliente no existe',400)


@vendedor.route('/vendedor/buscarsiexistewapp/<string:wapp>/<int:idcliente>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_buscarsiexistewapp(wapp,idcliente):
    con = get_con()
    print('idcliente',idcliente)
    existe = len(pglist(con,f"select id from clientes where wapp={wapp} and \
                    wapp_verificado=1 and id != {idcliente}"))
    print('existe',existe)
    # if existe == 0:
    #     existe = len(pglist(con, f"select id from clientes where wapp={wapp}"))
    #     print('existe no se porque lo busco')
    #     if existe>1:
    #         existe = 0
    return jsonify(existe=existe)


@vendedor.route('/vendedor/marcaauthsinwapp/<int:idcliente>')
@login_required
@check_roles(['dev', 'gerente','admin'])
def vendedor_marcaauthsinwapp(idcliente):
    con = get_con()
    upd = f"update clientes set auth_sinwapp_verificado=1 where id={idcliente}"
    try:
        pgexec(con, upd)
    except mysql.connector.Error as _error:
            con.rollback()
            error = _error.msg
            logging.warning(
                f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
            return make_response(error, 400)
    else:
        return 'ok'
    finally:
        con.close()


@vendedor.route('/hayventa')
def hayventa():
    global hay_venta
    hay_venta_ = hay_venta
    if hay_venta == 1:
        hay_venta = 0
    return jsonify(hay_venta=hay_venta_)


@vendedor.route('/hayauth')
def hayauth():
    global hay_auth
    hay_auth_ = hay_auth
    if hay_auth == 1:
        hay_auth = 0
    return jsonify(hay_auth=hay_auth_)
