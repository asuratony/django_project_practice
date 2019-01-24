from django.conf.urls import url
from .views import AreaModelViewSet
urlpatterns = [

]

# areas/infos/
from rest_framework.routers import DefaultRouter

#1. 创建router实例
router = DefaultRouter()
#2. 注册路由
router.register(r'infos',AreaModelViewSet,base_name='area')
#3.添加到urlpatterns
urlpatterns += router.urls
