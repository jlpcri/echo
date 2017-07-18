from base import *
import socket


if socket.gethostname() == 'monolith':
    STATICFILES_DIRS = ('/home/ewhitcom/Dropbox/Static',)
    PRIVATE_KEY = '/home/ewhitcom/.ssh/id_rsa'
elif socket.gethostname() == 'OM1687L1':
    STATICFILES_DIRS = ('C:/Users/ewhitcom/Dropbox/Static',)
    PRIVATE_KEY = 'C:/Users/ewhitcom/.ssh/id_rsa'