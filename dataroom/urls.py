#coding=utf-8
from django.conf.urls import url
import views

dataroom = views.DataroomView.as_view({
        'get': 'list',
        'post': 'create',
})

dataroom_com = views.DataroomView.as_view({
        'get': 'companylist',
})


dataroom_one =  views.DataroomView.as_view({
        'get':'retrieve',
        'put':'update',
        'delete':'destroy',
})

dataroomfile = views.DataroomdirectoryorfileView.as_view({
        'get': 'list',
        'post': 'create',
        'put':'update',
        'delete':'destroy',
})


user_dataroom = views.User_DataroomfileView.as_view({
        'get': 'list',
        'post': 'create',
})

user_dataroomone =  views.User_DataroomfileView.as_view({
        'get':'retrieve',
        'post':'sendEmailNotifaction',
        'put':'update',
        'delete':'destroy',
})


checkZip = views.DataroomView.as_view({
    'get':'checkZipStatus'
})

downZip = views.DataroomView.as_view({
    'get':'downloadDataroomZip'
})

urlpatterns = [
    url(r'^$', dataroom,name='dataroom-list',),
    url(r'^com/$', dataroom_com, name='dataroom_com-list', ),
    url(r'^(?P<pk>\d+)/$', dataroom_one,name='dataroom-detail'),
    url(r'^file/$', dataroomfile,name='dataroom-fileordirectory'),
    url(r'^user/$', user_dataroom,name='user_dataroom-list',),
    url(r'^user/(?P<pk>\d+)/$', user_dataroomone,name='user_dataroom-detail'),
    url(r'^checkzip/(?P<pk>\d+)/$', checkZip,name='dataroom-checkZip'),
    url(r'^downzip/(?P<pk>\d+)/$', downZip,name='dataroom-downZip'),
]