from django.conf.urls import patterns, url
from django.contrib import admin
from echo.apps.core import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.form, name='form'),
    url(r'^home/$', views.home, name='home'),
    url(r'^signin/?$', views.signin, name='signin'),
    url(r'^signout/?$', views.signout, name='signout'),
)