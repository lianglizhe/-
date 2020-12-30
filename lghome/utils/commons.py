# @Time : 2020/12/6 23:18
# @Author : Lizhe

from werkzeug.routing import BaseConverter
from flask import session, jsonify, g
from lghome.response_code import RET
import functools

#定义的路由转换器
class ReConverter(BaseConverter):
    def __init__(self, map, regex):
        super().__init__(map)
        #super(ReConverter, self).__init__(map)
        self.regex = regex

#view-func是被装饰的函数   装饰器的定义
def login_required(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        #判断用户的登录状态
        user_id = session.get("uesr_id")
        if user_id is not None:
            #已登录
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    return wrapper