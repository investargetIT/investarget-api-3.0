from django.conf.urls import url, include
import views



org_list = views.OrganizationView.as_view({
        'get': 'list',
        'post': 'create'
})
org_detail = views.OrganizationView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
})


urlpatterns = [
    # url(r'^$', org_list,name='org-list'),
    # url(r'^(?P<pk>\d+)/$', org_detail,name='org-detail'),

]