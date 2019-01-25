
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadSignature

from mall import settings


def generic_verify_url(user_id):

    #1. 创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)
    #2. 组织数据
    data = {
        'id':user_id
    }

    #3. 对数据进行处理
    token = s.dumps(data)

    return 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token.decode()


def check_token(token):


    #1.  创建序列化器

    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
    #2. 对数据进行解密
    try:
        data = s.loads(token)
    except BadSignature:
        return None
    #3. 获取数据
    return data.get('id')

def encode_token(user_id):

    #1. 创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)
    #2. 组织数据
    data = {
        'id':user_id
    }

    #3. 对数据进行处理
    token = s.dumps(data)

    return token.decode()

