# -*- coding: utf-8 -*-

#
# Copyright 2017
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import sys
import json
import time
import datetime
from optparse import OptionParser
from celery import Celery

import settings
from rule_analysis.themis import Themis
from rule_analysis.db.db_operat import DbOperat
from rule_analysis.db.mongo_operat import MongoOperat
from capture.sql_obj_info import CaptureObj
# from capture.sql_other_info import CaptureOther
from task_export.export import export_task
from webui.main import run_server


class Command(object):
    """
    一个简单的命令类，用来统一执行抓取模块，分析模块，导出模块，web管理模块
    """

    def __init__(self):
        self.mongo_client = MongoOperat(settings.MONGO_SERVER,
                                        settings.MONGO_PORT,
                                        settings.MONGO_DB,
                                        settings.MONGO_USER,
                                        settings.MONGO_PASSWORD)
        self.func = {
            "capture_obj": self.run_capture,
            "capture_other": self.run_capture,
            "analysis_o_obj": self.run_analysis,
            "analysis_o_plan": self.run_analysis,
            "analysis_o_stat": self.run_analysis,
            "analysis_o_text": self.run_analysis,
            "analysis_m_obj": self.run_analysis,
            "analysis_m_plan": self.run_analysis,
            "analysis_m_stat": self.run_analysis,
            "analysis_m_text": self.run_analysis,
            "web": self.run_web,
            "export": self.run_export
        }

    def parse_init(self):
        self.parser = OptionParser()
        self.parser.add_option(
            "-m", "--module", dest="module",
            help=u"指定模块类型，分为抓取模块，分析模块，web端，导出模块")
        self.parser.add_option(
            "-c", "--config", dest="config",
            help=u"指定配置文件")

    def celery_init(self):
        backend = settings.REDIS_BACKEND
        broker = settings.REDIS_BROKER
        celery = Celery("task_other", backend=backend, broker=broker)
        celery.conf.update(settings.CELERY_CONF)
        return celery

    def get_last_date(self):
        last_date = datetime.datetime.now() - datetime.timedelta(days=1)
        return last_date.strftime("%Y-%m-%d")

    def parse_args(self):
        options, _ = self.parser.parse_args()
        if options.module in self.func.keys():
            if options.config:
                args = json.load(open(options.config))
                if "capture" in options.module:
                    db_host = args.get("db_server")
                    db_port = args.get("db_port")
                    key = ":".join([db_host, str(db_port)])
                    username = settings.ORACLE_ACCOUNT[key][1]
                    password = settings.ORACLE_ACCOUNT[key][2]
                    sid = settings.ORACLE_ACCOUNT[key][0]
                    capture_date = args.get("capture_date")
                    flag_type = args.get("type")
                    self.func[options.module](db_host, db_port, sid, username,
                                              password, capture_date,
                                              flag_type)
                elif "export" in options.module or "analysis" in options.module:
                    self.func[options.module](**args)
                else:
                    self.func[options.module]()
            else:
                self.parser.print_help()
                sys.exit(0)
        else:
            self.parser.print_help()
            sys.exit(0)

    def run_capture(self, host, port, sid, username,
                    password, capture_date, flag_type):
        """
        运行数据抓取模块，主要针对oracle，mysql依赖于pt-query-digest
        """
        db_client = DbOperat(host=host, port=port,
                             username=username, password=password, db=sid)
        if flag_type == "OBJ":
            CaptureObj(self.mongo_client, db_client.get_db_cursor(),
                       capture_date, host, sid=sid).run()
        elif flag_type == "OTHER":
            startdate = " ".join([capture_date, "00:00:00"])
            stopdate = " ".join([capture_date, "23:59:00"])
            from capture.sql_other_info import CaptureOther
            CaptureOther(self.mongo_client, db_client.get_db_cursor(),
                         ipaddress=host, sid=sid, etl_date=capture_date,
                         startdate=startdate, stopdate=stopdate).run()

    def run_analysis(self, **args):
        """
        规则解析模块，支持两种数据库，四种规则类型，主要是对Themis类的封装
        """
        kwargs = {
            "mongo_server": settings.MONGO_SERVER,
            "mongo_port": settings.MONGO_PORT,
            "mongo_db": settings.MONGO_DB,
            "mongo_user": settings.MONGO_USER,
            "mongo_password": settings.MONGO_PASSWORD
        }
        username = args.get("username")
        rule_type = args.get("rule_type")
        rule_status = args.get("rule_status", "ON")
        db_type = args.get("db_type")
        create_user = args.get("create_user")
        if rule_type == "OBJ":
            db_server = args.get("db_server")
            db_port = args.get("db_port")
            db_key = ":".join([db_server, str(db_port)])
            new_dict = dict(settings.ORACLE_ACCOUNT.items() +\
                settings.MYSQL_ACCOUNT.items())
            db_key = ":".join([db_server, str(db_port)])
            kwargs.update({
                "db_server": args.get("db_server"),
                "db_port": args.get("db_port"),
                "db_user": new_dict[db_key][1],
                "db_passwd": new_dict[db_key][2],
                "db": new_dict[db_key][0]
            })
            instance_name = kwargs.get("db")
            themis = Themis(username, rule_type, rule_status, db_type,
                            create_user=create_user, **kwargs)
            job_record = themis.run()
        elif db_type == "O" and rule_type in ["SQLPLAN", "SQLSTAT"]:
            instance_name = args.get("sid")
            capture_date = args.get("capture_date")
            themis = Themis(username, rule_type, rule_status, db_type,
                            startdate=capture_date, create_user=create_user,
                            **kwargs)
            job_record = themis.run()
        elif rule_type == "TEXT":
            startdate = args.get("startdate")
            stopdate = args.get("stopdate")
            if db_type == "O":
                instance_name = args.get("sid")
                hostname = args.get("hostname")
            elif db_type == "mysql":
                instance_name = "mysql"
                hostname = args.get("hostname_max")
                temp = {
                    "db_server": settings.PT_QUERY_SERVER,
                    "db_port": settings.PT_QUERY_PORT,
                    "db_user": settings.PT_QUERY_USER,
                    "db_passwd": settings.PT_QUERY_PASSWD,
                    "db": settings.PT_QUERY_DB
                }
                kwargs.update({"pt_server_args": temp})
            themis = Themis(username, rule_type, rule_status, db_type,
                            startdate=startdate, stopdate=stopdate,
                            create_user=create_user, hostname=hostname,
                            **kwargs)
            job_record = themis.run()
        elif db_type == "mysql" and rule_type in ["SQLPLAN", "SQLSTAT"]:
            instance_name = "mysql"
            startdate = args.get("startdate")
            stopdate = args.get("stopdate")
            temp = {
                "db_server": settings.PT_QUERY_SERVER,
                "db_port": settings.PT_QUERY_PORT,
                "db_user": settings.PT_QUERY_USER,
                "db_passwd": settings.PT_QUERY_PASSWD,
                "db": settings.PT_QUERY_DB
            }
            kwargs.update({"pt_server_args": temp})
            themis = Themis(username, rule_type, rule_status, db_type,
                            startdate=startdate, stopdate=stopdate,
                            create_user=create_user, **kwargs)
            db_server = args.get("db_server")
            db_port = args.get("db_port")
            hostname_max = ":".join([db_server, str(db_port)])
            job_args = {
                "user": settings.MYSQL_ACCOUNT[hostname_max][1],
                "passwd": settings.MYSQL_ACCOUNT[hostname_max][2],
                "hostname": hostname_max
            }
            job_record = themis.run(**job_args)
        task_ip = args.get("task_ip")
        task_port = args.get("task_port")
        self.save_result(themis, job_record, create_user,
                        instance_name, task_ip, task_port)

    def run_web(self):
        """
        web管理模块
        """
        celery = self.celery_init()
        config = {
            "mongo_client": self.mongo_client,
            "celery": celery,
            "mysql_account": settings.MYSQL_ACCOUNT,
            "oracle_account": settings.ORACLE_ACCOUNT,
        }
        run_server(config=config, port=settings.SERVER_PORT)

    def run_export(self, **args):
        """
        任务导出功能，需提供任务id
        """
        task_uuid = args.get("task_uuid")
        file_id = args.get("file_id")
        export_task(self.mongo_client, task_uuid, file_id)

    def save_result(self, themis, job_record, create_user, instance_name,
                    task_ip, task_port):
        """
        保存任务和结果功能
        """
        args = {
            "operator_user": create_user,
            "startdate": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "stopdate": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "instance_name": instance_name,
            "task_ip": task_ip,
            "task_port": task_port
        }
        themis.review_result.job_init(**args)
        job_record.update({"task_uuid": themis.review_result.task_id})
        themis.mongo_client.insert_one("results", job_record)
        sql = {"id": themis.review_result.task_id}
        condition = {"$set": {"status": "1"}}
        themis.mongo_client.update_one("job", sql, condition)

    def run(self):
        self.parse_init()
        self.parse_args()


if __name__ == "__main__":
    com = Command()
    com.run()
