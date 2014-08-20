from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Project(models.Model):
    """Contains data regarding testing and the Bravo server in use"""
    TESTING = 'Testing'
    CLOSED = 'Closed'
    BRAVO1137 = 'linux1137.wic.west.com'
    BRAVO4487 = 'linux4487.wic.west.com'
    PROJECT_STATUS_CHOICES = ((TESTING, 'Testing'), (CLOSED, 'Closed'))
    BRAVO_SERVER_CHOICES = ((BRAVO1137, 'linux1137'), (BRAVO4487, 'linux4487'))
    name = models.TextField(unique=True)
    users = models.ManyToManyField(User, blank=True)
    tests_run = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    bravo_server = models.TextField(choices=BRAVO_SERVER_CHOICES, default=BRAVO1137)
    status = models.TextField(choices=PROJECT_STATUS_CHOICES, default=TESTING)


class VoiceSlot(models.Model):
    """Represents a .wav file and its associated verbiage, status, and history"""
    NEW = 'New'
    PASS = 'Pass'
    FAIL = 'Fail'
    MISSING = 'Missing'
    VOICESLOT_STATUS_CHOICES = ((NEW, 'New'), (PASS, 'Pass'),
                                (FAIL, 'Fail'), (MISSING, 'Missing'))
    vuid = models.ForeignKey('VUID')
    language = models.ForeignKey('Language')
    file = models.TextField()
    user = models.ForeignKey(User, blank=True, null=True)
    history = models.TextField(blank=True, null=True, default="")
    status = models.TextField(choices=VOICESLOT_STATUS_CHOICES, default=NEW)
    verbiage = models.TextField()
    checked_out = models.BooleanField(default=False)
    checked_out_time = models.DateTimeField(default=False, blank=True, null=True)
    bravo_time = models.DateTimeField(blank=True, null=True)
    vuid_time = models.DateField()
    check_in_time = models.DateTimeField(blank=True, null=True)


class VUID(models.Model):
    """Represents the uploaded file used to generate VoiceSlot object"""
    project = models.ForeignKey('Project')
    filename = models.TextField()
    upload_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='/voiceslots')
    upload_by = models.ForeignKey(User)


class Language(models.Model):
    """Represents an available language in one project"""
    project = models.ForeignKey('Project')
    name = models.TextField()