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
    """Funcion que entrega lista fichas, lista zonas."""
    cobr = get_cobr()
    con = get_con()
    zonas = pglflat(con, f"select clientes.zona as zona from clientes,zonas \
    where asignada=1 and asignado={cobr} and clientes.zona=zonas.zona group \
    by clientes.zona")
    fichas = pgdict(con, f"select * from clientes,zonas where asignada=1 and \
    asignado={cobr} and clientes.zona=zonas.zona")
    return jsonify(zonas=zonas, fichas=fichas)


@cobrador.route('/cobrador/fecharficha/<int:idcliente>/<pmovto>')
@login_required
@check_roles(['dev','gerente','cobrador'])
def cobrador_fecharficha(idcliente,pmovto):
    con = get_con()
    upd = f"update clientes set pmovto='{pmovto}' where id={idcliente}"
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
