import os
import mysql.connector
#import pymysql



#con = pymysql.connect(host='localhost',database='hero',user='hero',password='ata')
con = mysql.connector.connect(host='localhost',database='hero',user='hero',password='ata')
def get_con():
    #con = pymysql.connect(host='localhost',database='hero',user='hero',password='ata')
    con = mysql.connector.connect(host='localhost',database='hero',user='hero',password='ata')
    return con





