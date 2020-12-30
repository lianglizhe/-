# @Time : 2020/12/6 16:15
# . 代表的是同一级目录

from flask import Blueprint

#蓝图
api = Blueprint('api_1_0', __name__, url_prefix='/api/v1.0')  #/api/v1.定义的是url前缀

#注册进来 , profile, houses, orders, pay
from . import demo, verify_code ,passport
