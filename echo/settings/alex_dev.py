from base import *

STATIC_URL = 'http://apps.qaci01.wic.west.com/static/'

PRIVATE_KEY = '/home/caheyden/.ssh/id_rsa'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pheme',
        'USER': 'caheyden',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}