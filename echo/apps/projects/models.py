from datetime import datetime, timedelta
import time
import os
import uuid

import pysftp

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

from echo.apps.activity.models import Action, Scope

User = get_user_model()


def vuid_location(instance, filename):
    return "{0}_{1}".format(str(time.time()).replace('.', ''), filename)


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
    preprod_server = models.ForeignKey('settings.PreprodServer', blank=True, null=True)
    preprod_path = models.TextField(blank=True, null=True)
    status = models.TextField(choices=PROJECT_STATUS_CHOICES, default=TESTING)

    def current_server_pk(self):
        return self.bravo_server.pk if self.bravo_server else 0

    def get_applications(self):
        return self.preprod_server.get_applications_for_client(self.preprod_client_id)

    def languages(self):
        return Language.objects.filter(project=self)

    def language_list(self):
        return [i.name.lower() for i in Language.objects.filter(project=self)]

    @property
    def preprod_client_id(self):
        return self.preprod_path.split('/')[-1]

    def set_preprod_path(self, client):
        self.preprod_path = self.preprod_server.get_path_for_client(client)
        self.save()

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

    def slots_untested(self):
        return self.voiceslots().filter(status=VoiceSlot.NEW).count()

    def slots_untested_percent(self):
        if self.slots_total() != 0:
            return float(self.slots_untested()) / self.slots_total() * 100
        else:
            return 0

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
        if filter_status == VoiceSlot.FAIL:
            vs = vs.filter(status__in=(VoiceSlot.FAIL, VoiceSlot.MISSING))
        if filter_status == VoiceSlot.MISSING:
            vs = vs.filter(status=VoiceSlot.MISSING)
        return vs

    def voiceslots_match(self, slot, request):
        vs = self.voiceslots().filter(
            verbiage=slot.verbiage, bravo_checksum=slot.bravo_checksum).exclude(
                pk=slot.pk).exclude(
                    status=VoiceSlot.MISSING)
        for s in vs:
            s.status = slot.status
            if s.status == VoiceSlot.PASS:
                s.history = "{0}: Test auto passed at {1}.\n{2}\n".format(request.user.username, datetime.now(),
                                                                         request.POST['notes']) + slot.history
            elif s.status == VoiceSlot.FAIL:
                s.history = "{0}: Test auto failed at {1}.\n{2}\n".format(request.user.username, datetime.now(),
                                                                         request.POST['notes']) + slot.history
            s.save()
        return vs.count()


    def voiceslots_queue(self, checked_out=False, filter_language=None, older_than_ten=False):
        vs = self.voiceslots().filter(checked_out=checked_out, status=VoiceSlot.NEW)
        if filter_language:
            vs = vs.filter(language__name__iexact=filter_language)
        if older_than_ten:
            vs.order_by('checked_out_time')
            time_threshold = datetime.now() - timedelta(minutes=10)
            vs = vs.filter(checked_out_time__gt=time_threshold)
        return vs

    def voiceslots_checked_out_by_user(self, user, filter_language=None):
        vs = self.voiceslots().filter(checked_out=True, user=user)
        if filter_language:
            vs = vs.filter(language__name__iexact=filter_language)
        return vs

    def voiceslots_failed(self):
        return self.voiceslots(filter_status=VoiceSlot.FAIL)

    def voiceslots_missing(self):
        return self.voiceslots(filter_status=VoiceSlot.MISSING)

    def actions(self, filter_status=None):
        actions = Action.objects.filter(scope__project=self)
        if filter_status == VoiceSlot.FAIL:
            actions = actions.filter(type__in=(Action.TESTER_FAIL_SLOT, Action.AUTO_FAIL_SLOT))
        return actions

    def actions_failed(self):
        return self.actions(filter_status=VoiceSlot.FAIL)


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
    bravo_checksum = models.TextField(blank=True, null=True, default="")
    bravo_time = models.DateTimeField(blank=True, null=True)
    vuid_time = models.DateField(blank=True, null=True)
    check_in_time = models.DateTimeField(blank=True, null=True)

    def check_in(self, user, forced=False):
        if self.checked_out is True:
            self.checked_out = False
            self.check_in_time = datetime.now()
            self.user = None
            if forced:
                self.history = "Forced check in by {0} at {1}\n".format(user, self.check_in_time.strftime("%b %d %Y, %H:%M")) + self.history
            else:
                self.history = "Checked in by {0} at {1}\n".format(user, self.check_in_time.strftime("%b %d %Y, %H:%M")) + self.history
            self.save()

    def check_out(self, user, forced=False):
        if self.checked_out is False:
            self.checked_out = True
            self.checked_out_time = datetime.now()
            self.user = user
            if forced:
                self.history = "Forced check out by {0} at {1}\n".format(user, self.checked_out_time.strftime("%b %d %Y, %H:%M")) + self.history
            else:
                self.history = "Checked out by {0} at {1}\n".format(user, self.checked_out_time.strftime("%b %d %Y, %H:%M")) + self.history
            self.save()

    def filepath(self):
        return "{0}/{1}.wav".format(self.path, self.name)

    def history_list(self):
        return [s for s in self.history.split('\n') if len(s) > 0]

    def download(self):
        """Downloads a file from the remote server and returns the path on the local server"""
        p = self.language.project
        with pysftp.Connection(p.bravo_server.address, username=p.bravo_server.account,
                               private_key=settings.PRIVATE_KEY) as conn:
            remote_path = self.filepath()
            filename = "{0}.wav".format(str(uuid.uuid4()))
            local_path = os.path.join(settings.MEDIA_ROOT, filename)
            conn.get(remote_path, local_path)
            filepath = settings.MEDIA_URL + filename
            last_modified = int(conn.execute('stat -c %Y {0}'.format(remote_path))[0])
            self.history = "Downloaded file last modified on {0}\n".format(
                datetime.fromtimestamp(last_modified).strftime("%b %d %Y, %H:%M")) + self.history
        return filepath


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