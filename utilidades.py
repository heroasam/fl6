from flask import Blueprint,render_template,jsonify,make_response, request, send_file
from flask_login import login_required, current_user
from lib import *
from con import get_con, log, check_roles
import pandas as pd
import simplejson as json
import mysql.connector
import os
import glob
from urllib.parse import urlparse
from formularios import listadocumentos


utilidades = Blueprint('utilidades',__name__)

@utilidades.route('/utilidades/planos')
@login_required
@check_roles(['dev','gerente','admin'])
def utilidades_planos():
    return render_template('/utilidades/planos.html')

@utilidades.route('/utilidades/impresos')
@login_required
@check_roles(['dev','gerente','admin'])
def utilidades_impresos():
    return render_template('/utilidades/impresos.html')


@utilidades.route('/utilidades/pdfsistema')
@login_required
@check_roles(['dev','gerente','admin'])
def utilidades_pdfimpresos():
    return render_template('/utilidades/pdfsistema.html')


@utilidades.route('/utilidades/users')
@login_required
@check_roles(['dev'])
def utilidades_users():
    return render_template('/utilidades/users.html')


@utilidades.route('/utilidades/getplanos')
@login_required
@check_roles(['dev','gerente','admin'])
def utilidades_getplanos():
    listaplanos = os.listdir('/home/hero/documentos/planos')
    listaplanos.sort()
    return jsonify(planos=listaplanos)


@utilidades.route('/utilidades/imprimirplanos/<string:plano>')
@login_required
@check_roles(['dev','gerente','admin'])
def utilidades_imprimirplano(plano):
    return send_file(os.path.join('/home/hero/documentos/planos',plano))


@utilidades.route('/utilidades/getimpresos')
@login_required
@check_roles(['dev','gerente','admin'])
def utilidades_getimpresos():
    listaimpresos = os.listdir('/home/hero/documentos/impresos')
    listaimpresos.sort()
    return jsonify(impresos=listaimpresos)


@utilidades.route('/utilidades/imprimirimpreso/<string:impreso>')
@login_required
@check_roles(['dev','gerente','admin'])
def utilidades_imprimirimpreso(impreso):
    return send_file(os.path.join('/home/hero/documentos/impresos',impreso))


@utilidades.route('/utilidades/getpdfsistema')
@login_required
@check_roles(['dev','gerente','admin'])
def utilidades_pdfsistema():
    listapdfs = os.listdir('/home/hero')
    pdfs = [os.path.split(pdf)[1] for pdf in listapdfs if pdf[-3:]=='pdf']
    pdfs.sort()
    return jsonify(pdfs=pdfs)


@utilidades.route('/utilidades/imprimirpdfsistema/<pdf>')
@login_required
@check_roles(['dev','gerente','admin'])
def utilidades_imprimirpdfsistema(pdf):
    return send_file(os.path.join('/home/hero',pdf))


@utilidades.route('/utilidades/contador')
@login_required
@check_roles(['dev','gerente','admin'])
def utilidades_contador():
    return render_template('/utilidades/contador.html')


@utilidades.route('/utilidades/calcprecios')
@login_required
@check_roles(['dev','gerente','admin'])
def utilidades_calcprecios():
    return render_template('/utilidades/calcprecios.html')


@utilidades.route('/utilidades/documentos')
@login_required
@check_roles(['dev','gerente','admin'])
def utilidades_documentos():
    return render_template('/utilidades/documentos.html')


@utilidades.route('/utilidades/getdocumentos/<int:desde>/<int:hasta>')
@login_required
@check_roles(['dev','gerente','admin'])
def utilidades_getdocumentos(desde,hasta):
    con = get_con()
    documentos = pglistdict(con, f"select ventas.id as id,nombre,concat\
    (calle,' ',num) as direccion, saldo from ventas,clientes where \
    ventas.idcliente=clientes.id and ventas.id>={desde} and ventas.id\
    <={hasta} and saldo>0")
    return jsonify(documentos=documentos)


@utilidades.route('/utilidades/imprimirlistadocumentos',   methods=["POST"])
@login_required
@check_roles(['dev','gerente','admin'])
def utilidades_imprimirlistadocumentos():
    con = get_con()
    lista_documentos = json.loads(request.data.decode("UTF-8"))
    listadocumentos(con, lista_documentos)
    return send_file('/home/hero/documentos/listadocumentos.pdf')


@utilidades.route('/utilidades/listawapp')
@login_required
@check_roles(['dev','gerente','admin'])
def utilidades_listawapp():
    """Lista whatsapps."""
    con = get_con()
    wapps = pglistdict(con, "select wapp,fecha,msg,file,id,idcliente,user,timein,\
    timeout,enviado,response from logwhatsapp order by id desc")
    return jsonify(wapps=wapps)


@utilidades.route('/utilidades/wapp')
@login_required
@check_roles(['dev','gerente','admin'])
def utilidades_wapp():
    """Muestro pagina wapp."""
    return render_template('/utilidades/wapp.html')


@utilidades.route('/utilidades/logthemes/<theme>/<ismobile>')
@login_required
def utilidades_logtheme(theme, ismobile):
    """Hago el log del theme usado por el usuario."""
    ruta = urlparse(request.referrer).path
    if "@" in str(current_user):
        email = current_user.email
    else:
        email = ""
    if ismobile =='true':
        ismobile = 'mobile'
    else:
        ismobile = 'desktop'
    with open("/home/hero/log/themes.log", "a", encoding="utf-8") as log_file:
        log_file.write('\n')
        log_file.write(time.strftime('%Y-%m-%d',time.localtime())+', '+\
                      time.strftime('%H:%M:%S',time.localtime())+', '+\
                       theme+', '+email+', '+ismobile+', '+ruta)
        log_file.close()
    return 'ok'

def update_dni_garantes():
    con = get_con()
    cur = con.cursor()
    listadni = pglflat(con, "select dnigarante from ventas where garantizado=1 and saldo>0")
    for dni in listadni:
        upd = f"update clientes set esgarante=1 where dni={dni}"
        cur.execute(upd)
    con.commit()
    con.close()


@utilidades.route('/utilidades/getusers')
@login_required
@check_roles(['dev'])
def utilidades_getusers():
    con = get_con()
    users = pglistdict(con, "select id,email,name,roles,auth from users")
    return jsonify(users=users)


@utilidades.route('/utilidades/editaruser', methods=['POST'])
@login_required
@check_roles(['dev'])
def utilidades_editaruser():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    upd = f"update users set name='{d['name']}', email='{d['email']}',\
    roles='{d['roles']}',auth={d['auth']} where id={d['id']}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        con.close()
        log(upd)
        return 'ok'


@utilidades.route('/utilidades/borraruser/<int:id>')
@login_required
@check_roles(['dev'])
def utilidades_borraruser(id):
    con = get_con()
    stm = f"delete from users where id={id}"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        con.close()
        log(stm)
        return 'ok'


@utilidades.route('/utilidades/variables')
@login_required
@check_roles(['dev'])
def utilidades_variables():
    return render_template('/utilidades/variables.html')


@utilidades.route('/utilidades/getdictvariables')
@login_required
@check_roles(['dev'])
def utilidades_getdictvariables():
    con = get_con()
    variables = pglistdict(con, f"select id,clave,valor from variables")
    return jsonify(variables=variables)


@utilidades.route('/utilidades/editarvariable' , methods=['POST'])
@login_required
@check_roles(['dev'])
def utilidades_editarvariable():
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    upd = f"update variables set clave='{d_data['clave']}', \
    valor='{d_data['valor']}' where id={d_data['id']}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        con.close()
        log(upd)
        return 'ok'


@utilidades.route('/utilidades/agregarvariable', methods=['POST'])
@login_required
@check_roles(['dev'])
def utilidades_agregarvariable():
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    ins = f"insert into variables(clave,valor) values('{d_data['clave']}',\
    '{d_data['valor']}')"
    cur = con.cursor()
    try:
        cur.execute(ins)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        con.close()
        log(ins)
        return 'ok'


@utilidades.route('/utilidades/borrarvariable/<int:id>')
@login_required
@check_roles(['dev'])
def utilidades_borrarvariable(id):
    con = get_con()
    stm = f"delete from variables where id={id}"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        con.close()
        log(stm)
        return 'ok'
