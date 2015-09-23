#!/usr/bin/env python
import os
import sys
import socket

if __name__ == "__main__":
    if socket.gethostname() == "QAIMint":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "echo.settings.alex_dev")
    elif socket.gethostname() == "qaci01":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "echo.settings.qaci")
    elif socket.gethostname() == "linux6436":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "echo.settings.qa_lab")
    elif socket.gethostname() == "sliu-OptiPlex-GX520":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "echo.settings.sliu_dev")
    elif socket.gethostname() == "bw_ubuntu_west":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "echo.settings.wew_dev")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "echo.settings.base")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
