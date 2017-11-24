#coding=utf-8
from django.conf.urls import url
import views

dataroom = views.DataroomView.as_view({
        'get': 'list',
        'post': 'create',
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
        'put':'update',
        'delete':'destroy',
})


dataroomadddata = views.DataroomView.as_view({
    'post':'addDataroom'
})
makeZip = views.DataroomView.as_view({
    'get':'makeDataroomAllFilesZip'
})
downZip = views.DataroomView.as_view({
    'get':'downloadDataroomZip'
})

urlpatterns = [
    url(r'^$', dataroom,name='dataroom-list',),
    url(r'^(?P<pk>\d+)/$', dataroom_one,name='dataroom-detail'),
    url(r'^file/$', dataroomfile,name='dataroom-fileordirectory'),
    url(r'^user/$', user_dataroom,name='user_dataroom-list',),
    url(r'^user/(?P<pk>\d+)/$', user_dataroomone,name='user_dataroom-detail'),
    url(r'^add/$', dataroomadddata, name='dataroom-add-dataroom'),
    url(r'^makezip/(?P<pk>\d+)/$', makeZip,name='dataroom-makeZip'),
    url(r'^down/$', downZip,name='dataroom-downZip'),
]