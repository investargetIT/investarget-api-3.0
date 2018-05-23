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



org_contactlist = views.OrgContactView.as_view({
        'get': 'list',
        'post': 'create'
})


org_contactdetail = views.OrgContactView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
})


org_managefundlist = views.OrgManageFundView.as_view({
        'get': 'list',
        'post': 'create'
})


org_managefunddetail = views.OrgManageFundView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
})


org_investeventlist = views.OrgInvestEventView.as_view({
        'get': 'list',
        'post': 'create'
})


org_investeventdetail = views.OrgInvestEventView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
})

org_investeventdelete = views.OrgInvestEventView.as_view({
        'get': 'deleteInvest',
})


org_cooprelationlist = views.OrgCooperativeRelationshipView.as_view({
        'get': 'list',
        'post': 'create'
})


org_cooprelationdetail = views.OrgCooperativeRelationshipView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
})


org_buyoutlist = views.OrgBuyoutView.as_view({
        'get': 'list',
        'post': 'create'
})


org_buyoutdetail = views.OrgBuyoutView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
})


org_typetemplatelist = views.OrgTypeTemplateView.as_view({
        'get': 'list',
        'post': 'create'
})


org_typetemplatedetail = views.OrgTypeTemplateView.as_view({
        'delete': 'destroy'
})



urlpatterns = [
        url(r'^$', org_list,name='org-list'),
        url(r'^(?P<pk>\d+)/$', org_detail,name='org-detail'),
        url(r'^remark/$', org_remarklist,name='orgremark-list'),
        url(r'^remark/(?P<pk>\d+)/$', org_remarkdetail,name='orgremark-detail'),
        url(r'^contact/$', org_contactlist,name='org_contact-list'),
        url(r'^contact/(?P<pk>\d+)/$', org_contactdetail,name='org_contact-detail'),
        url(r'^managefund/$', org_managefundlist,name='org_managefund-list'),
        url(r'^managefund/(?P<pk>\d+)/$', org_managefunddetail,name='org_managefund-detail'),
        url(r'^investevent/$', org_investeventlist,name='org_investevent-list'),
        url(r'^investevent/(?P<pk>\d+)/$', org_investeventdetail,name='org_investevent-detail'),
        url(r'^cooprelation/$', org_cooprelationlist,name='org_cooprelation-list'),
        url(r'^cooprelation/(?P<pk>\d+)/$', org_cooprelationdetail,name='org_cooprelation-detail'),
        url(r'^buyout/$', org_buyoutlist,name='org_buyout-list'),
        url(r'^buyout/(?P<pk>\d+)/$', org_buyoutdetail,name='org_buyout-detail'),
        url(r'^investevent/del/$', org_investeventdelete,name='org_buyout-detail'),
        url(r'^temp/$', org_typetemplatelist,name='org_typetemplate-list'),
        url(r'^temp/(?P<pk>\d+)/$', org_typetemplatedetail,name='org_typetemplate-detail'),
]