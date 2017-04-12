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

user_detailinfo = views.UserView.as_view({
        'get':'getdetailinfo'
})

find_password = views.UserView.as_view({
        'post': 'findpassword',
})

change_password = views.UserView.as_view({
        'get': 'resetpassword',
        'put': 'changepassword'
})


user_relationship = views.UserRelationView.as_view({
        'get': 'list',
        'post': 'create',
})
detail_relation = views.UserRelationView.as_view({
        'put': 'update',
        'delete': 'destroy',
        'get': 'retrieve',
})




urlpatterns = [
    url(r'^$', user_list,name='user-list',),
    url(r'^(?P<pk>\d+)/$', user_detail,name='user-one'),
    url(r'^detail/(?P<pk>\d+)/$', user_detailinfo,name='user-detailinfo'),
    url(r'^password/$', find_password ,name='find-password'),
    url(r'^password/(?P<pk>\d+)/$', change_password ,name='change-password'),
    url(r'^relationship/$', user_relationship, name='user-relationship'),
    url(r'^relationship/(?P<pk>\d+)/$', detail_relation, name='user-relationship'),
    url(r'^register/$', regist_user),
    url(r'^login/$', views.login),
]