from django.conf.urls import patterns, url
from django.contrib import admin
from echo.apps.settings import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^servers/$', views.servers, name='servers'),
    url(r'^servers_preprod/$', views.servers_preprod, name='servers_preprod'),
    url(r'^users/$', views.users, name='users'),
    url(r'^dollars/$', views.dollar_dashboard_config, name='dollar_dashboard_config'),
)