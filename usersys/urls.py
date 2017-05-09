#coding=utf-8
from django.conf.urls import url
import views


user_list = views.UserView.as_view({
        'get': 'list',
        'post': 'adduser',   #（系统内新增用户）
        'put': 'update',     #修改（批量）
        'delete': 'destroy', #删除（批量）
})

regist_user = views.UserView.as_view({
        'post':'create',   #注册
})

user_detail = views.UserView.as_view({
        'get': 'retrieve',   #查看详情
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


user_relationshiplist = views.UserRelationView.as_view({
        'get': 'list',
        'post': 'create',
        'put': 'update',         #（批量）
        'delete': 'destroy',     #（批量）
})
detail_relationone = views.UserRelationView.as_view({
        'get': 'retrieve',
})


user_friendship = views.UserFriendshipView.as_view({
        'get': 'list',
        'post': 'create',
})

user_friendship_detail = views.UserFriendshipView.as_view({
        'put': 'update',
        'delete': 'destroy',
})



urlpatterns = [
    url(r'^$', user_list,name='user-list',),
    url(r'^(?P<pk>\d+)/$', user_detail,name='user-one'),
    url(r'^detail/(?P<pk>\d+)/$', user_detailinfo,name='user-detailinfo'),
    url(r'^password/$', find_password ,name='find-password'),
    url(r'^password/(?P<pk>\d+)/$', change_password ,name='change-password'),
    url(r'^relationship/$', user_relationshiplist, name='user-relationshiplist'),
    url(r'^relationship/(?P<pk>\d+)/$', detail_relationone, name='user-relationshipone'),
    url(r'^register/$', regist_user),
    url(r'^login/$', views.login),
    url(r'^friend/$', user_friendship, name='user-friendship'),
    url(r'^friend/(?P<pk>\d+)/$', user_friendship_detail, name='user-friendship-detail'),
    url(r'^test$',views.testsendmsg)
]