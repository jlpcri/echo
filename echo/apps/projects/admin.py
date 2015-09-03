from django.contrib import admin

from models import Project, VoiceSlot, VUID, Language, UpdateStatus

model_list = [Project, VoiceSlot, VUID, Language, UpdateStatus]

for m in model_list:
    admin.site.register(m)