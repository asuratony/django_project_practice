from django.conf.urls import url
from . import views

urlpatterns = [

    #/goods/categories/(?P<category_id>\d+)/hotskus/
    url(r'^categories/(?P<category_id>\d+)/hotskus/$',views.HotSKUListAPIView.as_view(),name='hot'),

    url(r'^categories/(?P<category_id>\d+)/skus/$',views.SKUListAPIView.as_view(),name='hot'),
    url(r'^skus/(?P<sku_id>\d+)/comments/$', views.SKUCommentsAPIView.as_view(), name='comments')

]


from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('search', views.SKUSearchViewSet, base_name='skus_search')

urlpatterns += router.urls