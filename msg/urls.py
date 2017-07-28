from django.conf.urls import url, include
import views



msg_list = views.WebMessageView.as_view({
        'get': 'list',
})
msg_detail = views.WebMessageView.as_view({
        'post': 'update',
})
urlpatterns = [
        url(r'^$', msg_list,name='msg-list'),
        url(r'^(?P<pk>\d+)/$', msg_detail,name='msg-detail'),

]