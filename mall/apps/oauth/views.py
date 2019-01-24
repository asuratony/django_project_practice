from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from mall import settings
from oauth.models import OAuthQQUser
from oauth.serializers import OauthQQUserSerializer
from oauth.utils import generic_open_id

"""
1.  明确需求 (要知道我们要干什么)
2.  梳理思路
3. 确定请求方式和路由
4. 确定视图
5. 按照步骤进行开发
"""

"""
按照 qq的接口文档(API) 拼接一个url 返回给前端

GET     /oauth/qq/status/


"""
class OAuthQQURLAPIView(APIView):

    def get(self,request):

        # auth_url = 'https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=101474184&redirect_uri=http://www.meiduo.site:8080/oauth_callback.html&state=test'

        #????
        state='/'

        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=state)

        auth_url = oauth.get_qq_url()

        return Response({'auth_url':auth_url})



"""

1. 当用户同意登陆的时候 ,会返回code
2. 用code换取 token
3. 用token换取openid

"""

"""
当用户同意登陆的时候,会生成code,前端需要将获取的code提交给后端

GET    /oauth/qq/users/?code=xxxxx
"""
from rest_framework import status
class OauthQQUserAPIView(APIView):


    def get(self,request):
        #1.接收code
        code = request.query_params.get('code')
        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        #2. 用code换取 token

        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        access_token = oauth.get_access_token(code)
        # 'CFECC11168271B9A488EE931EC3551A4'
        #3. 用token换取openid
        # openid: 3A081305456FE349539EF844752FE8F7

        openid = oauth.get_open_id(access_token)


        #openid是此网站上唯一对应用户身份的标识，
        # 网站可将此ID进行存储便于用户下次登录时辨识其身份

        # 我们获取到openid之后,要根据这个openid去数据库中进行查询
        # 如果数据库中有此信息,说明用户绑定过,应该让用户登陆
        # 如果数据库中没有此信息,说明用户没有绑定过,应该让用户绑定
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            #说明用户没有绑定过

            # 1. openid 比较敏感我们需要对openid进行处理
            # 2. 想对绑定设置一个时效

            token = generic_open_id(openid)


            return Response({'access_token':token})

        else:
            # 说明用户绑定过
            #绑定过就应该登陆

            from rest_framework_jwt.settings import api_settings

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(qquser.user)
            token = jwt_encode_handler(payload)

            return Response({
                'token':token,
                'username':qquser.user.username,
                'user_id':qquser.user.id
            })

            pass
        # finally:

    """
    当用户绑定的时候,需要让前端传递  手机号,密码,短信验证码和 加密的openid

    # 1.接收数据
    # 2.验证数据
    #     1.openid
    #     2.短信验证码
    #     3.根据手机号进行判断,判断手机号是否注册过
    # 3.数据入库
    # 4.返回相应

    POST

    """
    def post(self,request):
        # 1.接收数据
        data = request.data
        # 2.验证数据
        serializer = OauthQQUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3.数据入库
        qquser = serializer.save()
        # 4.返回相应

        from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(qquser.user)
        token = jwt_encode_handler(payload)

        return Response({
            'token': token,
            'username': qquser.user.username,
            'user_id': qquser.user.id
        })







# from itsdangerous import JSONWebSignatureSerializer  -- 这个是不对的

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from mall import settings
#1. 创建序列化器实例
#secret_key         秘钥
#  expires_in=None  过期时间 单位是: 秒数
s = Serializer(secret_key=settings.SECRET_KEY,expires_in=60*60)

#2. 组织数据
data = {
    'openid':'1234567890'
}

#3.对数据进行处理
token = s.dumps(data)

#eyJpYXQiOjE1NDcxMTIyNTIsImFsZyI6IkhTMjU2IiwiZXhwIjoxNTQ3MTE1ODUyfQ.
# eyJvcGVuaWQiOiIxMjM0NTY3ODkwIn0.
# _v-vRCPopYDahqt81MdftYfmswxOBU0gGwL7xXGDHaQ

# 4. 对数据进行解密
s.loads(token)






s = Serializer(secret_key=settings.SECRET_KEY,expires_in=1)

#2. 组织数据
data = {
    'openid':'1234567890'
}

#3.对数据进行处理
token = s.dumps(data)





