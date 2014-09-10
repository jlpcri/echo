from django.conf.urls import patterns, url
from django.contrib import admin
from echo.apps.projects import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^new/$', views.new, name='new'),
    url(r'^(?P<pid>\d+)$', views.project, name='project'),
    url(r'^$', views.projects, name='projects'),
    url(r'^vuid/(?P<vid>\d+)$', views.vuid, name='vuid'),
)