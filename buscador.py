from flask import Blueprint,render_template,jsonify,make_response, request,send_file
from flask_login import login_required
from .lib import *
import simplejson as json
import re
from .formularios import *
from .con import get_con, log

buscador = Blueprint('buscador',__name__)



@buscador.route('/')
@buscador.route('/buscador', methods = ['GET','POST'])
@login_required
def buscador_():
    return render_template("buscador/buscar.html")


@buscador.route('/buscador/<string:buscar>')
def buscar_cuenta(buscar):
    con = get_con()
    rcuenta = r'^[0-9]{5}$'
    rdni = r'^[0-9]{7,8}$'
    if (re.match(rcuenta,buscar)):
        cur = con.cursor()
        cur.execute(f'select idcliente from ventas where id={buscar}')
        idcliente = cur.fetchone()[0]
        sql = f"select * from clientes where id={idcliente}"
    elif (re.match(rdni,buscar)):
        sql = f"select * from clientes where dni='{buscar}'"
    else:
        buscar = '%'+buscar.replace(' ','%')+'%'
        sql = f"select * from clientes where lower(concat(nombre,calle,num,barrio)) like lower('{buscar}')"
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    clientes = cur.fetchall()
    if len(clientes)==0:
        return make_response("No hay respuesta para esa busqueda",400)
    con.close()
    return jsonify(clientes=clientes)


@buscador.route('/buscador/clientesdireccion/<string:calle>/<string:num>')
def clientesdireccion(calle,num):
    con = get_con()
    cur = con.cursor(dictionary=True)
    cur.execute(f"select * from clientes where calle='{calle}' and num='{num}'")
    clientes = cur.fetchall()
    con.close()
    return jsonify(clientes=clientes)




@buscador.route('/buscador/pedirpagadasporidcliente/<int:idcliente>')
def buscar_pedirpagadasporidcliente(idcliente):
    sql = f"select * from pagos where idcliente={idcliente} order by id desc"
    con = get_con()
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    pagadas = cur.fetchall()
    con.close()
    return jsonify(pagadas=pagadas)


@buscador.route('/buscador/obtenerventasporidcliente/<int:idcliente>')
def buscar_obtenerventasporidcliente(idcliente):
    sql = f"select * from ventas where idcliente={idcliente} and saldo>0 order by id desc"
    con = get_con()
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    ventas = cur.fetchall()
    con.close()
    return jsonify(ventas=ventas)


@buscador.route('/buscador/pedircomentarios/<int:idcliente>')
def buscar_pedircomentarios(idcliente):
    sql = f"select fechahora,comentario from comentarios where idcliente={idcliente}"
    con = get_con()
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    comentarios = cur.fetchall()
    con.close()
    return jsonify(comentarios=comentarios)


@buscador.route('/buscador/guardarcomentario/<int:idcliente>', methods=['POST'])
def buscar_guardarcomentario(idcliente):
    d = json.loads(request.data.decode("UTF-8"))
    ins = f"insert into comentarios(idcliente,fechahora,comentario) values({idcliente},'{d['fechahora']}','{d['comentario']}')"
    con = get_con()
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    log(ins)
    con.close()
    return 'ok'


@buscador.route('/buscador/pedirlogcambiodireccion/<int:idcliente>')
def buscar_logcambiodireccion(idcliente):
    sql = f"select fecha,calle,num,wapp,acla from logcambiodireccion where idcliente={idcliente}"
    con = get_con()
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    logcambiodireccion = cur.fetchall()
    con.close()
    return jsonify(logcambiodireccion=logcambiodireccion)


@buscador.route('/buscador/obtenerventascanceladasporidcliente/<int:idcliente>')
def buscar_obtenerventascanceladasporidcliente(idcliente):
    sql = f"select * from ventas where idcliente={idcliente} and saldo=0 order by id desc"
    con = get_con()
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    ventascanceladas = cur.fetchall()
    con.close()
    return jsonify(ventascanceladas=ventascanceladas)


@buscador.route('/buscador/guardarpmovto/<int:idcliente>/<string:pmovto>')
def buscar_guardarpmovto(idcliente,pmovto):
    con = get_con()
    sql = f"update clientes set pmovto='{pmovto}' where id={idcliente}"
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    log(sql)
    con.close()
    return 'ok'


@buscador.route('/buscador/imprimirficha' , methods = ['POST'])
def buscar_imprimirficha():
    con = get_con()
    dni = json.loads(request.data.decode("UTF-8"))
    ficha(con,dni)
    con.close()
    return send_file('/tmp/ficha.pdf')


@buscador.route('/buscador/togglesube/<string:dni>')
def buscar_togglesube(dni):
    con = get_con()
    selsube = f"select subirseven from clientes where dni='{dni}'"
    selsev = f"select sev from clientes where dni='{dni}'"
    sube = pgonecolumn(con, selsube)
    sev = pgonecolumn(con, selsev)
    if sev==0:
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
        msg =  'No se sube pq ya esta en el seven'
        return jsonify(msg=msg)


@buscador.route('/buscador/togglegestion/<string:dni>')
def buscar_togglegestion(dni):
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
def buscar_togglemudado(dni):
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
        return make_response("un error se ha producido",400)
    else:
        con.commit()
        log(upd)
        cur.close()
        con.close()
        return jsonify(msg=msg)


@buscador.route('/buscador/toggleinc/<string:dni>')
def buscar_toggleinc(dni):
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
def buscar_togglenvm(dni):
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
def buscar_togglellamar(dni):
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
def buscar_toggleseguir(dni):
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


@buscador.route('/buscador/guardaredicioncliente/<int:idcliente>' , methods = ['POST'])
def busca_guardaredicioncliente(idcliente):
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    cliente_viejo = pgdict(con, f"select * from clientes where id={d['id']}")[0]    
    upd = f"update clientes set sex='{d['sex']}', dni='{d['dni']}', nombre='{d['nombre']}', calle='{d['calle']}', num={d['num']}, barrio='{d['barrio']}', zona='{d['zona']}', tel='{d['tel']}', wapp='{d['wapp']}', acla='{d['acla']}', mjecobr='{d['mjecobr']}', horario='{d['horario']}', infoseven='{d['infoseven']}' where id={idcliente}"
    cur = con.cursor()
    cur.execute(upd)
    log(upd)
    con.commit()
    ins = f"insert into logcambiodireccion(idcliente,calle,num,barrio,tel,acla,fecha,nombre,dni,wapp) values({cliente_viejo['id']},'{cliente_viejo['calle']}','{cliente_viejo['num']}','{cliente_viejo['barrio']}','{cliente_viejo['tel']}','{cliente_viejo['acla']}',curdate(),'{cliente_viejo['nombre']}','{cliente_viejo['dni']}','{cliente_viejo['wapp']}')"
    if cliente_viejo['calle']!=d['calle'] or cliente_viejo['num']!=d['num'] or cliente_viejo['acla']!=d['acla'] or cliente_viejo['wapp']!=d['wapp']:
        cur.execute(ins)
        con.commit()
        log(ins)
    con.close()
    return 'ok'


@buscador.route('/buscador/obtenerlistacalles')
def buscar_obtenerlistacalles():
    con = get_con()
    sql = f"select calle from calles order by calle"
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    calles = cur.fetchall()
    con.close()
    return jsonify(calles=calles)


@buscador.route('/buscador/obtenerlistabarrios')
def buscar_obtenerlistabarrios():
    con = get_con()
    sql = f"select barrio from barrios order by barrio"
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    barrios = cur.fetchall()
    con.close()
    return jsonify(barrios=barrios)



@buscador.route('/buscador/obtenerlistazonas')
def buscar_obtenerlistazonas():
    con = get_con()
    sql = f"select zona from zonas order by zona"
    cur = con.cursor(dictionary=True)
    cur.execute(sql)
    zonas = cur.fetchall()
    con.close()
    return jsonify(zonas=zonas)


@buscador.route('/buscador/generarplandepagos/<int:idcliente>', methods=['POST'])
def buscar_generarplandepagos(idcliente):
    d = json.loads(request.data.decode("UTF-8"))
    upd = f"update ventas set saldo=0, pcondo=1 where idcliente={idcliente} and saldo>0"
    con = get_con()
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    log(upd)
    ins = f"insert into ventas(fecha,cc,ic,p,primera,pp,idvdor,idcliente) values('{d['fecha']}',{d['cc']},{d['ic']},{d['p']},'{d['primera']}',1,10,{idcliente})"
    cur.execute(ins)
    con.commit()
    log(ins)
    con.close()
    return 'ok'


@buscador.route('/buscador/intimar', methods=['POST'])
def buscador_intimar():
    con = get_con()
    dni = json.loads(request.data.decode("UTF-8"))
    intimacion(con,dni)
    return send_file('/tmp/intimacion.pdf')


@buscador.route('/log')
@login_required
def buscador_log():
    return render_template('buscador/log.html')


@buscador.route('/buscador/obtenerlogs')
def buscador_obtenerlogs():
    con = get_con()
    logs = pgdict(con, f"select * from log order by id desc limit 1000")
    con.close()
    return jsonify(logs=logs)


@buscador.route('/buscador/cargarasunto' , methods=['POST'])
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