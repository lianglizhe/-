# @Time : 2020/12/6 21:36
# @Author : Lizhe

# 这个文件是做登录和注册的
from . import api
from flask import request,jsonify,session
from lghome.response_code import RET
import re
from lghome import redis_store
import logging
from lghome.models import User
from lghome import db
from sqlalchemy.exc import IntegrityError
from lghome import constants


#注册
@api.route("/users", methods=["POST"])
def register():
    """
    :param  手机号 短信验证码 密码 确认密码
    :return:  json
    """
    #接收参数
    request_dict= request.get_json()
    mobile = request_dict.get("mobile")
    sms_code = request_dict.get("sms_code")
    password = request_dict.get("password")
    password2 = request_dict.get("password2")

    #验证
    if not all([mobile, sms_code, password, password2]):
        return jsonify(errno= RET.PARAMERR, errmsg="参数不完整")

    #判断手机号格式
    if not re.match(r"1[345678]\d{9}", mobile):
        return jsonify(errno= RET.PARAMERR, errmsg="手机号格式错误")

    if password != password2:
        return jsonify(errno= RET.PARAMERR, errmsg="两次密码不一致")

    #业务逻辑
    #从redis中取短信验证码
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="读取短信验证码异常")

    #判断短信验证码是否过期
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码失效")
    # 删除redis中的短信验证码
    try:
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as e:
        logging.error(e)
    # 验证码的正确性
    real_sms_code = real_sms_code.decode()  #转码一下
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")
    # 手机号是否注册过
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     logging.error(e)
    # else:
    #     if user is not None:
    #         #表示手机号被注册过
    #         return jsonify(error=RET.DATAEXIST, errmsg="手机号已经存在")
    # 保存数据
    user = User(name=mobile, mobile=mobile)
    user.password = password
    #user.generate_pwd_hash(password)
    #User(name=mobile, mobile=mobile, password_hash="加密后的密码")
    try:
        db.session(user)
        db.session.commit()

    except IntegrityError as e:
        db.session.rollback()
        logging.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号已经存在")
    except Exception as e:
        #回滚
        db.session.rollback()
        logging.error(e) #记录异常
        return jsonify(errno=RET.DBERR, errmsg="插入数据库异常")
    #, password_hash=password
    #保存登录状态到session中
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id
    #返回结果
    return jsonify(errno=RET.OK, errmsg="注册成功")

#登录
@api.route("/sessions", methods=["POST"])
def login():
    """
    用户登录
    :param:手机号，密码
    :return: json
    """
    #接收参数
    request_dict = request.get_json()
    mobile = request_dict.get("mobile")
    password = request_dict.get("password")
    # 校验参数
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    #判断手机号格式
    if not re.match(r"1[345678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")
    #业务逻辑处理
    #判断错误次数是否超过限制，如果超过限制直接返回
    #redis 用户IP地址;次数
    user_ip = request.remote_addr
    try:
        #这是byte
        access_nums = redis_store.get("access_nums_%s"%user_ip)
    except Exception as e:
        logging.error(e)
    else:
        if access_nums is not None and int(access_nums) >= constants.LOGIN_ERROR_MAIN_TIEMS:
            return jsonify(errno=RET.REQERR, errmsg="错误次数太多稍后重试")

    #从数据库中查询手机号是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        logging.error(e)
        #查询数据库错误
        return jsonify(errno=RET.DBERR,errmsg="获取用户信息失败")
    #验证密码
    if user is None or not user.check_pwd_hash(password):
        try:
            redis_store.incr("access_nums_%s" % user_ip)
            redis_store.expire("access_nums_%s" % user_ip, constants.LOGIN_ERROR_MAIN_TIEMS)  #设置过期时间
        except Exception as e:
            logging.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="账号密码不匹配")
    #保存登录状态 使用session()
    session["name"] = user.name
    session["mobile"] = user.mobile
    session["id"] = user.id
    #返回
    return jsonify(errno=RET.OK,errmsg="登录成功")


@api.route("/session", methods=["GET"])
def check_login():
    """检查登录状态"""
    name = session.get("name")
    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="flase")

@api.route("/session", methods=["DELETE"])
def logout():
    """退出登录"""
    #清空session
    session.clear()
    return jsonify(errno=RET.OK, errmsg="ok")



