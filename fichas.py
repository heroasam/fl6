from flask import Blueprint,render_template,jsonify,make_response, request, send_file
from flask_login import login_required
from .lib import *
import simplejson as json
from .con import get_con, log
from .formularios import *
import mysql.connector

fichas = Blueprint('fichas',__name__)

@fichas.route('/fichas')
@login_required
def fichas_():
    return render_template("fichas/fichaje.html")


@fichas.route('/fichas/getcobradores')
def fichas_getcobradores():
    con = get_con()
    cobradores = pgdict(con,f"select id from cobr where activo=1 and prom=0 and id>15")
    con.close()
    return jsonify(cobradores=cobradores)


@fichas.route('/fichas/muestrazonas/<int:cobr>')
def fichas_muestrazona(cobr):
    con = get_con()
    zonas = pgdict(con,f"select zona from zonas where asignado={cobr}")
    con.close()
    return jsonify(zonas=zonas)


@fichas.route('/fichas/muestraclientes/<string:tipo>/<string:zona>')
def fichas_muestraclientes(tipo,zona):
    con = get_con()
    if tipo=='normales':
        clientes = pgdict(con,f"select nombre,calle,num,ultpago,pmovto,sev,novendermas,gestion,mudo,incobrable,dni,subirseven,comprado,deuda,zona,barrio from clientes where zona='{zona}' and ultpago>date_sub(curdate(),interval 365 day) and deuda>0  and gestion=0 and incobrable=0 and mudo=0 order by pmovto")
    elif tipo=='gestion':
        clientes = pgdict(con,f"select nombre,calle,num,ultpago,pmovto,sev,novendermas,gestion,mudo,incobrable,dni,subirseven,comprado,deuda,zona,barrio from clientes where zona='{zona}' and ultpago>date_sub(curdate(),interval 365 day) and deuda>0  and (gestion=1 or incobrable=1 or mudo=1) order by pmovto")
    elif tipo=='antiguos':
        clientes = pgdict(con,f"select nombre,calle,num,ultpago,pmovto,sev,novendermas,gestion,mudo,incobrable,dni,subirseven,comprado,deuda,zona,barrio from clientes where zona='{zona}' and ultpago<=date_sub(curdate(),interval 365 day) and deuda>0  order by ultpago desc")
    con.close()
    return jsonify(clientes=clientes)


@fichas.route('/fichas/imprimir', methods = ['POST'])
def fichas_imprimir():
    con = get_con()
    listadni = json.loads(request.data.decode("UTF-8"))
    # aca se el ast.literal entrega la lista enviada por el axios-post directamente

    ficha(con, listadni)
    con.close()
    return send_file('/tmp/ficha.pdf')


@fichas.route('/fichas/intimar', methods = ['POST'])
def fichas_intimar():
    con = get_con()
    listadni = json.loads(request.data.decode("UTF-8"))
    # aca se el ast.literal entrega la lista enviada por el axios-post directamente

    intimacion(con, listadni)
    con.close()
    return send_file('/tmp/intimacion.pdf')


@fichas.route('/fichas/cambiarzona/<string:zona>',methods=['POST'])
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
def fichas_cobradores():
    return render_template('fichas/cobr.html')


@fichas.route('/fichas/getfullcobradores')
def fichas_getfullcobradores():
    con = get_con()
    cobradores = pgdict(con,f"select id,dni,nombre,direccion,telefono,fechanac,desde,activo,prom from cobr order by id desc")
    con.close()
    return jsonify(cobradores=cobradores)


@fichas.route('/fichas/toggleactivo/<int:id>')
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


@fichas.route('/fichas/borrarcobrador/<int:id>')
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
def fichas_getcobradorbyid(id):
    con = get_con()
    cobrador = pgdict(con, f"select id,dni,nombre,direccion,telefono,fechanac, desde, activo,prom from cobr where id={id}")[0]
    con.close()
    return jsonify(cobrador=cobrador)


@fichas.route('/fichas/guardarcobrador' , methods=['POST'])
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
def fichas_fechador():
    return render_template('fichas/fechador.html')


@fichas.route('/fichas/buscacuenta/<int:idvta>')
def fichas_buscacuenta(idvta):
    con = get_con()
    cuenta = pgdict(con, f"select nombre, clientes.pmovto as pmovto,asignado from clientes, ventas,zonas where clientes.id=ventas.idcliente and clientes.zona=zonas.zona and ventas.id={idvta}")[0]
    con.close()
    return jsonify(cuenta=cuenta)


@fichas.route('/fichas/guardarfechado/<int:idvta>/<string:pmovto>')
def fichas_guardarfechado(idvta,pmovto):
    con = get_con()
    idcliente = pgonecolumn(con, f"select idcliente from ventas where id={idvta}")
    upd = f"update clientes set pmovto='{pmovto}' where id = {idcliente}"
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


@fichas.route('/fichas/listado')
def fichas_listado():
    return render_template('fichas/listado.html')


@fichas.route('/fichas/getzonas')
def fichas_getzonas():
    con = get_con()
    zonas = pglflat(con,f"select zona from zonas where asignado>700 and asignado !=820 order by zona")
    con.close()
    return jsonify(zonas=zonas)


@fichas.route('/fichas/getlistado/<string:zona>')
def fichas_getlistado(zona):
    con = get_con()
    listado = pgdict(con, f"select date_format(ultpago,'%Y') as year, ultpago, dni,nombre, concat(calle,' ',num) as direccion from clientes where zona='{zona}' and deuda=0 and incobrable=0 and mudo=0 and gestion=0 and novendermas=0 and comprado>0 and ultpago>'2010-01-01' and concat(calle,num) not in (select concat(calle,num) from clientes where deuda>300) order by ultpago desc")
    con.close()
    return jsonify(listado=listado)


@fichas.route('/fichas/getresumen/<string:zona>')
def fichas_getresumen(zona):
    con = get_con()
    resumen = pgdict(con, f"select date_format(ultpago,'%Y') as y, count(*) as cnt from clientes where zona='{zona}' and deuda=0 and incobrable=0 and mudo=0 and gestion=0 and novendermas=0 and ultpago>'2010-01-01' group by y order by y")
    # print(resumen)
    con.close()
    return jsonify(resumen=resumen)


@fichas.route('/fichas/imprimirlistado', methods=['POST'])
def fichas_imprimirlistado():
    con = get_con()
    listadni = json.loads(request.data.decode("UTF-8"))
    listado(con, listadni)
    # print(len(listadni))
    con.close()
    return send_file('/tmp/listado.pdf')
