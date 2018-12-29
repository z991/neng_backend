from rest_framework.exceptions import APIException


class PushError(Exception):
    # 自定义一个异常类
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value