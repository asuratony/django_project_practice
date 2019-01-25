import random

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection

from libs.yuntongxun.sms import CCP
from verifications.serializers import RegisterSmscodeSerializer

"""
1.  明确需求 (要知道我们要干什么)
2.  梳理思路
3. 确定请求方式和路由
4. 确定视图
5. 按照步骤进行开发
"""

"""
生成图片验证码

前端生成一个image_code_id  传递给后端

1.接收image_code_id
2. 生成图片验证码
3. 记录验证码到redis中
4. 返回图片

GET       /verifications/imagecodes/(?P<image_code_id>.+)/

 提取URL的特定部分，如/weather/beijing/2018，可以在服务器端的路由中用正则表达式截取；
查询字符串（query string)，形如key1=value1&key2=value2；


"""

# APIView                       基类
# GeneriAPIView                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
# ListAPIView,RetrieveAPIView   连 get方法都不用写


class RegisterImageCodeAPIView(APIView):

    def get(self,request,image_code_id):

        # 1.接收image_code_id
        # 2. 生成图片验证码
        text,image = captcha.generate_captcha()
        # 3. 记录验证码到redis中
        #3.1连接redis
        redis_conn = get_redis_connection('code')
        #3.2 设置数据
        redis_conn.setex('img_'+image_code_id,60,text)
        # 4. 返回图片
        # return HttpResponse(image)
        return HttpResponse(image,content_type='image/jpeg')
        # return Response()
        # pass




"""
1.  明确需求 (要知道我们要干什么)
2.  梳理思路
3. 确定请求方式和路由
4. 确定视图
5. 按照步骤进行开发
"""


"""
当用户点击 获取短信验证码的时候 ,前端需要将 手机号,图片验证码以及 image_code_id提交给后端

1.接收参数
2.校验参数
3.生成短信
4.记录在redis中
5.发送短信 (阿里云)
6.返回相应


GET          /verifications/smscodes/(?P<mobile>1[345789]\d{9})/?text=xxxx & image_code_id=xxxx

GET         /verifications/mobile/text/image_code_id/
GET         /verifications/?mobile=xxx&text=xxxx&=image_code_id=xxx

 提取URL的特定部分，如/weather/beijing/2018，可以在服务器端的路由中用正则表达式截取；
查询字符串（query string)，形如key1=value1&key2=value2；



敏感的数据用 post
POST


"""

# APIView                       基类
# GeneriAPIView                 对列表视图和详情视图做了通用支持,一般和mixin配合使用

# ListAPIView,RetrieveAPIView   连 get方法都不用写
class RegisterSmscodeAPIView(APIView):

    def get(self,request,mobile):
        # 1.接收参数
        query_params = request.query_params
        # 2.校验参数
        serialzier = RegisterSmscodeSerializer(data=query_params)
        serialzier.is_valid(raise_exception=True)
        # 3.生成短信
        sms_code = '%06d'%random.randint(0,999999)
        # 4.记录在redis中
        redis_conn = get_redis_connection('code')
        redis_conn.setex('sms_'+mobile,5*60,sms_code)
        # 5.发送短信 (阿里云)
        # 0.5

        # CCP().send_template_sms(mobile,[sms_code,5],1)
        from celery_tasks.sms.tasks import send_sms_code
        # delay 方法的参数 和 任务(函数)名一致
        send_sms_code.delay(mobile,sms_code)

        # 6.返回相应
        return Response({'msg':'ok'})

