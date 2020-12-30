# @Time : 2020/12/13 14:43
# @Author : Lizhe
# @File task_sms.py
# @software: {PyCharm}
from celery import Celery
from lghome.libs.ronglianyun.ccp_sms import CCP
#创建celery对象

celery_app = Celery("home", broker="redis://127.0.0.1:6379/1")   #1代表的是1号数据库  redis默认有16个数据库
@celery_app.task
def send_sms(mobile, datas, tid):
    """发送短信的异步任务"""
    cpp = CCP()
    cpp.send_message(mobile, datas ,tid)
