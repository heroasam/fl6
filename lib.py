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
# import base64, urllib
import redis
import simplejson as json


queue_wapps = redis.Redis()
FORMAT = '%(asctime)s  %(message)s'
logging.basicConfig(format=FORMAT)


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

# def send_file_whatsapp(file, wapp):
#     ssl._create_default_https_context = ssl._create_unverified_context
#     conn = http.client.HTTPSConnection("api.ultramsg.com")
#     with open(file, "rb") as image_file:
#         encoded_string = base64.b64encode(image_file.read())

#     img_bas64=urllib.parse.quote_plus(encoded_string)
#     payload = f"token=dr40pjod4ka6qmlf&to=+549{wapp}&document="+ img_bas64 +\
    # f"&filename={os.path.split(file)[1]}"
#     headers = { 'content-type': "application/x-www-form-urlencoded" }
#     conn.request("POST", "/instance15939/messages/document", payload,\
    # headers)
#     res = conn.getresponse()
#     data = res.read()
#     return data.decode("utf-8")

# def send_msg_whatsapp(wapp, msg):
#     url = "https://api.ultramsg.com/instance15939/messages/chat"

#     payload = f"token=dr40pjod4ka6qmlf&to=+549{wapp}&body={msg}&priority=\
    # 1&referenceId="
#     headers = {'content-type': 'application/x-www-form-urlencoded'}

#     response = requests.request("POST", url, data=payload, headers=headers)

#     return response.text


# def obtener_msg_enviados(to_number):
    # to_number = str(to_number)+"@c.us"
    # url = "https://api.ultramsg.com/instance15939/messages"
    # querystring = {"token":"dr40pjod4ka6qmlf","page":"1","limit":"10",\
    # "status":"sent","sort":"desc","id":"","referenceId":"","from":"",\
    # "to":to_number,"ack":""}
    # headers = {'content-type': 'application/x-www-form-urlencoded'}
    # response = requests.request("GET", url, headers=headers, \
    # params=querystring)
    # return response.text

# def send_msg_whatsapp(idcliente, wapp, msg):
#     logwhatsapp(idcliente,wapp,msg=msg)
#     wapp = "549"+wapp
#     payload = f"https://api.trenalyze.com/send?receiver={wapp}&msgtext=\
    # {msg}&sender=5493513882892&token=CRCNu7mOce4dN7S18iXW"
#     response = requests.request("GET", payload)

#     return response.text

# def send_file_whatsapp(idcliente,file, wapp, msg=""):
#     logwhatsapp(idcliente,wapp,file=file, msg=msg)
#     wapp = "549"+wapp
#     with open(file, "rb") as image_file:
#         encoded_string = base64.b64encode(image_file.read())

#     img_bas64=urllib.parse.quote_plus(encoded_string)
#     payload = f"https://api.trenalyze.com/send?receiver={wapp}&msgtext=\
    # {msg}&sender=5493513882892&token=CRCNu7mOce4dN7S18iXW&document={img_bas64}"
#     response = requests.request("GET", payload)

#     return response.text

# def send_file_whatsapp(idcliente,file, wapp, msg=""):
#     """API libre de VENOM"""
#     logwhatsapp(idcliente,wapp,file=file, msg=msg)
#     wapp = "549"+wapp
#     namefile = os.path.split(file)[1]
#     with open(file, "rb") as image_file:
#         encoded_string = base64.b64encode(image_file.read())

#     # img_bas64=urllib.parse.quote_plus(encoded_string)

#     url = 'https://pachito.xyz/sendFile'
#     data = {
#         'sessionName':"romitex10",
#         'number':wapp,
#         'base64Data':encoded_string,
#         'fileName':namefile,
#         'caption':msg,
#     }
#     response = requests.post(url,json=data)
#     return response.text


# def send_msg_whatsapp(idcliente, wapp, msg):
#     """Envia whatsapp por la api libre de VENOM"""
#     logwhatsapp(idcliente,wapp,msg=msg)
#     wapp = "549"+wapp
#     msg = msg.replace("%20"," ")
#     url = 'https://www.pachito.xyz/sendText'
#     data = {
#         'sessionName':"romitex10",
#         'number':wapp,
#         'text':msg,
#     }
#     response = requests.post(url,json=data)
#     return response.text


def send_msg_whatsapp(idcliente, wapp, msg):
    """Funcion que encola wapp de texto."""
    tipo = 'texto'
    hora_despacho = None
    ultimo_encolado = queue_wapps.rpop('hora')
    # print('redis ultimo encolado',ultimo_encolado)
    if ultimo_encolado is not None:
        hora_despacho = json.loads(ultimo_encolado)
        queue_wapps.rpush('hora', hora_despacho)
        # print('el ultimo encolado es not None y hora despacho es', hora_despacho)
    if hora_despacho is None:
        hora_despacho = time.time()
    else:
        if hora_despacho < time.time():
            hora_despacho = time.time() + 5
        else:
            hora_despacho = hora_despacho + 15
    # print('hora despacho establecida',hora_despacho)
    # logging.warning(f"hora despacho establecida {hora_despacho}")
    wapp_json = json.dumps([idcliente, wapp, msg, current_user.email,hora_despacho,tipo])
    queue_wapps.lpush('wapp', wapp_json)
    queue_wapps.rpush('hora',hora_despacho)


def procesar_msg_whatsapp(wapp):
    """Funcion envia wapp de texto."""
    idcliente, wapp, msg, email,hora_despacho,_ = json.loads(wapp)
    con = get_con()
    wapp_original = wapp
    pattern = r'^[0-9]+$'
    if re.match(pattern, wapp_original) == None:
        return 'error', 402
    wapp = "+549"+wapp
    payload = f"https://api.textmebot.com/send.php?recipient={wapp}&\
            apikey=kGdEFC1HvHVJ&text={msg}"
    ins = f"insert into logwhatsapp(idcliente,wapp,msg,file,user,timein,\
    timeout,response,enviado,fecha) values({idcliente},'{wapp_original}',\
    '{msg.replace('%20',' ')[:100]}','','{email}',{int(time.time())}\
    ,0,'',0,curdate())"
    pgexec(con, ins)
    idlog = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
    # logging.warning(f"antes del while'{str(time.time())} hora_despacho {hora_despacho}")
    while True:
        if time.time() > hora_despacho:
            # print('dentro de msgwapp',str(time.time()),'hora_despacho',hora_despacho)
            response = requests.request("GET", payload)
            break
        time.sleep(0.5)
    resultado = 'ninguno'
    match = re.search(r"Result: <b>(.*?)</b>", response.text)
    if match:
        resultado = match.group(1)
    logging.warning(
        f"mensaje {wapp} enviado a las:{str(time.ctime(time.time()))} {resultado}")
    wapp_log(response.status_code, resultado, wapp,
             str(time.ctime(time.time())), idcliente)
    wapp_logenviados(wapp_original, msg, email)
    if "Success" in response.text:
        upd = f"update logwhatsapp set response='success',\
        enviado={int(time.time())} where id = {idlog}"
        pgexec(con, upd)
        return 'success'
    elif "Invalid Destination WhatsApp" in response.text:
        updinv = f"update clientes set wapp_invalido='{wapp}',wapp='INVALIDO' \
                where id={idcliente}"
        upd = f"update logwhatsapp set response='invalid', enviado=\
                {int(time.time())} where id = {idlog}"
        pgexec(con, updinv)
        pgexec(con, upd)
        return 'invalid'
    elif "Failed" in response.text:
        upd = f"update logwhatsapp set response='failed', enviado=\
                {int(time.time())} where id = {idlog}"
        pgexec(con, upd)
        return 'failed'
    elif "limit" in response.text:
        upd = f"update logwhatsapp set response='limit', enviado=\
                {int(time.time())} where id = {idlog}"
        pgexec(con, upd)
        return 'limit'
    else:
        return 'error', 401


def send_msg_whatsapp1(idcliente, wapp, msg):
    wapp_original = wapp
    pattern = r'^[0-9]+$'
    if re.match(pattern, wapp_original) == None:
        return 'error', 402
    if "@" in str(current_user):
        email = current_user.email
    else:
        email = ""
    wapp = "+549"+wapp
    payload = f"https://api.textmebot.com/send.php?recipient={wapp}&\
            apikey=kGdEFC1HvHVJ&text={msg}"
    # primero encolo el mensaje en la base de datos
    con = get_con()
    last_timeout = pgonecolumn(con, "select timeout from logwhatsapp order \
            by id desc limit 1")
    last_enviado = pgonecolumn(con, "select enviado from logwhatsapp where \
            enviado!=0 order by id desc limit 1")
    if not last_timeout:
        last_timeout = int(time.time())
    if not last_enviado:
        last_enviado = int(time.time())
    timeout = last_enviado if last_enviado > last_timeout else last_timeout
    ins = f"insert into logwhatsapp(idcliente,wapp,msg,file,user,timein,\
    timeout,response,enviado,fecha) values({idcliente},'{wapp_original}',\
    '{msg.replace('%20',' ')[:100]}','','{email}',{int(time.time())}\
    ,{timeout+10},'',0,curdate())"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    id = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
    time_delivery = timeout+10
    # logging.warning(f"time_delivery:{time_delivery} real-time:{time.ctime(time.time())}")
    while True:
        if time.time() > time_delivery:
            response = requests.request("GET", payload)
            # logging.warning(f"time al request:{time.time()}")
            break
        time.sleep(0.5)
    resultado = 'ninguno'
    match = re.search(r"Result: <b>(.*?)</b>", response.text)
    if match:
        resultado = match.group(1)
    logging.warning(
        f"mensaje {wapp} enviado a las:{str(time.ctime(time.time()))} {resultado}")
    wapp_log(response.status_code, resultado, wapp,
             str(time.ctime(time.time())), idcliente)
    wapp_logenviados(wapp_original, msg, email)
    if "Success" in response.text:
        upd = f"update logwhatsapp set response='success',\
        enviado={int(time.time())} where id = {id}"
        # logging.warning(upd)
        cur.execute(upd)
        con.commit()
        con.close()
        return "success"
    elif "Invalid Destination WhatsApp" in response.text:
        updinv = f"update clientes set wapp_invalido='{wapp}',wapp='INVALIDO' \
                where id={idcliente}"
        # logging.warning(updinv)
        # logging.warning(f"Para resolver bug-invalido. Valor de <con> aqui:{con} y de cur:{cur}")
        # mientras resuelvo el bug con mas informacion recogida con el logging.warning de arriba
        # dejo las dos lineas de abajo que redefinen redundantemente con y cur, siendo que en
        # pruebas de oficina funcionan bien sin esas re-definiciones.
        # En si se buscaria que alguna vez apareciera que con y cur fuesen nulos.
        con = get_con()
        cur = con.cursor()
        cur.execute(updinv)
        log(updinv)
        upd = f"update logwhatsapp set response='invalid', enviado=\
                {int(time.time())} where id = {id}"
        # logging.warning(upd)
        try:
            cur.execute(upd)
        except mysql.connector.Error as _error:
            con.rollback()
            error = _error.msg
            # logging.warning(error)
            return make_response(error, 400)
        else:
            con.commit()
            con.close()
            return "invalid"
    elif "Failed" in response.text:
        upd = f"update logwhatsapp set response='failed', enviado=\
                {int(time.time())} where id = {id}"
        # logging.warning(upd)
        cur.execute(upd)
        con.commit()
        con.close()
        return "failed"
    elif "limit" in response.text:
        upd = f"update logwhatsapp set response='limit', enviado=\
                {int(time.time())} where id = {id}"
        # logging.warning(upd)
        cur.execute(upd)
        con.commit()
        con.close()
        return "limit"
    else:
        return 'error', 401


def send_file_whatsapp(idcliente, file, wapp, msg=''):
    """Funcion que encola wapp de file."""
    tipo = 'file'
    hora_despacho = None
    ultimo_encolado = queue_wapps.rpop('hora')
    # print('redis ultimo encolado',ultimo_encolado)
    if ultimo_encolado is not None:
        hora_despacho = json.loads(ultimo_encolado)
        queue_wapps.lpush('hora', hora_despacho)
        # print('el ultimo encolado es not None y hora despacho es', hora_despacho)
    if hora_despacho is None:
        hora_despacho = time.time()
    else:
        if hora_despacho < time.time():
            hora_despacho = time.time() + 5
        else:
            hora_despacho = hora_despacho + 15
    # logging.warning(f"hora despacho establecida {hora_despacho}")
    wapp_json = json.dumps([idcliente, file, wapp, current_user.email, hora_despacho,tipo])
    queue_wapps.lpush('wapp', wapp_json)
    queue_wapps.rpush('hora', hora_despacho)


def procesar_file_whatsapp(wapp):
    """Funcion que envia wapp de file."""
    con = get_con()
    idcliente, file, wapp, email,hora_despacho ,_ = json.loads(wapp)
    wapp_original = wapp
    pattern = r'^[0-9]+$'
    if re.match(pattern, wapp_original) == None:
        return 'error', 402
    file_log = os.path.split(file)[1]
    wapp = "+549"+wapp
    payload = f"https://api.textmebot.com/send.php?recipient={wapp}&\
            apikey=kGdEFC1HvHVJ&document={file}"
    ins = f"insert into logwhatsapp(idcliente,wapp,msg,file,user,timein,\
            timeout,response,enviado,fecha) values({idcliente},\
            '{wapp_original}','','{file_log}'\
            ,'{email}',{int(time.time())},0,'',0,curdate())"
    pgexec(con, ins)
    idlog = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
    while True:
        if time.time() > hora_despacho:
            # print('dentro de msgwapp',str(time.time()),'hora_despacho',hora_despacho)
            response = requests.request("GET", payload)
            break
        time.sleep(0.5)
    resultado = 'ninguno'
    match = re.search(r"Result: <b>(.*?)</b>", response.text)
    if match:
        resultado = match.group(1)
        logging.warning(
            f"mensaje {wapp} enviado a las:{str(time.ctime(time.time()))} {resultado}")
    wapp_log(response.status_code, resultado, wapp,
             str(time.ctime(time.time())), idcliente)
    wapp_logenviados(wapp_original, file_log, email)
    if "Success" in response.text:
        upd = f"update logwhatsapp set response='success',\
        enviado={int(time.time())} where id = {idlog}"
        pgexec(con, upd)
        return 'success'
    elif "Invalid Destination WhatsApp" in response.text:
        updinv = f"update clientes set wapp_invalido='{wapp}',wapp='INVALIDO' \
                where id={idcliente}"
        upd = f"update logwhatsapp set response='invalid', enviado=\
                {int(time.time())} where id = {idlog}"
        pgexec(con, updinv)
        pgexec(con, upd)
        return 'invalid'
    elif "Failed" in response.text:
        upd = f"update logwhatsapp set response='failed', enviado=\
                {int(time.time())} where id = {idlog}"
        pgexec(con, upd)
        return 'failed'
    elif "limit" in response.text:
        upd = f"update logwhatsapp set response='limit', enviado=\
                {int(time.time())} where id = {idlog}"
        pgexec(con, upd)
        return 'limit'
    else:
        return 'error', 401


def send_file_whatsapp1(idcliente, file, wapp, msg=""):
    """Funcion que envia un archivo por whatsapp."""
    wapp_original = wapp
    pattern = r'^[0-9]+$'
    if re.match(pattern, wapp_original) == None:
        return 'error', 402
    file_log = os.path.split(file)[1]
    if "@" in str(current_user):
        email = current_user.email
    else:
        email = ""
    wapp = "+549"+wapp
    payload = f"https://api.textmebot.com/send.php?recipient={wapp}&\
            apikey=kGdEFC1HvHVJ&document={file}"
    # primero encolo el mensaje en la base de datos
    con = get_con()
    last_timeout = pgonecolumn(con, "select timeout from logwhatsapp order by\
            id desc limit 1")
    last_enviado = pgonecolumn(con, "select enviado from logwhatsapp where\
            enviado!=0 order by id desc limit 1")
    if not last_timeout:
        last_timeout = int(time.time())
    if not last_enviado:
        last_enviado = int(time.time())
    timeout = last_enviado if last_enviado > last_timeout else last_timeout
    ins = f"insert into logwhatsapp(idcliente,wapp,msg,file,user,timein,\
            timeout,response,enviado,fecha) values({idcliente},\
            '{wapp_original}','{msg.replace('%20',' ')[:100]}','{file_log}'\
            ,'{email}',{int(time.time())},{timeout+20},'',0,curdate())"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    id = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
    time_delivery = timeout+20
    # logging.warning(f"time_delivery:{time_delivery} real-time:{time.ctime(time.time())}")
    while True:
        if time.time() > time_delivery:
            response = requests.request("GET", payload)
            # logging.warning(f"Time al request:{time.time()}")
            break
        time.sleep(1)
    resultado = 'ninguno'
    match = re.search(r"Result: <b>(.*?)</b>", response.text)
    if match:
        resultado = match.group(1)
        logging.warning(
            f"mensaje {wapp} enviado a las:{str(time.ctime(time.time()))} {resultado}")
    wapp_log(response.status_code, resultado, wapp,
             str(time.ctime(time.time())), idcliente)
    wapp_logenviados(wapp_original, file_log, email)
    if "Success" in response.text:
        upd = f"update logwhatsapp set response='success', enviado=\
                {int(time.time())} where id = {id}"
        # logging.warning(upd)
        cur.execute(upd)
        con.commit()
        con.close()
        return "success"
    elif "Invalid Destination WhatsApp" in response.text:
        updinv = f"update clientes set wapp_invalido='{wapp}',wapp='INVALIDO' \
                where id={idcliente}"
        # logging.warning(updinv)
        con = get_con()
        cur = con.cursor()
        # logging.warning(updinv)
        cur.execute(updinv)
        log(updinv)
        upd = f"update logwhatsapp set response='invalid', enviado=\
                {int(time.time())} where id = {id}"
        # logging.warning(upd)
        cur.execute(upd)
        con.commit()
        con.close()
        return "invalid"
    elif "Failed" in response.text:
        upd = f"update logwhatsapp set response='failed', enviado=\
                {int(time.time())} where id = {id}"
        # logging.warning(upd)
        cur.execute(upd)
        con.commit()
        con.close()
        return "failed"
    elif "limit" in response.text:
        upd = f"update logwhatsapp set response='limit', enviado=\
                {int(time.time())} where id = {id}"
        # logging.warning(upd)
        cur.execute(upd)
        con.commit()
        con.close()
        return "limit"
    else:
        return 'error', 401


def send_img_whatsapp(idcliente, file, wapp, msg=""):
    """Funcion que envia un archivo por whatsapp."""
    wapp_original = wapp
    file_log = os.path.split(file)[1]
    file = "/home/hero/imagenes/romitex.png"
    if "@" in str(current_user):
        email = current_user.email
    else:
        email = ""
    wapp = "+549"+wapp
    # with open(file, "rb") as image_file:
    #     encoded_string = base64.b64encode(image_file.read())
    #     img_base64=urllib.parse.quote_plus(encoded_string)

    payload = f"https://api.textmebot.com/send.php?recipient={wapp}&\
            apikey=kGdEFC1HvHVJ&file={file}"
    # primero encolo el mensaje en la base de datos
    con = get_con()
    last_timeout = pgonecolumn(con, "select timeout from logwhatsapp order by\
            id desc limit 1")
    last_enviado = pgonecolumn(con, "select enviado from logwhatsapp where\
            enviado!=0 order by id desc limit 1")
    if not last_timeout:
        last_timeout = int(time.time())
    if not last_enviado:
        last_enviado = int(time.time())
    timeout = last_enviado if last_enviado > last_timeout else last_timeout
    ins = f"insert into logwhatsapp(idcliente,wapp,msg,file,user,timein,\
            timeout,response,enviado,fecha) values({idcliente},\
            {wapp_original},'{msg.replace('%20',' ')[:100]}','{file_log}'\
            ,'{email}',{int(time.time())},{timeout+20},'',0,curdate())"
    cur = con.cursor()
    cur.execute(ins)
    con.commit()
    id = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
    time_delivery = timeout+20
    # logging.warning(f"time_delivery:{time_delivery} real-time:{time.ctime(time.time())}")
    while True:
        if time.time() > time_delivery:
            response = requests.request("GET", payload)
            # logging.warning(f"Time al request:{time.time()}")
            break
        time.sleep(1)
    wapp_log(response.status_code, response.text, idcliente)
    if "Success" in response.text:
        upd = f"update logwhatsapp set response='success', enviado=\
                {int(time.time())} where id = {id}"
        # logging.warning(upd)
        cur.execute(upd)
        con.commit()
        con.close()
        return "success"
    elif "Invalid Destination WhatsApp" in response.text:
        updinv = f"update clientes set wapp_invalido='{wapp}',wapp='INVALIDO' \
                where id={idcliente}"
        # logging.warning(updinv)
        con = get_con()
        cur = con.cursor()
        # logging.warning(updinv)
        cur.execute(updinv)
        log(updinv)
        upd = f"update logwhatsapp set response='invalid', enviado=\
                {int(time.time())} where id = {id}"
        # logging.warning(upd)
        cur.execute(upd)
        con.commit()
        con.close()
        return "invalid"
    elif "Failed" in response.text:
        upd = f"update logwhatsapp set response='failed', enviado=\
                {int(time.time())} where id = {id}"
        # logging.warning(upd)
        cur.execute(upd)
        con.commit()
        con.close()
        return "failed"
    elif "limit" in response.text:
        upd = f"update logwhatsapp set response='limit', enviado=\
                {int(time.time())} where id = {id}"
        # logging.warning(upd)
        cur.execute(upd)
        con.commit()
        con.close()
        return "limit"
    else:
        return 'error', 401


def wapp_logenviados(wapp, msg, user):
    """Funcion que registra el wapp en la tabla wappsenviados."""
    con = get_con()
    msg = msg.replace("%20", " ")
    ins = f"insert into wappsenviados(wapp,msg,user) values('{wapp}',\
        '{msg}','{user}')"
    pgexec(con, ins)
    con.close()


def wapp_log(log1, log2, wapp, tiempo, idcliente):
    """Funcion que hace un log en txt de las responses de la api."""
    with open("/home/hero/log/wapp.log", "a", encoding="utf-8") as log_file:
        log_file.write('\n')
        log_file.write(str(wapp)+' '+str(log1)+' '+tiempo+' ' +
                       str(time.time())+' Idcliente:'+str(idcliente)+' '
                       + str(log2))
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
