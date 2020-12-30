from ronglian_sms_sdk import SmsSDK
import json

accId = '8aaf0708762cb1cf017641123808071f'
accToken = '6d508397a3014378ab979eba9462d490'
appId = '8aaf0708762cb1cf01764112397c0725'

#单例的设计模式
class CCP(object):
    """
    发送短信的单例类
    """
    #_instance = None
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls , *args, **kwargs)
            cls._instance.sdk = SmsSDK(accId, accToken, appId)

        return cls._instance

    def send_message(self, mobile, datas, tid='1'):
        sdk = self._instance.sdk
        #sdk = self.sdk
        #tid = '1'

        # mobile = '18222287109, 15870879568'
        # # datas  验证码   过期时间单位分钟
        # datas = ('1234', '5')
        resp = sdk.sendMessage(tid, mobile, datas)
        result = json.loads(resp)
        #print(resp)
        if result['statusCode'] == '000000':
            return 0
        else:
             return -1


if __name__ == '__main__':

    c = CCP()
    c.send_message('18222287109', ('1234','6'),1)
