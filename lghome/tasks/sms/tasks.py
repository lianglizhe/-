# @Time : 2020/12/13 15:23
# @Author : Lizhe
# @File tasks.py
# @software: {PyCharm}
from lghome.tasks.main import celery_app
from lghome.libs.ronglianyun.ccp_sms import CCP

@celery_app.task
def send_sms(mobile, datas, tid):
    """发送短信的异步任务"""
    cpp = CCP()
    cpp.send_message(mobile, datas ,tid)