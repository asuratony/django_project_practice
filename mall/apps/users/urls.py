from django.conf.urls import url
from . import views

from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    #/users/usernames/(?P<username>\w{5,20})/count/
    url(r'^usernames/(?P<username>\w{5,20})/count/$',views.RegisterUsernameAPIView.as_view(),name='usernamecount'),
    url(r'^$', views.RegisterUserAPIView.as_view()),
    url(r'^(?P<user_id>\d+)/password/$',views.Changepassword.as_view()),
    url(r'^(?P<username>\w{5,20})/sms/token/$',views.FindPassAPIView.as_view()),
    url(r'^sms_codes/$',views.SmsAPIView.as_view()),
    url(r'^accounts/(?P<username>\w{5,20})/password/token/$',views.FindPassSmsAPIView.as_view()),
    url(r'^(?P<user_id>\d+)/resetpassword/$',views.ResetPasswordAPIView.as_view()),


    # 添加JWT认证
    # url(r'^auths/',obtain_jwt_token),
    url(r'^auths/',views.MergeLoginView.as_view()),
    # JWT是先使用的django自带的认证方式进行认证,如果认证成功 才生成token


    url(r'^infos/$',views.UserCenterInfoAPIView.as_view()),

    url(r'^emails/$',views.UserEmailAPIView.as_view()),

    url(r'^emails/verification/$',views.UserEmailActiveAPIView.as_view()),


    # url(r'^addresses/$',views.AddressAPIView.as_view()),

    url(r'^browerhistories/$',views.UserHistoryAPIView.as_view()),
]

from .views import AddressViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'addresses',AddressViewSet,base_name='address')
urlpatterns += router.urls


"""
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJ1c2VyX2lkIjo2LCJlbWFpbCI6IiIsImV4cCI6MTU0NzAyMzY0OCwidXNlcm5hbWUiOiJpdGhlaW1hIn0.
sk-HC8McV9CZWdoUsKb1zPNYtH7YToo-SDXxzxxQMEY
"""
