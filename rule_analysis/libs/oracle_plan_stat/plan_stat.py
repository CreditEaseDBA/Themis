# -*- coding: utf-8 -*-

import re


class OraclePlanOrStat(object):

    def __init__(self, mongo_client, username, capture_date):
        """
        """
        self.mongo_client = mongo_client
        self.func_list = ['sum\(', 'max\(', 'count\(',
                            'min\(', 'avg\(', 'rank\(']
        self.username = username
        self.capture_date = capture_date

    def query_sql_plan(self, sql_id, hash_value):
        """
        获取oracle执行计划信息
        """

        sql = {
            "USERNAME": self.username,
            "SQL_ID": sql_id,
            "PLAN_HASH_VALUE": hash_value,
            "ETL_DATE": self.capture_date
        }
        condition = {
            "ID":1,
            "OPERATION_DISPLAY":1,
            "OPTIONS":1,
            "OBJECT_OWNER":1,
            "OBJECT_NAME":1,
            "DEPTH": 1,
            "COST": 1,
            "_id": 0,
            "PARENT_ID": 1,
            "CARDINALITY":1
        }
        plan = self.mongo_client.find("sqlplan", sql, condition)
        return plan

    def query_sql_text(self, sql_id):
        """
        获取oracle文本信息
        """

        sql = {
            "USERNAME": self.username,
            "SQL_ID": sql_id,
            "ETL_DATE": self.capture_date
        }
        condition = {"SQL_TEXT": 1, "SQL_TEXT_DETAIL": 1, "_id": 0}
        text = self.mongo_client.find("sqltext", sql, condition)
        return text

    def query_obj_info(self, obj_type, obj_name):
        """
        获取oracle对象信息
        """
        sql = {
                "OWNER": self.username,
                "ETL_DATE": self.capture_date
            }
        if obj_type == "TABLE":
            sql.update({"TABLE_NAME": obj_name})
            condition = {
                "TABLE_NAME": 1,
                "TABLE_TYPE": 1,
                "NUM_ROWS": 1,
                "PHY_SIZE(MB)": 1,
                "COL_NUM": 1,
                "LAST_ANALYZED": 1,
                "LAST_DDL_TIME": 1,
                "AVG_ROW_LEN": 1,
                "OBJECT_TYPE": 1,
                "BLOCKS": 1,
                "_id":0
            }
            collection = "obj_tab_info"
        elif obj_type == "INDEX":
            sql.update({"INDEX_NAME": obj_name})
            condition = {
                "DISTINCT_KEYS": 1,
                "IDX_TYPE": 1,
                "UNIQUENESS": 1,
                "TABLE_NAME": 1,
                "LAST_ANALYZED": 1,
                "LAST_DDL_TIME": 1,
                "CLUSTERING_FACTOR": 1,
                "PHY_SIZE(MB)": 1,
                "BLEVEL": 1,
                "_id":0
            }
            collection = "obj_ind_info"
        elif obj_type == "PART_TABLE":
            sql.update({"TABLE_NAME": obj_name})
            condition = {
                "NUM_ROW": 1,
                "PHY_SIZE(MB)": 1,
                "PARTITIONING_TYPE": 1,
                "PARTITION_COUNT": 1,
                "COLUMN_NAME": 1,
                "LAST_DDL_TIME": 1,
                "_id":0
            }
            collection = "obj_part_tab_parent"
        elif obj_type == "VIEW":
            sql.update({"VIEW_NAME": obj_name})
            condition = {
                "OBJECT_TYPE": 1,
                "REFERENCED_OWNER": 1,
                "REFERENCED_NAME": 1,
                "REFERENCED_TYPE": 1,
                "_id":0
            }
            collection = "obj_view_info"
        else:
            return [None]
        temp_data = self.mongo_client.find(collection, sql, condition)
        return temp_data

        

    def query_sql_stat(self, sql_id, hash_value):
        """
        获取oracle统计特征信息
        """

        sql = {
            "USERNAME": self.username,
            "SQL_ID": sql_id,
            "PLAN_HASH_VALUE": hash_value,
            "ETL_DATE": self.capture_date
        }
        condition = {
            "CPU_TIME_DELTA": 1,
            "PER_CPU_TIME": 1,
            "EXECUTIONS_DELTA": 1,
            "ELAPSED_TIME_DELTA": 1,
            "PER_ELAPSED_TIME": 1,
            "BUFFER_GETS_DELTA": 1,
            "PER_BUFFER_GETS": 1,
            "DISK_READS_DELTA": 1,
            "PER_DISK_READS": 1,
            "_id":0
        }
        stat = self.mongo_client.find("sqlstat", sql, condition)
        return stat

    def execute(self, rule_type, temp_data, rule_cmd_attach, obj_type,
                weight, max_score):
        data = []
        sql_plans = []
        sql_texts = []
        sql_stats = []
        sql_objs = []
        sql_score = []
        if rule_cmd_attach:
            sql_id_list = self.exclude(temp_data, self.capture_date)
            for sql in temp_data:
                if sql["SQL_ID"] in sql_id_list:
                    data.append(sql)
        else:
            data = temp_data
        for sql in data:
            sql_id = sql["SQL_ID"]
            hash_value = sql["PLAN_HASH_VALUE"]
            temp_plan = [sql_id, hash_value]
            temp_text = [sql_id]
            temp_stat = [sql_id, hash_value]
            temp_obj = []
            if rule_type == "SQLPLAN":
                object_name = sql["OBJECT_NAME"]
                temp_plan.append(sql["ID"])
                temp_stat.append(sql["ID"])
                temp_obj.extend([sql_id, hash_value, self.username,
                    object_name, sql["ID"], sql["COST"], sql["COUNT"]])
                query_obj = list(self.query_obj_info(obj_type, object_name))
                if not query_obj:
                    query_obj = [None]
                temp_obj.extend(query_obj)

            # if rule type is stat and rule_name is SQL_BLOCK_NUM,
            # exclude the sql which text like sum,count,avg ......
            # elif rule_type == "sqltext":
            #     if sql_id not in sql_score:
            #         sql_score.append(sql_id)
            #     score = self.get_score(len(sql_score), weight, max_score)
            #     return "", "", temp_data, "", score
            temp_stat.append(self.username)
            temp_plan.append(list(self.query_sql_plan(sql_id, hash_value)))
            temp_text.extend(list(self.query_sql_text(sql_id)))
            temp_stat.extend(list(self.query_sql_stat(sql_id, hash_value)))
            sql_plans.append(temp_plan)
            sql_texts.append(temp_text)
            sql_stats.append(temp_stat)
            if temp_obj:
                sql_objs.append(temp_obj)
            tmp = sql_id + "#" + str(hash_value)
            if tmp not in sql_score:
                sql_score.append(tmp)
        score = self.get_score(len(sql_score), weight, max_score)
        return sql_objs, sql_plans, sql_texts, sql_stats, score

    def exclude(self, temp_data):
        """
        """

        sql_text_list = []
        all_sql_id_list = []
        ex_sql_id_list = []
        for sql in temp_data:
            text = self.query_sql_text(sql["SQL_ID"], self.capture_date)
            sql_text_list.append(sql["SQL_ID"], text)
            all_sql_id_list.append(sql_text_list[0][0])
            sql_id = sql_text_list[0][0]
            sql_text = sql_text_list[0][1][0]["SQL_TEXT_DETAIL"]
            # 匹配sql文本中是否有聚合函数,如果有聚合函数，该sql不作为审核对象
            for func in self.func_list:
                match = re.search(func, sql_text, re.IGNORECASE)
                if match:
                    ex_sql_id_list.append(sql_id)
        #Get diff between a_sql_id_list and e_sql_id_list
        return list(set(all_sql_id_list) - set(ex_sql_id_list))


    def iter(self, ls):
        temp_data = []
        [temp_data for data in ls]
        return temp_data

    def get_score(self, num, weight, max_score):
        """
        计算分数值
        """
        score = num * float(weight)
        if score > float(max_score):
            return "%0.2f" % float(max_score)
        return "%0.2f" % score

