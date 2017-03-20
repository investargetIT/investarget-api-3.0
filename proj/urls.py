from django.conf.urls import url, include
# from rest_framework import routers

import views
# router = routers.DefaultRouter()
# router.register(r'proj', views.ProjViewSet)

urlpatterns = [

        url(r'^$', views.projlist.as_view() , name='proj_list'),
        url(r'^(?P<pk>\d+)/', views.projdetail.as_view(), name='proj_detail'),
        url(r'^favorite/$' , views.allfavorite),
        url(r'^favorite/(?P<pk>\d+)/$' , views.favoritetype),


]