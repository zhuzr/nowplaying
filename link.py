#!/usr/bin/env python
import MySQLdb
from configparser import ConfigParser
global DBLINK
DBLINK={}

cf = ConfigParser()
cf.read("link.conf")
host = cf.get("db", "host")
username = cf.get("db", "username")
password = cf.get("db", "password")
database = cf.get("db", "database")


class linkDB():
    global DBLINK
    def __init__(self,name ='none',arg_host = host,arg_user=username,arg_passwd=password,arg_db=database,charset="utf8"):
        self.host = arg_host
        self.user = arg_user
        self.passwd = arg_passwd
        self.db = arg_db      
        self.name = name  
        if self.name not in DBLINK:
            try:
                DBLINK[name]={}
                conn = MySQLdb.connect(self.host, self.user, self.passwd,self.db,charset=charset)            
                DBLINK[name][self.db] = conn
            except Exception as msg:
                print (msg)
                print ('connect database failed!')
            
    def RetExecSQL(self,sql):
        conn = DBLINK[self.name][self.db]
        cursor = conn.cursor()
        count = cursor.execute(sql)
        result = cursor.fetchmany(count)
        cursor.close()
        return result
    
    def NretExecSQL(self,sql):
        conn = DBLINK[self.name][self.db]
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        
    
    def close(self):
        if self.name in DBLINK:
            DBLINK[self.name][self.db].close()
            del DBLINK[self.name]
    
def get_conn():
    return MySQLdb.connect(host, username, password,database,charset="utf8") 
