from collections import defaultdict, namedtuple
import os

import pysftp

from django.contrib.auth.models import User
from django.conf import settings
from django.db import models


class Server(models.Model):
    """Bravo or similar server for hosting .wav files after recording"""
    name = models.TextField(unique=True, blank=False)
    address = models.TextField(unique=True, blank=False)
    account = models.TextField(blank=False)
    active = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class PreprodServer(models.Model):
    """Server to host .wav files for playback on preprod IVR"""
    PRODUCER = 1
    NATIVE_VXML = 2
    APPLICATION_TYPE_CHOICES = ((PRODUCER, "Producer"), (NATIVE_VXML, "Native VXML"))
    TUVOX_ROOT = '/usr/local/tuvox/public/Projects/'

    name = models.TextField(unique=True, blank=False)
    address = models.TextField(unique=True, blank=False)
    account = models.TextField(blank=False)
    application_type = models.PositiveSmallIntegerField(choices=APPLICATION_TYPE_CHOICES)

    def __unicode__(self):
        return self.name

    def get_clients(self):
        """Fetch list of project/client directories from preprod server file system"""
        if self.application_type == self.PRODUCER:
            with pysftp.Connection(self.address, username=self.account, private_key=settings.PRIVATE_KEY) as conn:
                return conn.listdir(remotepath=self.TUVOX_ROOT)
        elif self.application_type == self.NATIVE_VXML:
            return []

    def get_path_for_client(self, client):
        """Returns a string representing the path to the preprod project"""
        if self.application_type == self.PRODUCER:
            return self.TUVOX_ROOT + client
        elif self.application_type == self.NATIVE_VXML:
            return ''

    def get_applications_for_client(self, client):
        """Returns a list of application directories for the specified client on this server"""
        if self.application_type == self.PRODUCER:
            with pysftp.Connection(self.address, username=self.account, private_key=settings.PRIVATE_KEY) as conn:
                return conn.listdir(remotepath=self.TUVOX_ROOT + client)
        elif self.application_type == self.NATIVE_VXML:
            return []

    def get_wavs_from_apps(self, client, apps):
        """
        Returns a dict of languages and files for specified applications in client directory

        Returns a defaultdict(list) where the keys are the languages found and the value is a list of files
        """
        WavFile = namedtuple('WavFile', ['md5sum', 'filename'])
        if self.application_type == self.PRODUCER:
            files = defaultdict(list)
            with pysftp.Connection(self.address, username=self.account, private_key=settings.PRIVATE_KEY) as conn:
                for app in apps:
                    try:
                        dirs = conn.listdir(remotepath=os.path.join(self.TUVOX_ROOT, client, app))
                        latest_date = 0
                        latest_dir = ''
                        for dir in dirs:
                            if dir.startswith("External_Resources_2"):
                                current_dir_date = int(dir.split('_')[-1])
                                if current_dir_date > latest_date:
                                    latest_date = current_dir_date
                                    latest_dir = dir
                        voice_root = os.path.join(self.TUVOX_ROOT, client, app, latest_dir, 'voice')
                        language_candidates = conn.listdir(remotepath=voice_root)

                        for entry in language_candidates:
                            if conn.isdir(os.path.join(voice_root, entry)):

                                to_split = conn.execute(
                                    "find " + os.path.join(voice_root, entry) + ' -name "*.wav" -exec md5sum {} \;')
                                for f in to_split:
                                    try:
                                        md5sum, filename = f.split(None, 1)
                                        files[entry].append(WavFile(md5sum, filename.strip()))
                                    except TypeError:
                                        print 'Error: ' + repr(f.split(None, 1))

                    except IOError as e:
                        if str(e) == "[Errno 2] No such file":
                            print "No voice dir in " + app
                            continue
                        else:
                            raise e
            return files
        elif self.application_type == self.NATIVE_VXML:
            raise NotImplementedError


class QEIUser(models.Model):
    user = models.OneToOneField(User)
    creative_services = models.BooleanField(default=False)
    project_manager = models.BooleanField(default=False)