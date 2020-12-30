# @Time : 2020/12/13 15:28
# @Author : Lizhe
# @File config.py
# @software: {PyCharm}

BROKER_URL = "redis://127.0.0.1:6379/1"

CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/2"