from base import *

#STATIC_URL = 'http://linux6436.wic.west.com/static/'
#STATIC_ROOT = ''
STATICFILES_DIRS = ('/home/seenaomi/opt/static/',)


PRIVATE_KEY = '/home/seenaomi/.ssh/id_rsa'

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



