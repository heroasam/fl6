from flask import Blueprint,render_template,jsonify,make_response, request, send_file
from flask_login import login_required, current_user
from lib import *
from con import get_con, log
import pandas as pd
import simplejson as json
import mysql.connector
import os
import glob


utilidades = Blueprint('utilidades',__name__)

@utilidades.route('/utilidades/planos')
def utilidades_planos():
    return render_template('/utilidades/planos.html')

@utilidades.route('/utilidades/impresos')
def utilidades_impresos():
    return render_template('/utilidades/impresos.html')


@utilidades.route('/utilidades/pdfsistema')
def utilidades_pdfimpresos():
    return render_template('/utilidades/pdfsistema.html')


@utilidades.route('/utilidades/getplanos')
def utilidades_getplanos():
    listaplanos = os.listdir('/home/hero/documentos/planos')
    listaplanos.sort()
    return jsonify(planos=listaplanos)


@utilidades.route('/utilidades/imprimirplanos/<string:plano>')
def utilidades_imprimirplano(plano):
    return send_file(os.path.join('/home/hero/documentos/planos',plano))


@utilidades.route('/utilidades/getimpresos')
def utilidades_getimpresos():
    listaimpresos = os.listdir('/home/hero/documentos/impresos')
    listaimpresos.sort()
    return jsonify(impresos=listaimpresos)


@utilidades.route('/utilidades/imprimirimpreso/<string:impreso>')
def utilidades_imprimirimpreso(impreso):
    return send_file(os.path.join('/home/hero/documentos/impresos',impreso))


@utilidades.route('/utilidades/getpdfsistema')
def utilidades_pdfsistema():
    listapdfs = os.listdir('/home/hero')
    pdfs = [os.path.split(pdf)[1] for pdf in listapdfs if pdf[-3:]=='pdf']
    pdfs.sort()
    return jsonify(pdfs=pdfs)


@utilidades.route('/utilidades/imprimirpdfsistema/<pdf>')
def utilidades_imprimirpdfsistema(pdf):
    return send_file(os.path.join('/home/hero',pdf))


@utilidades.route('/utilidades/contador')
def utilidades_contador():
    return render_template('/utilidades/contador.html')
