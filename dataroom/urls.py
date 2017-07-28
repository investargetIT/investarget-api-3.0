#coding=utf-8
from django.conf.urls import url
import views

dataroom = views.DataroomView.as_view({
        'get': 'list',
        'post': 'create',
        'put':'update',
        'delete':'destroy',
})

dataroom_one = views.DataroomView.as_view({
        'get': 'retrieve',
})

dataroomfile = views.DataroomdirectoryorfileView.as_view({
        'get': 'list',
        'post': 'create',
        'put':'update',
        'delete':'destroy',
})




urlpatterns = [
    url(r'^$', dataroom,name='dataroom-list',),
    url(r'^(?P<pk>\d+)/$', dataroom_one,name='dataroom-detail'),
    url(r'^file/$', dataroomfile,name='dataroom-fileordirectory'),

]