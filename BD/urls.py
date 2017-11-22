from django.conf.urls import url, include
import views

projbd_list = views.ProjectBDView.as_view({
        'get': 'list',
        'post': 'create'
})

projbd_detail = views.ProjectBDView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
})
projdbcomment_list = views.ProjectBDCommentsView.as_view({
        'get': 'list',
        'post': 'create'
})
projbdcomment_detail = views.ProjectBDCommentsView.as_view({
        'delete': 'destroy'
})


orgbd_list = views.OrgBDView.as_view({
        'get': 'list',
        'post': 'create'
})

orgbd_detail = views.OrgBDView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
})
orgbdcomment_list = views.OrgBDCommentsView.as_view({
        'get': 'list',
        'post': 'create'
})
orgbdcomment_detail = views.OrgBDCommentsView.as_view({
        'delete': 'destroy'
})


urlpatterns = [
        url(r'^projbd/$', projbd_list, name='projbd_list'),
        url(r'^projbd/(?P<pk>\d+)/$', projbd_detail, name='projbd_detail'),
        url(r'^projbd/$', projdbcomment_list, name='projdbcomment_list'),
        url(r'^projbd/(?P<pk>\d+)/$', projbdcomment_detail, name='projbdcomment_detail'),
        url(r'^orgbd/$', orgbd_list, name='orgbd_list'),
        url(r'^orgbd/(?P<pk>\d+)/$', orgbd_detail, name='orgbd_detail'),
        url(r'^orgbd/$', orgbdcomment_list, name='orgbdcomment_list'),
        url(r'^orgbd/(?P<pk>\d+)/$', orgbdcomment_detail, name='orgbdcomment_detail'),

]