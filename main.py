# -*- coding: utf-8 -*-
from flask import Flask, json, Response, jsonify
from flask import render_template, url_for, request, redirect, make_response, session, flash, g, send_file
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from flask_cors import CORS
from flask_cors import cross_origin
from flask_wtf import csrf
import gevent
from werkzeug.urls import url_parse
from formularios import *
import mysql.connector
import simplejson as json
from datetime import datetime
import logging
import time
import threading
import base64
import re
from functools import wraps
from lib import *
import urllib.parse

app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
CORS(app)
csrf = CSRFProtect(app)
login = LoginManager(app)
login.login_view = "login"
bcrypt = Bcrypt(app)

# engine = create_engine('mysql+mysqlconnector://hero:ataH2132**/@localhost/hero')
def get_con():
    con = mysql.connector.connect(host='localhost',database='hero',user='hero',password='ataH2132**/')
    return con

def check_roles(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "roles" in session and session["roles"] in roles:
                return func(*args, **kwargs)
            return redirect('login')
        return wrapper
    return decorator


def verifica_login(email):
    con = get_con()
    ins = f"insert into falsologin(email,time) values('{email}',{int(time.time())})"

    try:
        pgexec(con,ins)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:

        log(ins)
        cnt = pgonecolumn(con, f"select count(*) from falsologin where email=\
        '{email}' and time>{int(time.time())-3600}")
        if cnt>4:
            upd = f"update users set auth=0 where email='{email}'"
            pgexec(con,upd)

            log(upd)
        con.close()


class User(UserMixin):
    def __init__(self, id, name, email, password,roles, auth=0):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.roles = roles
        self.auth = auth

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.email)


def log_login(email, status, password=None):
    """Funcion que hace un log en txt de los log, errores y logouts"""
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d, %H:%M:%S")
    with open("/home/hero/log/login.log", "a", encoding="utf-8") as log_file:
        log_file.write('\n')
        if password:
            # log_file.write(str(date_time)+' '+str(email)+' '+str(password)+' '+str(status))
            # por motivos de seguridad desactivo el registro de logins
            log_file.write(str(date_time)+' '+str(email)+' '+str(status))
        else:
            log_file.write(str(date_time)+' '+str(email)+' '+str(status))
        log_file.close()


def log(stmt):
    if not current_user.is_anonymous:
        current = current_user.email
    else:
        current = "no user yet"
    con = get_con()

    ins = f'insert into log(fecha, user, stmt) \
    values(CURRENT_TIMESTAMP,"{current}","{stmt}")'
    pgexec(con,ins)

    con.close()


@login.user_loader
def load_user(id):
    con = get_con()
    try:
        log = pglistdict(con, f"select id,name,email,password,roles,auth from users where id={id}")[0]
        user = User(log['id'], log['name'], log['email'], log['password'], log['roles'], log['auth'])
        return user
    except:
        return None


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    con = get_con()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        sel = f"select id,name,email,password,roles,auth from users where email='{email}'"
        logs = pglistdict(con, sel)
        if logs:
            logs = logs[0]
        errormail = "Ese email no existe en la base de datos. Registrese"
        errorpassword = "Ha ingresado una contraseña incorrecta"
        errorauth = "Ese email no esta autorizado a ingresar"
        if not logs:
            log_login(email,'error-email')
            return render_template('login_form.html', errormail=errormail)
        user = User(logs['id'], logs['name'],
                    logs['email'], logs['password'],logs['roles'],logs['auth'])
        if not user.check_password(password):
            log_login(user.email, 'error-password')
            verifica_login(user.email)
            return render_template('login_form.html', errorpassword=errorpassword)
        if not user.auth:
            log_login(user.email, 'error-auth')
            return render_template('login_form.html', errorauth=errorauth)
        if user is not None and user.check_password(password) and user.auth:
            login_user(user, remember=False)
            session['roles'] = user.roles
            session['user'] = user.email
            log_login(user.email,'login',password)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                if session['roles']=='vendedor':
                    next_page = url_for('vendedor_listadatos')
                elif session['roles']=='cobrador':
                    next_page = url_for('cobrador_listafichas')
                else:
                    next_page = url_for('buscador.buscador_')
            return redirect(next_page)
    return render_template('login_form.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    log_login(session['user'],'logout')
    session['user'] = ''
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
#@login_required
def signup():
    con = get_con()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        error = None

        if not name:
            error = "Nombre es requerido"
        elif not password:
            error = "Password es requerido"
        elif not email:
            error = "Email es requerido"
        elif pgonecolumn(con, f"select email from users where email='{email}'"):
            error = f"El email {email} ya esta en uso. Haga Login"

        if error is None:
            password = bcrypt.generate_password_hash(password).decode('utf-8')
            ins = f"insert into users(name, email, password) values('{name}', '{email}', '{password}')"

            try:
                pgexec(con,ins)
            except mysql.connector.Error as e:
                con.rollback()
                error = e.msg
                return make_response(error, 400)
            else:
                log(ins)

                cur.close()
                flash("Registro correctamente ingresado")
                return redirect(url_for('login'))
        flash(error, category='error')
    return render_template('signup.html')


var_sistema = {}
def leer_variables():
    """Funcion para leer variables de sistema.

    Las variables estan ubicadas en la tabla variables con los campos clave,
    valor.
    Y seran incorporados en una variable  que es un dict."""

    con = get_con()
    try:
        variables = pglistdict(con, "select clave,valor from variables")
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        for row in variables:
            var_sistema[row['clave']] = row['valor']
        return 1
    finally:
        con.close()


leer_variables()


def calculo_sin_extension(idcliente):
    """Determina si a un cliente se le puede ofrecer automaticamente extension.

    de la cuota_maxima. Toma los parametros: cantidad de ventas: 1 venta no,
    atrasos>60 en ultimos 3 años no.
    Return 1 negativo sin_extension. 0 positivo se puede ofrecer extension."""

    con = get_con()
    try:
        cnt_vtas = pgonecolumn(con, f"select count(*) from ventas where \
        saldo=0 and idcliente = {idcliente}")
        if cnt_vtas == 1:
            return 1
        atraso = pgonecolumn(con, f"select atraso from clientes where \
        id={idcliente}")
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        if atraso and atraso > 60:
            return 1
        return 0
    finally:
        con.close()


def calculo_cuota_maxima(idcliente):
    """Funcion que calcula la cuota maxima vendible del cliente.

    Busca la cuota maxima de los ultimos tres años y la actualiza por inflacion
    le disminuye 5% por cada mes de atraso que haya tenido
    le aumenta 5% por cada compra que haya tenido en los ultimos tres años.
    Esto ultimo se suspende pq aumenta mucho la cuota por la gran inflacion que
    hay.
    Cambios: se saco el incremento por cantidad de ventas.
    Se toman las ventas de los ultimos tres años canceladas o no, y se
    actualizan luego se pone la cuota actualizada mas alta.
    Tambien se tiene en cuenta el monto total de la venta/6 para el calculo de
    la cuota para evitar distorsion si el plan fue en 4 o 5 cuotas.
    """
    con = get_con()
    cuotas = pglistdict(con, f"select comprado as monto,\
    date_format(fecha,'%Y%c') as fecha from ventas where idcliente={idcliente} \
    and fecha>date_sub(curdate(),interval 3 year) and devuelta=0 and pp=0")
    cuota_actualizada = 0
    try:
        if cuotas:
            ultimo_valor = pgonecolumn(con, "select indice from inflacion \
            order by id desc limit 1")
            cuotas_actualizadas = []
            for venta in cuotas:
                cuota = venta['monto']/6
                fecha = venta['fecha']
                indice = pgonecolumn(con, f"select indice from inflacion \
                where concat(year,month)='{fecha}'")
                if not indice:  # esto sucede si es un mes sin indice cargado aun
                    indice = ultimo_valor
                actualizada = ultimo_valor/indice * cuota
                cuotas_actualizadas.append(actualizada)
            cuota_actualizada = max(cuotas_actualizadas)

            atraso = pgonecolumn(con, f"select atraso from clientes where \
            id={idcliente}")
            if atraso is None:
                atraso = 0
            if atraso > 0:
                cuota_actualizada = cuota_actualizada * (1-(atraso/30)*0.05)
                cuota_actualizada = max(cuota_actualizada, 0)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        if cuota_actualizada>10000:
            cuota_actualizada = 10000
        return cuota_actualizada
    finally:
        con.close()


def es_dni_valido(dni):
    patron = r'^\d{7,8}$'
    if dni is None:
        return False
    dni = str(dni)
    if re.match(patron, dni):
        return True
    else:
        return False


def get_cobr():
    return var_sistema[current_user.email]


@app.route('/2xxXix5cnz7IKcYegqs6qf0R6')
# @vendedor.route('/vendedor/listadatos')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_listadatos():
    """Ruta para render pagina listadatos."""
    return render_template('listadatos.html')


@app.route('/Hb0IQfDEnbLV4eyWZeg5kbcff')
@app.route('/vendedor/agregarcliente')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_agregarcliente():
    """Ruta para render pagina agregarcliente."""
    return render_template('agregarcliente.html')


@app.route('/pEmPj7NAUn0Odsru4aL2BhlOu', methods=['POST'])
@app.route('/vendedor/envioclientenuevo', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_envioclientenuevo():
    """Proceso para agregar cliente nuevo por el vendedor."""
    logging.warning("envioclientenuevo %s", current_user.email)
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    cliente_viejo = {}
    vdor = var_sistema[current_user.email]
    dni = d_data['dni']

    cliente = pglistdict(con, f"select * from clientes where dni={dni}")
    if cliente:  # o sea esta en la base de Romitex
        cliente = cliente[0]
        sin_extension = calculo_sin_extension(d_data['id'])
        cuota_maxima = calculo_cuota_maxima(d_data['id'])
        cuota_basica = var_sistema['cuota_basica']
        if cuota_maxima == 0 or cuota_maxima < float(cuota_basica):
            cuota_maxima = cuota_basica
        direccion_cliente = pgonecolumn(con, f"select concat(calle,num) from \
        clientes where id={d_data['id']}")
        deuda_en_la_casa = pgonecolumn(con, f"select sum(deuda) from clientes \
        where concat(calle,num)='{direccion_cliente}' and id!={d_data['id']}")
        es_garante = pgonecolumn(con, f"select esgarante from clientes where \
        id={d_data['id']}")
        zona = pgonecolumn(con, f"select zona from clientes where id=\
        {d_data['id']}")
        if es_garante:
            dni = pgonecolumn(con, f"select dni from clientes where id=\
            {d_data['id']}")
            monto_garantizado = pgonecolumn(con, f"select sum(saldo) from \
            ventas where garantizado=1 and dnigarante={dni}")
        else:
            monto_garantizado = 0
        if deuda_en_la_casa is None:
            deuda_en_la_casa = 0
        # consulta para ver si el dato ha sido asignado a otro vendedor
        # aca primero buscamos un dato cargado no definido.
        iddato = pgonecolumn(con, f"select id from datos where idcliente =\
        {d_data['id']} and resultado = 0")
        if iddato:  # o sea hay ya un dato sin definir de ese cliente
            ins = None
        else:
            ins = f"insert into datos(fecha, user, idcliente, fecha_visitar, \
            art,horarios, comentarios, cuota_maxima,deuda_en_la_casa,\
            sin_extension,monto_garantizado,vendedor,dnigarante,enviado_vdor,\
            zona,resultado) values (curdate(),'{current_user.email}',{d_data['id']},\
            curdate(),'','','cliente enviado por vendedor', {cuota_maxima}, \
            '{deuda_en_la_casa}', {sin_extension}, {monto_garantizado},\
            {vdor},{d_data['dnigarante']},0,'{zona}',0)"
        # Testeo si hay cambios en los datos del cliente que envia el vendedor
        upd = None
        inslog = None
        cliente_nuevo = [cliente['calle'], cliente['num'], cliente['barrio'],
                         cliente['wapp'], cliente['tel'], cliente['acla']]
        cliente_viejo = [d_data['calle'], d_data['num'], d_data['barrio'],
                         d_data['wapp'], d_data['tel'], d_data['acla']]
        if cliente_nuevo != cliente_viejo:
            upd = f"update clientes set calle='{d_data['calle']}', \
            num={d_data['num']},barrio='{d_data['barrio']}',\
            wapp='{d_data['wapp']}',tel='{d_data['tel']}', \
            modif_vdor=1,acla='{d_data['acla']}' where id={d_data['id']}"
            inslog = f"insert into logcambiodireccion(idcliente,calle,\
            num,barrio,tel,acla,fecha,nombre,dni,wapp) values({cliente['id']},\
            '{cliente['calle']}','{cliente['num']}','{cliente['barrio']}',\
            '{cliente['tel']}','{cliente['acla']}',curdate(),\
            '{cliente['nombre']}','{cliente['dni']}','{cliente['wapp']}')"
        try:
            if ins:
                pgexec(con,ins)
                iddato = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
                insaut = f"insert into autorizacion(fecha,vdor,iddato,\
                idcliente,cuota_requerida,cuota_maxima,arts) \
                values(current_timestamp(),{vdor},{iddato},{d_data['id']},\
                {d_data['cuota_requerida']},{cuota_maxima},'{d_data['arts']}')"
                pgexec(con,insaut)
                idautorizacion = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
                vdorasignado = vdor
            else:  # dato repetido inserto auth con iddato que ya tenia de antes
                # busco el vdorasignado al dato si es que existe.
                vdorasignado = str(pgonecolumn(con, f"select vendedor from datos \
                where id={iddato}"))
                # si el dato era del vdor inserto la autorizacion.
                if vdorasignado == vdor:
                    insauth = f"insert into autorizacion(fecha,vdor,iddato,\
                    idcliente,cuota_requerida,cuota_maxima,arts) \
                    values(current_timestamp(),{vdor},{iddato},{d_data['id']},\
                    {d_data['cuota_requerida']},{cuota_maxima},\
                    '{d_data['arts']}')"
                # si no hay vdorasignado- Se asigna dato y crea la auth.
                else:
                    upddato = f"update datos set vendedor={vdor} where id=\
                        {iddato}"
                    insauth = f"insert into autorizacion(fecha,vdor,iddato,\
                    idcliente,cuota_requerida,cuota_maxima,arts) \
                    values(current_timestamp(),{vdor},{iddato},{d_data['id']},\
                    {d_data['cuota_requerida']},{cuota_maxima},\
                    '{d_data['arts']}')"
                    pgexec(con,upddato)
                pgexec(con,insauth)
                idautorizacion = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
            if upd:
                pgexec(con,upd)
            if inslog:
                pgexec(con,inslog)
        except mysql.connector.Error as _error:
            con.rollback()
            error = _error.msg
            logging.warning(
                f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
            return make_response(error, 400)
        else:

            log(ins)
            if ins:
                log(insaut)
            if upd:
                log(upd)
            if inslog:
                log(inslog)
            if vdor != vdorasignado:
                otroasignado = 1
                if vdorasignado is None:
                    otroasignado = 0
                return jsonify(idautorizacion=idautorizacion,
                               otroasignado=otroasignado)
            return jsonify(idautorizacion=idautorizacion, otroasignado=0)
        finally:
            con.close()

    else:  # o sea es un cliente nuevo
        sin_extension = 1
        cuota_maxima = var_sistema['cuota_basica']
        direccion_cliente = d_data['calle']+d_data['num']
        deuda_en_la_casa = pgonecolumn(con, f"select sum(deuda) from clientes \
        where concat(calle,num)='{direccion_cliente}'")
        es_garante = 0
        monto_garantizado = 0
        # el cliente recien ingresado no tiene zona
        zona = ''
        if deuda_en_la_casa is None:
            deuda_en_la_casa = 0
        if d_data['dnigarante'] == '':
            dnigarante = 0
        else:
            dnigarante = d_data['dnigarante']
        inscliente = f"insert into clientes(sex,dni, nombre,calle,num,barrio,\
        tel,wapp,zona,modif_vdor,acla,horario,mjecobr,infoseven) values('F',\
        {d_data['dni']},'{d_data['nombre']}','{d_data['calle']}',\
        {d_data['num']},'{d_data['barrio']}','{d_data['tel']}',\
        '{d_data['wapp']}','-CAMBIAR',1,'{d_data['acla']}','','','')"
        try:
            pgexec(con,inscliente)
            idcliente = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
            ins = f"insert into datos(fecha, user, idcliente, fecha_visitar, \
            art,horarios, comentarios, cuota_maxima,deuda_en_la_casa,\
            sin_extension,monto_garantizado,vendedor,dnigarante,zona,resultado) values \
            (curdate(), '{current_user.email}',{idcliente},curdate(),'','',\
            'cliente enviado por vendedor', {cuota_maxima}, \
            '{deuda_en_la_casa}',{sin_extension}, {monto_garantizado},{vdor},\
            {dnigarante},'{zona}',0)"
            pgexec(con, ins)
            iddato = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
            insaut = f"insert into autorizacion(fecha,vdor,iddato,idcliente,\
            cuota_requerida,cuota_maxima,arts) values(current_timestamp(),\
            {vdor},{iddato},{idcliente},{d_data['cuota_requerida']},\
            {cuota_maxima},'{d_data['arts']}')"
            pgexec(con,insaut)
            idautorizacion = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
        except mysql.connector.Error as _error:
            con.rollback()
            error = _error.msg
            logging.warning(
                f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
            return make_response(error, 400)
        else:

            log(ins)
            log(insaut)
            return jsonify(idautorizacion=idautorizacion)
        finally:
            con.close()


@app.route('/4mY6khlmZKUzDRZDJkakr75iH')
@app.route('/vendedor/listavisitasvdor')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_visitasvdor():
    """Ruta que render pagina listavisitasvdor."""
    return render_template('listavisitasvdor.html')


@app.route('/VGIdj7tUnI1hWCX3N7W7WAXgU')
@app.route('/vendedor/getlistadodatosvendedor')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getlistadodatosvendedor():
    """Funcion que obtiene la lista de datos de un vendedor en particular."""
    logging.warning("GETLISTADODATOSVENDEDOR, %s", current_user.email)
    con = get_con()
    vdor = var_sistema[current_user.email]
    agrupar = var_sistema["agrupar"+str(vdor)]
    listadodatos = pglistdict(con, f"select datos.id, fecha, fecha_visitar,\
    art, horarios, comentarios,  dni, nombre,calle,num,acla,wapp,tel,barrio, \
    clientes.zona as zona, cuota_maxima,idcliente, sin_extension,idvta,\
    resultado,datos.dnigarante as dnigarante,quiere_devolver,vendedor,\
    wapp_verificado,tipo_devolucion,comentario_devolucion from  datos,clientes \
    where clientes.id = datos.idcliente \
    and vendedor={vdor} and (resultado = 0  or (resultado=1 \
    and quiere_devolver=1) or (resultado=1 and date(fecha_definido)=\
    curdate())) and fecha_visitar <=curdate() and enviado_vdor=1 order by id \
                              desc")
    return jsonify(listadodatos=listadodatos, agrupar=agrupar)


@app.route('/pnZWxv9Nicwt6TQ6zxohzvats/<int:iddato>')
@app.route('/vendedor/getdato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getdato(iddato):
    """Simple funcion que levanta un dato dado su id."""
    con = get_con()
    dato = pgdict(con, f"select datos.id, fecha, fecha_visitar,\
    art, horarios, comentarios,  dni, nombre,calle,num,acla,wapp,tel,barrio, \
    clientes.zona as zona, cuota_maxima,idcliente, sin_extension,vendedor, \
    datos.dnigarante as dnigarante,idvta,monto_vendido,nosabana,\
    wapp_verificado, auth_sinwapp_verificado, quiere_devolver, tipo_devolucion,\
    comentario_devolucion from datos, clientes where \
                  clientes.id = datos.idcliente and datos.id={iddato}")
    return jsonify(dato=dato)


@app.route('/kHEhacFNmI2vflFHBbaT1AQ1Z')
@app.route('/vendedor/getlistadoarticulos')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getlistadoarticulos():
    """Simple funcion que levanta la lista de articulos activos."""
    con = get_con()
    articulos = pglistdict(
        con,
        "select art,cuota from articulos where activo=1 \
    order by art")
    return jsonify(articulos=articulos)


@app.route('/uQ3gisetQ8v0n6tw81ORnpL1s', methods=['POST'])
@app.route('/vendedor/editarwapp', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor', 'cobrador'])
def vendedor_editarwapp():
    """Proceso para editar el wapp del cliente."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    wapp = d_data['wapp']
    if wapp!='' and wapp is not None and wapp != 'INVALIDO':
        try:
            comprueba_si_wapp_en_uso = pglist(con, f"select id from clientes \
                        where wapp={wapp} and id!={d_data['idcliente']}")
            if len(comprueba_si_wapp_en_uso)>0:
                return make_response("ese wapp ya esta en uso",400)
        except mysql.connector.Error as _error:
            con.rollback()
            error = _error.msg
            logging.warning(
                f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
            return make_response(error, 400)
    wapp_viejo = pgonecolumn(con, f"select wapp from clientes where id= \
    {d_data['idcliente']}")
    upd = f"update clientes set wapp='{d_data['wapp']}' where \
    id={d_data['idcliente']}"
    if wapp_viejo and wapp_viejo != 'INVALIDO':
        inslogcambio = f"insert into logcambiodireccion(idcliente,wapp,fecha) \
        values ({d_data['idcliente']},'{wapp_viejo}', current_date())"
    else:
        inslogcambio = None

    try:
        pgexec(con,upd)
        if inslogcambio is not None:
            pgexec(con,inslogcambio)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:

        log(upd)
        return 'ok'
    finally:
        con.close()


@app.route('/HvjJNtFgF71pRYafzcTC74nUt', methods=['POST'])
@app.route('/vendedor/guardardatofechado', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_guardardatofechado():
    """Proceso para el fechado de un dato."""
    logging.warning("guardardatofechado, %s", current_user.email)
    vdor = var_sistema[current_user.email]
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    upd = f"update datos set fecha_visitar='{d_data['fecha_visitar']}' where \
    id = {d_data['id']}"
    ins = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{vdor},{d_data['id']},4,0)"

    try:
        pgexec(con,upd)
        pgexec(con,ins)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:

        log(upd)
        return 'ok'
    finally:
        con.close()


@app.route('/UtVc3f6y5hfxu2dPmcrV9Y7mc/<int:iddato>')
@app.route('/vendedor/anulardato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_anulardato(iddato):
    """Proceso para anular un dato."""
    logging.warning("anulardato, %s", current_user.email)
    vdor = var_sistema[current_user.email]
    con = get_con()
    upd = f"update datos set resultado=2, fecha_definido=current_timestamp()\
    where id = {iddato}"
    ins = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{vdor},{iddato},2,0)"

    try:
        pgexec(con,upd)
        pgexec(con,ins)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:

        log(upd)
        return 'ok'
    finally:
        con.close()


@app.route('/gJUmonE8slTFGZqSKXSVwqPJ1/<int:iddato>')
@app.route('/vendedor/mudodato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_mudodato(iddato):
    """Proceso para registrar la mudanza de un cliente."""
    logging.warning("mudodato, %s", current_user.email)
    vdor = var_sistema[current_user.email]
    con = get_con()
    idcliente = pgonecolumn(con, f"select idcliente from datos where \
    id={iddato}")
    upd = f"update datos set resultado=5, fecha_definido=current_timestamp()\
    where id = {iddato}"
    ins = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{vdor},{iddato},5,0)"
    updcliente = f"update clientes set mudo=1,mudofallecio_proceso=1 where id={idcliente}"
    inscomentario = f"insert into comentarios(idcliente, ingreso, comentario) \
    values({idcliente},'{current_user.email}','puesto como mudado por \
    vendedor {vdor}')"

    try:
        pgexec(con,upd)
        pgexec(con,ins)
        pgexec(con,updcliente)
        pgexec(con,inscomentario)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:

        log(upd)
        log(updcliente)
        return 'ok'
    finally:
        con.close()


@app.route('/sLTFCMArYAdVsrEgwsz7utyRi/<int:iddato>')
@app.route('/vendedor/falleciodato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_falleciodato(iddato):
    """Proceso para registrar el fallecimiento de un cliente."""
    logging.warning("falleciodato, %s", current_user.email)
    vdor = var_sistema[current_user.email]
    con = get_con()
    idcliente = pgonecolumn(con, f"select idcliente from datos where id=\
    {iddato}")
    upd = f"update datos set resultado=6, fecha_definido=current_timestamp()\
    where id = {iddato}"
    ins = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{vdor},{iddato},6,0)"
    updcli = f"update clientes set zona='-FALLECIDOS', modif_vdor=1,mudofallecio_proceso=1 where id=\
    {idcliente}"
    inscomentario = f"insert into comentarios(idcliente, ingreso, comentario) \
    values({idcliente},'{current_user.email}','puesto como fallecido por \
    vendedor {vdor}')"

    try:
        pgexec(con,upd)
        pgexec(con,ins)
        pgexec(con,updcli)
        pgexec(con,inscomentario)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:

        log(upd)
        log(updcli)
        return 'ok'
    finally:
        con.close()


@app.route('/fc3vpQG6SzEH95Ya7kTJPZ48M', methods=['POST'])
@app.route('/vendedor/validardni', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_validardni():
    """Proceso para validar un DNI."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    logging.warning(d_data)
    dni = pgonecolumn(con, f"select dni from clientes where id={d_data['id']}")
    if d_data['dni'] != '' and dni == int(d_data['dni']):
        return make_response('aprobado', 200)
    return make_response('error', 400)


@app.route('/vaHQ2gFYLW2pIWSr5I0ogCL0k', methods=['POST'])
@app.route('/vendedor/registrarautorizacion', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_registrarautorizacion():
    """Proceso para registrar un pedido de autorizacion."""
    logging.warning("registrarautorizacion, %s", current_user.email)
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    vdor = var_sistema[current_user.email]
    if 'dnigarante' in d_data:
        dnigarante_propuesto = d_data['dnigarante']
    else:
        dnigarante_propuesto = ''
    ins = f"insert into autorizacion(fecha,vdor,iddato,idcliente,\
    cuota_requerida,cuota_maxima,arts,dnigarante_propuesto) values\
        (current_timestamp(),\
    {vdor},{d_data['id']},{d_data['idcliente']},{d_data['cuota_requerida']},\
    {d_data['cuota_maxima']},'{d_data['arts']}','{dnigarante_propuesto}')"
    logging.warning(ins)

    try:
        if len(str(dnigarante_propuesto)) > 0:
            upddato = f"update datos set dnigarante='{dnigarante_propuesto}' \
                where id={d_data['id']}"
            logging.warning(upddato)
            pgexec(con,upddato)
        pgexec(con,ins)
        idautorizacion = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:

        log(ins)
        return jsonify(idautorizacion=idautorizacion)
    finally:
        con.close()


@app.route('/vendedor/getlistadoautorizados')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getlistadoautorizados():
    """Funcion que entrega lista de autorizaciones pendientes."""
    con = get_con()
    listadoautorizados = pglistdict(con, "select autorizacion.id as id,\
    datos.id as iddato,datos.fecha as fecha, datos.user as user, nombre, \
    datos.resultado as resultado, datos.art as art, datos.cuota_maxima as \
    cuota_maxima, datos.sin_extension as sin_extension,datos.nosabana as \
    nosabana, datos.deuda_en_la_casa as deuda_en_la_casa,datos.vendedor as \
    vendedor, clientes.novendermas as novendermas, clientes.incobrable as \
    incobrable,clientes.sev as sev, clientes.baja as baja, autorizacion.fecha \
    as fechahora, autorizacion.cuota_requerida as cuota_requerida,\
    autorizacion.tomado as tomado, autorizacion.arts as arts,horarios,\
    comentarios,(select count(*) from autorizacion where \
    autorizacion.idcliente=clientes.id) as cnt,autorizacion.idcliente, \
    autorizacion.dnigarante_propuesto as dnigarante from \
    datos, autorizacion,clientes  where datos.idcliente=clientes.id and \
    autorizacion.iddato=datos.id and autorizacion.autorizado=0 and \
    autorizacion.rechazado=0 and autorizacion.sigueigual=0 and datos.resultado \
    is null")
    cuotabasica = var_sistema['cuota_basica']
    return jsonify(listadoautorizados=listadoautorizados,
                   cuotabasica=cuotabasica)


@app.route('/vendedor/getlistadoautorizadosporid/<int:idcliente>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getlistadoautorizadosporid(idcliente):
    """Funcion que entrega la lista de autorizaciones que tuvo un cliente."""
    con = get_con()
    listadoautorizadosporid = pglistdict(con, f"select datos.id as id,\
    datos.fecha as fecha, datos.user as user, nombre, datos.resultado as \
    resultado, datos.art as art, datos.cuota_maxima as cuota_maxima, \
    datos.sin_extension as sin_extension,datos.nosabana as nosabana, \
    datos.deuda_en_la_casa as deuda_en_la_casa,datos.vendedor as vendedor, \
    clientes.novendermas as novendermas, clientes.incobrable as incobrable,\
    clientes.sev as sev,clientes.baja as baja, autorizacion.fecha as fechahora,\
    autorizacion.cuota_requerida as cuota_requerida, autorizacion.arts as arts,\
    horarios,comentarios,(select count(*) from autorizacion where \
    autorizacion.idcliente=clientes.id) as cnt from datos,autorizacion,\
    clientes  where datos.idcliente=clientes.id and autorizacion.iddato=\
    datos.id and autorizacion.idcliente={idcliente}")
    return jsonify(listadoautorizadosporid=listadoautorizadosporid)


@app.route('/vendedor/autorizardato/<int:idauth>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_autorizardato(idauth):
    """Proceso para autorizar un dato."""
    con = get_con()
    cuota_requerida = pgonecolumn(con, f"select cuota_requerida from \
    autorizacion where id={idauth}")
    upd_aut = f"update autorizacion set autorizado=1,rechazado=0,sigueigual=0,\
    user = '{current_user.email}' where id={idauth}"
    iddato = pgonecolumn(con, f"select iddato from autorizacion where \
    id={idauth}")
    upd_dat = f"update datos set cuota_maxima = {cuota_requerida}, \
    autorizado=1,rechazado=0,sigueigual=0,enviado_vdor=1, fecha_visitar=\
         curdate() where id={iddato}"
    con = get_con()

    try:
        pgexec(con,upd_aut)
        pgexec(con,upd_dat)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:

        log(upd_dat)
        log(upd_aut)
        return 'ok'
    finally:
        con.close()


@app.route('/vendedor/noautorizardato/<int:idauth>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_noautorizardato(idauth):
    """Proceso para NO autorizar un dato, y que siga igual, venda la basica."""
    con = get_con()
    upd_aut = f"update autorizacion set autorizado=0, user = \
    '{current_user.email}',rechazado=0,sigueigual=1 where id={idauth}"
    iddato = pgonecolumn(con, f"select iddato from autorizacion where \
    id={idauth}")
    upddato = f"update datos set rechazado=0, autorizado=0,sigueigual=1, \
    resultado=null, enviado_vdor=1 where id={iddato}"
    con = get_con()

    try:
        pgexec(con,upd_aut)
        pgexec(con,upddato)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:

        log(upd_aut)
        log(upddato)
        return 'ok'
    finally:
        con.close()


@app.route('/vendedor/rechazardato/<int:idauth>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_rechazardato(idauth):
    """Proceso para rechazar dato, no se puede vender alli."""
    con = get_con()
    upd_aut = f"update autorizacion set autorizado=0, user = \
    '{current_user.email}',rechazado=1,sigueigual=0 where id={idauth}"
    iddato = pgonecolumn(con, f"select iddato from autorizacion where \
    id={idauth}")
    upddato = f"update datos set rechazado=1, autorizado=0, sigueigual=0, \
    resultado=8 where id={iddato}"
    con = get_con()

    try:
        pgexec(con,upd_aut)
        pgexec(con,upddato)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:

        log(upd_aut)
        log(upddato)
        return 'ok'
    finally:
        con.close()


@app.route('/xuNzBi4bvtSugd5KbxSQzD0Ey', methods=['POST'])
@app.route('/vendedor/pasarventa', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_pasarventa():
    """Proceso para pasar una venta por el vendedor."""
    con = get_con()
    d_data = json.loads(request.data.decode("UTF-8"))
    vdor = var_sistema[current_user.email]
    ant = 0
    cant_cuotas = 6
    imp_cuota = d_data['cuota']
    per = 1
    if d_data['dnigarante']:
        garantizado = 1
    else:
        garantizado = 0
    if es_dni_valido(d_data['dnigarante']):
        dnigarante = d_data['dnigarante']
    else:
        dnigarante = 0

    insvta = f"insert into ventas(fecha,idvdor,ant,cc,ic,p,primera,idcliente,\
    garantizado,dnigarante) values(curdate(),{vdor},{ant},{cant_cuotas},{imp_cuota},{per},\
    '{d_data['primera']}',{d_data['idcliente']},{garantizado},{dnigarante})"
    insvis = f"insert into visitas(fecha,hora,vdor,iddato,result,\
    monto_vendido) values(curdate(),curtime(),{vdor},{d_data['id']},1,{imp_cuota*cant_cuotas})"
    try:
        ultinsvta = pgonecolumn(con, "select valor from variables where id=13")
        listart = ''
        for item in d_data['arts']:
            listart += item['cnt']
            listart += item['art']
        if str(ultinsvta) != f"{cant_cuotas}{imp_cuota}{per}{d_data['primera']}{d_data['idcliente']}\
        {d_data['id']}{listart}":
            pgexec(con, insvis)
            pgexec(con, insvta)

            idvta = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
            # lo siguiente ha sido trasladado al trigger ventas_ins_clientes
            # upd = f"update datos set resultado=1, monto_vendido={imp_cuota*6}, \
            # fecha_definido=# current_timestamp(), idvta={idvta} where \
            #     id={d_data['id']}"
            # pgexec(con,upd)
            listart = ''
            for item in d_data['arts']:
                listart += item['cnt']
                listart += item['art']
                cnt = item['cnt']
                art = item['art']
                imp_cuota = item['cuota']
                if 'color' in item:
                    color = item['color']
                else:
                    color = ''
                costo = pgonecolumn(con, f"select costo from articulos where \
                art='{art}'")
                ins = f"insert into detvta(idvta,cnt,art,cc,ic,costo,\
                devuelta,color) values({idvta},{cnt},'{art}',6,{imp_cuota},\
                {costo},0,'{color}')"
                pgexec(con, ins)
                log(ins)
            inslog = f"update variables set valor='{cant_cuotas}{imp_cuota}{per}{d_data['primera']}\
            {d_data['idcliente']}{d_data['id']}{listart}' where id=13"
            pgexec(con, inslog)
              # pruebo con hacer commit instantaneo de la variable
            # que quizas no sea leida pq no se hizo el commit.
        else:
            logging.warning("duplicacion de venta %s Dara cod 401", ultinsvta)
            return make_response('error de duplicacion de venta', 401)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        logging.warning(insvta, insvis)
        return make_response(error, 400)
    else:
        log(insvta)
        return 'ok'
    finally:
        con.close()


@app.route('/G9S85pbqWVEX17nNQuOOnpxvn/<int:iddato>')
@app.route('/vendedor/noestabadato/<int:iddato>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_noestabadato(iddato):
    """Proceso de noestaba. Vendedor visita y no esta el cliente."""
    logging.warning("noestabadato, %s", current_user.email)
    con = get_con()
    vdor = var_sistema[current_user.email]
    ins = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{vdor},{iddato},3,0)"
    id = pgonecolumn(con,f"select idcliente from datos where id={iddato}")
    sexo,nombre,wapp = pgtuple(con,f"select sex,nombre,wapp from clientes where id={id}")
    if sexo=='F':
        sufijo = 'a'
    else:
        sufijo = 'o'
    msg_noestaba = f"""Estimad{sufijo} {nombre}: hoy l{sufijo} hemos visitado de Romitex, Ud supo ser cliente nuestr{sufijo} y veniamos a mostrarle los nuevos articulos que han llegado. Tenemos acolchados, sabanas, cortinas, manteles, toallones todo en 6 cuotas mensuales fijas y con entrega inmediata. No dude en avisarnos en que horario podemos encontrarl{sufijo}, sin compromiso le mostraremos y explicaremos el plan 🤗."""

    try:
        pgexec(con,ins)
        # msg_noestaba = urllib.parse.quote(msg_noestaba)
        response = send_msg_whatsapp(id,wapp,msg_noestaba)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:

        return response
    finally:
        con.close()


@app.route('/F8cq9GzHJIG9hENBo0Xq7hdH7')
@app.route('/vendedor/getvisitasvdor')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getvisitasvdor():
    """Funcion que entrega la lista de visitas hechas por un vendedor."""
    logging.warning("getvisitasvdor, %s", current_user.email)
    con = get_con()
    vdor = var_sistema[current_user.email]
    visitasvendedor = pglistdict(con, f"select visitas.fecha as fecha,\
    cast(hora as char) as hora, visitas.vdor as vdor, result, \
    visitas.monto_vendido as monto_vendido, idcliente,nombre,calle,num,\
    clientes.zona as zona from visitas,datos,clientes where visitas.iddato=\
    datos.id and clientes.id=datos.idcliente and visitas.vdor={vdor} and \
    visitas.fecha>date_sub(curdate(),interval 6 day) order by \
    visitas.fecha desc,hora")
    fechasvisitas = pglistdict(
        con, f"select visitas.fecha as fecha, visitas.vdor \
    as vdor, count(*) as cnt, sum(visitas.monto_vendido) as monto_vendido \
    from visitas,datos where visitas.iddato=datos.id and visitas.vdor={vdor} \
    and visitas.fecha>date_sub(curdate(),interval 6 day) \
    group by visitas.fecha,visitas.vdor order by visitas.fecha,visitas.vdor \
    desc")
    return jsonify(visitasvendedor=visitasvendedor,
                   fechasvisitas=fechasvisitas)


@app.route('/3ZbXanrRQalY6JL5eOBi49Nyc', methods=["POST"])
@app.route('/vendedor/wappaut', methods=["POST"])
@login_required
@check_roles(['dev', 'gerente', 'admin', 'vendedor'])
def vendedor_wappaut():
    """Funcion que procesa el wapp de autorizacion.

    Si el tipo = 'retiro de zona' aparte de enviar wapp al wapp_auth envia un
    segundo wapp a mi."""

    d_data = json.loads(request.data.decode("UTF-8"))
    logging.warning("wappaut, %s", current_user.email)
    vdor = var_sistema[current_user.email]
    msg = d_data['msg']
    if "tipo" in d_data and d_data['tipo']== "retiro zona":
        msg = f"Retiro zona vdor {vdor}"
    else:
        msg = f"Autorizacion para el vdor {vdor}"
    # wapp1 = var_sistema['wapp_auth']
    # wapp2 = var_sistema['wapp_auth2']
    wapp = '3512411963'
    # logging.warning(f"wapp1 {wapp1} wapp2 {wapp2}")
    logging.warning(f"wapp autorizacion a {wapp}")
    try:
        # if wapp1:
        #     send_msg_whatsapp(0, wapp1, msg)
        # if wapp2:
        #     send_msg_whatsapp(0, wapp2, msg)
        send_msg_whatsapp(0, wapp, msg)
    except mysql.connector.Error as _error:
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    else:
        return 'ok'


@app.route('/hX53695XAOpaLY9itLgmghkhH', methods=["POST"])
@app.route('/vendedor/wapp', methods=["POST"])
@login_required
@check_roles(['dev', 'gerente', 'admin', 'vendedor'])
def vendedor_wapp():
    """Funcion que procesa wapp enviados por el vendedor."""
    d_data = json.loads(request.data.decode("UTF-8"))
    idcliente = d_data['idcliente']
    wapp = d_data['wapp']
    msg = d_data['msg']
    if wapp:
        response = send_msg_whatsapp(idcliente, wapp, msg)
        if response is None:
            response = 'Encolado'
        return response
    return 'error', 400


@app.route('/4qUK6eNZnCYjIiGTt3HSj2YDp', methods=['POST'])
@app.route('/vendedor/filewapp', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'admin', 'vendedor'])
def vendedor_filewapp():
    """Funcion que procesa el envio de pdf por el vendedor."""

    d_data = json.loads(request.data.decode("UTF-8"))
    wapp = d_data['wapp']
    idcliente = d_data['idcliente']
    file = d_data['file']
    if wapp:
        response = send_file_whatsapp(
            idcliente, f"https://fedesal.lol/pdf/{file}.pdf", wapp)
        return jsonify(response=response)
    return 'error', 400


@app.route('/MeHzAqFYsbb78KAVFAGTlZRW9/<dni>')
@app.route('/vendedor/buscaclientepordni/<dni>')
@login_required
@check_roles(['dev', 'gerente', 'admin', 'vendedor'])
def vendedor_buscaclientepordni(dni):
    """Simple funcion que levanta datos del cliente por dni."""
    con = get_con()
    cliente = pgdict(con, f"select * from clientes where dni={dni}")
    if cliente:
        return jsonify(cliente=cliente)
    return make_response("error", 401)


@app.route('/k8E5hsVs4be3jsJJaob6OQmAX')
@app.route('/vendedor/getcargavendedor')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getcargavendedor():
    """Funcion entrega lista de articulos a cargar para el vendedor."""
    logging.warning("getcargavendedor, %s", current_user.email)
    con = get_con()
    vdor = var_sistema[current_user.email]
    artvendedor = pglistdict(con, f"select sum(detvta.cnt) as cnt,\
    detvta.art as art, group_concat(color) as colores from detvta,ventas \
    where detvta.idvta=ventas.id and cargado=0 and idvdor={vdor} group by \
    detvta.art")
    # no se filtra mas por devuelta=0, solo por cargado=0
    return jsonify(artvendedor=artvendedor)


@app.route('/TWGQV0TM0p7Oa9tMPvrNWIHyd')
@app.route('/vendedor/cargararticulos')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_cargararticulos():
    """Ruta que renderiza la pagina cargarart."""
    return render_template('cargarart.html')


@app.route('/DDFEwfGEDYv5UHTVgcDPFUWm1')
@app.route('/vendedor/comisionesvdor')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_comisionesvdor():
    """Ruta que renderiza la pagina comisionesvdor."""
    return render_template('comisionesvdor.html')


@app.route('/IrV7gmqz4Wu8Q8rwmXMftphaB')
@app.route('/vendedor/getcomisionesparavendedor')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getcomisionesparavendedor():
    """Funcion que entrega lista de comisiones pendiente para el vendedor."""
    logging.warning("getcomisionesparavendedor, %s", current_user.email)
    vdor = var_sistema[current_user.email]
    com = 'com'+str(vdor)
    comision = var_sistema[com]
    con = get_con()
    comisiones = pglistdict(con, f"select date(fecha_definido) as fecha,\
    monto_vendido*{comision} as com, idvta as id from datos where \
    vendedor={vdor} and com_pagada=0 and monto_vendido>0 order by \
    date(fecha_definido)")
    devoluciones = pglistdict(
        con, f"select fecha,monto_devuelto*{comision}*(-1) \
    as com, idvta as id from datos where vendedor={vdor} and com_pagada_dev=0 \
    and monto_devuelto!=0 order by fecha")
    fechascomisiones = pglistdict(
        con, f"select date(fecha_definido) as fecha,  \
    count(*) as cnt,sum(case when com_pagada=0 then monto_vendido*{comision} \
    when com_pagada=1 then 0 end)+sum(monto_devuelto*{comision}*(-1)) as \
    comision from datos where ((resultado=1 and com_pagada=0) or \
    (monto_devuelto>0 and com_pagada_dev=0)) and vendedor={vdor} group by \
    date(fecha_definido) order by date(fecha_definido) desc")
    if devoluciones:
        comisiones = comisiones+devoluciones
    return jsonify(comisiones=comisiones, fechascomisiones=fechascomisiones)


@app.route('/u0IEJT3i1INZpKoNKbyezlfRy/<int:auth>')
@app.route('/vendedor/isatendido/<int:auth>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_isatendido(auth):
    """Simple funcion que marca si una autorizacion ya esta atendida."""
    con = get_con()
    tomado = pgonecolumn(con, f"select tomado from autorizacion where id=\
    {auth}")
    return jsonify(tomado=tomado)


@app.route('/ymIVWKdjgnCeJvo2zcodwRTQM/<int:auth>')
@app.route('/vendedor/isrespondidoauth/<int:auth>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_isrespondidoauth(auth):
    """Funcion que entrega la respuesta que tuvo la autorizacion."""
    con = get_con()
    respuesta, motivo = pgtuple(con, f" select \
                            case when autorizado=1 then 'autorizado' \
                                 when rechazado=1 then 'rechazado' \
                                 when sigueigual=1 then 'sigueigual' end \
                            as respuesta, motivo \
    from autorizacion where id={auth}")
    if motivo is None:
        motivo = ''
    logging.warning(f"respuesta{respuesta}, motivo:{motivo}")
    return jsonify(respuesta=respuesta, motivo=motivo)


@app.route('/quBXVVWkNijghkJ4JpwSgluJQ', methods=['POST'])
@app.route('/vendedor/imprimirfichapantalla', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_imprimirfichapantalla():
    """Funcion para imprimir ficha de cliente en pantalla a vendedor."""
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    idcliente = d['idcliente']
    dni = pgonecolumn(con, f"select dni from clientes where id={idcliente}")
    ficha(con, [dni])
    con.close()
    return send_file('/home/hero/ficha.pdf')


@app.route('/S0rjYKB35QIcHunPmebg2tmr1', methods=['POST'])
@app.route('/vendedor/visitadevolucion', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_visitadevolucion():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    iddato = pgonecolumn(con, f"select id from datos where idvta={d['idvta']}")
    updvta = f"update ventas set retirado=1,comentario_retirado='{d['msg']}' where id={d['idvta']}"
    ins = f"insert into visitas(fecha,hora,vdor,iddato,result,monto_vendido) \
    values(curdate(),curtime(),{d['vendedor']},{iddato},7,0)"
    try:
        pgexec(con, ins)
        pgexec(con, updvta)
    except mysql.connector.Error as _error:
            con.rollback()
            error = _error.msg
            logging.warning(
                f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
            return make_response(error, 400)
    else:
        con.close()
        return 'ok'


@app.route('/PssVAeUAoTjbuFuPxRGWdQeyn/<string:wapp>/<int:idcliente>')
@app.route('/vendedor/asignawappacliente/<string:wapp>/<int:idcliente>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_asignawappacliente(wapp,idcliente):
    con = get_con()
    clientes_con_ese_wapp = pglist(con, f"select id from clientes where \
                                   wapp='{wapp}'")
    if clientes_con_ese_wapp!='':
        clientes_con_ese_wapp = listsql(clientes_con_ese_wapp)
        updborrar = f"update clientes set wapp='' where id in \
            {clientes_con_ese_wapp}"
        updasignar = f"update clientes set wapp='{wapp}' where id={idcliente}"
        insverificables = f"insert into verificables(wapp,idcliente) values(\
            '{wapp}',{idcliente})"
        try:
            pgexec(con, updborrar)
            pgexec(con, updasignar)
            pgexec(con, insverificables)
        except mysql.connector.Error as _error:
            con.rollback()
            error = _error.msg
            logging.warning(
                f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
            return make_response(error, 400)
        else:

            return 'ok'
        finally:
            con.close()
    else:
        return make_response('ese idcliente no existe',400)


@app.route('/vendedor/buscarsiexistewapp/<string:wapp>/<int:idcliente>')
@app.route('/M6Kbc3KfN6san3nK9nUKy3zSi/<string:wapp>/<int:idcliente>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_buscarsiexistewapp(wapp,idcliente):
    con = get_con()
    existe = len(pglist(con,f"select id from clientes where wapp={wapp} and \
                    wapp_verificado=1 and id != {idcliente}"))
    return jsonify(existe=existe)


@app.route('/GPeryq1AYmObDUlpuXpQOGXAu')
@app.route('/cobrador/listafichas')
@login_required
@check_roles(['dev','gerente','cobrador','vendedor'])
def cobrador_listafichas():
    """Muestra pagina lista de fichas."""
    return render_template('listafichas.html')


@app.route('/pMsu7gxjhVpTlfN6gaTMN9rCv')
@app.route('/cobrador/planilla')
@login_required
@check_roles(['dev','gerente','cobrador','vendedor'])
def cobrador_planilla():
    """Muestra planilla de cobranza de cobrador para rendir."""
    return render_template('planillacobr.html')


@app.route('/wMV70TmnTmxOVv0iu2RC9hXNi')
@app.route('/vendedor/verstock')
@login_required
@check_roles(['dev','gerente','cobrador','vendedor'])
def vendedor_verstock():
    """Muestra stock personal del vendedor para contar y dar conformidad."""
    return render_template('verstock.html')


@app.route('/plzdCxZQMZVcHAYTitEcN1Ugi')
@app.route('/cobrador/getlistadofichas')
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


@app.route('/XD8y31yQk8o1wm9Xx5y7psDfq/<int:idcliente>/<pmovto>')
@app.route('/cobrador/fecharficha/<int:idcliente>/<pmovto>')
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

    try:
        pgexec(con,upd)
        pgexec(con,insvisita)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:

        return 'ok'
    finally:
        con.close()


@app.route('/lfM7683w0nFC8Fvl9YCrqIgu8/<int:idcliente>')
@app.route('/cobrador/noestabaficha/<int:idcliente>')
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

    try:
        pgexec(con,ins)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:

        return 'ok'
    finally:
        con.close()


@app.route('/W6BbKGuF9P62bEwUd9iG45nSj/<int:idcliente>')
@app.route('/cobrador/mudoficha/<int:idcliente>')
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

    try:
        pgexec(con,ins)
        pgexec(con,upd)
        pgexec(con,inscomentario)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:

        return 'ok'
    finally:
        con.close()


@app.route('/2WEhYdAcDYH6D3xUlgrZnMLlS/<int:idcliente>')
@app.route('/cobrador/fallecioficha/<int:idcliente>')
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

    try:
        pgexec(con,ins)
        pgexec(con,upd)
        pgexec(con,inscomentario)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:

        return 'ok'
    finally:
        con.close()


@app.route('/Rd76eHrCKpkPRpt2NOjiov0q2')
@app.route('/cobrador/imprimirfichapantalla' , methods=['POST'])
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


@app.route('/lFgengVKS37IFtKfPi7Qzchgz')
@app.route('/cobrador/pasarpagos' , methods=['POST'])
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

            return 'ok'
    finally:
            con.close()


@app.route('/yGaGGogxb0ss1wGJMzS08eTvj')
@app.route('/cobrador/getvisitascobrador')
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


@app.route('/MvJgBxRvsymMT6GSTaEa3BcPn')
@app.route('/cobrador/getcobranzahoy')
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


@app.route('/lRHtjv5m60nvavfwRUQYpPjXC')
@app.route('/cobrador/getcobroscobr')
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


@app.route('/CZI6X7BC6wNtseAN22HiXsmqc')
@app.route('/ventas/getcalles')
@login_required
@check_roles(['dev','gerente','admin','vendedor'])
def ventas_getcalles():
    con = get_con()
    calles = pglist(con, f"select calle from calles order by calle")
    con.close()
    return jsonify(result=calles)


@app.route('/w98LuAaWBax9c6rENQ2TjO3PR')
@app.route('/ventas/getbarrios')
@login_required
@check_roles(['dev','gerente','admin','vendedor'])
def ventas_getbarrios():
    con = get_con()
    barrios = pglist(con, f"select barrio from barrios order by barrio")
    con.close()
    return jsonify(result=barrios)


@app.route('/DNmetyHCIOicjxkTThv0MYuIQ/<int:idcliente>')
@app.route('/buscador/obtenerventasporidcliente/<int:idcliente>')
@login_required
@check_roles(['dev','gerente','admin','cobrador','vendedor'])
def buscar_obtenerventasporidcliente(idcliente):
    """Entrega lista de ventas por idcliente."""
    sql = f"select * from ventas where idcliente={idcliente} and saldo>0 order \
    by id desc"
    con = get_con()
    ventas = pglistdict(con, sql)
    con.close()
    return jsonify(ventas=ventas)


@app.route('/gUHjeS2q49o5CoZRzKL5mpSF6', methods=['POST'])
@app.route('/pagos/pasarpagos', methods=['POST'])
@login_required
@check_roles(['dev', 'gerente', 'admin', 'cobrador', 'vendedor'])
def pagos_pasarpagos():
    con = get_con()
    d = json.loads(request.data.decode("UTF-8"))
    if (d['rec'] == ''):
        d['rec'] = 0
    ins = f"insert into pagos(idvta,fecha,imp,rec,rbo,cobr,idcliente,rendido) \
    values({d['idvta']},'{d['fecha']}',{d['imp']},{d['rec']},{d['rbo']},\
    {d['cobr']},{d['idcliente']},{d['rendido']})"
    pgexec(con, ins)
    # Si el pago proviene del cobrador directamente con pmovto incluido:
    if (d['pmovto'] is not None):
        upd = f"update clientes set pmovto='{d['pmovto']}' where id = \
            {d['idcliente']}"
        pgexec(con, upd)
        log(upd)
    con.close()
    log(ins)
    return 'ok'


@app.route('/KgcigrlPdMMjIFsWucdrEVDzX')
@app.route('/utilidades/imprimirlistaprecios')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def utilidades_imprimirlistaprecios():
    return send_file(os.path.join('/home/hero/documentos/impresos', \
                                  'listaprecios.pdf'))


@app.route('/PVYbQdohCbAqADI8D65C6Jeyk')
@app.route('/vendedor/getzonasporsectores')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getzonasporsectores():
    con = get_con()
    zonas = pglistdict(con, "select zona,sector from zonas where sector is \
    not null")
    recomendaciones = pglistdict(con, "select art,recomendacion from articulos \
    where recomendacion is not null")
    return jsonify(zonas=zonas, recomendaciones=recomendaciones)


@app.route('/ei6GWPF1PmBSLPC5b4zFMtlTg')
@app.route('/vendedor/getstockvdor')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_getstockvdor():
    con = get_con()
    vdor = var_sistema[current_user.email]
    stockvdor = pglistdict(con, f"select sum(cnt) as cnt, art from stockvdor \
    where vdor={vdor} group by art order by art")
    return jsonify(stockvdor=stockvdor)


@app.route('/Chwxov7tfRBfT6DiPImui03D9')
@app.route('/vendedor/contadoconforme')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_contadoconforme():
    con = get_con()
    vdor = var_sistema[current_user.email]
    fecha = str(time.ctime(time.time()))
    wapp = var_sistema['wapp_auth']
    msg = f"Mercaderia contada conforme vendedor:{vdor} fecha:{fecha} -"
    stockvdor = pglistdict(con, f"select sum(cnt) as cnt, art from stockvdor \
    where vdor={vdor} group by art order by art")
    for item in stockvdor:
        if int(item['cnt'])>0:
            msg += f" {item['cnt']} {item['art']} - "
    msg = msg.replace('1/2','y media')
    msg = msg.replace('/','-')
    send_msg_whatsapp(0,wapp,msg)
    con.close()
    return 'ok'



@app.route('/uAiiulEHyn5KoZ3JRcafe9a8k/<idcliente>')
@app.route('/vendedor/metodopagotransferencia/<idcliente>')
@login_required
@check_roles(['dev', 'gerente', 'vendedor'])
def vendedor_metodopagotransferencia(idcliente):
    con = get_con()
    upd = f"update clientes set zona='TRANS_SANTANDER' where id={idcliente}"
    pgexec(con, upd)
    return 'ok'



@app.route('/pDfkNKQMQvgp8Zbqa0C6ETYAh/<int:idvta>')
@app.route('/ventas/marksendwapp/<int:idvta>')
@login_required
@check_roles(['dev','gerente','vendedor'])
def ventas_marksendwapp(idvta):
    con = get_con()
    upd = f"update ventas set sendwapp=1 where id={idvta} and pp=0"
    # pp=0 asegura que no se marcaran los planes de pago
    pgexec(con, upd)
    con.close()
    return 'ok'
