
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from mall import settings
from itsdangerous import BadSignature,SignatureExpired
from rest_framework import request


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





#  sina  itdangerous 的加密与解密

def generic_access_token(access_token):

    # 1. 创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)

    # 2.组织数据
    data = {
        'access_token': access_token
    }

    # 3.对数据进行处理
    token = s.dumps(data)

    return token.decode()


def check_access(token):

    #1. 创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)

    #2. 进行loads操作
    # 需要捕获异常(数据被篡改, 过期)
    try:
        data = s.loads(token)
    except BadSignature:
        return None

    return data.get('access_token')




from django.conf import settings
from urllib.parse import urlencode, parse_qs
import json
import requests


class OAuthSina(object):
    """
    sina认证辅助工具类
    """

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state = state   # 用于保存登录成功后的跳转页面路径

    def get_sina_url(self):
        # 微博登录url参数组建
        data_dict = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state
        }

        # 构建url
        sina_url = 'https://api.weibo.com/oauth2/authorize?' + urlencode(data_dict)

        return sina_url


    # 获取access_token值
    def get_access_token(self, code):
        # 构建参数数据
        data_dict = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }

        # 构建url
        access_url = 'https://api.weibo.com/oauth2/access_token'

        # 发送请求
        try:
            response = requests.post(access_url,data_dict)

            # 提取数据  返回json
            #  "access_token": "ACCESS_TOKEN",
            #        "expires_in": 1234,
            #        "remind_in":"798114",
            #        "uid":"12341234"
            data = response.text
            # data = request.data

        except:
            raise Exception('微博请求失败')

# TODO:  token 转化字典可能出现问题

        # 转化为字典
        try:
            data_dict = json.loads(data)
            # 获取access_token
            access_token = data_dict.get('access_token')
        except:
            raise Exception('access_token获取失败')


        return access_token



