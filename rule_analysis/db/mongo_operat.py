# -*- coding: utf-8 -*-

import pymongo


class MongoOperat(object):
    """
    mongodb连接模块，负责初始化mongo，认证，动态获取集合等功能
    """

    def __init__(self, hostname, port, dbname=None, account=None,
                 password=None):
        """
        mongo初始化
        """
        self.conn = pymongo.MongoClient(
            hostname, port, serverSelectionTimeoutMS=1000)
        if account and password:
            self.conn.admin.authenticate(account, password)
        self.dbname = dbname if dbname else "sqlreview"
        self.db = getattr(self.conn, self.dbname)

    def get_collection(self, collection):
        """
        动态获取collection
        参数 collection：collecion名称
        示例：
            client = MongoOperat("127.0.0.1", 27017)
            rule = client.get_collection("rule")
        """
        return getattr(self.db, collection)

    def command(self, rule_cmd, nolock=True):
        """
        利用mongo自身的优势去执行一些命令
        参数 rule_cmd: 需要在mongo中执行的一些语句
            nolock: 防止阻塞选项
        示例：
            client = MongoOperat("127.0.0.1", 27017)
            rule_cmd = "db.rule.find({'db_type' : 'O'})"
            client.command(rule_cmd)
        """
        self.db.command("eval", rule_cmd, nolock)

    def find(self, collection, sql, condition=None):
        result = self.get_collection(collection).find(sql, condition)
        return result

    def update(self, collection, sql, condition=None):
        self.get_collection(collection).update(sql, condition)

    def update_one(self, collection, sql, condition=None):
        self.get_collection(collection).update_one(sql, condition)

    def insert_one(self, collection, sql, condition=None):
        object_id = self.get_collection(collection).insert_one(sql, condition)
        return object_id

    def insert(self, collection, sql, condition=None):
        object_id = self.get_collection(collection).insert(sql, condition)
        return object_id

    def drop(self, collection):
        self.get_collection(collection).drop()
