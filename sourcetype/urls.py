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

country = views.CountryView.as_view({
        'get': 'list',
        'post':'create',
})
countrydetail = views.CountryView.as_view({
        'put': 'update',
        'delete': 'destroy'
})

continent = views.ContinentalView.as_view({
        'get': 'list',
        'post':'create',
})
continentdetail = views.ContinentalView.as_view({
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



urlpatterns = [
    url(r'^tag$', tag,name='tagsource',),
    url(r'^tag/(?P<pk>\d+)$', tagdetail,name='tagdetail',),
    url(r'^country$', country,name='countrysource',),
    url(r'^country/(?P<pk>\d+)$', countrydetail,name='countrydetail',),
    url(r'^continent$', continent,name='continentsource',),
    url(r'^continent/(?P<pk>\d+)$', continentdetail,name='continentdetail',),
    url(r'^industry$', industry,name='industrysource',),
    url(r'^industry/(?P<pk>\d+)$', industrydetail,name='industrydetail',),
    url(r'^title$', title,name='titlesource',),
    url(r'^title/(?P<pk>\d+)$', titledetail,name='titledetail',),
    url(r'^datasource$', datasource,name='datasourcesource',),
    url(r'^datasource/(?P<pk>\d+)$', datasourcedetail,name='datasourcedetail',),

]