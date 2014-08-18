from django.conf.urls import patterns, include, url
from django.contrib import admin

import echo.apps.core.urls as coreUrls

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^echo/$', include(coreUrls, namespace="core")),
)
