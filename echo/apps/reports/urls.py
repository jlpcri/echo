from django.conf.urls import patterns, url
from django.contrib import admin
from echo.apps.reports import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^(?P<rid>\d+)$', views.report, name='report'),
    url(r'^$', views.reports, name='reports'),
)