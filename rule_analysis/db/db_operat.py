# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] == 2:
    import MySQLdb
elif sys.version_info[0] == 3:
    import mysql.connector as MySQLdb

class DbOperat(object):
    """
    数据库连接模块，支持oracle和mysql的连接
    oracle连接支持sid和service_name的方式，建议通过sid的方式连接
    """

    def __init__(self, host, port, username, password, db=None,
                 service_name=None, charset="utf8", flag=True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.db = db
        if flag:
            if int(self.port) != 1521:
                self.db = db
                self.conn = MySQLdb.connect(host=self.host,
                                            port=int(self.port),
                                            user=self.username,
                                            passwd=self.password, db=self.db,
                                            charset=charset)
                self.cursor = self.conn.cursor()
            else:
                import cx_Oracle
                # self.sid = sid
                self.service_name = service_name
                if self.db:
                    self.dsn = cx_Oracle.makedsn(self.host,
                        str(self.port), self.db)
                    self.conn = cx_Oracle.connect(
                        self.username, self.password, self.dsn)
                elif self.service_name:
                    self.handle = "%s:%s/%s" % \
                        (self.host, str(self.port), self.service_name)
                    self.conn = cx_Oracle.connect(
                        self.username, self.password, self.handle)
                self.cursor = self.conn.cursor()
        else:
            self.db = db

    def get_db_cursor(self):
        return self.cursor

    def execute(self, sql):
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return results

    def close(self):
        self.cursor.close()
        self.conn.close()

    def escape(self, string):
        return MySQLdb.escape_string(string)

    def new_connect(self, host, port, db, user, passwd):
        self.conn = MySQLdb.connect(host=host, port=port,
            user=user, passwd=passwd, db=db, charset="utf8")
        self.cursor = self.conn.cursor()


if __name__ == "__main__":
    pass
