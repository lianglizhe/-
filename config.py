import redis
#配置信息
class Config(object):

    #加密
    SECRET_KEY = 'FHSDJKFVXJCHHSADNFLFSGB'
    #mysql配置
    USERNAME = 'root'
    PASSWORD = 'root'
    HOSTNAME = '127.0.0.1'
    PORT = 3306
    DATEBASE = 'home01'

    #redis 的配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    #flask_session
    SESSION_TYPE = 'redis'
    # 不同的服务器
    SESSION_REDIS = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)  #地址和端口
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 8640  # 单位是秒

    #数据库的配置
    DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATEBASE)
    SQLALCHEMY_DATABASE_URI = DB_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False



class DevConfig(Config):
    """开发环境"""
    DEBUG = True
class ProConfig(Config):
    """
    生产环境
    """
    #print('cccc')

config_map = {
    'dev':DevConfig,
    'pro':ProConfig
}
