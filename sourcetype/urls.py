#coding=utf-8
from django.conf.urls import url
import views

tag = views.TagView.as_view({
        'get': 'list',
        'post':'create',
})


tagdetail = views.TagView.as_view({
        'put': 'update',
        'delete': 'destroy'
})



urlpatterns = [
    url(r'^tag/$', tag,name='tagsource',),
    url(r'^tag/(?P<pk>\d+)/$', tagdetail,name='tagdetail',),

]