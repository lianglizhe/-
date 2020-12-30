# @Time : 2020/12/6 16:24



from . import api
from lghome import db, models
import logging

@api.route('/index')
def index():
    logging.warning('数据库连接失败')
    return '测试'

@api.route('/profile')
def profile():
    return '个人中心'
