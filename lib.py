# -*- coding: utf-8 -*-
"""Librerias generales."""
import time
from datetime import datetime
import os
import logging
import requests
import re
from flask_login import current_user
from flask import make_response
import mysql.connector
from con import get_con, log
from urllib.parse import quote
import redis
import simplejson as json
import base64


queue_wapps = redis.Redis()
FORMAT = '%(asctime)s  %(message)s'
logging.basicConfig(format=FORMAT)



def convert_file_to_base64(file_path):
    with open(file_path, "rb") as file:
        pdf_bytes = file.read()
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        return base64_pdf

    
def pgtuple(con, sel):
    """Funcion que entrega una tupla de valores listo para desempacar.

    Debe proporcionarse un select que entregue una sola fila.
    """
    cur = con.cursor()
    cur.execute(sel)
    rec = cur.fetchone()
    return rec


def pglistdict(con, sel):
    """Funcion que entrega una lista de diccionarios.

    Un diccionario por cada fila. Cuyas claves son los nombres de los campos.
    """
    cur = con.cursor(dictionary=True)
    cur.execute(sel)
    rec = cur.fetchall()
    return rec


def pgdict(con, sel):
    """Funcion que entrega un diccionario.

    Las claves son los campos del select.
    Si no hay resultado entrega None.
    """
    cur = con.cursor(dictionary=True)
    cur.execute(sel)
    rec = cur.fetchall()
    if rec:
        return rec[0]
    else:
        return None


def pglisttuples(con, sel):
    """Funcion que entrega una lista de tuplas.

    Una tupla por fila.
    """
    cur = con.cursor()
    cur.execute(sel)
    rec = cur.fetchall()
    return rec


def pgonecolumn(con, sel):
    """Funcion que entrega un solo valor.

    Si el select no lo especifica, entrega el primer campo de la primera fila.
    """
    cur = con.cursor()
    cur.execute(sel)
    res = cur.fetchone()
    if res is None:
        return ""
    else:
        return res[0]
    return res


def pglist(con, sel):
    """Funcion que entrega una lista de valores."""
    lista = pglisttuples(con, sel)
    flatlist = []
    for lis in lista:
        flatlist.append(lis[0])
    return flatlist


def pgexec(con, sel):
    """Funcion que ejecuta una sentencia."""
    cur = con.cursor()
    cur.execute(sel)
    con.commit()
    return 'ok'


def listsql(lista):
    """Formatea una lista para usar en un stm sqlite.

    o sea del formato (a,b,c), en especial maneja el caso
    en que la lista de longitud 1, y entrega (a)
    """
    if len(lista) == 1:
        sqllist = '('+str(lista[0])+')'
    else:
        sqllist = str(tuple(lista))
    return sqllist


def strbuscar(search):
    """Funcion que formatea una cadena para buscar en base de datos."""
    list = ['%']
    if search is not None:
        searchlist = search.split()
    else:
        searchlist = []
    for s in searchlist:
        list.append(s)
        list.append('%')
    return "".join(list)


def per(periodicidad):
    """Devuelve la periodicidad en una cadena legible."""
    if periodicidad == 1:
        return "MEN"
    elif periodicidad == 3:
        return "SEM"
    else:
        return "QUIN"


def desnull(cadena):
    """Filtro que elimina la cadena NULL."""
    if cadena == "NULL":
        return ""
    else:
        return cadena


def letras(num):
    """Funcion que traduce numeros a letras."""
    millares = {'0': '', '1': 'mil', '2': 'dos mil', '3': 'tres mil',
                '4': 'cuatro mil', '5': 'cinco mil', '6': 'seis mil',
                '7': 'siete mil', '8': 'ocho mil', '9': 'nueve mil',
                '10': 'diez mil', '11': 'once mil', '12': 'doce mil',
                '13': 'trece mil', '14': 'catorce mil', '15': 'quince mil',
                '16': 'dieciseis mil', '17': 'diecisiete mil',
                '18': 'dieciocho mil', '19': 'diecinueve mil',
                '20': 'veinte mil', '21': 'veintiun mil',
                '22': 'veintidos mil', '23': 'veintitres mil',
                '24': 'veinticuatro mil', '25': 'veinticinco mil',
                '26': 'veintiseis mil', '27': 'veintisiete mil',
                '28': 'veintiocho mil', '29': 'veintinueve mil',
                '30': 'treinta mil'}
    centenas = {'0': '', '1': 'ciento', '2': 'doscientos', '3':
                'trescientos', '4': 'cuatrocientos', '5': 'quinientos',
                '6': 'seiscientos', '7': 'setecientos', '8': 'ochocientos',
                '9': 'novecientos'}
    decenas = {'3': 'treinta', '4': 'cuarenta', '5': 'cincuenta', '6':
               'sesenta', '7': 'setenta', '8': 'ochenta', '9': 'noventa'}
    sueltos = {'29': 'veintinueve', '28': 'veintiocho', '27': 'veintisiete',
               '26': 'veintiseis', '25': 'veinticinco', '24': 'veinticuatro',
               '23': 'veintitres', '22': 'veintidos', '21': 'veintiuno',
               '20': 'veinte', '19': 'diecinueve', '18': 'dieciocho', '17':
               'diecisiete', '16': 'dieciseis', '15': 'quince', '14':
               'catorce', '13': 'trece', '12': 'doce', '11': 'once', '10':
               'diez', '09': 'nueve', '08': 'ocho', '07': 'siete', '06':
               'seis', '05': 'cinco', '04': 'cuatro', '03': 'tres', '02':
               'dos', '01': 'uno', '00': ''}
    unidades = {'0': '', '1': 'uno', '2': 'dos', '3': 'tres', '4': 'cuatro',
                '5': 'cinco', '6': 'seis', '7': 'siete', '8': 'ocho', '9':
                'nueve'}
    millar = '0'
    centena = '0'
    decena = '0'
    if len(str(num)) > 3:
        millar = str(num)[:-3]

    if len(str(num)) > 2:
        centena = str(num)[-3]

    decena = str(num)[-2]
    unidad = str(num)[-1]
    dosdigitos = str(num)[-2:]
    if int(decena) > 2:
        num = millares[millar] + ' ' + centenas[centena]+' '+decenas[decena]\
            + ' ' + unidades[unidad]
    else:
        num = millares[millar]+' '+centenas[centena]+' '+sueltos[dosdigitos]
    return (num.lstrip().rstrip().upper())


def send_msg_whatsapp(idcliente, wapp, msg):
    """Funcion que encola wapp de texto."""
    tipo = 'texto'
    hora_despacho = None
    ultimo_encolado = queue_wapps.rpop('hora')
    if ultimo_encolado is not None:
        hora_despacho = json.loads(ultimo_encolado)
        logging.warning(f"ultimo_encolado {hora_despacho}")
        queue_wapps.rpush('hora', hora_despacho)
    if hora_despacho is None:
        hora_despacho = time.time()
    else:
        if hora_despacho < time.time():
            hora_despacho = time.time() + 5
        else:
            hora_despacho = hora_despacho + 15
    logging.warning(f"'hora_depacho establecida'{hora_despacho}")
    wapp_json = json.dumps(
        [idcliente, wapp, msg, current_user.email, hora_despacho, tipo])
    queue_wapps.lpush('wapp', wapp_json)
    queue_wapps.rpush('hora', hora_despacho)


def get_msgs(api='5493515919883'):
    payload = f"https://heroasam.xyz/readAllMsgs"
    try:
        response = requests.request("GET", payload)
    except requests.Timeout:
        # Manejo del error de tiempo de espera
        return "Tiempo de espera de la solicitud agotado"
    except requests.RequestException as e:
        # Manejo de otros errores de solicitud
        logging.warning(f"errores de RequestException {str(e)}")
        return str(e)
    else:
        con = get_con()
        if response.status_code==200:
            mensajes_recibidos = response.json()
            # logging.error(f"mensajes_recibidos {mensajes_recibidos}")
            if len(mensajes_recibidos)>0:
                for data in mensajes_recibidos:
                    if "message" in data:
                        message = data["message"]
                    else:
                        message = ""
                    sender = data["from"]
                    media = None
                    tipo = data["tipo"]
                    hora = str(data["time"])
                    hora = datetime.strptime(hora, '%Y-%m-%d %H:%M:%S')
                    timestamp = str(int(hora.timestamp()))+str(int(time.time()*1000000))[-6:-3]
                    idtime = str(sender)+timestamp
                    existe_msg = pgonecolumn(con,f"select id from wappsrecibidos where \
                                                fecha='{hora}' and wapp={sender}")
                    if existe_msg == '' or existe_msg is None:
                        if tipo=='document' or tipo=='ptt':
                            media = data["media"]
                            media = base64.b64decode(data["media"]["base64"])
                            # logging.warning(media)
                        if tipo=='document' and message=='':
                            message = 'pdf'
                        elif tipo=='document' and message!='' and 'pdf' not in message:
                            message = message + ' ' + 'pdf'
                        elif tipo=='ptt':
                            message = 'audio'
                        api = data["api"]
                        guardar_msg(sender,message,idtime,api,hora,media,tipo)  
                        logging.error(f'se procede a guardar message {message}')
    finally:
        con.close()


def guardar_msg(wapp,msg,idtime,api='5493513882892',time=None, media=None, tipo=None):
    """Guarda el msg recibido por el webhook en la tabla correspondiente."""
    con = get_con()
    logging.warning("entrando en guardar_msg")
    if time is None:
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ins = f"insert into wappsrecibidos(wapp,msg,fecha,api,idtime) values\
        ('{wapp}','{msg}','{time}','{api}','{idtime}')"
    try:
        pgexec(con, ins)
        logging.warning(f"media is None? {media is None} tipo {tipo}")
        if media is not None:
            logging.warning("media is not None")
            id = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
            if tipo=='document':
                logging.warning("es documento")
                filename = os.path.join('/home/hero/',str(id)+'.pdf')
            elif tipo=='ptt':
                filename = os.path.join('/home/hero/',str(id)+'.ogg')
            logging.warning(f"filename: {filename}")
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


def procesar_msg_whatsapp(wapp, api = '5493513882892'):
    """Funcion envia wapp de texto."""
    logging.warning("ejecutandose msg_whatsapp")
    idcliente, wapp, msg, email, hora_despacho, _ = json.loads(wapp)
    con = get_con()
    # api = pgonecolumn(con, f"select api from wappsrecibidos where wapp=\
    #                   '549{wapp}' and id = (select max(id) from \
    #                   wappsrecibidos where wapp='549{wapp}')")
    # if api == '':
    #     api = '54935919883'
    if wapp == '5493512411963' or wapp == '3512411963':
        api = '5493515919883'
    pattern = r'^[0-9]+$'
    if re.match(pattern, wapp) == None:
        return 'error', 402
    if api == '5493513882892':
        wapp = "+549"+wapp
        payload = f"https://api.textmebot.com/send.php?recipient={wapp}&\
                apikey=kGdEFC1HvHVJ&text={msg}"
    elif api == '5493515919883':
        payload = f"https://heroasam.xyz/sendMsg/3/{wapp}/{msg}"
    ins = f"insert into logwhatsapp(idcliente,wapp,msg,file,user,timein,\
    timeout,response,enviado,fecha) values({idcliente},'{wapp}',\
    '{msg.replace('%20',' ')[:100]}','','{email}',{int(time.time())}\
    ,0,'',0,curdate())"
    pgexec(con, ins)
    idlog = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
    while True:
        if time.time() > hora_despacho:
            logging.warning(
                f"hora_despacho {hora_despacho} time {time.time()}")
            try:
                # Establece un tiempo máximo de 5 segundos para la respuesta
                response = requests.request("GET", payload)
            except requests.Timeout:
                # Manejo del error de tiempo de espera
                send_msg_whatsapp(idcliente, wapp, msg)
                logging.warning(f"Tiempo de espera agotado para {wapp}")
                return "Tiempo de espera de la solicitud agotado"
            except requests.RequestException as e:
                # Manejo de otros errores de solicitud
                logging.warning(f"errores de RequestException {str(e)}")
                return str(e)
            else:
                resultado = 'ninguno'
                if api == "5493513882892":
                    match = re.search(r"Result: <b>(.*?)</b>", response.text)
                    if match:
                        resultado = match.group(1)
                else:
                    resultado = response.text
                logging.warning(
                    f"mensaje {wapp} enviado a las:{str(time.ctime(time.time()))} {resultado} {time.time()}")
                wapp_log(response.status_code, resultado, wapp,
                         str(time.ctime(time.time())), idcliente,api)
                if "Success" in resultado or "success" in resultado:
                    upd = f"update logwhatsapp set response='success',\
                    enviado={int(time.time())} where id = {idlog}"
                    wapp_logenviados(wapp, msg, email,api)
                    pgexec(con, upd)
                    return 'success'
                elif "Invalid Destination WhatsApp" in resultado:
                    updinv = f"update clientes set wapp_invalido='{wapp}',wapp='INVALIDO' \
                            where id={idcliente}"
                    upd = f"update logwhatsapp set response='invalid', enviado=\
                            {int(time.time())} where id = {idlog}"
                    logging.warning(
                        f"ante envio Invalid Destination WhatsApp: {resultado}")
                    pgexec(con, updinv)
                    pgexec(con, upd)
                    return 'invalid'
                elif "Failed" in resultado:
                    upd = f"update logwhatsapp set response='failed', enviado=\
                            {int(time.time())} where id = {idlog}"
                    logging.warning(
                        f"ante envio Failed: {resultado}")
                    pgexec(con, upd)
                    return 'failed'
                elif "limit" in resultado:
                    upd = f"update logwhatsapp set response='limit', enviado=\
                            {int(time.time())} where id = {idlog}"
                    logging.warning(
                        f"ante envio Limit: {resultado}")
                    pgexec(con, upd)
                    return 'limit'
                else:
                    return 'error', 401
            finally:
                time.sleep(0.5)
                break


def send_file_whatsapp(idcliente, file, wapp, msg=''):
    """Funcion que encola wapp de file."""
    tipo = 'file'
    hora_despacho = None
    ultimo_encolado = queue_wapps.rpop('hora')
    if ultimo_encolado is not None:
        hora_despacho = json.loads(ultimo_encolado)
        logging.warning(f"ultimo_encolado {hora_despacho}")
        queue_wapps.rpush('hora', hora_despacho)
    if hora_despacho is None:
        hora_despacho = time.time()
    else:
        if hora_despacho < time.time():
            hora_despacho = time.time() + 5
        else:
            hora_despacho = hora_despacho + 15
    logging.warning(f"'hora_depacho establecida'{hora_despacho}")
    wapp_json = json.dumps(
        [idcliente, file, wapp, current_user.email, hora_despacho, tipo])
    queue_wapps.lpush('wapp', wapp_json)
    queue_wapps.rpush('hora', hora_despacho)
    time.sleep(1)


def procesar_file_whatsapp(wapp, api = '5493513882892'):
    """Funcion que envia wapp de file  ."""
    logging.warning("procesar_file_whatsapp")
    api = '5493513882892'
    con = get_con()
    idcliente, file, wapp, email, hora_despacho, _ = json.loads(wapp)
    # api = pgonecolumn(con, f"select api from wappsrecibidos where wapp=\
    #                   '549{wapp}' and id = (select max(id) from \
    #                   wappsrecibidos where wapp='549{wapp}')")
    # if api == '':
    #     api = '54935919883'
    if wapp == '5493512411963' or wapp == '3512411963':
        api = '5493515919883'
    logging.warning(f"api {api}")
    pattern = r'^[0-9]+$'
    if re.match(pattern, wapp) == None:
        return 'error', 402
    file_log = os.path.split(file)[1]
    ins = f"insert into logwhatsapp(idcliente,wapp,msg,file,user,timein,\
            timeout,response,enviado,fecha) values({idcliente},\
            '{wapp}','','{file_log}'\
            ,'{email}',{int(time.time())},0,'',0,curdate())"
    pgexec(con, ins)
    idlog = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
    while True:
        if time.time() > hora_despacho:
            logging.warning(
                f"hora_despacho {hora_despacho} time {time.time()}")
            try:
                # logging.warning(f"api{api}")
                # Establece un tiempo máximo de 5 segundos para la respuesta
                if api=='5493513882892':
                    wapp = "+549"+wapp
                    payload = f"https://api.textmebot.com/send.php?recipient={wapp}&\
                                apikey=kGdEFC1HvHVJ&document={file}"
                    response = requests.request("GET", payload, timeout=8)
                else:
                    data = {'wapp':wapp,'file':file, 'api':3}
                    # logging.warning(f"data={data}")
                    payload = "https://heroasam.xyz/sendFile"
                    response =requests.post(payload, data=data)
                    # logging.warning(f"response del POST --> {response.text}")
            except requests.Timeout:
                # Manejo del error de tiempo de espera
                send_file_whatsapp(idcliente, file, wapp)
                logging.warning(f"Tiempo de espera agotado para {wapp}")
                return "Tiempo de espera de la solicitud agotado"
            except requests.RequestException as e:
                # Manejo de otros errores de solicitud
                logging.warning(f"errores de RequestException {str(e)}")
                return str(e)
            else:
                resultado = 'ninguno'
                if api == "5493513882892":
                    match = re.search(r"Result: <b>(.*?)</b>", response.text)
                    if match:
                        resultado = match.group(1)
                else:
                    resultado = response.text
                logging.warning(
                    f"mensaje {wapp} enviado a las:{str(time.ctime(time.time()))} {resultado} {time.time()}")
                wapp_log(response.status_code, resultado, wapp,
                         str(time.ctime(time.time())), idcliente,api)
                if "Success" in resultado or "success" in resultado:
                    upd = f"update logwhatsapp set response='success',\
                    enviado={int(time.time())} where id = {idlog}"
                    wapp_logenviados(wapp, file_log, email,api)
                    pgexec(con, upd)
                    return 'success'
                elif "Invalid Destination WhatsApp" in resultado:
                    updinv = f"update clientes set wapp_invalido='{wapp}',wapp='INVALIDO' \
                            where id={idcliente}"
                    upd = f"update logwhatsapp set response='invalid', enviado=\
                            {int(time.time())} where id = {idlog}"
                    logging.warning(
                        f"ante envio Invalid Destination WhatsApp: {resultado}")
                    pgexec(con, updinv)
                    pgexec(con, upd)
                    return 'invalid'
                elif "Failed" in resultado:
                    upd = f"update logwhatsapp set response='failed', enviado=\
                            {int(time.time())} where id = {idlog}"
                    logging.warning(f"ante envio Failed: {resultado}")
                    pgexec(con, upd)
                    return 'failed'
                elif "limit" in resultado:
                    upd = f"update logwhatsapp set response='limit', enviado=\
                            {int(time.time())} where id = {idlog}"
                    logging.warning(f"ante envio Limit: {resultado}")
                    pgexec(con, upd)
                    return 'limit'
                else:
                    return 'error', 401
            finally:
                time.sleep(0.5)
                break


def wapp_logenviados(wapp, msg, user,api):
    """Funcion que registra el wapp en la tabla wappsenviados."""
    con = get_con()
    msg = msg.replace("%20", " ")
    msg = msg.replace("'", " ")
    if '.pdf' in msg:
        msg = msg.replace('.pdf', '')
        msg = 'enviado '+msg
    wapp = wapp[-10:]
    ins = f"insert into wappsenviados(wapp,msg,user,api) values('{wapp}',\
        '{msg}','{user}','{api}')"
    try:
        pgexec(con, ins)
    except mysql.connector.Error as _error:
        con.rollback()
        error = _error.msg
        logging.warning(
            f"error mysql Nº {_error.errno},{ _error.msg},codigo sql-state Nº {_error.sqlstate}")
        return make_response(error, 400)
    con.close()


def wapp_log(log1, log2, wapp, tiempo, idcliente,api):
    """Funcion que hace un log en txt de las responses de la api."""
    with open("/home/hero/log/wapp.log", "a", encoding="utf-8") as log_file:
        log_file.write('\n')
        log_file.write(str(wapp)+' '+str(log1)+' '+tiempo+' ' +
                       str(time.time())+' Idcliente:'+str(idcliente)+' '
                       + str(log2) + str(api))
        log_file.close()


def log_busqueda(busqueda):
    """Funcion que hace un log de busquedas globales en buscador."""
    with open("/home/hero/log/busquedas.log", "a", encoding="utf-8") as log_file:
        if "@" in str(current_user):
            email = current_user.email
        else:
            email = ""
        log_file.write('\n')
        log_file.write(time.strftime('%Y-%m-%d', time.localtime())+', ' +
                       time.strftime('%H:%M:%S', time.localtime())+', ' +
                       busqueda+', '+email)
        log_file.close()


def logcaja(asiento_id, cuenta, imp, comentario):
    """Funcion que hace un log en txt de los movimientos de caja."""
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d, %H:%M:%S")
    if "@" in str(current_user):
        email = current_user.email
    else:
        email = ""
    con = get_con()
    saldo = pgonecolumn(con, "select sum(imp) from caja")
    con.close()
    with open("/home/hero/log/caja.log", "a", encoding="utf-8") as log_file:
        log_file.write('\n')
        log_file.write('$' + str(saldo) + ' ' + str(asiento_id) + ' ' +
                       str(date_time) + ' ' + (cuenta) + ' ' + '$' + str(imp) + ' ' +
                       str(comentario) + ' ' + str(email))
        log_file.close()


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


def actualizar(monto, fecha):
    con = get_con()
    ultimo_valor = pgonecolumn(con, "select indice from inflacion order \
            by id desc limit 1")
    indice = pgonecolumn(con, f"select indice from inflacion \
            where concat(year,month)='{fecha}'")
    if not indice:
        indice = ultimo_valor
    actualizada = ultimo_valor/indice * int(monto)
    return actualizada
