from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from orders.serializers import PlaceOrderSerializer, PlaceSerializer

"""
当用户点击结算的时候 必须要登陆

提交订单的页面必须是登陆用户才可以访问

1.连接redis
2.获取hash    {b'sku_id':b'count'}
    set
3. 选中商品的数据 对数据进行类型转换 {sku_id:count}
4.从redis中获取选中商品的id  [sku_id,sku_id]
5.根据id进行数据的查询   [SKu,SKU,SKU]
6.将列表数据转换位字典数据
7.返回相应

GET     /orders/placeorders/

"""
from rest_framework.permissions import IsAuthenticated
class PlaceOrderAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):
        user = request.user
        # 1.连接redis
        redis_conn = get_redis_connection('cart')
        # 2.获取hash    {b'sku_id':b'count'}
        redis_count_id = redis_conn.hgetall('cart_%s'%user.id)
        #     set
        selected_ids = redis_conn.smembers('cart_selected_%s'%user.id)

        # 3. 选中商品的数据 对数据进行类型转换 {sku_id:count}
        selected_cart = {}
        for sku_id in selected_ids:
            selected_cart[int(sku_id)]=int(redis_count_id[sku_id])

        #{sku_id:count,sku_id:count,sku_id:count}

        # 4.从selected_cart中获取选中商品的id  [sku_id,sku_id]
        ids = selected_cart.keys() # [1,2,3,4]
        # 5.根据id进行数据的查询   [SKu,SKU,SKU]
        skus = SKU.objects.filter(pk__in=ids)

        for sku in skus:
            sku.count = selected_cart[sku.id]
        # 6.将列表数据转换位字典数据
        # serializer = PlaceOrderSerializer(skus,many=True)
        # # 7.返回相应
        # # return Response(serializer.data)
        #
        # data = {
        #     'freight':10,
        #     'skus':serializer.data
        # }
        #
        # return Response(data)


        serializer = PlaceSerializer({
            'freight':10,
            'skus':skus
        })

        return Response(serializer.data)

"""
当用户点击提交订单按钮的时候 ,我们前端必须要提交的数据是:
用户信息, 支付方式,地址信息

1.后端接收数据
2.对数据进行校验
3.数据入库
4.返回相应

POST  /orders/

"""
from rest_framework.generics import CreateAPIView
from .serializers import OrderCommitSerializer

class OrderAPIView(CreateAPIView):

    serializer_class = OrderCommitSerializer


# GET /orders/(?P<order_id>)\d+/uncommentgoods/
from rest_framework.generics import RetrieveAPIView
from .serializers import CommentSkusDataSerializer, SaveCommentSerializer
from .models import OrderGoods


class CommentGoodsDataAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request, order_id):
        order_id = order_id
        order_goods = OrderGoods.objects.filter(order_id=order_id)
        uncommentskus = []
        for order_good in order_goods:
            if order_good.is_commented == 0:
                sku = order_good.sku
                uncommentskus.append(sku)
        serializer = CommentSkusDataSerializer(uncommentskus, many=True)
        return Response(serializer.data)


class SaveCommentAPIView(APIView):
    def post(self, request, order_id):
        req_data = request.data
        instance = OrderGoods.objects.filter(sku_id=req_data['sku'], order_id=req_data['order']).first()
        data = {'comment': req_data['comment'], 'score': req_data['score'], 'is_anonymous': req_data['is_anonymous'], 'is_commented': True}
        serializer = SaveCommentSerializer(instance=instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        sku = SKU.objects.get(id=req_data['sku'])
        sku.comments += 1
        sku.save()
        return Response('OK')
