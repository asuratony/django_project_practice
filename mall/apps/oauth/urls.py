from django.conf.urls import url
from . import views

urlpatterns =[
    #/oauth/qq/statues/
    url(r'^qq/statues/$',views.OAuthQQURLAPIView.as_view()),
    url(r'^qq/users/$',views.OauthQQUserAPIView.as_view()),
]