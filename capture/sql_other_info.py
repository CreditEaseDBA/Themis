# -*- coding: utf-8 -*-

import cx_Oracle

from capture.sql import *
from capture.base import Capture


class CaptureOther(Capture):

    def __init__(self, mongo_client, db_cursor, ipaddress, sid,
                 etl_date, startdate, stopdate):
        # self.username = username
        self.ipaddress = ipaddress
        self.sid = sid
        self.etl_date = etl_date
        self.startdate = startdate
        self.stopdate = stopdate
        super(CaptureOther, self).__init__(mongo_client, db_cursor)

    def query_sql_plan(self, sql_id, hash_value, username, collection):
        v_sql_plan = SQL_PLAN_SET.\
            replace("&sql_id", sql_id).\
            replace("&h_value", hash_value)
        records, columns = self.query_sql(v_sql_plan)
        for value in records:
            temp_dict = {}
            for i in range(len(value)):
                temp_dict.update({
                    columns[i]: value[i],
                    "USERNAME": username,
                    "ETL_DATE": self.etl_date,
                    "IPADDR": self.ipaddress,
                    "DB_SID": self.sid
                })
            if temp_dict.get("COST") == 18446744073709551615:
                temp_dict["COST"] = str(long(temp_dict["COST"]))
            if temp_dict.get("POSITION", None) == 18446744073709551615:
                temp_dict["POSITION"] = str(long(temp_dict["POSITION"]))
            if temp_dict.get("CPU_COST", None) == 18446744073709551615:
                temp_dict["CPU_COST"] = str(long(temp_dict["CPU_COST"]))
            if temp_dict.get("BYTES", None) == 18446744073709551615:
                temp_dict["BYTES"] = str(long(temp_dict["BYTES"]))
            if temp_dict.get("CARDINALITY", None) == 18446744073709551615:
                temp_dict["CARDINALITY"] = str(long(temp_dict["CARDINALITY"]))
            self.mongo_client.insert(collection, temp_dict)

    def query_sql_stat(self, begin_snap_id, end_snap_id, sql_id,
                       hash_value, collection, username):
        v_sql_stat = SQL_STAT_SET.\
            replace("&beg_snap", begin_snap_id).\
            replace("&end_snap", end_snap_id).\
            replace("&username", username).\
            replace("&sql_id", sql_id).\
            replace("&plan_hash_value", hash_value)
        records, columns = self.query_sql(v_sql_stat)
        for value in records:
            temp_dict = {}
            for i in range(len(value)):
                temp_dict.update({
                    columns[i]: value[i],
                    "ETL_DATE": self.etl_date,
                    "IPADDR": self.ipaddress,
                    "DB_SID": self.sid
                })
            self.mongo_client.insert(collection, temp_dict)

    def query_sql_text(self, sql_id, collection, username):
        sql_text = SQL_TEXT_SET.replace("&sql_id", sql_id)
        try:
            records, columns = self.query_sql(sql_text)
        except cx_Oracle.DatabaseError:
            records = []
            columns = []
        for value in records:
            temp_dict = {}
            for i in range(len(value)):
                temp_dict.update({
                    columns[i]: value[i],
                    "IPADDR": self.ipaddress,
                    "DB_SID": self.sid,
                    "USERNAME": username,
                    "ETL_DATE": self.etl_date
                })
            self.mongo_client.insert(collection, temp_dict)

    def query_no_bind(self, username):
        sql_no_bind = SQL_NO_BIND_SET.\
            replace("&username", username)
        sql_no_bind_data = self.query_no_bind_sql_info(sql_no_bind)

        for key, value in sql_no_bind_data.items():
            sql_no_bind_data[key].update({
                "IPADDR": self.ipaddress,
                "DB_SID": self.sid,
                "ETL_DATE": self.etl_date
            })
            self.mongo_client.insert("sqltext", sql_no_bind_data[key])

    def query_sql_cursor(self, begin_snap_id, end_snap_id, username):
        sql_cursor = SQL_CURSOR_SET.\
            replace("&username", username).\
            replace("&beg_snap", begin_snap_id).\
            replace("&end_snap", end_snap_id)
        records, columns = self.query_sql(sql_cursor)
        for data in sql_cursor:
            cursor_dict = {}
            for i in range(len(data)):
                cursor_dict.update({
                    columns[i]: data[i],
                    "IPADDR": self.ipaddress,
                    "DB_SID": self.sid,
                    "ETL_DATE": self.etl_date
                })
            self.mongo_client.insert("stat_cursor", cursor_dict)

    def query_no_bind_sql_info(self, sql):
        self.db_cursor.execute(sql)
        records = self.db_cursor.fetchall()
        sql_text_set = {}
        sql_text = {}
        for data in records:
            schema = data[1]
            signature = data[2]
            hash_value = data[3]
            count = data[4]
            tmp = "#".join([str(signature), str(hash_value)])
            temp_sql = """
            SELECT sql_id,
                   dbms_lob.substr(a.sql_text,40,1) sql_text,
                   dbms_lob.substr(a.sql_fulltext,3000,1) sql_text_detail
            FROM gv$sql a
            WHERE to_char(a.FORCE_MATCHING_SIGNATURE) = '{signature}'
              AND a.PLAN_HASH_VALUE={hash}
              AND a.MODULE <> 'DBMS_SCHEDULER'
              AND a.MODULE <> 'PL/SQL Developer'
              AND rownum = 1
            """
            self.db_cursor.execute(temp_sql)
            records_text = self.db_cursor.fetchall()
            sql_text.update({
                "USERNAME": schema,
                "FORCE_MATCHING_SIGNATURE": signature,
                "PLAN_HASH_VALUE": hash_value,
                "SQL_ID": records_text[0][0],
                "SQL_TEXT": records_text[0][1],
                "SQl_TEXT_DETAIL": records_text[0][2],
                "SUM": count
            })
            sql_text_set[tmp] = sql_text
        return sql_text_set

    def query_snap_id(self):
        sql = """
        SELECT min(snap_id),
        max(snap_id)
        FROM DBA_HIST_SNAPSHOT
        WHERE instance_number=1
          AND (end_interval_time BETWEEN to_date('{startdate}','yyyy-mm-dd hh24:mi:ss') 
          AND to_date('{stopdate}','yyyy-mm-dd hh24:mi:ss'))
        """
        self.db_cursor.execute(
            sql.format(startdate=self.startdate, stopdate=self.stopdate))
        result = self.db_cursor.fetchall()
        return str(result[0][0]), str(result[0][1])

    def parse_result(self, username):

        parameter = [
            "elapsed_time",
            "cpu_time",
            "disk_reads",
            "executions",
            "buffer_gets"
        ]

        begin_snap_id, end_snap_id = self.query_snap_id()

        sql_id_text_set = []
        sql_id_set = []

        # return resource top sql
        for value in parameter:
            v_sql_id = SQL_SET.\
                replace("&beg_snap", begin_snap_id).\
                replace("&end_snap", end_snap_id).\
                replace("&parameter", value).\
                replace("&username", username)
            sql_id_data, _ = self.query_sql(v_sql_id)
            for sql_id in sql_id_data:
                sql_id_text = "#".join([sql_id[0], sql_id[2]])
                sql_id_hash = "#".join([sql_id[0], str(sql_id[1]), sql_id[2]])
                if sql_id_hash not in sql_id_set:
                    sql_id_set.append(sql_id_hash)
                if sql_id_text not in sql_id_text_set:
                    sql_id_text_set.append(sql_id_text)

        # single sql plan/stat
        for data in sql_id_set:
            tmp = data.split("#")
            self.query_sql_stat(begin_snap_id,
                end_snap_id, tmp[0], tmp[1], "sqlstat", username)
            self.query_sql_plan(tmp[0], tmp[1], tmp[2], "sqlplan")

        for data in sql_id_text_set:
            tmp = data.split("#")
            self.query_sql_text(tmp[0], "sqltext", tmp[1])

        sql_cursor = SQL_CURSOR_SET.\
            replace("&username", username).\
            replace("&beg_snap", begin_snap_id).\
            replace("&end_snap", end_snap_id)
        sql_cursor_data, cursor_columns = self.query_sql(sql_cursor)
        for data in sql_cursor_data:
            cursor_dict = {}
            data_length = len(data)
            for i in range(data_length):
                cursor_dict.update({
                    cursor_columns[i]: data[i],
                    "IPADDR": self.ipaddress,
                    "DB_SID": self.sid,
                    "ETL_DATE": self.etl_date
                })
            self.mongo_client.insert("stat_cursor", cursor_dict)
            self.query_sql_plan(
                data[1], str(data[2]), data[0], "stat_cursor_plan")
            self.query_sql_stat(begin_snap_id, end_snap_id,
                data[1], str(data[2]), "stat_cursor_stat", username)
            self.query_sql_text(data[1], "stat_cursor_text", data[0])

    def run(self):
        owner_list, _ = self.query_sql(OWNER_LIST_SQL)
        for obj_owner in owner_list:
            self.parse_result(obj_owner[0])
