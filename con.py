import psycopg2
import psycopg2.extras
import os

# DATABASE_URL = os.environ['DATABASE_URL']
# con = psycopg2.connect(DATABASE_URL, sslmode='require')

#con = psycopg2.connect(dbname='daq6n3vvmrg79o', user='ynpqvlqqsidhga', host='ec2-3-95-87-221.compute-1.amazonaws.com', password='4bded69478ac502d5223655094cbc2241ed5aaf025f0b31fd19494c5aa35d6f0',sslmode='require')
con = psycopg2.connect(dbname='hero', user='hero', host='localhost', password='ata', port=5432)