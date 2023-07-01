# -*- coding: utf-8 -*-
"""Librerias generales."""
import os
from flask_login import current_user
import requests
import time
from datetime import datetime
import logging
import mysql.connector
import urllib.parse



def get_con():
    con = mysql.connector.connect(host='localhost',database='hero',user='hero',password='ataH2132**/')
    return con


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

def send_msg_whatsapp(idcliente, wapp, msg, api=1):
    """Funcion que encola wapp de texto."""
    api = 2
    procesar_msg_whatsapp_apis(idcliente, wapp, msg, api)


def procesar_msg_whatsapp_apis(idcliente,wapp, msg_uri, api):
    """procesar msg para nuevas apis."""
    con = get_con()
    if hasattr(current_user, 'email'):
        email = current_user.email
    else:
        email = 'sistema'
    # if api==1:
    #     servidor = "heroasam.xyz"
    # elif api==2:
    #     servidor = "romulana.xyz"
    # elif api==3:
    #     servidor = "catalina.lol"
    servidor = "heroasam.xyz"
    msg = urllib.parse.unquote(msg_uri)
    payload = f"https://{servidor}/sendMsg/{api}/{wapp}/{msg_uri}"
    ins = f"insert into logwhatsapp(idcliente,wapp,msg,file,user,timein,\
    timeout,response,enviado,fecha,api) values({idcliente},'{wapp}',\
    '{msg.replace('%20',' ')[:100]}','','{email}',{int(time.time())}\
    ,0,'',0,curdate(),{api})"
    pgexec(con, ins)
    idlog = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
    try:
        response = requests.get(payload)
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
        resultado = response.text
    logging.warning(
        f"mensaje {wapp} enviado a las:{str(time.ctime(time.time()))} {resultado} por api {api} msg {msg}")
    wapp_log(response.status_code, resultado, wapp,
            str(time.ctime(time.time())), idcliente,api)
    if "ok" in resultado:
        upd = f"update logwhatsapp set response='success',\
        enviado={int(time.time())} where id = {idlog}"
        wapp_logenviados(wapp, msg, email,api)
        pgexec(con, upd)
        return 'success'
    else:
        return resultado


def send_file_whatsapp(idcliente, file, wapp, msg='', api=1):
    """Funcion que encola wapp de file."""
    api = 2
    procesar_file_whatsapp_apis(idcliente, file, wapp,api)


def procesar_file_whatsapp_apis(idcliente, file, wapp,api):
    logging.warning(f"procesar_file_whatsapp en api:{api}")
    con = get_con()
    if hasattr(current_user, 'email'):
        email = current_user.email
    else:
        email = 'sistema'
    # if api==1:
    #     servidor = "heroasam.xyz"
    # elif api==2:
    #     servidor = "romulana.xyz"
    # elif api==3:
    #     servidor = "catalina.lol"
    servidor = "heroasam.xyz"
    file_log = os.path.split(file)[1]
    ins = f"insert into logwhatsapp(idcliente,wapp,msg,file,user,timein,\
            timeout,response,enviado,fecha) values({idcliente},\
            '{wapp}','','{file_log}'\
            ,'{email}',{int(time.time())},0,'',0,curdate())"
    pgexec(con, ins)
    idlog = pgonecolumn(con, "SELECT LAST_INSERT_ID()")
    try:
        payload =f"https://{servidor}/sendFile/{api}/{wapp}/{file_log}"
        response =requests.get(payload)
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
        resultado = response.text
        logging.warning(
            f"mensaje {wapp} enviado a las:{str(time.ctime(time.time()))} {resultado} {time.time()} api{api}")
        wapp_log(response.status_code, resultado, wapp,
                    str(time.ctime(time.time())), idcliente,api)
        if "ok" in resultado:
            upd = f"update logwhatsapp set response='success',\
            enviado={int(time.time())} where id = {idlog}"
            wapp_logenviados(wapp, file_log, email,api)
            pgexec(con, upd)
            return 'success'
        else:
            return resultado


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
