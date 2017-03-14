# -*- coding: utf-8 -*-

from celery import Celery

import settings
from command import Command


celery = Celery("task_exports",
    backend=settings.REDIS_BACKEND, broker=settings.REDIS_BROKER)

@celery.task
def export(**args):
    command = Command()
    command.run_export(**args)
