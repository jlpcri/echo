from base import *

DEBUG = False

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

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': 'echo',
#        'USER': 'visilog',
#        'PASSWORD': '6ewuON0>;wHTe(DttOwjg#5NY)U497xKVwOxmQt60A1%}r:@qC&`7OdSP8u[.l[',
#        'HOST': 'linux6437.wic.west.com',
#        'PORT': '5432'
#    }
#}
