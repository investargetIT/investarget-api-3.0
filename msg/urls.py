from django.conf.urls import url, include
import views



msg_list = views.WebMessageView.as_view({
        'get': 'list',
})
msg_detail = views.WebMessageView.as_view({
        'post': 'update',
})

schedule_list = views.ScheduleView.as_view({
        'get':'list',
        'post':'create',
})

schedule_detail = views.ScheduleView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy',
})

webexuser_list = views.WebEXUserView.as_view({
        'get':'list',
        'post':'create',
})

webexuser_detail = views.WebEXUserView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy',
})



urlpatterns = [
        url(r'^$', msg_list,name='msg-list'),
        url(r'^(?P<pk>\d+)/$', msg_detail,name='msg-detail'),
        url(r'^schedule/$', schedule_list, name='schedule-list'),
        url(r'^schedule/(?P<pk>\d+)/$', schedule_detail, name='schedule-detail'),
        url(r'^webex/$', webexuser_list, name='webexuser-list'),
        url(r'^webex/(?P<pk>\d+)/$', webexuser_detail, name='webexuser-detail'),

]