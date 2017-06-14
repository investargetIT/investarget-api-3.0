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

proj_finance = views.ProjFinanceView.as_view({
        'get': 'list',
        'post':'create',
        'put': 'update',
        'delete': 'destroy'
})

userfavorite_proj = views.ProjectFavoriteView.as_view({
        'get': 'list',
        'post': 'create',
        'delete':'destroy'
})

getshareprojtoken = views.ProjectView.as_view({
        'get':'getshareprojtoken'
})

getshareproj = views.ProjectView.as_view({
        'get':'getshareprojdetail'
})


urlpatterns = [
        url(r'^$', proj_list , name='proj_list'),
        url(r'^(?P<pk>\d+)/$', proj_detail, name='proj_detail'),
        url(r'^finance/$', proj_finance, name='proj_finance'),
        url(r'^favorite/$' , userfavorite_proj,name='user_favoriteproj'),
        url(r'^share/(?P<pk>\d+)/$',getshareprojtoken,name='getshareprojtoken'),
        url(r'^shareproj/$',getshareproj,name='getshareprojdetail')
]