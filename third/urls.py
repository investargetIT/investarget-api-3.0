#coding=utf-8
from django.conf.urls import url
import views.submail
import views.qiniufile
import views.others
urlpatterns = [
    url(r'^email$', views.submail.sendEmail ,name='sendmail',),
    url(r'^sms$', views.submail.sendSmscode, name='sendsmscode', ),
    url(r'^intersms$', views.submail.sendInternationalsmscode, name='sendintersmscode', ),
    url(r'^qiniubigupload$', views.qiniufile.bigfileupload, name='qiniubig', ),
    url(r'^currencyrate$', views.others.getcurrencyreat, name='getcurrencyrate', ),
]