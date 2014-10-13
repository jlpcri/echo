import os

import pysftp

from django.db import models


class Server(models.Model):
    """Bravo or similar server for hosting .wav files after recording"""
    name = models.TextField(unique=True, blank=False)
    address = models.TextField(blank=False)
    account = models.TextField(blank=False)

    def __unicode__(self):
        return self.name


class PreprodServer(models.Model):
    """Server to host .wav files for playback on preprod IVR"""
    PRODUCER = 1
    NATIVE_VXML = 2
    APPLICATION_TYPE_CHOICES = ((PRODUCER, "Producer"), (NATIVE_VXML, "Native VXML"))
    TUVOX_ROOT = '/usr/local/tuvox/public/Projects/'

    name = models.TextField(unique=True, blank=False)
    address = models.TextField(blank=False)
    account = models.TextField(blank=False)
    application_type = models.PositiveSmallIntegerField(choices=APPLICATION_TYPE_CHOICES)

    def __unicode__(self):
        return self.name

    def get_clients(self):
        """Fetch list of project/client directories from preprod server file system"""
        if self.application_type == self.PRODUCER:
            with pysftp.Connection(self.address, username=self.account) as conn:
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
        if self.application_type == self.PRODUCER:
            with pysftp.Connection(self.address, username=self.account) as conn:
                return conn.listdir(remotepath=self.TUVOX_ROOT + client)
        elif self.application_type == self.NATIVE_VXML:
            return []

    def get_wavs_from_apps(self, client, apps):
        if self.application_type == self.PRODUCER:
            files = []
            with pysftp.Connection(self.address, username=self.account) as conn:
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
                        languages = conn.listdir(remotepath=os.path.join(self.TUVOX_ROOT, client, app, latest_dir, 'voice'))
                        print languages
                    except IOError as e:
                        if str(e) == "[Errno 2] No such file":
                            print "No voice dir in " + app
                            continue
                        else:
                            raise e

            return files