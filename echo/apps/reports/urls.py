from django.conf.urls import patterns, url
from django.contrib import admin
from echo.apps.reports import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.allreports, name='allreports'),
)