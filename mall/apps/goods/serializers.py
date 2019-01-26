from rest_framework import serializers
from goods.models import SKU
from orders.models import OrderInfo, OrderGoods


class HotSKUListSerialzier(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')


from .search_indexes import SKUIndex
from drf_haystack.serializers import HaystackSerializer


class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """

    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'id', 'name', 'price', 'default_image_url', 'comments')


# 订单商品信息序列化器
class UserSKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        # fields=['default_image_url']
        fields = ['price', 'default_image_url', 'name']


# 订单商品序列化器
class UserGoodsSerializer(serializers.ModelSerializer):
    sku = UserSKUSerializer()

    class Meta:
        model = OrderGoods
        fields = ['sku', 'count']
        # fields = ['sku', 'count', 'price']


# # 个人中心订单列表序列化器
class UserAllOrderSerializer(serializers.ModelSerializer):
    skus = UserGoodsSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = ('skus', 'order_id', 'create_time',
                  'total_count', 'total_amount', 'pay_method', 'status', 'freight')
