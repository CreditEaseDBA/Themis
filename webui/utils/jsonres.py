# -*-coding:utf-8-*-

from webui.utils.raiseerr import APIError


def temRes(func):
    def _jsonRes(parameter):
        try:
            response = func(parameter)
            if not isinstance(response, dict):
                raise APIError(u"类型错误", 10000)
            if 'message' not in response:
                response.update({'message': ''})
            if 'errcode' not in response:
                response.update({'errcode': 0})
        except APIError as e:
            response = {'message': e.message, 'errcode': e.errcode}
        parameter.write(response)
        return
    return _jsonRes
