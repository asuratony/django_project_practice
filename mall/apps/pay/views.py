from alipay import AliPay
from django.shortcuts import render
from django_redis import get_redis_connection

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import OrderInfo
from pay.models import Payment

"""
1. 第一步：创建应用  (首先用沙箱环境)
2.  第二步：配置密钥 (有2对秘钥,一对是我们自己服务器的,另外一对是 支付宝)
    2.1一对是我们自己服务器的
        我们需要将我们自己生成的私钥 放在自己服务器上
        我们需要将我们自己生成的公钥 放在支付宝服务器上
    2.2另外一对是 支付宝
        支付宝的私钥 在支付宝服务器上
        支付宝的公钥 我们需要 复制过来 (需要放在 有公钥分割线的文件中)
3. 第三步：搭建和配置开发环境  (下载安装 SDK 支付宝已经写好的库)
4. 第四步：接口调用  (开发)

买家账号axirmj7487@sandbox.com
登录密码111111

"""

"""

当用户点击支付按钮的时候,需要让前端将订单id返回给后端

# 1. 后端接收参数
# 2. 查询订单
# 3. 创建支付宝实例对象
# 4. 生成order_string
# 5. 拼接url
# 6. 返回

GET   /pay/orders/(?P<order_id>\d+)/
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from mall import settings

class PaymentAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request,order_id):
        # 1. 后端接收参数
        # 2. 查询订单
        try:
            # 为了查询的更准确 我们再添加2个条件
            # user
            # 状态
            order = OrderInfo.objects.get(order_id=order_id,
                                          user = request.user,
                                          status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 3. 创建支付宝实例对象
        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()



        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug = settings.ALIPAY_DEBUG  # 默认False
        )
        # 4. 生成order_string
        # 如果你是 Python 3的用户，使用默认的字符串即可
        subject = "测试订单"

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount), #  这里需要给它传递 字符串
            subject=subject,
            return_url="http://www.meiduo.site:8080/pay_success.html",
            # notify_url="https://example.com/notify"  # 可选, 不填则使用默认notify url
        )
        # 5. 拼接url
        alipay_url = settings.ALIPAY_URL  + '?' + order_string
        # 6. 返回
        return Response({'alipay_url':alipay_url})



"""
获取支付宝返回的 参数,根据支付宝的验证接口获取 支付宝的交易id,
从而把支付宝的交易id和商家id保存起来
同时改变订单的状态

PUT  pay/status/?key=value&xxxxx

"""

class PayStatusAPIView(APIView):


    def put(self,request):
        #1. 获取参数
        data = request.query_params.dict()
        # sign 不能参与签名验证
        signature = data.pop("sign")

        #2. 创建alipay
        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()

        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )
        # verify
        #3.校验
        success = alipay.verify(data, signature)
        if success:
            # 保存支付宝订单id和商户id
            # 支付宝订单号:
            trade_no = data.get('trade_no')
            # 商家id
            out_trade_no = data.get('out_trade_no')

            Payment.objects.create(
                order_id=out_trade_no,  #商家
                trade_id=trade_no  #支付宝
            )
            # 修改订单的状态
            OrderInfo.objects.filter(order_id=out_trade_no).update(status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'])

            return Response({'trade_id':trade_no},status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)



