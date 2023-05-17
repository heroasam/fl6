"""Modulo que concentra la mayoria de las funciones del sistema cobrador."""

import logging
import time
from flask_login import login_required, current_user
import mysql.connector
from flask import Blueprint, render_template, jsonify, make_response, request,\
send_file
import simplejson as json
from lib import pgonecolumn, pglistdict, send_msg_whatsapp, send_file_whatsapp,\
    pglist,  listsql, pgdict, pgexec
from con import get_con, log, check_roles
from formularios import ficha



cobrador = Blueprint('cobrador', __name__)


var_sistema = {}
def leer_variables():
    """Funcion para leer variables de sistema.

    Las variables estan ubicadas en la tabla variables con los campos clave,
    valor.
    Y seran incorporados en una variable  que es un dict."""

    con = get_con()
    variables = pglistdict(con, "select clave,valor from variables")
    for row in variables:
        var_sistema[row['clave']] = row['valor']
    return 1
leer_variables()

def get_cobr():
    return var_sistema[current_user.email]


@cobrador.route('/cobrador/listafichas')
@login_required
@check_roles(['dev','gerente','cobrador','vendedor'])
def cobrador_listafichas():
    """Muestra pagina lista de fichas."""
    return render_template('/cobrador/listafichas.html')


@cobrador.route('/cobrador/visitas')
@login_required
@check_roles(['dev','gerente','cobrador'])
def cobrador_visitas():
    """Muestra pagina lista de visitas."""
    return render_template('/cobrador/visitas.html')


@cobrador.route('/cobrador/tablero')
@login_required
@check_roles(['dev','gerente','cobrador'])
def cobrador_tablero():
    """Muestra pagina tablero de cobranzas."""
    return render_template('/cobrador/tablerocobranza.html')


@cobrador.route('/cobrador/planilla')
@login_required
@check_roles(['dev','gerente','cobrador','vendedor'])
def cobrador_planilla():
    """Muestra planilla de cobranza de cobrador para rendir."""
    return render_template('/cobrador/planillacobr.html')


@cobrador.route('/cobrador/planillageneral')
@login_required
@check_roles(['dev','gerente'])
def cobrador_planillageneral():
    """Muestra planilla de cobranza general para gerencia."""
    return render_template('/cobrador/planillageneral.html')


@cobrador.route('/cobrador/getlistadofichas')
@login_required
@check_roles(['dev','gerente','cobrador','vendedor'])
def cobrador_getlistadofichas():
    """Funcion que entrega lista fichas, lista zonas.

    Filtro mudados, fallecidos, fechados y cobrados.
    El filtro cobrados opera para los ultpago>-7dias y <hoy.
    Para que no se muestren los que pueden haber sido cobrados luego de la
    asignacion, pero si se muestren los cobrados en el dia de la fecha."""
    cobr = get_cobr()
    con = get_con()
    zonas = pglist(con, f"select clientes.zona as zona from clientes,zonas \
    where asignada=1 and asignado={cobr} and clientes.zona=zonas.zona \
    group by clientes.zona")
    fichas = pglistdict(con, f"select clientes.* from clientes,zonas where \
    asignada=1 and asignado={cobr} and clientes.zona=zonas.zona and \
    mudo=0 and clientes.zona!='-FALLECIDOS' and fechado=0 and ((datediff(now(),\
    ultpago) >6 or datediff(now(), ultpago) is null) or datediff(now(),\
    ultpago)=0) and deuda>0")
    fichasvdor = pglistdict(con, f"select clientes.* from clientes,ventas \
                            where ventas.idcliente=clientes.id and \
                            ventas.idvdor={cobr} and ventas.fecha=curdate()") 
    return jsonify(zonas=zonas, fichas=fichas, cobr=cobr, \
                   fichasvdor=fichasvdor)


@cobrador.route('/cobrador/fecharficha/<int:idcliente>/<pmovto>')
@login_required
@check_roles(['dev','gerente','cobrador','vendedor'])
def cobrador_fecharficha(idcliente,pmovto):
    """Proceso para fechar fichas por el cobrador.

    Hay un campo fechada en clientes que permite filtrarle al cobrador las
    fichas fechadas. Tambien registro en visitascobr."""
    con = get_con()
    upd = f"update clientes set pmovto='{pmovto}',fechado=1 where id=\
    {idcliente}"
    cobr = var_sistema[current_user.email]
    insvisita = f"insert into visitascobr(fecha,hora,cobr,idcliente,result)\
        values(curdate(),curtime(),{cobr},{idcliente},2)"
    cur = con.cursor()
    try:
        cur.execute(upd)
        cur.execute(insvisita)
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
@check_roles(['dev','gerente','cobrador','vendedor'])
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
@check_roles(['dev','gerente','cobrador','vendedor'])
def cobrador_mudoficha(idcliente):
    """Proceso para poner 'mudado' a la ficha por el cobrador."""
    con = get_con()
    cobr = var_sistema[current_user.email]
    ins = f"insert into visitascobr(fecha,hora,cobr,idcliente,result) \
    values(curdate(),curtime(),{cobr},{idcliente},4)"
    upd = f"update clientes set mudo=1,mudofallecio_proceso=1,asignada=0 where \
    id={idcliente}"
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
@check_roles(['dev','gerente','cobrador','vendedor'])
def cobrador_fallecioficha(idcliente):
    """Proceso para poner 'fallecido' a la ficha por el cobrador."""
    con = get_con()
    cobr = var_sistema[current_user.email]
    ins = f"insert into visitascobr(fecha,hora,cobr,idcliente,result) \
    values(curdate(),curtime(),{cobr},{idcliente},5)"
    upd = f"update clientes set zona='-FALLECIDOS',mudofallecio_proceso=1, \
    asignada=0 where id={idcliente}"
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


@cobrador.route('/cobrador/limpiar/<zona>')
@login_required
@check_roles(['dev','gerente','admin'])
def cobrador_limpiar(zona):
    con = get_con()
    upd = f"update clientes set asignada=0 where zona='{zona}'"
    pgexec(con, upd)
    con.close()
    return 'ok'


@cobrador.route('/cobrador/imprimirfichapantalla' , methods=['POST'])
@login_required
@check_roles(['dev','gerente','cobrador','vendedor'])
def cobrador_imprimirfichapantalla():
    """Funcion para imprimir ficha de cliente en pantalla a cobrador."""
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    idcliente = d['idcliente']
    dni = pgonecolumn(con, f"select dni from clientes where id={idcliente}")
    ficha(con, [dni])
    con.close()
    return send_file('/home/hero/ficha.pdf')


@cobrador.route('/cobrador/pasarpagos' , methods=['POST'])
@login_required
@check_roles(['dev','gerente','cobrador','vendedor'])
def cobrador_pasarpagos():
    """Sobre un pago exitosamente pagado registro la visita."""
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    idcliente = d['idcliente']
    monto = d['imp']
    cobr = var_sistema[current_user.email]
    ins = f"insert into visitascobr(fecha,hora,idcliente,result,cobr, \
        monto_cobrado) values(curdate(),curtime(),{idcliente},1,{cobr},\
            {monto})"
    try:
        pgexec(con, ins)
    except mysql.connector.Error as _error:
            con.rollback()
            error = _error.msg
            return make_response(error, 400)
    else:
            con.commit()
            return 'ok' 
    finally:
            con.close()


@cobrador.route('/cobrador/getvisitascobrador')
@login_required
@check_roles(['dev', 'gerente', 'cobrador'])
def cobrador_getvisitascobrador():
    """Funcion que entrega lista de visitas hechas por el cobrador."""
    con = get_con()
    visitascobrador = pglistdict(con, "select visitascobr.fecha as fecha,\
    cast(hora as char) as hora, visitascobr.cobr as cobr, result, \
    visitascobr.monto_cobrado as monto_cobrado, idcliente,nombre,calle,num,\
    clientes.zona as zona from visitascobr,clientes where clientes.id=\
    visitascobr.idcliente order by visitascobr.fecha desc,hora")

    fechasvisitas = pglistdict(con, "select fecha,cobr, count(*) as cnt, \
    sum(monto_cobrado) as monto_cobrado from visitascobr group by fecha,\
    cobr order by fecha,cobr desc")
    return jsonify(visitascobrador=visitascobrador, fechasvisitas=fechasvisitas)


@cobrador.route('/cobrador/getcobranzahoy')
@login_required
@check_roles(['dev','gerente','cobrador','vendedor'])
def cobrador_getcobranzahoy():
    """Funcion que entrega lista de las cobranza del dia para los cobradores."""
    con = get_con()
    cobranzahoy = pglistdict(con, "select fecha,imp+rec as imp, cobr, idvta,\
                             idcliente,rbo,rendido,dni,nombre,\
                             concat(calle,' ',num) as direccion, zona from \
                             pagos,clientes where clientes.id=idcliente and \
                             rendido=0 and fecha=curdate()")
    visitashoy = pglistdict(con, "select visitascobr.fecha as fecha,\
    cast(hora as char) as hora, visitascobr.cobr as cobr, result, \
    visitascobr.monto_cobrado as monto_cobrado, idcliente,\
    concat(calle,' ',num) as direccion from visitascobr,clientes where \
    clientes.id=visitascobr.idcliente and visitascobr.fecha=curdate() \
    order by visitascobr.hora")
    return jsonify(cobranzahoy=cobranzahoy,visitashoy=visitashoy)


@cobrador.route('/cobrador/getcobroscobr')
@login_required
@check_roles(['dev','gerente','cobrador','vendedor'])
def cobrador_getcobroscobr():
    con = get_con()
    cobr = get_cobr()
    listacobros = pglistdict(con, f"select * from pagos where cobr={cobr} \
                             and rendido=0")
    listafechas = pglistdict(con, f"select fecha,count(*) as cnt, sum(imp) \
                             as cobrado from pagos where cobr={cobr} \
                             and rendido = 0 group by fecha")
    return jsonify(listacobros=listacobros, listafechas=listafechas)


@cobrador.route('/cobrador/getcobroscobr/<int:cobr>')
@login_required
@check_roles(['dev','gerente'])
def cobrador_getcobroscobrgral(cobr):
    con = get_con()
    listacobros = pglistdict(con, f"select * from pagos where cobr={cobr} \
                             and rendido=0")
    listafechas = pglistdict(con, f"select fecha,count(*) as cnt, sum(imp) \
                             as cobrado from pagos where cobr={cobr} \
                             and rendido = 0 group by fecha")
    return jsonify(listacobros=listacobros, listafechas=listafechas)


@cobrador.route('/cobrador/getcobradores')
@login_required
@check_roles(['dev','gerente'])
def cobrador_getcobradores():
    con = get_con()
    cobradores = pglist(con, f"select id from cobr where activo=1 and \
                             prom=0 and vdor is NULL and id>15")
    return jsonify(cobradores=cobradores)


@cobrador.route('/cobrador/marcarpagadas/<int:cobr>')
@login_required
@check_roles(['dev','gerente'])
def cobrador_marcarpagadas(cobr):
    con = get_con()
    upd = f"update pagos set rendido=1 where cobr={cobr} and rendido=0"
    try:
        pgexec(con, upd)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        log(upd)
        return 'ok'
    finally:
        con.close()


@cobrador.route('/cobrador/marcarpagadasseleccionados', methods=['POST'])
@login_required
@check_roles(['dev','gerente'])
def cobrador_marcarpagadasseleccionados():
    """Proceso que marca pagadas las comisiones de un cobr en ciertos dias."""
    d_data = json.loads(request.data.decode("UTF-8"))
    cobr = d_data['cobr']
    fechas = d_data['fechas']
    lpg ='('
    for fecha in fechas:
        lpg+=f"'{str(fecha)}',"
    lpg = lpg[0:-1]+')'
    con = get_con()
    upd = f"update pagos set rendido=1 where cobr={cobr} and fecha in {lpg}"
    try:
        pgexec(con, upd)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        log(upd)
        return 'ok'
    finally:
        con.close()