from django.conf.urls import url, include
# from rest_framework import routers

import views
proj_list = views.ProjectView.as_view({
        'get': 'list',
        'post': 'create'
})
urlpatterns = [

        url(r'^$', proj_list , name='proj_list'),
        # url(r'^(?P<pk>\d+)/', views.projdetail.as_view(), name='proj_detail'),
        # url(r'^favorite/$' , views.allfavorite),
        # url(r'^favorite/(?P<pk>\d+)/$' , views.favoritetype),


]