from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.serializers import HotSKUListSerialzier, UserAllOrderSerializer
from orders.models import OrderInfo

"""
1. 尽量多的分析表(定义出表)的字段 (不要分析表和表之间的关系)

2.找一个安静的 没有人打扰的 地方  分析表和表之间的关系(只分析2个表之间的关系)


供应商和商品


商品id        商品的名字
1               iphone
2               huawei

供应商id      供应商名字
1               富士康
2               富土康


商品id        供应商id
1               1
2               1
2               2
1               2


"""

"""
静态化技术  (提升用户体验, SEO)

我们是通过先查询数据,将查询的数据渲染到模板中,模板就
生成了一个html, 这个时候我们将html写入到指定的文件

当用户访问的时候,我们让用户访问指定的文件就可以了

"""

"""

1. 列表数据是分为热销数据 和 列表数据的

热销数据

需要让前端将 分类id传递给后端

1.接收数据 category_id
2.根据id获取数据  [SKU,SKU]
3.将对象列表转换为字典(JSON数据)
4. 返回相应

GET     /goods/categories/category_id/hotskus/

"""
# APIView                       基类
# GeneriAPIView                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
# ListAPIView,RetriveAPIView    连 get方法都不用写


from rest_framework.generics import ListAPIView
from goods.models import SKU


class HotSKUListAPIView(ListAPIView):
    pagination_class = None

    serializer_class = HotSKUListSerialzier

    # queryset = SKU.objects.filter(category=category_id).order_by('-sales')[:2]
    # queryset = SKU.objects.all().order_by('-sales')[:2]

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category=category_id).order_by('-sales')[:2]


"""

列表数据 有 数据获取,分页功能和排序功能 我们就从一个工程出发


"""
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView

from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination


class SKUListAPIView(ListAPIView):
    serializer_class = HotSKUListSerialzier

    # 排序
    filter_backends = [OrderingFilter]
    ordering_fields = ['create_time', 'price', 'sales']

    # 分页
    # permission_classes = LimitOffsetPagination
    # permission_classes = StandardResultsSetPagination

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category=category_id)


from .serializers import SKUIndexSerializer
from drf_haystack.viewsets import HaystackViewSet


# SKU搜索
class SKUSearchViewSet(HaystackViewSet):
    index_models = [SKU]
    serializer_class = SKUIndexSerializer


from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer


# 个人中心 全部订单
class UserAllOrderView(ListAPIView):
    # 身份验证
    # permission_classes = [IsAuthenticated]
    # pagination_class = None

    # def get(self, request):
    #     # 获取用户id
    #     user_id = request.user.id
    #     # 从数据库查询所有包括用户id的订单
    #     order_set = OrderInfo.objects.filter(user_id=6)
    #     serializer = UserAllOrderSerializer(instance=order_set, many=True)
    #     # 遍历获取订单数量
    #     count = 0
    #     for i in order_set:
    #         count += 1
    #     return Response(serializer.data)
    serializer_class = UserAllOrderSerializer

    # permission_classes = [IsAuthenticated]
    # pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return OrderInfo.objects.filter(user_id=user.id)