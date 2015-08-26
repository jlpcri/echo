from django.conf.urls import patterns, url
from django.contrib import admin
from echo.apps.jira import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^sync/?$', views.sync_tickets, name='sync_tickets'),
    url(r'^versions/(?P<project_id>\w+)$', views.get_versions_by_project, name='versions'),
    url(r'^key/?$', views.set_jira_key, name='set_key')
)