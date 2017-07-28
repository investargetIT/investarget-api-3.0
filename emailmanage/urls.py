#coding=utf-8
from django.conf.urls import url
import views

sendemaillist = views.EmailgroupsendlistView.as_view({
        'get': 'list',

})
sendread = views.EmailgroupsendlistView.as_view({
        'post': 'update',
})
urlpatterns = [
    url(r'^$', sendemaillist,name='sendemail-list',),
    url(r'^(?P<pk>\d+)/$', sendread,name='sendemailread',),
]