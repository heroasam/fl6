from flask import Blueprint,render_template,jsonify,make_response, request,send_file
from flask_login import login_required
from lib import *
import ast
from con import con
import re
from formularios import *

buscador = Blueprint('buscador',__name__)


@buscador.route('/')
@buscador.route('/buscador', methods = ['GET','POST'])
@login_required
def buscador_():
    return render_template("buscador.html")


@buscador.route('/buscador/<string:buscar>')
def buscar_cuenta(buscar):
    rcuenta = r'^[0-9]{5}$'
    rdni = r'^[0-9]{7,8}$'
    if (re.match(rcuenta,buscar)):
        clientes = pgdict(con,f"select dni,nombre,calle||' '||num,barrio,tel,wapp,clientes.zona,clientes.pmovto,deuda::integer,sev,incobrable,gestion,subirseven,novendermas,seguir,mudo,llamar,acla,horario,mjecobr,infoseven,sex,clientes.id as id from clientes,ventas where clientes.id=ventas.idcliente and ventas.id={buscar}")
    elif (re.match(rdni,buscar)):
        clientes = pgdict(con,f"select dni,nombre,calle,num,barrio,tel,wapp,zona,pmovto,deuda::integer,sev,incobrable,gestion,subirseven,novendermas,seguir,mudo,llamar,acla,horario,mjecobr,infoseven,sex,clientes.id as id from clientes where dni='{buscar}'")
    else:
        buscar = '%'+buscar.replace(' ','%')+'%'
        clientes = pgdict(con,f"select dni,nombre,calle||' '||num from clientes where nombre||calle||num||barrio ilike '{buscar}'")
    if len(clientes)==0:
        return make_response("No hay respuesta para esa busqueda",400)
    return jsonify(clientes=clientes)


@buscador.route('/buscador/pedirventas/<int:id>')
def buscar_ventas(id):
    ventas = pgdict(con,f"select id,fecha,cc,ic::integer,p,idvdor,saldo::integer,comprado::integer,pp,pcc,pic::integer,pper,devuelta,condonada,cnt,art,pagado::integer,primera,pprimera,ppagado from ventas where idcliente={id}")
    return jsonify(ventas=ventas)


@buscador.route('/buscador/pedircuotas/<string:dni>')
def buscar_cuotas(dni):
    idcliente = pgonecolumn(con,f"select id from clientes where dni='{dni}'")
    ventas = pgdict(con,f"select id from ventas where idcliente={idcliente} and saldo>0")
    cur = con.cursor()
    for v in ventas:
        cur.execute(f"select gc({v[0]})")
    cur.close()
    cuotas = pgdict(con, f"select nc,vto,ic::integer,idvta from cuotas where debe>0 and idcliente={idcliente} order by vto")
    pagadas = pgdict(con, f"select fecha,rbo,imp::integer,rec::integer,cobr from pagos where idcliente={idcliente} and \
             idvta in (select id from ventas where saldo>0) order by fecha desc")
    return jsonify(cuotas=cuotas,pagadas=pagadas)


@buscador.route('/buscador/pedirpagadas/<int:id>')
def buscador_pedirpagadas(id):
    pagadas = pgdict(con, f"select fecha,rbo,imp::integer,rec::integer,cobr from pagos where idcliente={id} order by fecha desc")
    return jsonify(pagadas=pagadas)


@buscador.route('/buscador/fecharpmovto/<string:dni>/<string:pmovto>')
def buscar_fecharpmovto(dni,pmovto):
    upd = f"update clientes set pmovto='{pmovto}' where dni='{dni}'"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return 'ok'


@buscador.route('/buscador/imprimirficha' , methods = ['POST'])
def buscar_imprimirficha():
    dni = ast.literal_eval(request.data.decode("UTF-8"))
    ficha(con,dni)
    return send_file('ficha.pdf')


@buscador.route('/buscador/datosultvta/<string:dni>')
def buscar_datosultvta(dni):
    idcliente = pgonecolumn(con,f"select id from clientes where dni='{dni}'")
    ultvta = pgdict(con,f"select fecha, (select max(art) from detvta where idvta=ventas.id) from ventas where idcliente={idcliente} order by id desc")
    return jsonify(ultvta=ultvta)


@buscador.route('/buscador/togglesube/<string:dni>')
def buscar_togglesube(dni):
    sube = pgonecolumn(con,f"select subirseven from clientes where dni='{dni}'")
    sev = pgonecolumn(con,f"select sev from clientes where dni='{dni}'")
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
        cur.close()
        return msg
    else:
        return 'No se sube pq ya esta en el seven'


@buscador.route('/buscador/togglegestion/<string:dni>')
def buscar_togglegestion(dni):
    sube = pgonecolumn(con,f"select gestion from clientes where dni='{dni}'")
    if sube:
        upd = f"update clientes set gestion=0 where dni='{dni}'"
        msg = "Registro desmarcado como Gestion"
    else:
        upd = f"update clientes set gestion=1 where dni='{dni}'"
        msg = "Registro marcado como Gestion"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return msg


@buscador.route('/buscador/togglemudado/<string:dni>')
def buscar_togglemudado(dni):
    sube = pgonecolumn(con,f"select mudo from clientes where dni='{dni}'")
    if sube:
        upd = f"update clientes set mudo=0 where dni='{dni}'"
        msg = "Registro desmarcado como Mudado"
    else:
        upd = f"update clientes set mudo=1 where dni='{dni}'"
        msg = "Registro marcado como Mudado"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return msg


@buscador.route('/buscador/toggleinc/<string:dni>')
def buscar_toggleinc(dni):
    sube = pgonecolumn(con,f"select incobrable from clientes where dni='{dni}'")
    if sube:
        upd = f"update clientes set incobrable=0 where dni='{dni}'"
        msg = "Registro desmarcado como Incobrable"
    else:
        upd = f"update clientes set incobrable=1 where dni='{dni}'"
        msg = "Registro marcado como Incobrable"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return msg


@buscador.route('/buscador/toggleln/<string:dni>')
def buscar_toggleln(dni):
    sube = pgonecolumn(con,f"select novendermas from clientes where dni='{dni}'")
    if sube:
        upd = f"update clientes set novendermas=0 where dni='{dni}'"
        msg = "Registro desmarcado como No Vender Mas"
    else:
        upd = f"update clientes set novendermas=1 where dni='{dni}'"
        msg = "Registro marcado como No Vender Mas"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return msg


@buscador.route('/buscador/togglellamar/<string:dni>')
def buscar_togglellamar(dni):
    sube = pgonecolumn(con,f"select llamar from clientes where dni='{dni}'")
    if sube:
        upd = f"update clientes set llamar=0 where dni='{dni}'"
    else:
        upd = f"update clientes set llamar=1 where dni='{dni}'"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return 'ok'


@buscador.route('/buscador/toggleseguir/<string:dni>')
def buscar_toggleseguir(dni):
    sube = pgonecolumn(con,f"select seguir from clientes where dni='{dni}'")
    if sube:
        upd = f"update clientes set seguir=0 where dni='{dni}'"
    else:
        upd = f"update clientes set seguir=1 where dni='{dni}'"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return 'ok'


@buscador.route('/buscador/gettablas')
def buscar_gettablas():
    calles = pglflat(con,f"select calle from calles order by calle")
    barrios = pglflat(con,f"select barrio from barrios order by barrio")
    zonas = pglflat(con,f"select zona from zonas order by zona")
    return jsonify(calles=calles,barrios=barrios,zonas=zonas)


@buscador.route('/buscador/getzonas')
def buscar_getzonas():
    zonas = pgdict(con,f"select zona from zonas order by zona")
    return jsonify(zonas=zonas)


@buscador.route('/buscador/editardatos/<string:dni>' , methods = ['POST'])
def busca_editardatos(dni):
    d = ast.literal_eval(request.data.decode("UTF-8"))
    upd = f"update clientes set sex='{d['sex']}', dni='{d['dni']}', nombre='{d['nombre']}', calle='{d['calle']}', num={d['num']}, barrio='{d['barrio']}', zona='{d['zona']}', tel='{d['tel']}', wapp={d['wapp']}, acla='{d['acla']}', mjecobr='{d['mjecobr']}', horario='{d['horario']}', infoseven='{d['infoseven']}' where dni='{dni}'"
    cur = con.cursor()
    cur.execute(upd)
    con.commit()
    cur.close()
    return 'ok'


@buscador.route('/buscador/pedircomentarios/<int:id>')
def buscar_pedircomentarios(id):
    comentarios=pgdict(con,f"select fechahora,comentario from comentarios where idcliente={id}")
    return jsonify(comentarios=comentarios)