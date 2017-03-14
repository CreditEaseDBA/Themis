# -*- coding: utf-8 -*-

def oracle_connect(ip, port, username, passwd, sid=None, service_name=None):
    import cx_Oracle
    if sid:
        # sid connect
        dsn = cx_Oracle.makedsn(ip, port, sid)
        instance_status = 1
        db = cx_Oracle.connect(username, passwd, dsn)
        return db
    if service_name:
        # service_name connect
        handle = ip + ":" + port + "/" + service_name
        db = cx_Oracle.connect(username, passwd, handle)
        return db
