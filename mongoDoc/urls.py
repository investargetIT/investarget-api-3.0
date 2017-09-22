#coding=utf-8
from django.conf.urls import url
import views

CompanyCatDataList = views.CompanyCatDataView.as_view({
        'get': 'list',
        'post':'create',
})


MergeFinanceDataList = views.MergeFinanceDataView.as_view({
        'get': 'list',
        'post':'create',
})

ProjectDataList = views.ProjectDataView.as_view({
        'get': 'list',
        'post':'create',
})


EmailGroupList = views.GroupEmailDataView.as_view({
        'get': 'list',

})

IMChatMessagesList = views.IMChatMessagesView.as_view({
        'get': 'list',

})
urlpatterns = [
    url(r'^cat', CompanyCatDataList, name='CompanyCatData-list', ),
    url(r'^event$', MergeFinanceDataList, name='MergeFinanceData-list', ),
    url(r'^proj$', ProjectDataList, name='ProjectData-list',),
    url(r'^email$', EmailGroupList,name='WXContent-list',),
    url(r'^chatmsg$', IMChatMessagesList, name='IMChatMessages-list', ),
]