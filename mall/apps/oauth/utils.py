
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from mall import settings
from itsdangerous import BadSignature,SignatureExpired

def generic_open_id(openid):

    # 1. 创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)

    # 2.组织数据
    data = {
        'openid': openid
    }

    # 3.对数据进行处理
    token = s.dumps(data)

    return token.decode()


def check_access_token(token):

    #1. 创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)

    #2. 进行loads操作
    # 需要捕获异常(数据被篡改, 过期)
    try:
        data = s.loads(token)
    except BadSignature:
        return None

    return data.get('openid')






