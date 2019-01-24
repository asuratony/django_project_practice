from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView

from areas.models import Area
from areas.serializers import AreaSerializer, SubsAreaSerialzier

"""
获取省份信息
select * from tb_areas where parent_id is null;


获取市的信息
获取区县信息
select * from tb_areas where parent_id=110000;
select * from tb_areas where parent_id=110100;


"""

# class AreaProvienceAPIView(APIView):
#
#     def get(self,request):
#
#         pass
#
#
# class AreaDistrictAPIView(APIView):
#
#     def get(self,request,parent_id):
#         pass

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin
from rest_framework_extensions.cache.mixins import RetrieveCacheResponseMixin
from rest_framework_extensions.cache.mixins import CacheResponseMixin

class AreaModelViewSet(CacheResponseMixin,ReadOnlyModelViewSet):

    pagination_class = None

    #序列化器
    # serializer_class = AreaSerializer

    # queryset = Area.objects.filter(parent=None)  # 省的信息       list
    # queryset = Area.objects.all()                # 市,区县信息     retrieve

    def get_queryset(self):

        # 重写方法的化 我们可以返回不同的数据源
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()


    def get_serializer_class(self):

        if self.action == 'list':
            return AreaSerializer
        else:
            return SubsAreaSerialzier
