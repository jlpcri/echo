from django.conf.urls import patterns, url
from django.contrib import admin
from echo.apps.reports import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^reports$', views.reports, name='reports'),
    url(r'^reports/failed/(?P<pid>\d+)/?$', views.failed, name='failed'),
    url(r'^reports/missing/(?P<pid>\d+)/?$', views.missing, name='missing'),
    url(r'^reports/(?P<pid>\d+)$', views.report_project, name='report_project')
)