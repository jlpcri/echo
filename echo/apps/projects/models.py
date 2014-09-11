import datetime
import time
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


def change_filename(instance, filename):
    return '/'.join(['voiceslots', "{0}_{1}".format(str(time.time()), filename)])


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

    def voiceslots(self):
        slots = []
        for l in Language.objects.filter(project=self):
            slots.extend(l.voiceslots())
        return slots

    def voiceslot_count(self):
        languages = Language.objects.filter(project=self)
        count = 0
        for language in languages:
            count += language.voiceslot_count()
        return count


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
    name = models.TextField()
    path = models.TextField()
    user = models.ForeignKey(User, blank=True, null=True)
    history = models.TextField(blank=True, null=True, default="")
    status = models.TextField(choices=VOICESLOT_STATUS_CHOICES, default=NEW)
    verbiage = models.TextField(blank=True, null=True)
    checked_out = models.BooleanField(default=False)
    checked_out_time = models.DateTimeField(blank=True, null=True)
    bravo_time = models.DateTimeField(blank=True, null=True)
    vuid_time = models.DateField(blank=True, null=True)
    check_in_time = models.DateTimeField(blank=True, null=True)

    def check_in(self, user):
        if self.checked_out is True:
            self.checked_out = False
            self.check_in_time = datetime.datetime.now()
            self.user = user
            self.history = "Checked in by {0} at {1}\n".format(self.user, self.check_in_time.strftime("%b %d %Y, %H:%M")) + self.history
            self.save()

    def check_out(self, user):
        if self.checked_out is False:
            self.checked_out = True
            self.checked_out_time = datetime.datetime.now()
            self.user = user
            self.history = "Checked out by {0} at {1}\n".format(self.user, self.checked_out_time.strftime("%b %d %Y, %H:%M")) + self.history
            self.save()

    def filepath(self):
        return "{0}/{1}".format(self.path, self.name)

    def history_list(self):
        return [s for s in self.history.split('\n') if len(s) > 0]


class VUID(models.Model):
    """Represents the uploaded file used to generate VoiceSlot object"""
    project = models.ForeignKey('Project')
    filename = models.TextField()
    upload_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=change_filename)
    upload_by = models.ForeignKey(User)


class Language(models.Model):
    """Represents an available language in one project"""
    project = models.ForeignKey('Project')
    name = models.TextField()

    def voiceslots(self):
        return VoiceSlot.objects.filter(language=self)

    def voiceslot_count(self):
        return len(VoiceSlot.objects.filter(language=self))