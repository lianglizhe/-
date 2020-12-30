# @Time : 2020/12/8 12:49
# @Author : Lizhe
# @File verify_code.py
# @software: {PyCharm}

from . import api
from lghome.utils.captcha.captcha import captcha
from lghome import redis_store
import logging
from flask import jsonify, make_response,request
from lghome import constants
from lghome.response_code import RET
from lghome.models import User
import random
from lghome.libs.ronglianyun.ccp_sms import CCP
from lghome.tasks.sms.tasks import send_sms
"""

goods
/add_goods
/update_goods
/delete_goods
/get_goods

REST风格
goods
请求方式
GET    查询
POST   保存
PUT    修改
DELETE  删除

"""

#uuid 标识验证码
#时间戳  + 随机数也可以
#get  请求127.0.0.1/api/v1.0/image_codes/<image_code_id>
#处理过期时间
@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    获取图形验证码
    :param image_code_id:图片的编号
    :return:验证码 ， 验证码图像
    """
    #验证参数
    #业务逻辑   生成验证码图片
    text, image_data = captcha.generate_captcha()
    #保存图形验证码
    #reids_store.set()
    #redis_store.expire()
    #相当于
    try:
        redis_store.setex("image_code_%s" % image_code_id, constants.IMAGE_CODE_REDISE_EXPIRE, text)
    except Exception as e:
        logging.error(e)
        #返回json字符串
        return jsonify(errno= RET.DBERR, errmsg = "验证码图片保存失败")

    #返回值
    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/jpg'
    return response

@api.route("/sms_codes/<re(r'1[345678]\d{9}'):mobile>")
def get_sms_code(mobile):
    """
    获取短信验证码
    :param mobile:
    :return:
    """
    #获取参数
    #图片验证码
    image_code = request.args.get('image_code')
    #uuid
    image_code_id = request.args.get('image_code_id')
    #校验参数
    if not all([image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    #业务逻辑
    #从redis中取出参数
    try:
        real_image_code = redis_store.get('image_code_%s'% image_code_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno = RET.DBERR, errmsg='redis数据库异常')
    #判断图片验证码是否过期
    if real_image_code is None:
        return jsonify(errno=RET.NODATA, errmsg='图片验证码失效了')


    #删除redis中的图片验证码
    try:
         redis_store.delete('image_code_%s' % image_code_id)
    except Exception as e:
        logging.error(e)


    #与用户填写的图片验证码对比
    real_image_code = real_image_code.decode()
    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg='图片验证码错误了！')

    #判断手机号的操作
    try:
        send_flag = redis_store.get('send_sms_code_%s'% mobile)
    except Exception as e:
        logging.error(e)
    else:
        if send_flag is not None:
            return jsonify(errno =RET.REQERR, errmasg='请求过于频繁')


    #判断手机号存在吗
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        logging.error(e)
    else:
        if user is not None:
            #表示手机号被注册过
            return jsonify(error=RET.DATAEXIST, errmsg="手机号已经存在")
    #生成短信验证码
    sms_code = "%06d"%random.randint(0, 999999)
    # 保存正确的短信验证码到redis
    try:
        #redis管道
        pl = redis_store.pipeline()
        pl.setex("sms_code_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        #保存发给这个手机号的记录
        pl.setex("send_cms_code_%s" % mobile, constants.SEND_SMS_CODE_EXPIRES,1)
        pl.execute()
    except Exception as e:
        logging.error(e)
        return jsonify(errno= RET.DBERR, errmsg='短信验证码验证异常' )

    # #发短信
    # try:
    #     ccp = CCP()
    #     result = ccp.send_message(mobile, (sms_code, int(constants.SMS_CODE_REDIS_EXPIRES/60)) ,1)
    # except Exception as e:
    #     logging.error(e)
    #     return  jsonify(errno=RET.THIRDERR, errmsg='发送异常')

    #from lghome.tasks.task_sms import send_sms
    #from lghome.tasks.sms.tasks import send_sms
    send_sms.delay(mobile, (sms_code, int(constants.IMAGE_CODE_REDISE_EXPIRE/60)),1)
    return jsonify(errno=RET.OK, errmsg='发送成功')

    # if result == 0:
    #     return jsonify(errno = RET.OK, errmsg='发送成功')
    # else:
    #     return jsonify(errno=RET.THIRDERR, errmsg='发送失败')

    #返回值






