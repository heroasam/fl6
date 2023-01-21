from flask_login import login_required, current_user
import mysql.connector
from flask import Blueprint, render_template, jsonify, make_response, request,\
    send_file, redirect, url_for
import simplejson as json
from lib import pgonecolumn, pgdict, send_msg_whatsapp, send_file_whatsapp, \
    pglflat, log_busqueda, listsql, pgdict1
from con import get_con, log, check_roles
import logging

vendedor = Blueprint('vendedor', __name__)


var_sistema = {}
def leer_variables():
    """Funcion para leer variables de sistema.

    Las variables estan ubicadas en la tabla variables con los campos keys,value.
    Y seran incorporados en una variable global var_sistema que es un dict."""
    global var_sistema
    con = get_con()
    variables = pgdict(con, f"select clave,valor from variables")
    for row in variables:
        var_sistema[row['clave']] = row['valor']
    return 1


leer_variables()


def calculo_cuota_maxima(idcliente):
    """Funcion que calcula la cuota maxima vendible del cliente.

    Busca la cuota maxima de los ultimos tres años y la actualiza por inflacion
    le disminuye 5% por cada mes de atraso que haya tenido
    le aumenta 5% por cada compra que haya tenido en los ultimos tres años.
    Esto ultimo se suspende pq aumenta mucho la cuota por la gran inflacion que
    hay.
    Cambios: se saco el incremento por cantidad de ventas.
    Se toman las ventas de los ultimos tres años canceladas o no, y se actualizan
    luego se pone la cuota actualizada mas alta.
    Tambien se tiene en cuenta el monto total de la venta/6 para el calculo de la
    cuota para evitar distorsion si el plan fue en 4 o 5 cuotas.
    """
    con = get_con()
    cuotas = pgdict(con, f"select comprado as monto,date_format(fecha,'%Y%c') \
    as fecha from ventas where idcliente={idcliente} and fecha>\
    date_sub(curdate(),interval 3 year) and devuelta=0")
    if cuotas:
        ultimo_valor = pgonecolumn(con, "select indice from inflacion order \
            by id desc limit 1")
        cuotas_actualizadas = []
        for venta in cuotas:
            cuota = venta['monto']/6
            fecha = venta['fecha']
            indice = pgonecolumn(con, f"select indice from inflacion \
            where concat(year,month)='{fecha}'")
            actualizada = ultimo_valor/indice * cuota
            cuotas_actualizadas.append(actualizada)
        cuota_actualizada = max(cuotas_actualizadas)

        atraso = pgonecolumn(con, f"select atraso from clientes where id={idcliente}")
        if atraso is None:
            atraso = 0
        if atraso>0:
            cuota_actualizada = cuota_actualizada * (1-(atraso/30)*0.05)
            if cuota_actualizada < 0:
                cuota_actualizada = 0
        return cuota_actualizada
    else:
        return 0


def calculo_sin_extension(idcliente):
    """Determina si a un cliente se le puede ofrecer automaticamente extension.

    de la cuota_maxima. Toma los parametros: cantidad de ventas: 1 venta no,
    atrasos>60 en ultimos 3 años no.
    Return 1 negativo sin_extension. 0 positivo se puede ofrecer extension."""

    con = get_con()
    cnt_vtas = pgonecolumn(con, f"select count(*) from ventas where saldo=0 \
    and idcliente = {idcliente}")
    if cnt_vtas==1:
        return 1
    atraso = pgonecolumn(con, f"select atraso from clientes where id={idcliente}")
    if atraso and atraso>60:
        return 1
    return 0


@vendedor.route('/vendedor/guardardato', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def vendedor_guardardato():
    global var_sistema
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    cuota_maxima = calculo_cuota_maxima(d['idcliente'])
    sin_extension = calculo_sin_extension(d['idcliente'])
    # if cuota_maxima==0 or cuota_maxima<float(d['cuota_maxima']):
    if cuota_maxima < float(var_sistema['cuota_basica']):
        cuota_maxima = var_sistema['cuota_basica']
    direccion_cliente = pgonecolumn(con, f"select concat(calle,num) from \
    clientes where id={d['idcliente']}")
    deuda_en_la_casa = pgonecolumn(con, f"select sum(deuda) from clientes \
    where concat(calle,num)='{direccion_cliente}' and id!={d['idcliente']}")
    es_garante = pgonecolumn(con, f"select esgarante from clientes where id=\
    {d['idcliente']}")
    if es_garante:
        dni = pgonecolumn(con, f"select dni from clientes where id=\
        {d['idcliente']}")
        monto_garantizado = pgonecolumn(con, f"select sum(saldo) from ventas \
        where garantizado=1 and dnigarante={dni}")
    else:
        monto_garantizado = 0
    if deuda_en_la_casa is None:
        deuda_en_la_casa = 0
    ins = f"insert into datos(fecha, user, idcliente, fecha_visitar, art,\
    horarios, comentarios, cuota_maxima,deuda_en_la_casa,sin_extension,\
    monto_garantizado) values ('{d['fecha']}', '{d['user']}',\
    {d['idcliente']},'{d['fecha_visitar']}','{d['art']}','{d['horarios']}',\
    '{d['comentarios']}', {cuota_maxima}, '{deuda_en_la_casa}',{sin_extension},\
    {monto_garantizado})"
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


@vendedor.route('/vendedor/togglerechazardato/<int:id>')
@login_required
@check_roles(['dev','gerente'])
def vendedor_togglerechazardato(id):
    con = get_con()
    resultado = pgonecolumn(con, f"select resultado from datos where id={id}")
    if resultado == 8: # o sea ya esta rechazado
        upd = f"update datos set resultado=NULL, rechazado=0 where id={id}"
        updaut = f"update autorizacion set rechazado=0,autorizado=0 where iddato={id}"
    elif resultado is None: # o sea se puede rechazar
        upd = f"update datos set resultado=8,rechazado=1 where id={id}"
        updaut = f"update autorizacion set rechazado=1,autorizado=0 where iddato={id}"
    else:
        return make_response("error", 400)
    cur = con.cursor()
    try:
        cur.execute(upd)
        cur.execute(updaut)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        con.close()
        log(upd)
        log(updaut)
        return 'ok'


@vendedor.route('/vendedor/getlistadodatos')
@login_required
@check_roles(['dev','gerente','admin'])
def vendedor_getlistadodatos():
    global var_sistema
    con = get_con()
    listadodatos = pgdict(con, "select datos.id, fecha, user,fecha_visitar,\
    art, horarios, comentarios,  dni, nombre, resultado,monto_vendido, \
    cuota_maxima, novendermas, incobrable, sev, baja, deuda_en_la_casa, \
    sin_extension, autorizado from datos, clientes where clientes.id = \
    datos.idcliente order by id desc limit 300")
    # vendedor is null filtra los datos no asignados
    cuotabasica = var_sistema['cuota_basica']
    vdores = pglflat(con, "select id from cobr where vdor=1 and activo=1")
    return jsonify(listadodatos=listadodatos, cuotabasica=cuotabasica, \
                   vdores=vdores)


@vendedor.route('/vendedor/getlistadodatosenviar')
@login_required
@check_roles(['dev','gerente','admin'])
def vendedor_getlistadodatosenviar():
    global var_sistema
    con = get_con()
    listadodatos = pgdict(con, "select datos.id, fecha, user,fecha_visitar,\
    art, horarios, comentarios,  dni, nombre, resultado,monto_vendido, \
    cuota_maxima, novendermas, incobrable, sev, baja, deuda_en_la_casa, \
    sin_extension, autorizado, monto_garantizado from datos, clientes where \
    clientes.id = datos.idcliente and enviado_vdor=0 and rechazado=0 \
    order by id desc limit 300")
    # vendedor is null filtra los datos no asignados
    cuotabasica = var_sistema['cuota_basica']
    vdores = pglflat(con, "select id from cobr where vdor=1 and activo=1")
    return jsonify(listadodatos=listadodatos, cuotabasica=cuotabasica, \
                   vdores=vdores)


@vendedor.route('/vendedor/getlistadodatosenviados')
@login_required
@check_roles(['dev','gerente'])
def vendedor_getlistadodatosenviados():
    global var_sistema
    con = get_con()
    listadodatos = pgdict(con, "select datos.id, fecha, user,fecha_visitar,\
    art, horarios, comentarios,  dni, nombre, resultado,monto_vendido,autorizado, \
    cuota_maxima, novendermas, incobrable, sev, baja, deuda_en_la_casa, \
    vendedor, autorizado from datos, clientes where clientes.id = \
    datos.idcliente and enviado_vdor=1 order by id desc")
    # vendedor is null filtra los datos no asignados
    cuotabasica = var_sistema['cuota_basica']
    vdores = pglflat(con, "select id from cobr where vdor=1 and activo=1")
    print(vdores)
    return jsonify(listadodatos=listadodatos, cuotabasica=cuotabasica, \
                   vdores=vdores)


@vendedor.route('/vendedor/asignardatosvendedor', methods=['POST'])
@login_required
@check_roles(['dev','gerente'])
def vendedor_asignardatosvendedor():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    ids = listsql(d['ids'])
    upd = f"update datos set vendedor = {d['vendedor']},enviado_vdor=1 \
    where id in {ids}"
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
        return 'ok'


@vendedor.route('/vendedor/ingresardatoyasignardatosvendedor', methods=['POST'])
@login_required
@check_roles(['dev','gerente'])
def vendedor_ingresardatoyasignardatosvendedor():
    global var_sistema
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    ids = d['ids']
    cur = con.cursor()
    try:
        for dni in ids:
            idcliente = pgonecolumn(con, f"select id from clientes where dni=\
            {dni}")
            cuota_maxima = calculo_cuota_maxima(idcliente)
            sin_extension = calculo_sin_extension(idcliente)
            cuotabasica = var_sistema['cuota_basica']
            if cuota_maxima==0 or int(cuota_maxima)<int(cuotabasica):
                cuota_maxima = cuotabasica
            direccion_cliente = pgonecolumn(con, f"select concat(calle,num) \
            from clientes where id={idcliente}")
            deuda_en_la_casa = pgonecolumn(con, f"select sum(deuda) from \
            clientes where concat(calle,num)='{direccion_cliente}' \
            and id!={idcliente} and ultpago<date_sub(curdate(), \
            interval 120 day)")
            if deuda_en_la_casa is None:
                deuda_en_la_casa = 0
            ins = f"insert into datos(fecha, user, idcliente, fecha_visitar,\
            art,horarios, comentarios, cuota_maxima,deuda_en_la_casa,\
            sin_extension,vendedor,listado) values (curdate(), \
            '{current_user.email}',{idcliente},curdate(),'','','', \
            {cuota_maxima},'{deuda_en_la_casa}',{sin_extension},\
            {d['vendedor']},1)"
            upd = f"update clientes set fechadato=curdate() where \
            id={idcliente}"
            cur.execute(ins)
            cur.execute(upd)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        con.close()
        return 'ok'


@vendedor.route('/vendedor/getcuotabasica')
@login_required
@check_roles(['dev','gerente'])
def vendedor_getcuotabasica():
    global var_sistema
    con = get_con()
    cuotabasica = var_sistema['cuota_basica']
    return jsonify(cuotabasica=cuotabasica)


@vendedor.route('/vendedor/borrardato/<int:id>')
@login_required
@check_roles(['dev','gerente','admin'])
def vendedor_borrardato(id):
    con = get_con()
    stm = f"delete from datos where id={id}"
    cur = con.cursor()
    try:
        cur.execute(stm)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(error)
        return make_response(error, 400)
    else:
        con.commit()
        con.close()
        log(stm)
    return 'ok'


@vendedor.route('/vendedor/editardato', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin'])
def vendedor_editardato():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    upd = f"update datos set fecha='{d['fecha']}', user='{d['user']}',\
    fecha_visitar='{d['fecha_visitar']}', horarios='{d['horarios']}',\
    art='{d['art']}', comentarios='{d['comentarios']}', cuota_maxima=\
    {d['cuota_maxima']} where id={d['id']}"
    cur = con.cursor()
    try:
        cur.execute(upd)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(error)
        return make_response(error, 400)
    else:
        con.commit()
        con.close()
        log(upd)
    return 'ok'


@vendedor.route('/vendedor/verificarqueyaesdato/<int:idcliente>')
@login_required
@check_roles(['dev','gerente','admin'])
def vendedor_verificarqueyaesdato(idcliente):
    con = get_con()
    dato = pgonecolumn(con, f"select idcliente from datos where idcliente={idcliente} and resultado is null")
    print('dato',dato)
    if dato:
        return make_response("error", 400)
    else:
        return make_response("ok", 200)


@vendedor.route('/vendedor/guardarcuotabasica/<int:cuota>')
@login_required
@check_roles(['dev','gerente','admin'])
def vendedor_guardarcuotabasica(cuota):
    con = get_con()
    upd = f"update variables set valor={cuota} where clave='cuota_basica'"
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
        leer_variables()
        return 'ok'


@vendedor.route('/2xxXix5cnz7IKcYegqs6qf0R6')
# @vendedor.route('/vendedor/listadatos')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_listadatos():
    return render_template('/vendedor/listadatos.html')


@vendedor.route('/Hb0IQfDEnbLV4eyWZeg5kbcff')
@vendedor.route('/vendedor/agregarcliente')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_agregarcliente():
    return render_template('/vendedor/agregarcliente.html')


@vendedor.route('/pEmPj7NAUn0Odsru4aL2BhlOu', methods=['POST'])
@vendedor.route('/vendedor/envioclientenuevo', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_envioclientenuevo():
    global var_sistema
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    dni = d['dni']
    cur = con.cursor()
    cliente = pgdict(con, f"select * from clientes where dni={dni}")
    if cliente: # o sea esta en la base de Romitex
        cliente = cliente[0]
        sin_extension = calculo_sin_extension(d['id'])
        cuota_maxima = calculo_cuota_maxima(d['id'])
        cuota_basica = var_sistema['cuota_basica']
        if cuota_maxima==0 or cuota_maxima<float(cuota_basica):
            cuota_maxima = cuota_basica
        direccion_cliente = pgonecolumn(con, f"select concat(calle,num) from \
        clientes where id={d['id']}")
        deuda_en_la_casa = pgonecolumn(con, f"select sum(deuda) from clientes \
        where concat(calle,num)='{direccion_cliente}' and id!={d['id']}")
        es_garante = pgonecolumn(con, f"select esgarante from clientes where id=\
        {d['id']}")
        if es_garante:
            dni = pgonecolumn(con, f"select dni from clientes where id=\
            {d['id']}")
            monto_garantizado = pgonecolumn(con, f"select sum(saldo) from ventas \
            where garantizado=1 and dnigarante={dni}")
        else:
            monto_garantizado = 0
        if deuda_en_la_casa is None:
            deuda_en_la_casa = 0
        iddato = pgonecolumn(con, f"select id from datos where idcliente =\
        {d['id']} and resultado is null")
        if iddato: # o sea hay ya un dato sin definir de ese cliente
            ins = None
        else:
            ins = f"insert into datos(fecha, user, idcliente, fecha_visitar, \
            art,horarios, comentarios, cuota_maxima,deuda_en_la_casa,\
            sin_extension,monto_garantizado,vendedor,dnigarante,enviado_vdor) \
            values (curdate(),'{current_user.email}',{d['id']},curdate(),'','',\
            'cliente enviado por vendedor', {cuota_maxima}, \
            '{deuda_en_la_casa}', {sin_extension}, {monto_garantizado},\
            {vdor},{d['dnigarante']},0)"
        # Testeo si hay cambios en los datos del cliente que envia el vendedor
        upd = None
        inslog = None
        if cliente['calle']!=d['calle'] or cliente['num']!=d['num'] or \
           cliente['barrio']!=d['barrio'] or cliente['wapp']!=d['wapp'] \
               or cliente['tel']!=d['tel'] or cliente['acla']!=d['acla']:
            upd = f"update clientes set calle='{d['calle']}', num={d['num']},\
            barrio='{d['barrio']}',wapp='{d['wapp']}',tel='{d['tel']}', \
            modif_vdor=1,acla='{d['acla']}' where id={d['id']}"
            inslog = f"insert into logcambiodireccion(idcliente,calle,\
            num,barrio,tel,acla,fecha,nombre,dni,wapp) values({cliente['id']},\
            '{cliente['calle']}','{cliente['num']}','{cliente['barrio']}',\
            '{cliente['tel']}','{cliente['acla']}',curdate(),\
            '{cliente['nombre']}','{cliente['dni']}','{cliente['wapp']}')"
        try:
            if ins:
                cur.execute(ins)
                iddato = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
                insaut = f"insert into autorizacion(fecha,vdor,iddato,idcliente,\
                cuota_requerida,cuota_maxima,arts) values(current_timestamp(),\
                {vdor},{iddato},{d['id']},{d['cuota_requerida']},\
                {cuota_maxima},'{d['arts']}')"
                cur.execute(insaut)
            else: # dato repetido update autorizacion en cuota_requerida y arts
                updaut = f"update autorizacion set cuota_requerida=\
                {d['cuota_requerida']},arts='{d['arts']}' where iddato={iddato}"
                cur.execute(updaut)

            if upd:
                cur.execute(upd)
            if inslog:
                cur.execute(inslog)
        except mysql.connector.Error as _error:
            con.rollback()
            error = _error.msg
            return make_response(error, 400)
        else:
            con.commit()
            con.close()
            log(ins)
            if ins:
                log(insaut)
            if upd:
                log(upd)
            if inslog:
                log(inslog)
            return 'ok'
    else:
        sin_extension = 1
        cuota_maxima = var_sistema['cuota_basica']
        direccion_cliente = d['calle']+d['num']
        deuda_en_la_casa = pgonecolumn(con, f"select sum(deuda) from clientes \
        where concat(calle,num)='{direccion_cliente}'")
        es_garante = 0
        monto_garantizado = 0
        if deuda_en_la_casa is None:
            deuda_en_la_casa = 0
        if d['dnigarante']=='':
            dnigarante = 0
        else:
            dnigarante = d['dnigarante']
        inscliente = f"insert into clientes(sex,dni, nombre,calle,num,barrio,\
        tel,wapp,zona,modif_vdor,acla,horario,mjecobr,infoseven) values('F',\
        {d['dni']},'{d['nombre']}','{d['calle']}',{d['num']},'{d['barrio']}',\
        '{d['tel']}','{d['wapp']}','-CAMBIAR',1,'{d['acla']}','','','')"
        print(inscliente)
        try:
            cur.execute(inscliente)
            idcliente = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
            ins = f"insert into datos(fecha, user, idcliente, fecha_visitar, art,\
            horarios, comentarios, cuota_maxima,deuda_en_la_casa,sin_extension,\
            monto_garantizado,vendedor,dnigarante) values (curdate(), \
            '{current_user.email}',{idcliente},curdate(),'','',\
            'cliente enviado por vendedor', {cuota_maxima}, '{deuda_en_la_casa}',\
            {sin_extension}, {monto_garantizado},{vdor},{dnigarante})"
            cur.execute(ins)
            print(ins)
            iddato = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
            insaut = f"insert into autorizacion(fecha,vdor,iddato,idcliente,\
            cuota_requerida,cuota_maxima,arts) values(current_timestamp(),\
            {vdor},{iddato},{idcliente},{d['cuota_requerida']},\
            {cuota_maxima},'{d['arts']}')"
            cur.execute(insaut)
            print(insaut)
        except mysql.connector.Error as _error:
            con.rollback()
            error = _error.msg
            return make_response(error, 400)
        else:
            con.commit()
            con.close()
            log(ins)
            log(insaut)
            return 'ok'





@vendedor.route('/4mY6khlmZKUzDRZDJkakr75iH')
@vendedor.route('/vendedor/listavisitasvdor')
@login_required
@check_roles(['dev', 'gerente','vendedor'])
def vendedor_visitasvdor():
    return render_template('/vendedor/listavisitasvdor.html')


@vendedor.route('/VGIdj7tUnI1hWCX3N7W7WAXgU')
@vendedor.route('/vendedor/getlistadodatosvendedor')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getlistadodatosvendedor():
    global var_sistema
    con = get_con()
    # if current_user.email == var_sistema['816']:
    #     vdor = 816
    # if current_user.email == var_sistema['835']:
    #     vdor = 835
    logging.warning(f"current {current_user.email, var_sistema['816'], current_user.email==var_sistema['816']}")
    vdor = 816
    listadodatos = pgdict(con, f"select datos.id, fecha, fecha_visitar,\
    art, horarios, comentarios,  dni, nombre,calle,num,acla,wapp,tel,barrio, \
    zona, cuota_maxima,idcliente, sin_extension,idvta,resultado,\
    datos.dnigarante as dnigarante from datos, clientes where clientes.id = \
    datos.idcliente and vendedor={vdor} and (resultado is null or (resultado in \
    (1,7) and date(fecha_definido)=curdate())) and fecha_visitar <=curdate() \
    and enviado_vdor=1 order by id desc")
    return jsonify(listadodatos=listadodatos)


@vendedor.route('/pnZWxv9Nicwt6TQ6zxohzvats/<int:iddato>')
@vendedor.route('/vendedor/getdato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getdato(iddato):
    con = get_con()
    dato = pgdict1(con, f"select datos.id, fecha, fecha_visitar,\
    art, horarios, comentarios,  dni, nombre,calle,num,acla,wapp,tel,barrio, \
    zona, cuota_maxima,idcliente, sin_extension, datos.dnigarante as \
    dnigarante,idvta,monto_vendido from datos, clientes where clientes.id = \
    datos.idcliente and datos.id={iddato}")
    return jsonify(dato=dato)


@vendedor.route('/kHEhacFNmI2vflFHBbaT1AQ1Z')
@vendedor.route('/vendedor/getlistadoarticulos')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getlistadoarticulos():
    con = get_con()
    articulos = pgdict(con, "select art,cuota from articulos where activo=1 \
    order by art")
    return jsonify(articulos=articulos)


@vendedor.route('/uQ3gisetQ8v0n6tw81ORnpL1s' , methods=['POST'])
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


@vendedor.route('/HvjJNtFgF71pRYafzcTC74nUt' , methods=['POST'])
@vendedor.route('/vendedor/guardardatofechado' , methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_guardardatofechado():
    global var_sistema
    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    upd = f"update datos set fecha_visitar='{d['fecha_visitar']}' where id = \
    {d['id']}"
    ins = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{vdor},{d['id']},4,0)"
    cur = con.cursor()
    try:
        cur.execute(upd)
        cur.execute(ins)
    except mysql.connector.Error as _error:
       con.rollback()
       error = _error.msg
       return make_response(error,400)
    else:
       con.commit()
       con.close()
       log(upd)
       return 'ok'


@vendedor.route('/UtVc3f6y5hfxu2dPmcrV9Y7mc/<int:iddato>')
@vendedor.route('/vendedor/anulardato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_anulardato(iddato):
    global var_sistema
    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    con = get_con()
    upd = f"update datos set resultado=2, fecha_definido=current_timestamp()\
    where id = {iddato}"
    ins = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{vdor},{iddato},2,0)"
    cur = con.cursor()
    try:
        cur.execute(upd)
        cur.execute(ins)
    except mysql.connector.Error as _error:
       con.rollback()
       error = _error.msg
       return make_response(error,400)
    else:
       con.commit()
       con.close()
       log(upd)
       return 'ok'


@vendedor.route('/gJUmonE8slTFGZqSKXSVwqPJ1/<int:iddato>')
@vendedor.route('/vendedor/mudodato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_mudodato(iddato):
    global var_sistema
    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    con = get_con()
    upd = f"update datos set resultado=5, fecha_definido=current_timestamp()\
    where id = {iddato}"
    ins = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{vdor},{iddato},5,0)"
    cur = con.cursor()
    try:
        cur.execute(upd)
        cur.execute(ins)
    except mysql.connector.Error as _error:
       con.rollback()
       error = _error.msg
       return make_response(error,400)
    else:
       con.commit()
       con.close()
       log(upd)
       return 'ok'


@vendedor.route('/sLTFCMArYAdVsrEgwsz7utyRi/<int:iddato>')
@vendedor.route('/vendedor/falleciodato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_falleciodato(iddato):
    global var_sistema
    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    con = get_con()
    idcliente = pgonecolumn(con, f"select idcliente from datos where id=\
    {iddato}")
    upd = f"update datos set resultado=6, fecha_definido=current_timestamp()\
    where id = {iddato}"
    ins = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{vdor},{iddato},6,0)"
    updcli = f"update clientes set zona='-FALLECIDOS', modif_vdor=1 where id=\
    {idcliente}"
    cur = con.cursor()
    try:
        cur.execute(upd)
        cur.execute(ins)
        cur.execute(updcli)
    except mysql.connector.Error as _error:
       con.rollback()
       error = _error.msg
       return make_response(error,400)
    else:
       con.commit()
       con.close()
       log(upd)
       log(updcli)
       return 'ok'


@vendedor.route('/fc3vpQG6SzEH95Ya7kTJPZ48M' , methods=['POST'])
@vendedor.route('/vendedor/validardni' , methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_validardni():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    dni = pgonecolumn(con, f"select dni from clientes where id={d['id']}")
    if dni==int(d['dni']):
        return make_response('aprobado', 200)
    else:
        return make_response('error', 400)


@vendedor.route('/vaHQ2gFYLW2pIWSr5I0ogCL0k', methods=['POST'])
@vendedor.route('/vendedor/registrarautorizacion', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_registrarautorizacion():
    global var_sistema
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    if current_user.email == var_sistema['816']:
        vdor = 816
    if current_user.email == var_sistema['835']:
        vdor = 835
    ins = f"insert into autorizacion(fecha,vdor,iddato,idcliente,\
    cuota_requerida,cuota_maxima,arts) values(current_timestamp(),\
    {vdor},{d['id']},{d['idcliente']},{d['cuota_requerida']},\
    {d['cuota_maxima']},'{d['arts']}')"
    cur = con.cursor()
    try:
        cur.execute(ins)
    except mysql.connector.Error as _error:
       con.rollback()
       error = _error.msg
       return make_response(error,400)
    else:
       con.commit()
       con.close()
       log(ins)
       return 'ok'

@vendedor.route('/vendedor/getlistadoautorizados')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getlistadoautorizados():
    global var_sistema
    con = get_con()
    listadoautorizados = pgdict(con, f"select datos.id as id,datos.fecha as \
    fecha, datos.user as user, nombre, datos.resultado as resultado, datos.art \
    as art, datos.cuota_maxima as cuota_maxima, datos.sin_extension as \
    sin_extension, datos.deuda_en_la_casa as deuda_en_la_casa,datos.vendedor as vendedor, \
    clientes.novendermas as novendermas, clientes.incobrable as incobrable,\
    clientes.sev as sev, clientes.baja as baja, autorizacion.fecha as \
    fechahora, autorizacion.cuota_requerida as cuota_requerida, \
    autorizacion.arts as arts,horarios,comentarios,(select count(*) from \
    autorizacion where autorizacion.idcliente=clientes.id) as cnt, \
    autorizacion.idcliente from datos, autorizacion,clientes  where \
    datos.idcliente=clientes.id and autorizacion.iddato=datos.id and \
    autorizacion.autorizado=0 and resultado is null and datos.rechazado=0")
    cuotabasica = var_sistema['cuota_basica']
    return jsonify(listadoautorizados=listadoautorizados, cuotabasica=cuotabasica)


@vendedor.route('/vendedor/getlistadoautorizadosporid/<int:idcliente>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getlistadoautorizadosporid(idcliente):
    con = get_con()
    listadoautorizadosporid = pgdict(con, f"select datos.id as id,datos.fecha \
    as fecha, datos.user as user, nombre, datos.resultado as resultado, \
    datos.art as art, datos.cuota_maxima as cuota_maxima, datos.sin_extension \
    as sin_extension, datos.deuda_en_la_casa as deuda_en_la_casa,datos.vendedor as vendedor,  \
    clientes.novendermas as novendermas, clientes.incobrable as incobrable,\
    clientes.sev as sev, clientes.baja as baja, autorizacion.fecha as \
    fechahora, autorizacion.cuota_requerida as cuota_requerida, \
    autorizacion.arts as arts,horarios,comentarios,(select count(*) from \
    autorizacion where autorizacion.idcliente=clientes.id) as cnt from datos,\
    autorizacion,clientes  where datos.idcliente=clientes.id and \
    autorizacion.iddato=datos.id and autorizacion.idcliente={idcliente}")
    return jsonify(listadoautorizadosporid=listadoautorizadosporid)

@vendedor.route('/vendedor/autorizardato/<int:id>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_autorizardato(id):
    con = get_con()
    cuota_requerida = pgonecolumn(con, f"select cuota_requerida from \
    autorizacion where iddato={id}")
    upd_aut = f"update autorizacion set autorizado=1, user = \
    '{current_user.email}' where iddato={id}"
    upd_dat = f"update datos set cuota_maxima = {cuota_requerida}, \
    autorizado=1,enviado_vdor=1 where id={id}"
    con = get_con()
    cur = con.cursor()
    try:
        cur.execute(upd_aut)
        cur.execute(upd_dat)
    except mysql.connector.Error as _error:
       con.rollback()
       error = _error.msg
       return make_response(error,400)
    else:
       con.commit()
       con.close()
       log(upd_dat)
       log(upd_aut)
       return 'ok'


@vendedor.route('/vendedor/noautorizardato/<int:id>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_noautorizardato(id):
    con = get_con()
    cuota_requerida = pgonecolumn(con, f"select cuota_requerida from \
    autorizacion where iddato={id}")
    upd_aut = f"update autorizacion set autorizado=0, user = \
    '{current_user.email}',rechazado=1 where iddato={id}"
    upddato = f"update datos set rechazado=1 where id={id}"
    con = get_con()
    cur = con.cursor()
    try:
        cur.execute(upd_aut)
        cur.execute(upddato)
    except mysql.connector.Error as _error:
       con.rollback()
       error = _error.msg
       return make_response(error,400)
    else:
       con.commit()
       con.close()
       log(upd_aut)
       log(upddato)
       return 'ok'


@vendedor.route('/xuNzBi4bvtSugd5KbxSQzD0Ey' , methods=['POST'])
@vendedor.route('/vendedor/pasarventa' , methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_pasarventa():
    global var_sistema
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    ant = 0
    cc = 6
    ic = d['cuota']
    p = 1
    # gar = pgdict1(con, f"select garantizado,dnigarante from clientes where \
    # id={d['idcliente']}")
    # garantizado = gar['garantizado']
    # dnigarante = gar['dnigarante']
    if d['dnigarante']:
        garantizado = 1
    else:
        garantizado = 0
    insvta = f"insert into ventas(fecha,idvdor,ant,cc,ic,p,primera,idcliente,\
    garantizado,dnigarante) values(curdate(),{vdor},{ant},{cc},{ic},{p},\
    '{d['primera']}',{d['idcliente']},{garantizado},{d['dnigarante']})"
    insvis = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{vdor},{d['id']},1,{ic*cc})"
    cur = con.cursor()
    try:
        cur.execute(insvis)
        cur.execute(insvta)
    except mysql.connector.Error as _error:
       con.rollback()
       error = _error.msg
       return make_response(error,400)
    else:
       idvta = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
       # lo siguiente ha sido trasladado al trigger ventas_ins_clientes
       # upd = f"update datos set resultado=1, monto_vendido={ic*6}, fecha_definido=\
       # current_timestamp(), idvta={idvta} where id={d['id']}"
       # cur.execute(upd)
       for item in d['arts']:
           cnt = item['cnt']
           art = item['art']
           ic = item['cuota']
           costo = pgonecolumn(con, f"select costo from articulos where \
           art='{art}'")
           ins = f"insert into detvta(idvta,cnt,art,cc,ic,costo,devuelta) \
           values({idvta},{cnt},'{art}',6,{ic},{costo},0)"
           cur.execute(ins)
           log(ins)
       con.commit()
       con.close()
       # log(upd)
       log(insvta)
       return 'ok'


@vendedor.route('/G9S85pbqWVEX17nNQuOOnpxvn/<int:iddato>')
@vendedor.route('/vendedor/noestabadato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_noestabadato(iddato):
    global var_sistema
    con = get_con()
    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    ins = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{vdor},{iddato},3,0)"
    cur = con.cursor()
    try:
        cur.execute(ins)
    except mysql.connector.Error as _error:
       con.rollback()
       error = _error.msg
       return make_response(error,400)
    else:
       con.commit()
       con.close()
       return 'ok'



@vendedor.route('/vendedor/getvisitasvendedor')
@login_required
@check_roles(['dev', 'gerente'])
def vendedor_getvisitasvendedor():
    con = get_con()
    visitasvendedor = pgdict(con, "select visitas.fecha as fecha,\
    cast(hora as char) as hora, visitas.vdor as vdor, result, \
    visitas.monto_vendido as monto_vendido, idcliente,nombre,calle,num,zona \
    from visitas,datos,clientes where visitas.iddato=datos.id and \
    clientes.id=datos.idcliente order by visitas.fecha desc,hora")

    fechasvisitas = pgdict(con, "select visitas.fecha as fecha, visitas.vdor \
    as vdor, count(*) as cnt, sum(visitas.monto_vendido) as monto_vendido \
    from visitas,datos where visitas.iddato=datos.id group by visitas.fecha,\
    visitas.vdor order by visitas.fecha,visitas.vdor desc")
    return jsonify(visitasvendedor=visitasvendedor, fechasvisitas=fechasvisitas)


@vendedor.route('/F8cq9GzHJIG9hENBo0Xq7hdH7')
@vendedor.route('/vendedor/getvisitasvdor')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getvisitasvdor():
    global var_sistema
    con = get_con()
    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    visitasvendedor = pgdict(con, f"select visitas.fecha as fecha,\
    cast(hora as char) as hora, visitas.vdor as vdor, result, \
    visitas.monto_vendido as monto_vendido, idcliente,nombre,calle,num,zona \
    from visitas,datos,clientes where visitas.iddato=datos.id and \
    clientes.id=datos.idcliente and visitas.vdor={vdor} order by \
    visitas.fecha desc,hora")

    fechasvisitas = pgdict(con,f"select visitas.fecha as fecha, visitas.vdor \
    as vdor, count(*) as cnt, sum(visitas.monto_vendido) as monto_vendido \
    from visitas,datos where visitas.iddato=datos.id and visitas.vdor={vdor} \
    group by visitas.fecha,visitas.vdor order by visitas.fecha,visitas.vdor \
    desc")
    return jsonify(visitasvendedor=visitasvendedor, fechasvisitas=fechasvisitas)


@vendedor.route('/vendedor/getclientesingresadosporvdor')
@login_required
@check_roles(['dev','gerente'])
def vendedor_getclientesingresadosporvdor():
    con = get_con()
    clientes = pgdict(con, "select * from clientes where modif_vdor=1")
    return jsonify(clientes=clientes)


@vendedor.route('/vendedor/getventashoy')
@login_required
@check_roles(['dev','gerente'])
def vendedor_getventashoy():
    con = get_con()
    ventashoy = pgdict(con, "select fecha_definido,\
    nombre,concat(calle,num) as direccion, zona, monto_vendido, vendedor,dni \
    from datos,clientes where datos.idcliente = clientes.id and \
    date(fecha_definido)=curdate() and resultado=1")
    return jsonify(ventashoy=ventashoy)





@vendedor.route('/3ZbXanrRQalY6JL5eOBi49Nyc', methods=["POST"])
@vendedor.route('/vendedor/wappaut', methods=["POST"])
@login_required
@check_roles(['dev','gerente','admin','vendedor'])
def vendedor_wappaut():
    global var_sistema
    d = json.loads(request.data.decode("UTF-8"))
    msg = d['msg']
    # tipo = d['tipo'] # a discriminar en el futuro
    # idcliente = var_sistema['idcliente_auth']
    wapp = var_sistema['wapp_auth']
    logging.warning(f"wapp {wapp}")
    if wapp:
        response = send_msg_whatsapp(0, wapp, msg)
        return response
    else:
        return 'error', 400


@vendedor.route('/vendedor/wapprespauth', methods=["POST"])
@login_required
@check_roles(['dev','gerente','admin'])
def vendedor_wapprespaut():
    global var_sistema
    d = json.loads(request.data.decode("UTF-8"))
    vdor = 'wapp'+str(d['vdor'])
    wappvdor = var_sistema[vdor]
    msg = d['msg']
    if wappvdor:
        response = send_msg_whatsapp(0, wappvdor, msg)
        return response
    else:
        return 'error', 400


@vendedor.route('/hX53695XAOpaLY9itLgmghkhH', methods=["POST"])
@vendedor.route('/vendedor/wapp', methods=["POST"])
@login_required
@check_roles(['dev','gerente','admin','vendedor'])
def vendedor_wapp():
    d = json.loads(request.data.decode("UTF-8"))
    idcliente = d['idcliente']
    wapp = d['wapp']
    msg = d['msg']
    devel = var_sistema['devel']
    if devel=='1':
        prod=0
    else:
        prod=1
    if wapp and prod:
        response = send_msg_whatsapp(idcliente, wapp, msg)
        if response is None:
            response = 'Rejected'
        return response
    else:
        return 'error', 400



@vendedor.route('/4qUK6eNZnCYjIiGTt3HSj2YDp', methods=['POST'])
@vendedor.route('/vendedor/filewapp', methods=['POST'])
@login_required
@check_roles(['dev','gerente','admin','vendedor'])
def vendedor_filewapp():
    global var_sistema
    d = json.loads(request.data.decode("UTF-8"))
    wapp = d['wapp']
    idcliente = d['idcliente']
    file = d['file']
    devel = var_sistema['devel']
    if devel=='1':
        prod=0
    else:
        prod=1
    if wapp and prod:
        response = send_file_whatsapp(
            idcliente,f"https://www.fedesal.lol/pdf/{file}.pdf", wapp)
        return jsonify(response=response)


@vendedor.route('/vendedor/getcomisionesvendedor/<int:vdor>')
@login_required
@check_roles(['dev','gerente'])
def vendedor_getcomisionesvendedor(vdor):
    global var_sistema
    com = 'com'+str(vdor)
    comision = var_sistema[com]
    con = get_con()
    comisiones = pgdict(con, f"select fecha,monto_vendido*{comision} \
    as com,idvta as id from datos where vendedor={vdor} and com_pagada=0 \
    and monto_vendido>0 order by fecha")
    devoluciones = pgdict(con, f"select fecha,monto_devuelto*{comision}*(-1) \
    as com, idvta as id from datos where vendedor={vdor} and com_pagada_dev=0 \
    and monto_devuelto!=0 order by fecha")
    if devoluciones:
        comisiones = comisiones+devoluciones
    return jsonify(comisiones=comisiones)


@vendedor.route('/MeHzAqFYsbb78KAVFAGTlZRW9/<dni>')
@vendedor.route('/vendedor/buscaclientepordni/<dni>')
@login_required
@check_roles(['dev','gerente','admin','vendedor'])
def vendedor_buscaclientepordni(dni):
    con = get_con()
    cliente = pgdict1(con, f"select * from clientes where dni={dni}")
    if cliente:
        return jsonify(cliente=cliente)
    else:
        return make_response("error", 401)


@vendedor.route('/vendedor/getartvendedor/<int:vdor>')
@login_required
@check_roles(['dev','gerente'])
def vendedor_getartvendedor(vdor):
    con = get_con()
    artvendedor = pgdict(con, f"select sum(detvta.cnt) as cnt,\
    detvta.art as art from detvta,ventas where detvta.idvta=ventas.id and \
    cargado=0 and detvta.devuelta=0 and idvdor={vdor} group by detvta.art")
    return jsonify(artvendedor=artvendedor)


@vendedor.route('/vendedor/getvendedores')
@login_required
@check_roles(['dev','gerente'])
def vendedor_getvendedores():
    con = get_con()
    vendedores = pglflat(con, "select id from cobr where activo=1 and vdor=1")
    return jsonify(vendedores=vendedores)


@vendedor.route('/vendedor/marcarcargado/<int:vdor>')
@login_required
@check_roles(['dev','gerente'])
def vendedor_marcarcargado(vdor):
    con = get_con()
    upd = f"update detvta set cargado=1 where idvta in (select id from ventas \
    where idvdor={vdor})"
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


@vendedor.route('/vendedor/marcarpagadas/<int:vdor>')
@login_required
@check_roles(['dev','gerente'])
def vendedor_marcarpagadas(vdor):
    con = get_con()
    upd = f"update datos set com_pagada=1, fechapagocom=current_date() where \
    idvta in (select idvta from datos where vendedor={vdor} and com_pagada=0 \
    and monto_vendido>0)"
    upddev = f"update datos set com_pagada_dev=1, fechapagocomdev=\
    current_date() where idvta in (select idvta from datos where vendedor=\
    {vdor} and com_pagada_dev=0 and monto_devuelto!=0)"
    cur = con.cursor()
    try:
        cur.execute(upd)
        cur.execute(upddev)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        con.close()
        log(upd)
        log(upddev)
        return 'ok'


@vendedor.route('/k8E5hsVs4be3jsJJaob6OQmAX')
@vendedor.route('/vendedor/getcargavendedor')
@login_required
@check_roles(['dev','gerente','vendedor'])
def vendedor_getcargavendedor():
    global var_sistema
    con = get_con()
    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    artvendedor = pgdict(con, f"select sum(detvta.cnt) as cnt,\
    detvta.art as art from detvta,ventas where detvta.idvta=ventas.id and \
    cargado=0 and detvta.devuelta=0 and idvdor={vdor} group by detvta.art")
    return jsonify(artvendedor=artvendedor)


@vendedor.route('/TWGQV0TM0p7Oa9tMPvrNWIHyd')
@vendedor.route('/vendedor/cargararticulos')
@login_required
@check_roles(['dev','gerente','vendedor'])
def vendedor_cargararticulos():
    return render_template('/vendedor/cargarart.html')


@vendedor.route('/DDFEwfGEDYv5UHTVgcDPFUWm1')
@vendedor.route('/vendedor/comisionesvdor')
@login_required
@check_roles(['dev','gerente','vendedor'])
def vendedor_comisionesvdor():
    return render_template('/vendedor/comisionesvdor.html')


@vendedor.route('/IrV7gmqz4Wu8Q8rwmXMftphaB')
@vendedor.route('/vendedor/getcomisionesparavendedor')
@login_required
@check_roles(['dev','gerente','vendedor'])
def vendedor_getcomisionesparavendedor():
    global var_sistema
    if current_user.email == var_sistema['816']:
        vdor = 816
    elif current_user.email == var_sistema['835']:
        vdor = 835
    com = 'com'+str(vdor)
    comision = var_sistema[com]
    con = get_con()
    comisiones = pgdict(con, f"select fecha,monto_vendido*{comision} \
    as com, idvta as id from datos where vendedor={vdor} and com_pagada=0 \
    and monto_vendido>0 order by fecha")
    devoluciones = pgdict(con, f"select fecha,monto_devuelto*{comision}*(-1) \
    as com, idvta as id from datos where vendedor={vdor} and com_pagada_dev=0 \
    and monto_devuelto!=0 order by fecha")
    if devoluciones:
        comisiones = comisiones+devoluciones
    return jsonify(comisiones=comisiones)
