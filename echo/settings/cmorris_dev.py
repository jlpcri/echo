from base import *
STATIC_URL = 'http://linux6436.wic.west.com/static/'
#STATIC_ROOT = ''

PRIVATE_KEY = '/home/cmorris/.ssh/id_rsa'

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

# pip install virtualenvwrapper
# pip install -r common.txt
# scp wicqacip@qaci01.wic.west.com:/home/wicqacip/.ssh/id_rsa* ~/.ssh/
# Keep Databases Commented out - ???
# manage.py syncdb
# manage.py migrate

# when changes are made to models after initial has been created
#./manage.py schemamigration projects --auto
# bravo setting for Server
# linux1137.wic.west.com    service account - web`