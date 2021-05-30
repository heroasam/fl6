from flask import Blueprint,render_template,jsonify,make_response, request, send_file
from flask_login import login_required
from lib import *
import ast
from con import con
from formularios import *

fichas = Blueprint('fichas',__name__)

@fichas.route('/fichas')
def fichas_():
    return render_template("fichas/fichaje.html")


@fichas.route('/fichas/getcobradores')
def fichas_getcobradores():
    cobradores = pgdict(con,f"select id from cobr where activo=1 and prom=0 and id>15")
    return jsonify(cobradores=cobradores)


@fichas.route('/fichas/muestrazonas/<int:cobr>')
def fichas_muestrazona(cobr):
    zonas = pgdict(con,f"select zona from zonas where asignado={cobr}")
    return jsonify(zonas=zonas)


@fichas.route('/fichas/muestraclientes/<string:tipo>/<string:zona>')
def fichas_muestraclientes(tipo,zona):
    if tipo=='normales':
        clientes = pgdict(con,f"select nombre,calle,num,ultpago,pmovto,sev,novendermas,gestion,mudo,incobrable,dni,subirseven,comprado::integer,deuda::integer,zona,barrio from clientes where zona='{zona}' and ultpago>now()-interval '12 month' and deuda>0  and gestion=0 and incobrable=0 and mudo=0 order by pmovto")
    elif tipo=='gestion':
        clientes = pgdict(con,f"select nombre,calle,num,ultpago,pmovto,sev,novendermas,gestion,mudo,incobrable,dni,subirseven,comprado::integer,deuda::integer,zona,barrio from clientes where zona='{zona}' and ultpago>now()-interval '12 month' and deuda>0  and (gestion=1 or incobrable=1 or mudo=1) order by pmovto")
    elif tipo=='antiguos':
        clientes = pgdict(con,f"select nombre,calle,num,ultpago,pmovto,sev,novendermas,gestion,mudo,incobrable,dni,subirseven,comprado::integer,deuda::integer,zona,barrio from clientes where zona='{zona}' and ultpago<=now()-interval '12 month' and deuda>0  order by ultpago desc")
    return jsonify(clientes=clientes)


@fichas.route('/fichas/imprimir', methods = ['POST'])
def fichas_imprimir():
    listadni = ast.literal_eval(request.data.decode("UTF-8"))
    # aca se el ast.literal entrega la lista enviada por el axios-post directamente

    ficha(con, listadni)
    return send_file('ficha.pdf')


@fichas.route('/fichas/cambiarzona/<string:zona>',methods=['POST'])
def fichas_cambiarzona(zona):
    listadni = ast.literal_eval(request.data.decode("UTF-8"))
    lpg ='('
    for dni in listadni:
        lpg+="'"+dni+"'"+","
    lpg = lpg[0:-1]+")"
    upd = f"update clientes set zona='{zona}' where dni in {lpg}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except psycopg2.Error as e:
        con.rollback()
        error = e.pgerror
        return make_response(error,400)
    else:
        con.commit()
        cur.close()
        return 'OK'


@fichas.route('/fichas/cobradores')
def fichas_cobradores():
    return render_template('fichas/cobr.html')


@fichas.route('/fichas/getfullcobradores')
def fichas_getfullcobradores():
    cobradores = pgdict(con,f"select id,dni,nombre,direccion,telefono,fechanac,desde,activo,prom from cobr order by id desc")
    return jsonify(cobradores=cobradores)


@fichas.route('/fichas/toggleactivo/<int:id>')
def fichas_toggleactivo(id):
    activo = pgonecolumn(con, f"select activo from cobr where id={id}")
    if activo:
        upd = f"update cobr set activo=0 where id={id}"
    else:
        upd = f"update cobr set activo=1 where id={id}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except psycopg2.Error as e:
        con.rollback()
        error = e.pgerror
        return make_response(error,400)
    else:
        con.commit()
        cur.close()
        return 'OK'


@fichas.route('/fichas/toggleprom/<int:id>')
def fichas_toggleprom(id):
    prom = pgonecolumn(con, f"select prom from cobr where id={id}")
    if prom:
        upd = f"update cobr set prom=0 where id={id}"
    else:
        upd = f"update cobr set prom=1 where id={id}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except psycopg2.Error as e:
        con.rollback()
        error = e.pgerror
        return make_response(error,400)
    else:
        con.commit()
        cur.close()
        return 'OK'


@fichas.route('/fichas/borrarcobrador/<int:id>')
def fichas_borrarcobrador(id):
    stm = f"delete from cobr where id={id}"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except psycopg2.Error as e:
        con.rollback()
        error = e.pgerror
        return make_response(error,400)
    else:
        con.commit()
        cur.close()
        return 'OK'


@fichas.route('/fichas/getcobradorbyid/<int:id>')
def fichas_getcobradorbyid(id):
    cobrador = pgdict(con, f"select id,dni,nombre,direccion,telefono,fechanac, desde, activo,prom from cobr where id={id}")
    return jsonify(cobrador=cobrador)


@fichas.route('/fichas/guardarcobrador' , methods=['POST'])
def fichas_guardarcobrador():
    d = ast.literal_eval(request.data.decode("UTF-8"))
    if d['id']!='':
        stm = f"update cobr set dni='{d['dni']}', nombre='{d['nombre']}', direccion='{d['direccion']}', telefono='{d['telefono']}', fechanac='{d['fechanac']}', desde='{d['desde']}', activo={d['activo']}, prom={d['prom']} where id= {d['id']}"
    else:
        stm = f"insert into cobr(dni,nombre, direccion, telefono, fechanac,desde,activo,prom) values('{d['dni']}','{d['nombre']}','{d['direccion']}','{d['telefono']}','{d['fechanac']}', '{d['desde']}', {d['activo']}, {d['prom']})"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except psycopg2.Error as e:
        con.rollback()
        error = e.pgerror
        return make_response(error,400)
    else:
        con.commit()
        cur.close()
        return 'OK'


@fichas.route('/fichas/fechador')
def fichas_fechador():
    return render_template('fichas/fechador.html')


@fichas.route('/fichas/buscacuenta/<int:idvta>')
def fichas_buscacuenta(idvta):
    cuenta = pgdict(con, f"select nombre, clientes.pmovto from clientes, ventas where clientes.id=ventas.idcliente and ventas.id={idvta}")
    return jsonify(cuenta=cuenta)


@fichas.route('/fichas/guardarfechado/<int:idvta>/<string:pmovto>')
def fichas_guardarfechado(idvta,pmovto):
    idcliente = pgonecolumn(con, f"select idcliente from ventas where id={idvta}")
    upd = f"update clientes set pmovto='{pmovto}' where id = {idcliente}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except psycopg2.Error as e:
        con.rollback()
        error = e.pgerror
        return make_response(error,400)
    else:
        con.commit()
        cur.close()
        return 'OK'