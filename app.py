from flask import Flask, json
from flask import render_template,url_for,request,redirect, make_response, session, flash
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from flask_cors import CORS
from werkzeug.urls import url_parse
import psycopg2
import psycopg2.extras
from lib import *
from formularios import *
# import pandas as pd
# import numpy as np
# import re
# import ast
# import os
from ventas import ventas
from stock import stock
from pagos import pagos
from buscador import buscador
from fichaje import fichaje
from con import con


app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
CORS(app)

csrf = CSRFProtect(app)
login = LoginManager(app)
login.login_view = "login"
bcrypt = Bcrypt(app)


app.register_blueprint(ventas)
app.register_blueprint(stock)
app.register_blueprint(pagos)
app.register_blueprint(buscador)
app.register_blueprint(fichaje)

class User(UserMixin):
    def __init__(self, id, name, email, password, auth=0):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.auth = auth
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    def __repr__(self):
        return '<User {}>'.format(self.email)


@login.user_loader
def load_user(id):
    try:
        log = pgdict(con, f"select id,name,email,password,auth from users where id={id}")
        user = User(log[0][0],log[0][1], log[0][2],log[0][3],log[0][4])
        return user
    except:
        return None


@app.route('/login', methods=['GET','POST'])
def login():
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        log = pgdict(con, f"select id,name,email,password,auth from users where email='{email}'")
        errormail = "Ese email no existe en la base de datos. Registrese"
        errorpassword = "Ha ingresado una contraseña incorrecta"
        errorauth = "Ese email no esta autorizado a ingresar"
        if log==[]:
            return render_template('login_form.html', errormail=errormail)
        user = User(log[0][0],log[0][1], log[0][2],log[0][3],log[0][4])
        if not user.check_password(password):
            return render_template('login_form.html', errorpassword=errorpassword)
        if user.auth==0:
            return render_template('login_form.html',errorauth=errorauth)
        if user is not None and user.check_password(password) and user.auth :
            login_user(user,remember=True)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('buscador.buscador_')
            return redirect(next_page)
    return render_template('login_form.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/signup' , methods=['GET','POST'])
def signup():
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
        elif pgonecolumn(con,f"select email from users where email='{email}'"):
            error = f"El email {email} ya esta en uso. Haga Login"

        if error is None:
            password = bcrypt.generate_password_hash(password).decode('utf-8')
            ins = f"insert into users(name, email, password) values('{name}', '{email}', '{password}')"
            cur = con.cursor()
            try:
                cur.execute(ins)
            except psycopg2.Error as e:
                con.rollback()
                error = e.pgerror
                return make_response(error,400)
            else:
                con.commit()
                cur.close()
                flash("Registro correctamente ingresado")
                return redirect(url_for('login'))
        flash(error,category='error')    
    return render_template('signup.html')
    

@app.template_filter()
def cur(monto):
    if monto==None:
        return None
    else:
        return f"${int(monto)}"
