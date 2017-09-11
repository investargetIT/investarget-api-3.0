#coding=utf-8
from django.conf.urls import url
import views

tag = views.TagView.as_view({
        'get': 'list',
        # 'post':'create',
})

projstatus = views.ProjectStatusView.as_view({
        'get': 'list',

})
service = views.ServiceView.as_view({
        'get': 'list',
        # 'post':'create',
})


country = views.CountryView.as_view({
        'get': 'list',
        # 'post':'create',
})


character = views.CharacterTypeView.as_view({
        'get': 'list',
        # 'post':'create',
})



title = views.TitleView.as_view({
        'get': 'list',
        # 'post':'create',
})


industry = views.IndustryView.as_view({
        'get': 'list',
        # 'post':'create',
})



datasource = views.DatasourceView.as_view({
        'get': 'list',
        # 'post':'create',
})



orgarea = views.OrgAreaView.as_view({
        'get': 'list',
        # 'post':'create',
})



orgtype = views.OrgTypeView.as_view({
        'get': 'list',
        # 'post':'create',
})

orgAttribute = views.OrgAttributeView.as_view({
        'get': 'list',
        # 'post':'create',
})

transactionType = views.TransactionTypeView.as_view({
        'get': 'list',
        # 'post':'create',
})


transactionPhases = views.TransactionPhasesView.as_view({
        'get': 'list',
        # 'post':'create',
})

transactionStatus = views.TransactionStatusView.as_view({
        'get': 'list',
        # 'post':'create',
})


currencyType = views.CurrencyTypeView.as_view({
        'get': 'list',
        # 'post':'create',
})


Orgtitletable = views.OrgtitletableView.as_view({
        'get': 'list',
        # 'post':'create',
})



urlpatterns = [
    url(r'^tag$', tag,name='tagsource',),

    url(r'^service', service,name='servicesource',),

    url(r'^orgAttribute', orgAttribute,name='orgAttributesource',),

    url(r'^projstatus$', projstatus, name='projstatus', ),

    url(r'^country$', country,name='countrysource',),

    url(r'^industry$', industry,name='industrysource',),

    url(r'^title$', title,name='titlesource',),

    url(r'^datasource$', datasource,name='datasourcesource',),

    url(r'^orgarea$', orgarea,name='orgareasource',),

    url(r'^orgtype$', orgtype,name='orgtypesource',),

    url(r'^transactionType$', transactionType,name='transactionTypesource',),

    url(r'^transactionPhases$', transactionPhases,name='transactionPhasessource',),

    url(r'^transactionStatus$', transactionStatus, name='transactionStatussource', ),

    url(r'^currencyType$', currencyType,name='currencyTypesource',),

    url(r'^character$', character,name='charactersource',),

    url(r'^orgtitletable$', Orgtitletable,name='Orgtitletablesource',),

]