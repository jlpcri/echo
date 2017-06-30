from django.contrib import messages

DEFAULT = 0
DEBUG = messages.DEBUG
PRIMARY = 15
INFO = messages.INFO
SUCCESS = messages.SUCCESS
WARNING = messages.WARNING
DANGER = 35
ERROR = messages.ERROR


def default(request, message):
    messages.add_message(request, DEFAULT, message)


def debug(request, message):
    messages.debug(request, message)


def primary(request, message):
    messages.add_message(request, PRIMARY, message)


def info(request, message):
    messages.info(request, message)


def success(request, message):
    messages.success(request, message)


def warning(request, message):
    messages.warning(request, message)


def danger(request, message):
    messages.add_message(request, DANGER, message)


def error(request, message):
    messages.error(request, message)