from django.conf.urls import url, include
import views

projbd_list = views.ProjectBDView.as_view({
        'get': 'list',
        'post': 'create'
})

projbd_count = views.ProjectBDView.as_view({
        'get': 'countBd',
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
        'put': 'update',
        'delete': 'destroy'
})
orgbd_baselist = views.OrgBDView.as_view({
        'get': 'countBDProjectOrg',
})

orgbd_list = views.OrgBDView.as_view({
        'get': 'list',
        'post': 'create'
})

orgbd_managercount = views.OrgBDView.as_view({
        'get': 'countBDManager',

})

orgbd_responsecount = views.OrgBDView.as_view({
        'get': 'countBDResponse',

})

orgbd_read = views.OrgBDView.as_view({
        'post': 'readBd',
})

orgbd_projectcount = views.OrgBDView.as_view({
        'get': 'countBDProject',
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


meetbd_list = views.MeetingBDView.as_view({
        'get': 'list',
        'post': 'create'
})

meetbd_detail = views.MeetingBDView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
})

deleteAttachment = views.MeetingBDView.as_view({
        'post': 'deleteAttachment',

})

urlpatterns = [
        url(r'^projbd/$', projbd_list, name='projbd_list'),
        url(r'^projbd/count/$', projbd_count, name='projbd_count'),
        url(r'^projbd/(?P<pk>\d+)/$', projbd_detail, name='projbd_detail'),
        url(r'^projbd/comment/$', projdbcomment_list, name='projdbcomment_list'),
        url(r'^projbd/comment/(?P<pk>\d+)/$', projbdcomment_detail, name='projbdcomment_detail'),
        url(r'^orgbd/$', orgbd_list, name='orgbd_list'),
        url(r'^orgbd/read/$', orgbd_read, name='orgbd_read'),
        url(r'^orgbdbase/$', orgbd_baselist, name='orgbdbase_list'),
        url(r'^orgbd/count/$', orgbd_managercount, name='orgbd_managercount'),
        url(r'^orgbd/response/$', orgbd_responsecount, name='orgbd_responsecount'),
        url(r'^orgbd/proj/$', orgbd_projectcount, name='orgbd_projectcount'),
        url(r'^orgbd/(?P<pk>\d+)/$', orgbd_detail, name='orgbd_detail'),
        url(r'^orgbd/comment/$', orgbdcomment_list, name='orgbdcomment_list'),
        url(r'^orgbd/comment/(?P<pk>\d+)/$', orgbdcomment_detail, name='orgbdcomment_detail'),
        url(r'^meetbd/$', meetbd_list, name='meetbd_list'),
        url(r'^meetbd/(?P<pk>\d+)/$', meetbd_detail, name='meetbd_detail'),
        url(r'^meetbd/delatt/(?P<pk>\d+)/$', deleteAttachment, name='deleteAttachment'),
]