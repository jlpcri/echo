from django.conf.urls import patterns, url
from django.contrib import admin
from echo.apps.projects import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.allprojects, name='allprojects'),
)