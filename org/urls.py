from django.conf.urls import url, include
import views



org_list = views.OrganizationView.as_view({
        'get': 'list',
        'post': 'create'
})
org_detail = views.OrganizationView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
})


org_remarklist = views.OrgRemarkView.as_view({
        'get': 'list',
        'post': 'create'
})
org_remarkdetail = views.OrgRemarkView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
})



urlpatterns = [
        url(r'^$', org_list,name='org-list'),
        url(r'^(?P<pk>\d+)/$', org_detail,name='org-detail'),
        url(r'^remark/$', org_remarklist,name='orgremark-list'),
        url(r'^remark/^(?P<pk>\d+)/$', org_remarkdetail,name='orgremark-detail'),
]