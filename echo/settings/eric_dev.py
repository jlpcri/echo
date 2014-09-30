from base import *


if socket.gethostname() == 'monolith':
    STATICFILES_DIRS = ('/home/ewhitcom/Dropbox/Static',)
elif socket.gethostname() == 'OM1687L1':
    STATICFILES_DIRS = ('C:/Users/ewhitcom/Dropbox/Static',)