import os
import mysql.connector
from flask_login import current_user
#import pymysql
from sqlalchemy import create_engine


engine = create_engine('mysql+mysqlconnector://hero:ataH2132**/@localhost/hero')

#con = pymysql.connect(host='localhost',database='hero',user='hero',password='ata')
con = mysql.connector.connect(host='localhost',database='hero',user='hero',password='ataH2132**/')
def get_con():
    #con = pymysql.connect(host='localhost',database='hero',user='hero',password='ata')
    con = mysql.connector.connect(host='localhost',database='hero',user='hero',password='ataH2132**/')
    return con


def log(stmt):
    if not current_user.is_anonymous:
        current = current_user.email
    else:
        current = "no user yet"
    con = get_con()
    cur = con.cursor()
    ins = f'insert into log(fecha, user, stmt) \
    values(CURRENT_TIMESTAMP,"{current}","{stmt}")'
    cur.execute(ins)
    con.commit()
    con.close()
