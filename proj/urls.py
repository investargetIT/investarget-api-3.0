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

proj_attachment = views.ProjAttachmentView.as_view({
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

getprojpdf = views.ProjectView.as_view({
        'get':'sendPDFMail'
})

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
        # 'get': 'list',
        'post': 'create'
})
projbdcomment_detail = views.ProjectBDCommentsView.as_view({
        'delete': 'destroy'
})

urlpatterns = [
        url(r'^$', proj_list , name='proj_list'),
        url(r'^(?P<pk>\d+)/$', proj_detail, name='proj_detail'),
        url(r'^finance/$', proj_finance, name='proj_finance'),
        url(r'^attachment/$', proj_attachment, name='proj_attachment'),
        url(r'^favorite/$' , userfavorite_proj,name='user_favoriteproj'),
        url(r'^share/(?P<pk>\d+)/$',getshareprojtoken,name='getshareprojtoken'),
        url(r'^shareproj/$',getshareproj,name='getshareprojdetail'),
        url(r'^pdf/(?P<pk>\d+)/$',getprojpdf,name='getprojpdf'),
        url(r'^BD/$', projbd_list , name='projbd_list'),
        url(r'^BD/(?P<pk>\d+)/$', projbd_detail, name='projbd_detail'),
        url(r'^BDCom/$', projdbcomment_list , name='projdbcomment_list'),
        url(r'^BDCom/(?P<pk>\d+)/$', projbdcomment_detail, name='projbdcomment_detail'),
        url(r'^test/$',views.testPdf),
]