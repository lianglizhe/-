# @Time : 2020/12/13 15:24
# @Author : Lizhe
# @File main.py
# @software: {PyCharm}

from celery import Celery
celery_app = Celery("home")

#加载配置文件
celery_app.config_from_object("lghome.tasks.config")

#注册任务
celery_app.autodiscover_tasks(["lghome.task.sms"])


#cmd中celery启动
#celery -A lghome.tasks.main worker -l info -P eventlet