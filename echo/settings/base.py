"""
Django settings for echo project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

import ldap
import pytz

from django_auth_ldap.config import LDAPSearch

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", 'media'))

MEDIA_URL = '/pheme/media/'

LOGIN_URL = '/pheme/'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'e4vx5)%)0t%%x@2v%sxjsfo_1dgx(&8dbd8h#79d73a8i07qzj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_auth_ldap.backend.LDAPBackend',
)

AUTH_LDAP_SERVER_URI = "ldap://10.27.116.51"
AUTH_LDAP_BIND_DN = "cn=LDAP Query\\, Domino Server, OU=Service Accounts,DC=corp,DC=westworlds,DC=com"
AUTH_LDAP_BIND_PASSWORD = "Qu3ryLd@p"
AUTH_LDAP_USER_SEARCH = LDAPSearch('DC=corp,DC=westworlds,DC=com',
    ldap.SCOPE_SUBTREE, "(samaccountname=%(user)s)")

AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_REFERRALS: 0
}

AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'givenname',
    'last_name': 'sn',
    'email': 'mail'
}

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_user_agents',
    'echo.apps.core',
    'echo.apps.projects',
    'echo.apps.reports',
    'echo.apps.settings',
    'echo.apps.elpis',
    'echo.apps.activity',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
)

ROOT_URLCONF = 'echo.urls'

WSGI_APPLICATION = 'echo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
   0: 'default',
   15: 'primary',
   35: 'danger',
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_ROOT = ''
STATIC_URL = '/static/'

# Celery config
CELERY_ACCEPT_CONTENT = ['pickle', 'json', ]
CELERY_TIMEZONE = pytz.timezone('US/Central')
CELERY_ENABLE_UTC = False
CELERY_RESULT_BACKEND = 'amqp'
CELERY_RESULT_SERIALIZER = 'pickle'

VOICESLOTS_METRICS = {
    'pass': 0,
    'fail': 0,
    'new': 0,
    'missing': 0
}