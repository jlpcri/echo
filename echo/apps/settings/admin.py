from django.contrib import admin

from models import Server, PreprodServer, UserSettings

model_list = [Server, PreprodServer, UserSettings]

for m in model_list:
    admin.site.register(m)
