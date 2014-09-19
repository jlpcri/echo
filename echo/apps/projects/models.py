import datetime
import time
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


def vuid_location(instance, filename):
    return '/'.join(["vuids", "{0}_{1}".format(str(time.time()), filename)])


class Project(models.Model):
    """Contains data regarding testing and the Bravo server in use"""
    TESTING = 'Testing'
    CLOSED = 'Closed'
    PROJECT_STATUS_CHOICES = ((TESTING, 'Testing'), (CLOSED, 'Closed'))
    name = models.TextField(unique=True)
    users = models.ManyToManyField(User, blank=True)
    tests_run = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    bravo_server = models.ForeignKey('settings.Server', blank=True, null=True)
    status = models.TextField(choices=PROJECT_STATUS_CHOICES, default=TESTING)

    def current_server_pk(self):
        return self.bravo_server.pk if self.bravo_server else 0

    def language_list(self):
        return [i.name.lower() for i in Language.objects.filter(project=self)]

    def slots_failed(self):
        return self.voiceslots().filter(status=VoiceSlot.FAIL).count()

    def slots_failed_percent(self):
        if self.slots_total() != 0:
            return float(self.slots_failed()) / self.slots_total() * 100
        else:
            return 0

    def slots_missing(self):
        return self.voiceslots().filter(status=VoiceSlot.MISSING).count()

    def slots_missing_percent(self):
        if self.slots_total() != 0:
            return float(self.slots_missing()) / self.slots_total() * 100
        else:
            return 0

    def slots_passed(self):
        return self.voiceslots().filter(status=VoiceSlot.PASS).count()

    def slots_passed_percent(self):
        if self.slots_total() != 0:
            return float(self.slots_passed()) / self.slots_total() * 100
        else:
            return 0

    def slots_tested(self):
        return self.voiceslots().filter(status__in=(VoiceSlot.PASS, VoiceSlot.FAIL)).count()

    def slots_tested_percent(self):
        if self.slots_total() != 0:
            return float(self.slots_tested()) / self.slots_total() * 100
        else:
            return 0

    def slots_total(self):
        return self.voiceslots().count()

    def slots_untested_percent(self):
        return 100 - self.slots_tested()

    def usernames(self):
        return [u.username for u in self.users.all()]

    def users_total(self):
        return self.users.count()

    def voiceslot_count(self):
        return VoiceSlot.objects.filter(language__project=self).count()

    def voiceslots(self, filter_language=None, filter_status=None):
        vs = VoiceSlot.objects.filter(language__project=self)
        if filter_language:
            vs = vs.filter(language=Language.objects.filter(name__iexact=filter_language))
            print vs
        if filter_status == VoiceSlot.FAIL:
            vs = vs.filter(status__in=(VoiceSlot.FAIL, VoiceSlot.MISSING))
        if filter_status == VoiceSlot.MISSING:
            vs = vs.filter(status=VoiceSlot.MISSING)
        return vs

    def voiceslots_failed(self):
        return self.voiceslots(filter_status=VoiceSlot.FAIL)

    def voiceslots_missing(self):
        return self.voiceslots(filter_status=VoiceSlot.MISSING)


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

    def check_in(self, user, forced=False):
        if self.checked_out is True:
            self.checked_out = False
            self.check_in_time = datetime.datetime.now()
            self.user = user
            if forced:
                self.history = u"Forced check in by {0} at {1}\n".format(self.user, self.check_in_time.strftime("%b %d %Y, %H:%M")) + self.history
            else:
                self.history = u"Checked in by {0} at {1}\n".format(self.user, self.check_in_time.strftime("%b %d %Y, %H:%M")) + self.history
            self.save()

    def check_out(self, user, forced=False):
        if self.checked_out is False:
            self.checked_out = True
            self.checked_out_time = datetime.datetime.now()
            self.user = user
            if forced:
                self.history = u"Forced check out by {0} at {1}\n".format(self.user, self.checked_out_time.strftime("%b %d %Y, %H:%M")) + self.history
            else:
                self.history = u"Checked out by {0} at {1}\n".format(self.user, self.checked_out_time.strftime("%b %d %Y, %H:%M")) + self.history
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
    file = models.FileField(upload_to=vuid_location)
    upload_by = models.ForeignKey(User)


class Language(models.Model):
    """Represents an available language in one project"""
    project = models.ForeignKey('Project')
    name = models.TextField()

    def voiceslot_count(self):
        return VoiceSlot.objects.filter(language=self).count()

    def voiceslots(self):
        return VoiceSlot.objects.filter(language=self)