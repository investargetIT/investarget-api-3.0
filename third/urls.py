#coding=utf-8
from django.conf.urls import url
import views.submail

urlpatterns = [
    url(r'^email/$', views.submail.sendEmail ,name='sendmail',),
    url(r'^sms/$', views.submail.sendSmscode, name='sendsmscode', ),
    url(r'^intersms/$', views.submail.sendInternationalsmscode, name='sendintersmscode', ),
]