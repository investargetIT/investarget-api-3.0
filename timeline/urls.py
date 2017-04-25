#coding=utf-8
from django.conf.urls import url
import views

timelines = views.TimelineView.as_view({
        'get': 'list',
        # 'post': 'create',
        'put': 'update',
        # 'delete': 'destroy',     #（批量）
})
timeline_detail = views.TimelineView.as_view({

    'put': 'update',
})

# user_timeline = views.TimelineView.as_view({
#         'get': 'usertimelinelist',
#
# })
# proj_timeline = views.TimelineView.as_view({
#         'get': 'projtimelinelist',
#
# })



timelineremark = views.TimeLineRemarkView.as_view({
        'get': 'retrieve',
})




urlpatterns = [
    url(r'^$', timelines,name='timeline-list',),
    url(r'^(?P<pk>\d+)/$', timeline_detail,name='timeline-detail'),
    # url(r'^detail/(?P<pk>\d+)/$', user_detailinfo,name='user-detailinfo'),
    # url(r'^password/$', find_password ,name='find-password'),
    # url(r'^password/(?P<pk>\d+)/$', change_password ,name='change-password'),
    # url(r'^relationship/$', user_relationshiplist, name='user-relationshiplist'),
    # url(r'^relationship/(?P<pk>\d+)/$', detail_relationone, name='user-relationshipone'),
    # url(r'^register/$', regist_user),
    # url(r'^login/$', views.login),
]