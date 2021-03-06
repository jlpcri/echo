from django.conf.urls import patterns, url
from django.contrib import admin
from echo.apps.projects import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^projects$', views.projects, name='projects'),
    url(r'^projects/new/$', views.new, name='new'),
    url(r'^projects/(?P<pid>\d+)$', views.project, name='project'),
    url(r'^projects/(?P<pid>\d+)/certify/$', views.certify, name='certify'),
    url(r'^projects/(?P<pid>\d+)/progress/$', views.project_progress, name='project_progress'),
    url(r'^projects/(?P<pid>\d+)/fetch$', views.fetch, name='fetch'),
    url(r'^projects/(?P<pid>\d+)/join$', views.join_project, name='joinproject'),
    url(r'^projects/(?P<pid>\d+)/leave$', views.leave_project, name='leaveproject'),
    url(r'^projects/(?P<pid>\d+)/archive$', views.archive_project, name='archive_project'),
    url(r'^projects/(?P<pid>\d+)/queue/?$', views.queue, name='queue'),
    url(r'^projects/(?P<pid>\d+)/vuids/(?P<vid>\d+)$', views.vuid, name='vuid'),
    url(r'^projects/(?P<pid>\d+)/voiceslots/?$', views.voiceslots, name='voiceslots'),
    url(r'^projects/(?P<pid>\d+)/voiceslots/(?P<vsid>\d+)$', views.testslot, name='testslot'),
    url(r'^projects/voiceslots/(?P<vsid>\d+)/submit$', views.submitslot, name='submitslot'),
    url(r'^projects/temp/$', views.temp, name='temp'),
    url(r'^projects/(?P<pid>\d+)/update/$', views.initiate_status_update, name='initiate_status_update'),
    url(r'^projects/(?P<vuid_id>\d+)/rollback$', views.rollback_vuid, name="rollback_vuid"),

    url(r'^voiceslots/(?P<slot_id>\d+)/delete$', views.delete_slot, name="delete_slot"),
)