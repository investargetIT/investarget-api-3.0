#coding=utf-8
from django.conf.urls import url
import views

timelines = views.TimelineView.as_view({
        'get': 'list',
        'post': 'create',
        'delete': 'destroy',
})
timeline_detail = views.TimelineView.as_view({
        'get':'retrieve',
        'put': 'update',
})

timelineremark = views.TimeLineRemarkView.as_view({
        'get': 'list',
        'post': 'create',
})


timelineremark_detail = views.TimeLineRemarkView.as_view({
        'get':'retrieve',
        'put': 'update',
        'delete': 'destroy',
})




urlpatterns = [
    url(r'^$', timelines,name='timeline-list',),
    url(r'^(?P<pk>\d+)/$', timeline_detail,name='timeline-detail'),
    url(r'^remark/$', timelineremark, name='timelineremark-list'),
    url(r'^remark/(?P<pk>\d+)/$', timelineremark_detail, name='timelineremark-detail'),

]