# -*- coding: utf-8 -*-

from celery import Celery
from celery.schedules import crontab

import settings
from command import Command


celery = Celery("task_capture",
    backend=settings.REDIS_BACKEND, broker=settings.REDIS_BROKER, include=["task_capture"])

def range_host(com, flag_type):
    for key, value in settings.ORACLE_ACCOUNT.items():
        host = key.split(":")[0]
        port = key.split(":")[1]
        sid = value[0]
        username = value[1]
        password = value[2]
        date = com.get_last_date()
        com.run_capture(host,
            port, sid, username, password, date, flag_type)
        
celery.conf.update(
    CELERY_ROUTES = {
        "task_capture.capture_obj": {"queue": "sqlreview_obj"},
        "task_capture.capture_other": {"queue": "sqlreview_other"}
        # "sql.c_sql_stru.capture_sql": {"queue": "sqlreview_sql"}
    },
    CELERY_TIMEZONE = 'Asia/Shanghai',
    CELERYBEAT_SCHEDULE = {
        "sql_capture_obj": {
            "task": "task_capture.capture_obj",
            # 每个月的2号，16号的22点执行任务
            # "schedule": crontab(minute=0, hour='22', day_of_month='2,16'),
            # 每天的晚上11点开始执行任务
            "schedule": crontab(minute=settings.CAPTURE_OBJ_MINUTE, hour=settings.CAPTURE_OBJ_HOUR),
            # 每隔10秒钟执行任务
            # "schedule": timedelta(seconds=10),
            "options": {"queue": "sqlreview_obj"}
        },
        "sql_capture_other": {
             "task": "task_capture.capture_other",
            # 每个月的2号，16号的22点执行任务
            # "schedule": crontab(minute=0, hour='22', day_of_month='2,16'),
            # 每天的晚上17点开始执行任务
            "schedule": crontab(minute=settings.CAPTURE_OTHER_MINUTE, hour=settings.CAPTURE_OTHER_HOUR),
            # 每隔10秒钟执行任务
            # "schedule": timedelta(seconds=10),
            "options": {"queue": "sqlreview_other"}
        }
    }
)

@celery.task
def capture_obj():
    com = Command()
    range_host(com, "OBJ")

@celery.task
def capture_other():
    com = Command()
    range_host(com, "OTHER")