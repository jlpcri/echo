from base import *

STATIC_URL = '/static/'
STATIC_ROOT = '/opt/static/'
STATICFILES_DIRS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'echo',
        'USER': 'visilog',
        'PASSWORD': '6ewuON0>;wHTe(DttOwjg#5NY)U497xKVwOxmQt60A1%}r:@qC&`7OdSP8u[.l[',
        'HOST': 'linux6437.wic.west.com',
        'PORT': '5432'
    }
}