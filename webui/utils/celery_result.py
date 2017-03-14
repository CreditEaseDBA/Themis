# -*-coding:utf-8-*-

from celery.backends.base import DisabledBackend


def backend_configured(result):
    return not isinstance(result.backend, DisabledBackend)
