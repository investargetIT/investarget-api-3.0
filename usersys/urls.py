from django.conf.urls import url
import views



user_list = views.UserView.as_view({
        'get': 'list',
        'post': 'create'
})
user_detail = views.UserView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
})

user_transuser = views.UserRelationView.as_view({
        'get': 'list',
        'put': 'update',
        'post': 'create',
        'delete': 'destroy',
})

urlpatterns = [
    url(r'^$', user_list,name='user-list'),
    url(r'^(?P<pk>\d+)/$', user_detail,name='user-detail'),
    url(r'^login/$', views.login),
    url(r'^transuser/$', user_transuser,name='user-transuser'),

]