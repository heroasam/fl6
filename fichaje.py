from flask import Blueprint,render_template,jsonify,make_response, request, send_file
from flask_login import login_required
from lib import *
import ast
from con import con
from formularios import *

fichaje = Blueprint('fichaje',__name__)

@fichaje.route('/fichaje')
def fichaje_():
    return render_template("fichaje.html")


@fichaje.route('/fichaje/getcobradores')
def fichaje_getcobradores():
    cobradores = pgdict(con,f"select id from cobr where activo=1 and prom=0 and id>15")
    return jsonify(cobradores=cobradores)


@fichaje.route('/fichaje/muestrazonas/<int:cobr>')
def fichaje_muestrazona(cobr):
    zonas = pgdict(con,f"select zona from zonas where asignado={cobr}")
    return jsonify(zonas=zonas)


@fichaje.route('/fichaje/muestraclientes/<string:tipo>/<string:zona>')
def fichaje_muestraclientes(tipo,zona):
    if tipo=='normales':
        clientes = pgdict(con,f"select nombre,calle,num,ultpago,pmovto,sev,novendermas,gestion,mudo,incobrable,dni,subirseven,comprado::integer,deuda::integer,zona,barrio from clientes where zona='{zona}' and ultpago>now()-interval '12 month' and deuda>0  and gestion=0 and incobrable=0 and mudo=0 order by pmovto")
    elif tipo=='gestion':
        clientes = pgdict(con,f"select nombre,calle,num,ultpago,pmovto,sev,novendermas,gestion,mudo,incobrable,dni,subirseven,comprado::integer,deuda::integer,zona,barrio from clientes where zona='{zona}' and ultpago>now()-interval '12 month' and deuda>0  and (gestion=1 or incobrable=1 or mudo=1) order by pmovto")
    elif tipo=='antiguos':
        clientes = pgdict(con,f"select nombre,calle,num,ultpago,pmovto,sev,novendermas,gestion,mudo,incobrable,dni,subirseven,comprado::integer,deuda::integer,zona,barrio from clientes where zona='{zona}' and ultpago<=now()-interval '12 month' and deuda>0  order by ultpago desc")
    return jsonify(clientes=clientes)


@fichaje.route('/fichaje/imprimir', methods = ['POST'])
def fichaje_imprimir():
    listadni = ast.literal_eval(request.data.decode("UTF-8"))
    # aca se el ast.literal entrega la lista enviada por el axios-post directamente

    ficha(con, listadni)
    return send_file('ficha.pdf')
