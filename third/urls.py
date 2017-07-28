#coding=utf-8
from django.conf.urls import url
import views.submail
import views.qiniufile
import views.others
urlpatterns = [
    url(r'^email$', views.submail.sendEmail ,name='sendmail',),
    url(r'^sms$', views.submail.sendSmscode, name='sendsmscode', ),
    url(r'^qiniubigupload$', views.qiniufile.bigfileupload, name='qiniubig', ),
    url(r'^qiniucoverupload$', views.qiniufile.qiniu_coverupload, name='qiniucover', ),
    url(r'^qiniudelete$', views.qiniufile.qiniu_deletefile, name='qiniudelete', ),
    url(r'^currencyrate$', views.others.getcurrencyreat, name='getcurrencyrate', ),
    url(r'^uploadToken$', views.qiniufile.qiniu_uploadtoken, name='getuploadtoken', ),
    url(r'^downloadUrl$', views.qiniufile.qiniu_downloadurl, name='getdownloadurl', ),
]