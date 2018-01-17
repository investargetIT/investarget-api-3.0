#coding=utf-8
from django.conf.urls import url
import views

sendemaillist = views.EmailgroupsendlistView.as_view({
        'get': 'list',
        'post': 'update',
})

urlpatterns = [
    url(r'^$', sendemaillist,name='sendemail-list',),
    # url(r'^test$', views.test, name='list', ),
]