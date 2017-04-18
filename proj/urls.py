from django.conf.urls import url, include
# from rest_framework import routers

import views
proj_list = views.ProjectView.as_view({
        'get': 'list',
        'post': 'create'
})

proj_detail = views.ProjectView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
})

org_remark = views.ProjectView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
})



urlpatterns = [

        url(r'^$', proj_list , name='proj_list'),
        url(r'^(?P<pk>\d+)/$', proj_detail, name='proj_detail'),
        # url(r'^favorite/$' , views.allfavorite),
        # url(r'^favorite/(?P<pk>\d+)/$' , views.favoritetype),


]