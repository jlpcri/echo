from django.conf.urls import patterns, url
from django.contrib import admin
from echo.apps.reports import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.reports, name='reports'),
    url(r'^failed/(?P<pid>\d+)$', views.failed, name='failed'),
    url(r'^missing/(?P<pid>\d+)$', views.missing, name='missing'),
)