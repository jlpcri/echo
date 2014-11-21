from base import *

STATIC_URL = '/static/'
STATIC_ROOT = '/opt/static_web/'
STATICFILES_DIRS = []

PRIVATE_KEY = '/home/wicqacip/.ssh/id_rsa'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pheme',
        'USER': 'wicqacip',
    }
}