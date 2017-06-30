from django.conf.urls import patterns, url
from django.contrib import admin
from echo.apps.usage import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^usage$', views.usage, name='usage'),
    url(r'^usage/project/(?P<pid>\d+)/?$', views.project, name='project'),
    url(r'^usage/projects$', views.projects, name='projects'),
    url(r'^usage/user/(?P<uid>\d+)/?$', views.user, name='user'),
    url(r'^usage/users$', views.users, name='users'),

    url(r'^usage/pheme_tests$', views.pheme_tests, name='pheme_tests'),
)