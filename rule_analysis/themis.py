# -*- coding: utf-8 -*-

import re
import time

from rule_analysis.db.db_operat import DbOperat
from rule_analysis.db.mongo_operat import MongoOperat
from rule_analysis.libs.oracle_plan_stat.plan_stat import OraclePlanOrStat
from rule_analysis.libs.mysql_plan_stat.plan_stat import MysqlPlanOrStat
from rule_analysis.review_result.rule_result import ReviewResult
from rule_analysis.libs.text.sql_text import SqlText


class Themis(object):
    """
    规则解析类，负责初始化各种数据库句柄，包括mongo，oracle，mysql
    判断规则类型
    """

    def __init__(self, username,
                 rule_type, rule_status,
                 db_type, startdate=None,
                 stopdate=None, create_user=None,
                 hostname=None, **kwargs):
        self.username = username
        self.rule_type = rule_type
        self.db_type = db_type
        self.rule_status = rule_status
        self.create_user = create_user
        self.mongo_client = MongoOperat(kwargs.get("mongo_server"),
                                        kwargs.get("mongo_port"),
                                        kwargs.get("mongo_db"),
                                        kwargs.get("mongo_user", None),
                                        kwargs.get("mongo_password", None))
        self.startdate = startdate
        self.stopdate = stopdate
        self.review_result = ReviewResult(self.mongo_client, self.db_type,
                                          self.rule_type, self.username,
                                          self.rule_status)
        if self.db_type == "O" and self.rule_type in ["SQLPLAN", "SQLSTAT"]:
            self.ora = OraclePlanOrStat(self.mongo_client,
                                        self.username, self.startdate)
        elif self.db_type == "mysql" and \
                self.rule_type in ["SQLPLAN", "SQLSTAT"]:
            pt_server_args = kwargs.get("pt_server_args")
            pt_query_client = self.db_server_init(**pt_server_args)
            self.db_client = self.db_server_init(flag=False, **kwargs)
            self.mys = MysqlPlanOrStat(
                pt_query_client, self.db_client,
                self.mongo_client, self.rule_type)
        elif self.db_type == "O" and self.rule_type == "OBJ":
            self.db_client = self.db_server_init(**kwargs)
        elif self.db_type == "mysql" and self.rule_type == "OBJ":
            self.db_client = self.db_server_init(**kwargs)
        elif self.db_type == "mysql" and self.rule_type == "TEXT":
            self.hostname = hostname
            pt_server_args = kwargs.get("pt_server_args")
            pt_query_client = self.db_server_init(**pt_server_args)
            self.sql_text = SqlText(self.mongo_client, self.startdate,
                                    self.stopdate, self.username,
                                    self.hostname, db_client=pt_query_client)
        elif self.db_type == "O" and self.rule_type == "TEXT":
            self.hostname = hostname
            self.sql_text = SqlText(self.mongo_client, self.startdate,
                                    self.stopdate, self.username,
                                    self.hostname)

    def db_server_init(self, flag=True, **kwargs):
        db_server = kwargs.get("db_server")
        db_port = kwargs.get("db_port")
        db_user = kwargs.get("db_user")
        db_passwd = kwargs.get("db_passwd")
        db = kwargs.get("db", None)
        db_client = DbOperat(db_server, db_port, db_user,
                             db_passwd, db=db, flag=flag)
        return db_client

    def o_rule_parse(self, key, rule_complexity, rule_cmd,
                     weight, max_score, input_parms):
        """
        oracle数据库sqlplan，sqlstat解析
        """
        if rule_complexity == "simple":
            cmd_attach = self.review_result.rule_info[key]["rule_cmd_attach"]
            info_type = self.review_result.rule_info[key]["obj_info_type"]
            # 生成随机的collection名字
            tmp0, tmp1 = self.review_result.gen_random_collection()
            # 替换掉用户自定义的参数
            if input_parms:
                for parm in input_parms:
                    rule_cmd = rule_cmd.replace(
                        "@" + parm["parm_name"] + "@",
                        str(parm["parm_value"]))
            # 替换掉默认参数
            rule_cmd = rule_cmd.replace("@username@", self.username).\
                replace("@tmp@", tmp0).\
                replace("@sql@", self.rule_type.lower()).\
                replace("@etl_date@", self.startdate).\
                replace("@tmp1@", tmp1)
            # 防止已经存在的collection对结果的生成产生影响
            self.mongo_client.drop(tmp0)
            self.mongo_client.drop(tmp1)
            self.mongo_client.command(rule_cmd)
            records = self.mongo_client.find(tmp0, {})
            # self.mongo_client.drop(tmp0)
            # self.mongo_client.drop(tmp1)
            objs, plans, texts, stats, score = self.ora.execute(
                self.rule_type, records, cmd_attach,
                info_type, weight, max_score)
            result = self.review_result.oracle_result(
                objs, texts, plans, stats)
            if result:
                return result, score
            return None, None

    def m_rule_parse(self, key, rule_complexity, rule_cmd,
                     weight, max_score, input_parms, hostname, user, passwd):
        """
        mysql数据库的sqlplan和sqlstat的解析
        """
        result = self.mys.get_sql_info(
            self.startdate, self.stopdate, self.username, hostname)
        if not result:
            return False
        # 回库查询获取执行计划
        self.mys.get_sql_plan(user, passwd)
        if rule_complexity == "simple":
            # 生成随机的collection名字
            tmp0, _ = self.review_result.gen_random_collection()
            self.mongo_client.drop(tmp0)
            # 替换掉自定义参数
            if input_parms:
                for parm in input_parms:
                    rule_cmd = rule_cmd.replace(
                        "@" + parm["parm_name"] + "@",
                        str(parm["parm_value"]))
            # 替换掉默认参数
            rule_cmd = rule_cmd.replace("@schema_name@", self.username).\
                replace("@tmp@", tmp0)
            self.mongo_client.command(rule_cmd)
            match_list, sql_text, sql_plan = self.mys.rule_match(tmp0)
            self.mongo_client.drop(tmp0)
            # 生成最终结果
            if match_list:
                temp = {}
                for data in match_list:
                    sql_id = str(data["checksum"]) + "#1#v"
                    temp_sql_plan = sql_plan[data["checksum"]]
                    temp_full_text = sql_text[data["checksum"]]
                    if len(temp_full_text) > 25:
                        temp_sql_text = temp_full_text[:25]
                    else:
                        temp_sql_text = ""
                    temp.update({
                        sql_id: {
                            "sql_id": data["checksum"],
                            "plan_hash_value": long(1),
                            "sql_text": temp_sql_text,
                            "sql_fulltext": temp_full_text,
                            "plan": temp_sql_plan,
                            "stat": data,
                            "obj_info": {},
                            "obj_name": None
                        }
                    })
                # 计算分数
                scores = len(temp.keys()) * float(weight)
                return temp, scores
            return None, None

    def text_parse(self, key, rule_complexity, rule_cmd,
                   weight, max_score, input_parms, sql_list):
        """
        解析oracle和mysql数据库的TEXT类规则
        """
        args = {}
        for parm in input_parms:
            args[parm["parm_name"]] = parm["parm_value"]
        score_list = []
        temp = {}
        for sql in sql_list:
            sql_id = sql["checksum"] + "#1#v"
            args["sql"] = sql["sqltext_form"]
            # 解析简单规则
            if rule_complexity == "simple":
                pat = re.compile(rule_cmd)
                if pat.search(args["sql"]):
                    score_list.append(sql["checksum"])
                    temp.update({
                        sql_id: {
                            "sql_id": sql["checksum"],
                            "sql_text": sql["sqltext_org"],
                            "obj_name": None,
                            "stat": sql["sqlstats"],
                            "plan": []
                        }
                    })
            # 解析复杂类规则
            elif rule_complexity == "complex":
                # 根据规则名称动态加载复杂规则
                module_name = ".".join(
                    ["rule", self.rule_type.lower(), key.lower()])
                module = __import__(module_name, globals(), locals(), "execute_rule")
                if module.execute_rule(**args):
                    score_list.append(sql["checksum"])
                    temp.update({
                        sql_id: {
                            "sql_id": sql["checksum"],
                            "sql_text": sql["sqltext_org"],
                            "obj_name": None,
                            "stat": sql["sqlstats"],
                            "plan": []
                        }
                    })
        scores = len(score_list) * float(weight)
        if scores > max_score:
            scores = max_score
        return temp, scores

    def obj_parse(self, key, rule_complexity, rule_cmd, weight,
                  max_score, input_parms):
        """
        解析oracle和mysql数据库的OBJ类规则
        """
        flag = True
        # 解析简单规则
        if rule_complexity == "simple":
            for parm in input_parms:
                rule_cmd = rule_cmd.replace(
                    "@" + parm["parm_name"] + "@",
                    str(parm["parm_value"]))
            rule_cmd = rule_cmd.replace("@username@", self.username)
            self.db_client.cursor.execute(rule_cmd)
            results = self.db_client.cursor.fetchall()
        # 解析复杂类规则
        elif rule_complexity == "complex":
            args = {
                "username": self.username,
                "weight": weight,
                "max_score": max_score,
                "db_cursor": self.db_client.cursor
            }
            [args.update({parm["parm_name"]: parm["parm_value"]})
                for parm in input_parms]
            # 根据规则名称动态加载规则模块
            module_name = ".".join(
                    ["rule", self.rule_type.lower(), key.lower()])
            module = __import__(module_name, globals(), locals(), "execute_rule")
            results, flag = module.execute_rule(**args)
        if isinstance(flag, bool):
            scores = len(results) * weight
            if scores > max_score:
                scores = max_score
        else:
            scores = flag
        return results, scores

    def run(self, **kwargs):
        job_record = {}
        if self.rule_type == "TEXT":
            sql_list = self.sql_text.get_text(self.db_type)
        for key, value in self.review_result.rule_info.items():
            job_record[key] = {}
            input_parms = value["input_parms"]
            rule_complexity = value["rule_complexity"]
            rule_cmd = value["rule_cmd"]
            weight = value["weight"]
            max_score = value["max_score"]
            input_parms = value["input_parms"]
            if self.db_type == "O" and \
                    self.rule_type in ["SQLPLAN", "SQLSTAT"]:
                result, score = self.o_rule_parse(key, rule_complexity,
                                                  rule_cmd, weight,
                                                  max_score, input_parms)
                if result:
                    job_record[key].update(result)
                    job_record[key].update({"scores": score})
            elif self.db_type == "mysql" and \
                    self.rule_type in ["SQLPLAN", "SQLSTAT"]:
                hostname = kwargs.get("hostname")
                user = kwargs.get("user")
                passwd = kwargs.get("passwd")
                result, scores = self.m_rule_parse(key, rule_complexity, rule_cmd,
                                                   weight, max_score, input_parms,
                                                   hostname, user, passwd)
                if result:
                    job_record[key].update(result)
                    job_record[key].update({"scores": scores})
            elif self.rule_type == "TEXT":
                result, scores = self.text_parse(key, rule_complexity,
                                                 rule_cmd, weight,
                                                 max_score, input_parms,
                                                 sql_list)
                if result:
                    job_record[key].update(result)
                    job_record[key].update({"scores": scores})
            elif self.db_type == "O" and self.rule_type == "OBJ":
                results, scores = self.obj_parse(key, rule_complexity,
                                                 rule_cmd, weight,
                                                 max_score, input_parms)
                job_record[key].update({"records": results, "scores": scores})
            elif self.db_type == "mysql" and self.rule_type == "OBJ":
                results, scores = self.obj_parse(key, rule_complexity,
                                                 rule_cmd, weight,
                                                 max_score, input_parms)
                job_record[key].update({"records": results, "scores": scores})
        return job_record

    def save_result(self, themis, job_record):
        """
        """
        args = {
            "operator_user": self.create_user,
            "startdate": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "stopdate": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "instance_name": self.username,
            "task_ip": self.task_ip,
            "task_port": self.task_port
        }
        themis.review_result.job_init(**args)
        job_record.update({"task_uuid": themis.review_result.task_id})
        themis.mongo_client.insert_one("results", job_record)
        sql = {"id": themis.review_result.task_id}
        condition = {"$set": {"status": "1"}}
        themis.mongo_client.update_one("job", sql, condition)
