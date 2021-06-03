import psycopg2
import psycopg2.extras
import os

# DATABASE_URL = os.environ['DATABASE_URL']
# con = psycopg2.connect(DATABASE_URL, sslmode='require')


con = psycopg2.connect(dbname='hero', user='hero', host='localhost', password='ata', port=5432)