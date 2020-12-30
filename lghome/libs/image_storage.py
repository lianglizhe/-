# flake8: noqa

from qiniu import Auth, put_file, etag, put_data

#需要填写你的 Access Key 和 Secret Key
access_key = '1_CHGVzi_NBBHDxnalGvDhH8LulkAmox_QYGga6i'
secret_key = '6213S97ljQdmjsCZ-RDxl34LEuxsl6B6ZAOaFyiX'

def storage(file_data):
    #构建鉴权对象
    q = Auth(access_key, secret_key)
    #要上传的空间
    bucket_name = 'lizhe-home-image'
    #上传后保存的文件名
    #key = 'my-python-logo.png'
    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)
    #要上传文件的本地路径
    localfile = './1.jpg'
    ret, info = put_data(token, None, file_data)

    if info.status ==200:
        return ret.get("key")
    else:
        raise Exception("上传图片失败")

