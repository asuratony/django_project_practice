from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.serializers import HotSKUListSerialzier, SKUCommentsListSerialzier
from orders.models import OrderGoods, OrderInfo
from users.models import User

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

from rest_framework.pagination import LimitOffsetPagination,PageNumberPagination
class SKUListAPIView(ListAPIView):

    serializer_class = HotSKUListSerialzier

    # 排序
    filter_backends = [OrderingFilter]
    ordering_fields = ['create_time','price','sales']

    #分页
    # permission_classes = LimitOffsetPagination
    # permission_classes = StandardResultsSetPagination

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category=category_id)


from .serializers import SKUIndexSerializer
from drf_haystack.viewsets import HaystackViewSet


class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer


class SKUCommentsAPIView(APIView):
    def get(self, request, sku_id):
        commented_goods = OrderGoods.objects.filter(sku_id=sku_id).all()
        # serializer = SKUCommentsListSerialzier(commented_goods, many=True)
        data = []
        for commented_good in commented_goods:
            order_info = OrderInfo.objects.get(order_id=commented_good.order_id)
            username = User.objects.get(id=order_info.user_id).username
            comment = {'username': username, 'comment': commented_good.comment, 'score': commented_good.score, 'is_anonymous': commented_good.is_anonymous}
            data.append(comment)

        return Response(data)
