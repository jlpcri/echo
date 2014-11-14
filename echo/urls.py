from django.conf.urls import patterns, include, url
from django.contrib import admin

import echo.apps.core.urls as coreUrls
import echo.apps.projects.urls as projectsUrls
import echo.apps.reports.urls as reportsUrls
import echo.apps.settings.urls as settingsUrls
import echo.apps.elpis.urls as elpisUrls

import echo.settings.base as settings

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^pheme/', include(coreUrls, namespace="core")),
    url(r'^pheme/', include(projectsUrls, namespace="projects")),
    url(r'^pheme/', include(reportsUrls, namespace="reports")),
    url(r'^pheme/settings/', include(settingsUrls, namespace="settings")),
    url(r'^pheme/elpis/', include(elpisUrls, namespace="elpis")),
)

urlpatterns += patterns('', (r'^pheme/media/(?P<path>.*)$', 'django.views.static.serve',
                             {'document_root': settings.MEDIA_ROOT}))
