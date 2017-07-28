#coding=utf-8
from django.conf.urls import url
import views


WXContentList = views.WXView.as_view({
        'get': 'list',
        'post': 'create',
        # 'put': 'update',
        # 'delete': 'destroy',
})

EmailGroupList = views.GroupEmailDataView.as_view({
        'get': 'list',
        # 'post': 'create',
})

urlpatterns = [
    url(r'^$', WXContentList,name='WXContent-list',),
    url(r'^email$', EmailGroupList,name='WXContent-list',),
]