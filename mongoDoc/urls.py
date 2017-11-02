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

ProjectNewsList = views.ProjectNewsView.as_view({
        'get': 'list',
        'post':'create',
})

ProjectRemarkList = views.ProjectRemarkView.as_view({
        'get': 'list',
        'post':'create',
        'put': 'update',
        'delete':'destroy',
})
EmailGroupList = views.GroupEmailDataView.as_view({
        'get': 'list',

})

IMChatMessagesList = views.IMChatMessagesView.as_view({
        'get': 'list',

})

WXChatDataList = views.WXChatDataView.as_view({
        'get': 'list',
        'put': 'update',
})

urlpatterns = [
    url(r'^cat', CompanyCatDataList, name='CompanyCatData-list', ),
    url(r'^event$', MergeFinanceDataList, name='MergeFinanceData-list', ),
    url(r'^proj$', ProjectDataList, name='ProjectData-list',),
    url(r'^projnews$', ProjectNewsList, name='ProjectNews-list',),
    url(r'^projremark$', ProjectRemarkList, name='ProjectRemark-list',),
    url(r'^email$', EmailGroupList,name='WXContent-list',),
    url(r'^chatmsg$', IMChatMessagesList, name='IMChatMessages-list', ),
    url(r'^wxmsg$', WXChatDataList, name='WXChatData-list', ),
]