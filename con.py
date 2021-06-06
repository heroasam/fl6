import os
import mysql.connector


con = mysql.connector.connect(host='localhost',database='hero',user='hero',password='ata')

def get_con():
    con = mysql.connector.connect(host='localhost',database='hero',user='hero',password='ata')
    return con





