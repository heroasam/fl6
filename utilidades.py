from flask import Blueprint,render_template,jsonify,make_response, request, send_file
from flask_login import login_required, current_user
from .lib import *
from .con import get_con, log
import pandas as pd
import simplejson as json
import mysql.connector
import os

utilidades = Blueprint('utilidades',__name__)

@utilidades.route('/utilidades')
def utilidades_home():
    return render_template('/utilidades/utilidades.html')

@utilidades.route('/utilidades/impresos')
def utilidades_impresos():
    return render_template('/utilidades/impresos.html')


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