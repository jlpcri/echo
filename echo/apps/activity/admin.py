from django.contrib import admin
from solo.admin import SingletonModelAdmin

from echo.apps.activity.models import DollarDashboardConfig

admin.site.register(DollarDashboardConfig, SingletonModelAdmin)

config = DollarDashboardConfig.get_solo()


