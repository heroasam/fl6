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
    zona, cuota_maxima,idcliente from datos, clientes where clientes.id = \
    datos.idcliente and vendedor={vdor} and resultado is null  and \
    fecha_visitar <=curdate() order by id desc")
    return jsonify(listadodatos=listadodatos)


@vendedor.route('/vendedor/editarwapp' , methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_editarwapp():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    wapp_viejo = pgonecolumn(con, f"select wapp from clientes where id= \
    {d['idcliente']}")
    upd = f"update clientes set wapp='{d['wapp']}' where id={d['idcliente']}"
    if wapp_viejo and wapp_viejo != 'INVALIDO':
        inslogcambio = f"insert into logcambiodireccion(idcliente,wapp,fecha) \
        values ({d['idcliente']},'{wapp_viejo}', current_date())"
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
       return make_response(error,400)
    else:
       con.commit()
       con.close()
       log(upd)
       return 'ok'


@vendedor.route('/vendedor/guardardatofechado' , methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_guardardatofechado():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    upd = f"update datos set fecha_visitar='{d['fecha_visitar']}' where id = \
    {d['id']}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as _error:
       con.rollback()
       error = _error.msg
       return make_response(error,400)
    else:
       con.commit()
       con.close()
       log(upd)
       return 'ok'


@vendedor.route('/vendedor/anulardato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_anulardato(iddato):
    con = get_con()
    upd = f"update datos set resultado=0, fecha_definido=current_timestamp()\
    where id = {iddato}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as _error:
       con.rollback()
       error = _error.msg
       return make_response(error,400)
    else:
       con.commit()
       con.close()
       log(upd)
       return 'ok'
