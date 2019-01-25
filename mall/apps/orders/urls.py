from django.conf.urls import url
from . import views

urlpatterns = [
    #/orders/places/
    url(r'^places/$',views.PlaceOrderAPIView.as_view(),name='placeorder'),

    url(r'^$',views.OrderAPIView.as_view(),name='order'),
    url(r'^(?P<order_id>\d+)/uncommentgoods/$', views.CommentGoodsDataAPIView.as_view(), name='uncommentgoods'),
    url(r'(?P<order_id>\d+)/comments/', views.SaveCommentAPIView.as_view(),name='savecomments'),
]