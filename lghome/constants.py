# @Time : 2020/12/8 13:31
# @Author : Lizhe
# @File constants.py


#图片验证码的有效期  单位s   设置过期时间
IMAGE_CODE_REDISE_EXPIRE = 180

#短信验证码的redis有效期  秒

SMS_CODE_REDIS_EXPIRES = 300


#短信验证码的过期时间  单位 秒
SEND_SMS_CODE_EXPIRES = 60

#登录次数的最大值是5
LOGIN_ERROR_MAIN_TIEMS = 5

#登录次数验证时间间隔  设置600秒
LOGIN_ERROR_FORBID_TIME = 600

#七牛云url   域名
QINIU_URL_DOMAIN = 'http://qkgi1wsiz.hd-bkt.clouddn.com/'

#地区有效期过期时间
AREA_INFO_REDIS_CACHE_EXPIRES = 10000

#首页展示的房屋数量
HOME_PAGE_MAX_NUMS = 5

#房屋轮播图过期时间
HOME_PAGE_DATA_REDIS_EXPIRES = 10000


#详情房屋信息过期时间
HOUSE_DETAIL_REDIS_EXPIRES = 10000

#每页显示的数据量
HOUSE_LIST_PAGE_NUMS = 2

#搜索页面的缓存时间
HOUSE_LIST_PAGE_REDIS_CACHE_EXPIRES = 7200

