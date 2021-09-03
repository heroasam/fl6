import os
import mysql.connector
from flask_login import current_user
#import pymysql



#con = pymysql.connect(host='localhost',database='hero',user='hero',password='ata')
con = mysql.connector.connect(host='localhost',database='hero',user='hero',password='ataH2132**/')
def get_con():
    #con = pymysql.connect(host='localhost',database='hero',user='hero',password='ata')
    con = mysql.connector.connect(host='localhost',database='hero',user='hero',password='ataH2132**/')
    return con


def log(stmt):
    con = get_con()
    cur = con.cursor()
    ins = f'insert into log(fecha, user, stmt) values(CURRENT_TIMESTAMP,"{current_user.email}","{stmt}")'
    cur.execute(ins)
    con.commit()
    con.close()



