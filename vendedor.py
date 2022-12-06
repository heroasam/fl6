from flask_login import login_required, current_user
import mysql.connector
from flask import Blueprint, render_template, jsonify, make_response, request,\
    send_file
import simplejson as json
from lib import pgonecolumn, pgdict, send_msg_whatsapp, send_file_whatsapp, \
    pglflat, log_busqueda, listsql
from con import get_con, log, check_roles

vendedor = Blueprint('vendedor', __name__)

@vendedor.route('/vendedor/listadatos')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_listadatos():
    return render_template('/vendedor/listadatos.html')


@vendedor.route('/vendedor/getlistadodatosvendedor')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getlistadodatosvendedor():
    con = get_con()
    if current_user.email =="hfj027@gmail.com":
        vdor = 816
    else:
        vdor = 0
    listadodatos = pgdict(con, f"select datos.id, fecha, fecha_visitar,\
    art, horarios, comentarios,  dni, nombre,calle,num,acla,wapp,tel,barrio, \
    cuota_maxima from datos, clientes where clientes.id = datos.idcliente and \
    vendedor={vdor} and resultado is null order by id desc")
    return jsonify(listadodatos=listadodatos)
