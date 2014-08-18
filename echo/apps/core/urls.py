from django.conf.urls import patterns, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('echo.apps.core.views',
    url(r'^$', 'index', name='index'),
)