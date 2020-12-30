# @Time : 2020/12/16 15

from . import api
from lghome.utils.commons import login_required
from flask import g, request, jsonify
from lghome.response_code import RET
import logging
from lghome.models import Order
from lghome import db
from alipay import AliPay
import os

@api.route("/orders/<int:order-id>/payment")
@login_required
def order_pay(order_id):
    """
    发起支付宝支付
    :param order_id:
    :return:
    """
    user_id = g.user_id
    try:
        order = Order.query.filter(Order.id == order_id, Order.status == "WAIT_PAYMENT", Order.user_id == user_id).first()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    if order is None:
        return jsonify(errno=RET.NODATA, errmsg='订单数据有误')

    app_private_key_string = open(os.path.join(os.path.dirname(__file__), "keys/app_private_key.pem")).read()
    alipay_public_key_string = open(os.path.join(os.path.dirname(__file__), "keys/alipay_public_key.pem")).read()

    alipay = AliPay(
        appid="2021000116672265",
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=False,  # 默认False
    )

    # 如果你是Python 2用户（考虑考虑升级到Python 3吧），请确保非ascii的字符串为utf8编码：
    #subject = u"测试订单".encode("utf8")  # 如果你是 Python 3的用户，使用默认的字符串即可
    # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no="20161112",#订单编号
        total_amount=0.01,   #订单金额
        subject="标题，测试订单",     #订单的标题
        return_url="https://127.0.0.1:5000/payCompolete.html",   #返回的订单地址
        notify_url=None      # 可选, 不填则使用默认notify url
    )
    pay_url = "https://openapi.alipaydev.com/gateway.do?" + order_string

    return jsonify(errno=RET.OK ,errmsg="ok", data={"pay_url":pay_url})

@api.route("/order/payment", methods=["PUT"])
def save_order_payment_result():
    """
    保存订单结果
    :return: json
    """
    data = request.form.to_dict()
    # sign 不能参与签名验证
    signature = data.pop("sign")

    app_private_key_string = open(os.path.join(os.path.dirname(__file__), "keys/app_private_key.pem")).read()
    alipay_public_key_string = open(os.path.join(os.path.dirname(__file__), "keys/alipay_public_key.pem")).read()

    alipay = AliPay(
        appid="2016091200492699",
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=False,  # 默认False
    )

    success = alipay.verify(data, signature)
    if success:
        order_id = data.get('out_trade_no')
        trade_no = data.get('trade_no')     # 支付宝的交易号

        try:
            Order.query.filter(Order.id == order_id).update({"status": "WAIT_COMMENT", "trade_no": trade_no})
            db.session.commit()
        except Exception as e:
            logging.error(e)
            db.session.rollback()

    return jsonify(errno=RET.OK, errmsg='OK')