#coding=utf-8
from django.conf.urls import url
import views


user_list = views.UserView.as_view({
        'get': 'list',
        'post': 'adduser'   #新增
})

regist_user = views.UserView.as_view({
        'post':'create',   #注册
})

user_detail = views.UserView.as_view({
        'get': 'retrieve',   #查看详情
        'patch': 'partial_update',  #修改
        'delete': 'destroy'     #删除
})
user_Permissions = views.UserView.as_view({
        'get': 'getUserPermissions',

})

user_transuser = views.UserRelationView.as_view({
        'get': 'list',
        'put': 'update',       #修改用户关系
        'post': 'create',      #增加用户关系
        'delete': 'destroy',
})




urlpatterns = [
    url(r'^$', user_list,name='user-list'),
    url(r'^(?P<pk>\d+)/$', user_detail,name='user-detail'),
    url(r'^login/$', views.login),
    url(r'^transuser/$', user_transuser,name='user-transuser'),

]