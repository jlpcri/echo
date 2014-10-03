from django.conf.urls import patterns, url
from django.contrib import admin
from echo.apps.projects import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.projects, name='projects'),
    url(r'^new/$', views.new, name='new'),
    url(r'^(?P<pid>\d+)$', views.project, name='project'),
    url(r'^(?P<pid>\d+)/fetch$', views.fetch, name='fetch'),
    url(r'^(?P<pid>\d+)/join$', views.join_project, name='joinproject'),
    url(r'^(?P<pid>\d+)/leave$', views.leave_project, name='leaveproject'),
    url(r'^(?P<pid>\d+)/queue/?$', views.queue, name='queue'),
    url(r'^(?P<pid>\d+)/vuids/(?P<vid>\d+)$', views.vuid, name='vuid'),
    url(r'^(?P<pid>\d+)/voiceslots/?$', views.voiceslots, name='voiceslots'),
    url(r'^(?P<pid>\d+)/voiceslots/(?P<vsid>\d+)$', views.testslot, name='testslot'),
    url(r'^(?P<pid>\d+)/voiceslots/(?P<vsid>\d+)/submit$', views.submitslot, name='submitslot'),
    url(r'^temp/$', views.temp, name='temp'),
)