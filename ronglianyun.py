# @Time : 2020/12/8 15:20
# @Author : Lizhe
# @File ronglianyun.py
# @software: {PyCharm}
from ronglian_sms_sdk import SmsSDK

accId = '8aaf0708762cb1cf017641123808071f'
accToken = '6d508397a3014378ab979eba9462d490'
appId = '8aaf0708762cb1cf01764112397c0725'


def send_message():
    sdk = SmsSDK(accId, accToken, appId)
    tid = '1'
    mobile = '18222287109, 15870879568'

    # datas  验证码   过期时间单位分钟
    datas = ('1234', '5')
    resp = sdk.sendMessage(tid, mobile, datas)
    print(resp)

send_message()