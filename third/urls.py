#coding=utf-8
from django.conf.urls import url
import views.submail
import views.qiniufile
import views.huanxin
import views.others
urlpatterns = [
    url(r'^sms$', views.submail.sendSmscode, name='sendsmscode', ),
    url(r'^qiniubigupload$', views.qiniufile.bigfileupload, name='qiniubig', ),
    url(r'^qiniucoverupload$', views.qiniufile.qiniu_coverupload, name='qiniucover', ),
    url(r'^currencyrate$', views.others.getcurrencyreat, name='getcurrencyrate', ),
    url(r'^ccupload', views.others.ccupload, name='ccupload', ),
    url(r'^uploadToken$', views.qiniufile.qiniu_uploadtoken, name='getuploadtoken',),
    url(r'^downloadUrl$', views.qiniufile.qiniu_downloadurl, name='getdownloadurl',),
    url(r'^getQRCode$',views.others.getQRCode,name='getQRCode',),
    url(r'^recordUpload',views.others.recordUpload,name='recordUpload',),
    url(r'^updateUpload',views.others.updateUpload,name='updateUploadRecord',),
    url(r'^selectUpload',views.others.selectUpload,name='selectFromUploadRecord',),
    url(r'^cancelUpload',views.others.cancelUpload,name='cancelUploadRecord',),
    url(r'^deleteUpload',views.others.deleteUpload,name='deleteUploadRecord',),
]