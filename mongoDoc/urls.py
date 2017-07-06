#coding=utf-8
from django.conf.urls import url
import views


WXContentList = views.WXView.as_view({
        'get': 'list',
        'post': 'create',
        # 'put': 'update',
        # 'delete': 'destroy',
})
urlpatterns = [
    url(r'^$', WXContentList,name='WXContent-list',),
    url(r'^test$', views.getBaiDuNLP_Accesstoken,name='WXContent-list',),
]