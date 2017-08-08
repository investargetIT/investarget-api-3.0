#coding=utf-8
from django.conf.urls import url
import views

tag = views.TagView.as_view({
        'get': 'list',
        'post':'create',
})
tagdetail = views.TagView.as_view({
        'put': 'update',
        'delete': 'destroy'
})
projstatus = views.ProjectStatusView.as_view({
        'get': 'list',

})
service = views.ServiceView.as_view({
        'get': 'list',
        'post':'create',
})
servicedetail = views.ServiceView.as_view({
        'put': 'update',
        'delete': 'destroy'
})

country = views.CountryView.as_view({
        'get': 'list',
        'post':'create',
})
countrydetail = views.CountryView.as_view({
        'put': 'update',
        'delete': 'destroy'
})

character = views.CharacterTypeView.as_view({
        'get': 'list',
        'post':'create',
})
characterdetail = views.CharacterTypeView.as_view({
        'put': 'update',
        'delete': 'destroy'
})


title = views.TitleView.as_view({
        'get': 'list',
        'post':'create',
})
titledetail = views.TitleView.as_view({
        'put': 'update',
        'delete': 'destroy'
})

industry = views.IndustryView.as_view({
        'get': 'list',
        'post':'create',
})
industrydetail = views.IndustryView.as_view({
        'put': 'update',
        'delete': 'destroy'
})


datasource = views.DatasourceView.as_view({
        'get': 'list',
        'post':'create',
})
datasourcedetail = views.DatasourceView.as_view({
        'put': 'update',
        'delete': 'destroy'
})


orgarea = views.OrgAreaView.as_view({
        'get': 'list',
        'post':'create',
})
orgareadetail = views.OrgAreaView.as_view({
        'put': 'update',
        'delete': 'destroy'
})


orgtype = views.OrgTypeView.as_view({
        'get': 'list',
        'post':'create',
})
orgtypedetail = views.OrgTypeView.as_view({
        'put': 'update',
        'delete': 'destroy'
})


transactionType = views.TransactionTypeView.as_view({
        'get': 'list',
        'post':'create',
})
transactionTypedetail = views.TransactionTypeView.as_view({
        'put': 'update',
        'delete': 'destroy'
})

transactionPhases = views.TransactionPhasesView.as_view({
        'get': 'list',
        'post':'create',
})
transactionPhasesdetail = views.TransactionPhasesView.as_view({
        'put': 'update',
        'delete': 'destroy'
})
transactionStatus = views.TransactionStatusView.as_view({
        'get': 'list',
        'post':'create',
})
transactionStatusdetail = views.TransactionStatusView.as_view({
        'put': 'update',
        'delete': 'destroy'
})

currencyType = views.CurrencyTypeView.as_view({
        'get': 'list',
        'post':'create',
})
currencyTypedetail = views.CurrencyTypeView.as_view({
        'put': 'update',
        'delete': 'destroy'
})

Orgtitletable = views.OrgtitletableView.as_view({
        'get': 'list',
        'post':'create',
})
Orgtitletabledetail = views.OrgtitletableView.as_view({
        'put': 'update',
        'delete': 'destroy'
})


urlpatterns = [
    url(r'^tag$', tag,name='tagsource',),
    url(r'^tag/(?P<pk>\d+)$', tagdetail,name='tagdetail',),
    url(r'^service', service,name='servicesource',),
    url(r'^service/(?P<pk>\d+)$', servicedetail,name='servicedetail',),
    url(r'^projstatus$', projstatus, name='projstatus', ),
    url(r'^country$', country,name='countrysource',),
    url(r'^country/(?P<pk>\d+)$', countrydetail,name='countrydetail',),
    url(r'^industry$', industry,name='industrysource',),
    url(r'^industry/(?P<pk>\d+)$', industrydetail,name='industrydetail',),
    url(r'^title$', title,name='titlesource',),
    url(r'^title/(?P<pk>\d+)$', titledetail,name='titledetail',),
    url(r'^datasource$', datasource,name='datasourcesource',),
    url(r'^datasource/(?P<pk>\d+)$', datasourcedetail,name='datasourcedetail',),
    url(r'^orgarea$', orgarea,name='orgareasource',),
    url(r'^orgarea/(?P<pk>\d+)$', orgareadetail,name='orgareadetail',),
    url(r'^orgtype$', orgtype,name='orgtypesource',),
    url(r'^orgtype/(?P<pk>\d+)$', orgtypedetail,name='orgtypedetail',),
    url(r'^transactionType$', transactionType,name='transactionTypesource',),
    url(r'^transactionType/(?P<pk>\d+)$',transactionTypedetail,name='transactionTypedetail',),
    url(r'^transactionPhases$', transactionPhases,name='transactionPhasessource',),
    url(r'^transactionPhases/(?P<pk>\d+)$', transactionPhasesdetail,name='transactionPhasesdetail',),
    url(r'^transactionStatus$', transactionStatus, name='transactionStatussource', ),
    url(r'^transactionStatus/(?P<pk>\d+)$', transactionStatusdetail, name='transactionStatusdetail', ),
    url(r'^currencyType$', currencyType,name='currencyTypesource',),
    url(r'^currencyType/(?P<pk>\d+)$', currencyTypedetail,name='currencyTypedetail',),
    url(r'^character$', character,name='charactersource',),
    url(r'^character/(?P<pk>\d+)$', characterdetail,name='characterdetail',),
    url(r'^orgtitletable$', Orgtitletable,name='Orgtitletablesource',),
    url(r'^orgtitletable/(?P<pk>\d+)$', Orgtitletabledetail,name='Orgtitletabledetail',),
]