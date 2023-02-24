"""Modulo que concentra la mayoria de las funciones del sistema cobrador."""

import logging
import time
from flask_login import login_required, current_user
import mysql.connector
from flask import Blueprint, render_template, jsonify, make_response, request
import simplejson as json
from lib import pgonecolumn, pgdict, send_msg_whatsapp, send_file_whatsapp, \
    pglflat,  listsql, pgdict1
from con import get_con, log, check_roles


cobrador = Blueprint('cobrador', __name__)


var_sistema = {}
def leer_variables():
    """Funcion para leer variables de sistema.

    Las variables estan ubicadas en la tabla variables con los campos clave,
    valor.
    Y seran incorporados en una variable  que es un dict."""

    con = get_con()
    variables = pgdict(con, "select clave,valor from variables")
    for row in variables:
        var_sistema[row['clave']] = row['valor']
    return 1
leer_variables()

def get_cobr():
    return var_sistema[current_user.email]


@cobrador.route('/cobrador/listafichas')
@login_required
@check_roles(['dev','gerente','cobrador'])
def cobrador_listafichas():
    """Muestra pagina lista de fichas."""
    return render_template('/cobrador/listafichas.html')



@cobrador.route('/cobrador/getlistadofichas')
@login_required
@check_roles(['dev','gerente','cobrador'])
def cobrador_getlistadofichas():
    """Funcion que entrega lista fichas, lista zonas.

    Filtro mudados, fallecidos, fechados y cobrados.
    El filtro cobrados opera para los ultpago>-7dias y <hoy.
    Para que no se muestren los que pueden haber sido cobrados luego de la
    asignacion, pero si se muestren los cobrados en el dia de la fecha."""
    cobr = get_cobr()
    con = get_con()
    zonas = pglflat(con, f"select clientes.zona as zona from clientes,zonas \
    where asignada=1 and asignado={cobr} and clientes.zona=zonas.zona \
    group by clientes.zona")
    fichas = pgdict(con, f"select clientes.* from clientes,zonas where \
    asignada=1 and asignado={cobr} and clientes.zona=zonas.zona and \
    mudo=0 and clientes.zona!='-FALLECIDOS' and fechado=0 and (datediff(now(),\
    ultpago) >6 or datediff(now(), ultpago) is null) or datediff(now(),\
    ultpago)=0")
    return jsonify(zonas=zonas, fichas=fichas)


@cobrador.route('/cobrador/fecharficha/<int:idcliente>/<pmovto>')
@login_required
@check_roles(['dev','gerente','cobrador'])
def cobrador_fecharficha(idcliente,pmovto):
    """Proceso para fechar fichas por el cobrador.

    Hay un campo fechada en clientes que permite filtrarle al cobrador las
    fichas fechadas."""
    con = get_con()
    upd = f"update clientes set pmovto='{pmovto}',fechado=1 where id=\
    {idcliente}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        return 'ok'
    finally:
        con.close()


@cobrador.route('/cobrador/asignar', methods = ['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def cobrador_asignar():
    """Proceso para marcar asignada la ficha a un cobrador.

    No se pone el idcobr porque ya esta registrado en la tabla zonas.
    Se pone fechado=0 para que permita marcar fechado luego de la asignacion."""
    con = get_con()
    listadni = json.loads(request.data.decode("UTF-8"))
    upd = f"update clientes set asignada=1, fechado=0 where dni in \
    {listsql(listadni)}"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    log(upd)
    con.close()
    return 'ok'


@cobrador.route('/cobrador/noestabaficha/<int:idcliente>')
@login_required
@check_roles(['dev','gerente','cobrador'])
def cobrador_noestabaficha(idcliente):
    """Proceso para poner 'no estaba' a la ficha por el cobrador.

    En la ficha(tabla clientes) no se registra nada, pero se registra la
    visita."""
    con = get_con()
    cobr = var_sistema[current_user.email]
    ins = f"insert into visitascobr(fecha,hora,cobr,idcliente,result) \
    values(curdate(),curtime(),{cobr},{idcliente},3)"
    cur = con.cursor()
    try:
        cur.execute(ins)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        return 'ok'
    finally:
        con.close()


@cobrador.route('/cobrador/mudoficha/<int:idcliente>')
@login_required
@check_roles(['dev','gerente','cobrador'])
def cobrador_mudoficha(idcliente):
    """Proceso para poner 'mudado' a la ficha por el cobrador."""
    con = get_con()
    cobr = var_sistema[current_user.email]
    ins = f"insert into visitascobr(fecha,hora,cobr,idcliente,result) \
    values(curdate(),curtime(),{cobr},{idcliente},5)"
    upd = f"update clientes set mudo=1 where id={idcliente}"
    inscomentario = f"insert into comentarios(idcliente, ingreso, comentario) \
    values({idcliente},'{current_user.email}','puesto como mudado por \
    cobrador {cobr}')"
    cur = con.cursor()
    try:
        cur.execute(ins)
        cur.execute(upd)
        cur.execute(inscomentario)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        return 'ok'
    finally:
        con.close()


@cobrador.route('/cobrador/fallecioficha/<int:idcliente>')
@login_required
@check_roles(['dev','gerente','cobrador'])
def cobrador_fallecioficha(idcliente):
    """Proceso para poner 'fallecido' a la ficha por el cobrador."""
    con = get_con()
    cobr = var_sistema[current_user.email]
    ins = f"insert into visitascobr(fecha,hora,cobr,idcliente,result) \
    values(curdate(),curtime(),{cobr},{idcliente},6)"
    upd = f"update clientes set zona='-FALLECIDOS' where id={idcliente}"
    inscomentario = f"insert into comentarios(idcliente, ingreso, comentario) \
    values({idcliente},'{current_user.email}','puesto como fallecido por \
    cobrador {cobr}')"
    cur = con.cursor()
    try:
        cur.execute(ins)
        cur.execute(upd)
        cur.execute(inscomentario)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        return 'ok'
    finally:
        con.close()
