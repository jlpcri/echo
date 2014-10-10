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

    name = models.TextField(unique=True, blank=False)
    address = models.TextField(blank=False)
    account = models.TextField(blank=False)
    application_type = models.PositiveSmallIntegerField(choices=APPLICATION_TYPE_CHOICES)

    def __unicode__(self):
        return self.name