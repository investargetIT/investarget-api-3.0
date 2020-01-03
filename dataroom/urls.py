#coding=utf-8
from django.conf.urls import url
from dataroom import views

dataroom = views.DataroomView.as_view({
        'get': 'list',
        'post': 'create',
})

dataroom_com = views.DataroomView.as_view({
        'get': 'companylist',
})


dataroom_one =  views.DataroomView.as_view({
        'get':'retrieve',
        'put':'update',
        'delete':'destroy',
})

dataroomfile = views.DataroomdirectoryorfileView.as_view({
        'get': 'list',
        'post': 'create',
        'put':'update',
        'delete':'destroy',
})


dataroomfilepath = views.DataroomdirectoryorfileView.as_view({
        'get': 'getFilePath',
})


user_dataroom = views.User_DataroomfileView.as_view({
        'get': 'list',
        'post': 'create',
})

user_dataroomone =  views.User_DataroomfileView.as_view({
        'get':'retrieve',
        'post':'sendEmailNotifaction',
        'put':'update',
        'delete':'destroy',
})

userUpdateFiles = views.User_DataroomfileView.as_view({
        'get': 'getUserUpdateFiles',
})

userFileUpdateEmail =  views.User_DataroomfileView.as_view({
        'post': 'sendFileUpdateEmailNotifaction',
})

user_dataroom_temp = views.User_Dataroom_TemplateView.as_view({
        'get': 'list',
        'post': 'create',
})

user_dataroomone_temp =  views.User_Dataroom_TemplateView.as_view({
        'get':'retrieve',
        'post':'userTempToUser',
        'put':'update',
        'delete':'destroy',
})


checkZip = views.DataroomView.as_view({
    'get':'checkZipStatus'
})

downZip = views.DataroomView.as_view({
    'get':'downloadDataroomZip'
})

urlpatterns = [
    url(r'^$', dataroom,name='dataroom-list',),
    url(r'^com/$', dataroom_com, name='dataroom_com-list', ),
    url(r'^(?P<pk>\d+)/$', dataroom_one,name='dataroom-detail'),
    url(r'^file/$', dataroomfile,name='dataroom-fileordirectory'),
    url(r'^filepath/$', dataroomfilepath,name='dataroom-filepath'),
    url(r'^user/$', user_dataroom,name='user_dataroom-list',),
    url(r'^userfile/update/$', userUpdateFiles,name='userUpdateFiles-list',),
    url(r'^userfile/update/(?P<pk>\d+)/$', userFileUpdateEmail,name='sendUserFileUpdateEmail',),
    url(r'^user/(?P<pk>\d+)/$', user_dataroomone,name='user_dataroom-detail'),
    url(r'^temp/$', user_dataroom_temp, name='user_dataroom_temp-list', ),
    url(r'^temp/(?P<pk>\d+)/$', user_dataroomone_temp, name='user_dataroom_temp-detail'),
    url(r'^checkzip/(?P<pk>\d+)/$', checkZip,name='dataroom-checkZip'),
    url(r'^downzip/(?P<pk>\d+)/$', downZip,name='dataroom-downZip'),
]