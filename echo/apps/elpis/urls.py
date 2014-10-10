from django.conf.urls import patterns, url
from django.contrib import admin
from echo.apps.elpis import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^(?P<pid>\d+)/$', views.dashboard, name='dashboard'),
    url(r'^(?P<pid>\d+)/set$', views.set_preprod_path, name='set'),
    url(r'^(?P<pid>\d+)/verify$', views.verify_file_transfer, name='verify'),
    )