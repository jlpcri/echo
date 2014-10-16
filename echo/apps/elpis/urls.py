from django.conf.urls import patterns, url
from django.contrib import admin
from echo.apps.elpis import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^(?P<pid>\d+)/$', views.dashboard, name='dashboard'),
    url(r'^(?P<pid>\d+)/server$', views.set_preprod_server, name='set_server'),
    url(r'^(?P<pid>\d+)/path$', views.set_preprod_path, name='set_path'),
    url(r'^(?P<pid>\d+)/verify$', views.verify_file_transfer, name='verify'),
    )