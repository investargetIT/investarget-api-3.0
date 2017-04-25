#coding=utf-8
from django.conf.urls import url
import views

# user_relationshiplist = views.UserRelationView.as_view({
#         'get': 'list',
#         'post': 'create',
#         'put': 'update',         #（批量）
#         'delete': 'destroy',     #（批量）
# })
# detail_relationone = views.UserRelationView.as_view({
#         'get': 'retrieve',
# })




urlpatterns = [
    # url(r'^$', user_list,name='user-list',),
    # url(r'^(?P<pk>\d+)/$', user_detail,name='user-one'),
    # url(r'^detail/(?P<pk>\d+)/$', user_detailinfo,name='user-detailinfo'),
    # url(r'^password/$', find_password ,name='find-password'),
    # url(r'^password/(?P<pk>\d+)/$', change_password ,name='change-password'),
    # url(r'^relationship/$', user_relationshiplist, name='user-relationshiplist'),
    # url(r'^relationship/(?P<pk>\d+)/$', detail_relationone, name='user-relationshipone'),
    # url(r'^register/$', regist_user),
    # url(r'^login/$', views.login),
]