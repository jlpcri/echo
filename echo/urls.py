from django.conf.urls import patterns, include, url
from django.contrib import admin

import echo.apps.core.urls as coreUrls
import echo.apps.projects.urls as projectsUrls
import echo.apps.reports.urls as reportsUrls
import echo.apps.settings.urls as settingsUrls

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^echo/', include(coreUrls, namespace="core")),
    url(r'^echo/projects/', include(projectsUrls, namespace="projects")),
    url(r'^echo/reports/', include(reportsUrls, namespace="reports")),
    url(r'^echo/settings/', include(settingsUrls, namespace="settings")),
)
