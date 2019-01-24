import re

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    #token,             生成的JWT token
    # user=None,        已经验证的用户信息
    # request=None      请求
    return {
        'token': token,
        'username': user.username,
        'user_id':user.id
    }


"""
对代码进行封装和抽取
1. 方便复用
2. 解耦,方便维护

如何进行封装和抽取
1. 重复的功能(第二次出现) 我们就 抽取
2. 实现了一个小功能


抽取的步骤:
1. 定义一个函数(方法)
2. 将要抽取的内容 复制过来(哪里有问题该哪里,没有的变量 定义为参数)
3. 验证
"""
from rest_framework.mixins import CreateModelMixin

def get_user_by_account(username):
    try:
        if re.match(r'1[3-9]\d{9}', username):
            # 手机号
            user = User.objects.get(mobile=username)
        else:
            # 用户名
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None


    return user

from django.contrib.auth.backends import ModelBackend

class UsernameMobileModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        #1. 根据正则来判断 用户的 username 是手机号还是 用户名
        # username =  18310820688
        # User.objects.get(mobile=)

        # username =  itheima
        # User.objects.get(username=)
        # try:
        #     if re.match(r'1[3-9]\d{9}',username):
        #         #手机号
        #         user = User.objects.get(mobile=username)
        #     else:
        #         #用户名
        #         user = User.objects.get(username=username)
        # except User.DoesNotExist:
        #     user = None
        user = get_user_by_account(username)
        #2. 根据user进行校验
        if user is not None and user.check_password(password):
            return user

        return None



# 扩展
class MyBackend(object):

    def authenticate(self, request, username=None, password=None):
        user = get_user_by_account(username)
        # 2. 根据user进行校验
        if user is not None and user.check_password(password):
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None