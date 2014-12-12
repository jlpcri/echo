import os
import socket

from celery import Celery

from django.conf import settings


if socket.gethostname() == "QAIMint":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "echo.settings.alex_dev")
elif socket.gethostname() == "qaci01":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "echo.settings.qaci")
elif socket.gethostname() == "linux6436":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "echo.settings.qa_lab")
elif socket.gethostname() == "sliu-OptiPlex-GX520":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "echo.settings.sliu_dev")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "echo.settings.base")

app = Celery('echo')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
