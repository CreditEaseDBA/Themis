# -*- coding: utf-8 -*-

from celery import Celery

import settings
from command import Command


celery = Celery("task_other",
    backend=settings.REDIS_BACKEND, broker=settings.REDIS_BROKER)

@celery.task
def analysis(**args):
    command = Command()
    command.run_analysis(**args)
