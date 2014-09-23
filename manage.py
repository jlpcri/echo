#!/usr/bin/env python
import os
import sys
import socket

if __name__ == "__main__":
    if socket.gethostname() == "QAIMint":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "echo.settings.alex_dev")
    elif socket.gethostname() == "qaci01":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "echo.settings.qaci")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "echo.settings.base")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
