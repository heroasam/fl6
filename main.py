# -*- coding: utf-8 -*-
from flask import Flask, json
from flask import render_template, url_for, request, redirect, make_response, session, flash, g, send_file
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from flask_cors import CORS
from flask_cors import cross_origin
from flask_wtf import csrf
<<<<<<< Updated upstream
#from flask_socketio import SocketIO, emit
=======
# from flask_socketio import SocketIO, emit
import gevent
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
>>>>>>> Stashed changes
from werkzeug.urls import url_parse
from lib import *
from formularios import *
from ventas import ventas
from stock import stock
from pagos import pagos
from buscador import buscador
from fichas import fichas
from utilidades import utilidades
from conta import conta
from vendedor import vendedor
from cobrador import cobrador
import mysql.connector
import simplejson as json
from con import get_con, log, check_roles
from datetime import datetime
import logging
import time
import threading
import base64


app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
CORS(app)

csrf = CSRFProtect(app)
login = LoginManager(app)
login.login_view = "login"
bcrypt = Bcrypt(app)
<<<<<<< Updated upstream
#socketio = SocketIO(app)
=======
# socketio = SocketIO(app)
>>>>>>> Stashed changes


app.register_blueprint(ventas)
app.register_blueprint(stock)
app.register_blueprint(pagos)
app.register_blueprint(buscador)
app.register_blueprint(fichas)
app.register_blueprint(utilidades)
app.register_blueprint(conta)
app.register_blueprint(vendedor)
app.register_blueprint(cobrador)


def verifica_login(email):
    con = get_con()
    ins = f"insert into falsologin(email,time) values('{email}',{int(time.time())})"
    cur = con.cursor()
    try:
        cur.execute(ins)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        return make_response(error, 400)
    else:
        con.commit()
        log(ins)
        cnt = pgonecolumn(con, f"select count(*) from falsologin where email=\
        '{email}' and time>{int(time.time())-3600}")
        if cnt>4:
            upd = f"update users set auth=0 where email='{email}'"
            cur.execute(upd)
            con.commit()
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
            log(sel)
            log_login(user.email,'login',password)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                if session['roles']=='vendedor':
                    next_page = url_for('vendedor.vendedor_listadatos')
                elif session['roles']=='cobrador':
                    next_page = url_for('cobrador.cobrador_listafichas')
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
            cur = con.cursor()
            try:
                cur.execute(ins)
            except mysql.connector.Error as e:
                con.rollback()
                error = e.msg
                return make_response(error, 400)
            else:
                log(ins)
                con.commit()
                cur.close()
                flash("Registro correctamente ingresado")
                return redirect(url_for('login'))
        flash(error, category='error')
    return render_template('signup.html')


@app.route('/log1')
@login_required
@check_roles(['dev'])
def log1_log():
    f = open('/tmp/log.txt', "w")
    log = open('/var/log/app/1.log', "r")
    log1log = log.read()
    f.write(log1log)
    f.close()
    log.close()
    return send_file('/tmp/log.txt')


@app.route('/log2')
@login_required
@check_roles(['dev'])
def log2_log():
    """Muestra log de login."""
    f = open('/tmp/login.txt', "w")
    log = open('/home/hero/log/login.log', "r")
    log2log = list(reversed(log.readlines()))
    log2log[0] = log2log[0]+'\n'
    f.writelines(log2log)
    f.close()
    log.close()
    return render_template('/utilidades/log2.html', log2log=log2log)


@app.route('/log3')
@login_required
@check_roles(['dev'])
def log3_log():
    """Muestra log de wapp."""
    f = open('/tmp/wapp.txt', "w")
    log = open('/home/hero/log/wapp.log', "r")
    log3log = list(reversed(log.readlines()))
    log3log[0] = log3log[0]+'\n'
    f.writelines(log3log)
    f.close()
    log.close()
    return render_template('/utilidades/log3.html', log3log=log3log)


@app.route('/log4')
@login_required
@check_roles(['dev'])
def log4_log():
    """Muestra log de busquedas."""
    f = open('/tmp/busquedas.txt', "w")
    log = open('/home/hero/log/busquedas.log', "r")
    log4log = list(reversed(log.readlines()))
    log4log[0] = log4log[0]+'\n'
    f.writelines(log4log)
    f.close()
    log.close()
    return render_template('/utilidades/log4.html', log4log=log4log)


@app.route('/log5')
@login_required
@check_roles(['dev'])
def log5_log():
    """Muestra log de themes."""
    f = open('/tmp/themes.txt', "w")
    log = open('/home/hero/log/themes.log', "r")
    log5log = list(reversed(log.readlines()))
    log5log[0] = log5log[0]+'\n'
    f.writelines(log5log)
    f.close()
    log.close()
    return render_template('/utilidades/log5.html', log5log=log5log)


@app.route('/log6')
@login_required
@check_roles(['dev'])
def log6_log():
    """Muestra log de caja."""
    f = open('/tmp/caja.txt', "w")
    log = open('/home/hero/log/caja.log', "r")
    log6log = list(reversed(log.readlines()))
    log6log[0] = log6log[0]+'\n'
    f.writelines(log6log)
    f.close()
    log.close()
    return render_template('/utilidades/log6.html', log6log=log6log)


@app.route('/webhook' , methods=['POST'])
@cross_origin()
@csrf.exempt
def webhook():
    """api wapp webhook"""
    # read and parse input data
    # logging.error('funcion webhook llamada')
    con = get_con()
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        # logging.error(f"webhook {data}")
        if "message" in data:
            message = data["message"]
        else:
            message = ""
        sender = data["from"]
        if 'time' in data:
            tipo = data["tipo"]
            hora = str(data["time"])
            hora = datetime.strptime(hora, '%Y-%m-%d %H:%M:%S')
            timestamp = str(int(hora.timestamp()))+str(int(time.time()*1000000))[-6:-3]
            idtime = str(sender)+timestamp
            # logging.error(f"hora {hora} wapp {sender}")
            existe_msg = pgonecolumn(con,f"select id from wappsrecibidos where \
                                     fecha='{hora}' and wapp={sender}")
            # logging.error(f"existe_msg{existe_msg}")
            if existe_msg == '' or existe_msg is None:
                if 'media' in data:
                    # media = base64.b64encode(bytes(data["media"]["base64"], 'utf-8'))   
                    media = base64.b64decode(data["media"]["base64"])
                    # logging.info(media)
                    if tipo=='document' and message=='':
                        message = 'pdf'
                    elif tipo=='document' and message!='' and 'pdf' not in message:
                        message = message + ' ' + 'pdf'
                    elif tipo=='ptt':
                        message = 'audio'
                else:
                    media = ""
                api = data["api"]
                guardar_msg(sender,message,idtime,api,hora,media,tipo)  
                logging.error('se procede a guardar message')      
        else:
            idtime = str(sender)+str(int(time.time()*1000))
            guardar_msg(sender,message,idtime)
        return 'ok'


@app.route('/webhookapis' , methods=['POST'])
@cross_origin()
@csrf.exempt
def webhookapis():
    """api wapp webhook para apis."""
    # read and parse input data
    # logging.error('funcion webhook llamada')
    con = get_con()
    if request.method == 'POST':
        datos = json.loads(request.data.decode('utf-8'))
        for data in datos:
            # logging.error(f"webhook {data}")
            if "message" in data:
                message = data["message"]
            else:
                message = ""
            sender = data["from"]
            tipo = data["tipo"]
            hora = str(data["time"])
            hora = datetime.strptime(hora, '%Y-%m-%d %H:%M:%S')
            timestamp = str(int(hora.timestamp()))+str(int(time.time()*1000000))[-6:-3]
            idtime = str(sender)+timestamp
            # logging.error(f"hora {hora} wapp {sender}")
            existe_msg = pgonecolumn(con,f"select id from wappsrecibidos where \
                                    fecha='{hora}' and wapp={sender}")
            # logging.error(f"existe_msg{existe_msg}")
            if existe_msg == '' or existe_msg is None:
                if 'media' in data:
                    media = base64.b64decode(data["media"]["base64"])
                    # logging.info(media)
                    if tipo=='document' and message=='':
                        message = 'pdf'
                    elif tipo=='document' and message!='' and 'pdf' not in message:
                        message = message + ' ' + 'pdf'
                    elif tipo=='ptt':
                        message = 'audio'
                else:
                    media = None
                api = data["api"]
                guardar_msg(sender,message,idtime,api,hora,media,tipo)  
                logging.error('se procede a guardar message')      
            return 'ok'
        

def guardar_msg(wapp,msg,idtime,api='5493513882892',time=None, media=None, tipo=None):
    """Guarda el msg recibido por el webhook en la tabla correspondiente."""
    con = get_con()
    if time is None:
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ins = f"insert into wappsrecibidos(wapp,msg,fecha,api,idtime) values\
        ('{wapp}','{msg}','{time}','{api}','{idtime}')"
    try:
        pgexec(con, ins)
        logging.warning(f"existe media? {media is not None} tipo {tipo}")
        if media is not None:
            id = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
            if tipo=='document':
                filename = os.path.join('/home/hero/',str(id)+'.pdf')
            elif tipo=='ptt':
                filename = os.path.join('/home/hero/',str(id)+'.ogg')
            with open(filename, 'wb') as f:
            # escribir el contenido de la respuesta en el archivo
                if isinstance(media, (bytes, bytearray, memoryview)):
                    # La variable media contiene datos de tipo "bytes-like"
                    # Puedes usarla para escribir en un archivo
                    f.write(media)
    except mysql.connector.Error as _error:
            con.rollback()
            error = _error.msg
            logging.warning(
                f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
            return make_response(error, 400)
    else:
        con.close()
        return


@app.template_filter()
def cur(monto):
    if monto == None:
        return None
    else:
        return f"${int(monto)}"


@app.route('/enviarwapppendientes')
def revisar_redis():
    # Esperar a que haya elementos en la cola
    _, item = queue_wapps.blpop('wapp')

    # Procesar el elemento
    # si tiene cuatro elementos es wapp de texto
    # si tiene cinco elementos es wapp de file
    if len(json.loads(item)) == 4:
        procesar_msg_whatsapp(item)
    else:
        procesar_file_whatsapp(item)
    return 'ok'


# def process_queue():
#     while True:
#         # Esperar a que haya elementos en la cola
#         _, item = queue_wapps.brpop('wapp')
#         _, _, _, _, hora_despacho, tipo = json.loads(item)
#         # print('resultado del redis', hora_despacho)
#         # print(time.time())
#         # print(json.loads(item))
#         if tipo == 'texto':
#             # logging.warning(f"hora de despacho {hora_despacho} y time.time es {time.time()}")
#             procesar_msg_whatsapp(item)
#         else:
#             # logging.warning(f"hora de despacho {hora_despacho}")
#             procesar_file_whatsapp(item)

def revisa_redis():
# Esperar a que haya elementos en la cola
    _, item = queue_wapps.brpop('wapp')
    _, _, _, _, hora_despacho, tipo = json.loads(item)
    # print('resultado del redis', hora_despacho, time.time())
    # print(time.time())
    # print(json.loads(item))
    if tipo == 'texto':
        # logging.warning(f"hora de despacho {hora_despacho} y time.time es {time.time()}")
        procesar_msg_whatsapp(item)
        # print('hora en que regresa el control desde wapp_send', time.time())
    else:
        # logging.warning(f"hora de despacho {hora_despacho}")
        procesar_file_whatsapp(item)


def process_queue():
    while True:
        revisa_redis()

# def check_wapps():
#     while True:
#         revisa_wapps()

# def revisa_wapps():
#     con = get_con()
#     changes = pgonecolumn(con, f"select count(*) from wappsrecibidos \
#                             where fecha>date_sub(now(), interval 40 \
#                             second)")
#     logging.warning(f"changes a {str(time.ctime(time.time()))} {changes}")

#     if changes!='' and changes is not None and changes > 0:
#         # Envía los cambios a los clientes conectados
#         socketio.emit('update_wapps', {'data': changes})

#     con.close()
#     time.sleep(10)   

class WebSocketApp(object):
    """Stream sine values"""
    def __call__(self, environ, start_response):
        ws = environ['wsgi.websocket']
        while True:
            con = get_con()
            changes = None
            with gevent.Timeout(10, False):
                changes = pgonecolumn(con, f"select count(*) from wappsrecibidos \
                            where fecha>date_sub(now(), interval 40 \
                            second)")
            if changes is None:
                ...  # 5 seconds passed without reading a line
            else:
                logging.warning(f"changes a {str(time.ctime(time.time()))} {changes}")
                # Envía los cambios a los clientes conectados
                ws.send(json.dumps(changes))
            con.close()


http_server = WSGIServer(('', 5000), app)

    # setup server to handle websocket requests
ws_server = WSGIServer(
        ('', 9999), WebSocketApp(),
        handler_class=WebSocketHandler
    )

gevent.joinall([
        gevent.spawn(http_server.serve_forever),
        gevent.spawn(ws_server.serve_forever)
    ])

# Iniciar la función de vigilancia de la cola en segundo plano
queue_thread = threading.Thread(target=process_queue)
<<<<<<< Updated upstream
#wapp_thread = threading.Thread(target=check_wapps)
queue_thread.daemon = True
#wapp_thread.daemon = True
queue_thread.start()
#wapp_thread.start()
=======
# wapp_thread = threading.Thread(target=check_wapps)
queue_thread.daemon = True
# wapp_thread.daemon = True
queue_thread.start()
# wapp_thread.start()
>>>>>>> Stashed changes
