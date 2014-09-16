from django.conf.urls import patterns, url
from django.contrib import admin
from echo.apps.projects import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^new/$', views.new, name='new'),
    url(r'^(?P<pid>\d+)$', views.project, name='project'),
    url(r'^$', views.projects, name='projects'),
    url(r'^(?P<pid>\d+)/vuids/(?P<vid>\d+)$', views.vuid, name='vuid'),
    url(r'^(?P<pid>\d+)/voiceslots/(?P<vsid>\d+)$', views.testslot, name='testslot'),
    url(r'^(?P<pid>\d+)/voiceslots/(?P<vsid>\d+)/submit$', views.submitslot, name='submitslot'),
    url(r'^(?P<pid>\d+)/voiceslots/master$', views.master, name='master'),
    url(r'^(?P<pid>\d+)/voiceslots/language/(?P<lid>\d+)$', views.language, name='language'),
)