#coding=utf-8
from django.conf.urls import url
import views


EmailGroupList = views.GroupEmailDataView.as_view({
        'get': 'list',

})

IMChatMessagesList = views.IMChatMessagesView.as_view({
        'get': 'list',

})
urlpatterns = [
    url(r'^email$', EmailGroupList,name='WXContent-list',),
    url(r'^chatmsg$', IMChatMessagesList, name='IMChatMessages-list', ),
]