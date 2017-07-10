from collections import defaultdict
from datetime import datetime, timedelta
import time
import os
import uuid

import pysftp

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db import connection

from echo.apps.activity.models import Action


def vuid_location(instance, filename):
    return "{0}_{1}".format(str(time.time()).replace('.', ''), filename)


class Project(models.Model):
    """Contains data regarding testing and the Bravo server in use"""
    INITIAL = 'Initial'
    TESTING = 'Testing'
    CLOSED = 'Closed'
    PROJECT_STATUS_CHOICES = ((INITIAL, 'Initial'), (TESTING, 'Testing'), (CLOSED, 'Closed'))
    name = models.TextField(unique=True)
    users = models.ManyToManyField(User, blank=True)
    tests_run = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    bravo_server = models.ForeignKey('settings.Server', blank=True, null=True, on_delete=models.SET_NULL)
    root_path = models.TextField(blank=True, null=True)
    preprod_server = models.ForeignKey('settings.PreprodServer', blank=True, null=True, on_delete=models.SET_NULL)
    preprod_path = models.TextField(blank=True, null=True)
    status = models.TextField(choices=PROJECT_STATUS_CHOICES, default=INITIAL)
    rollback_flag = models.BooleanField(default=False)
    jira_key = models.CharField(max_length=12, blank=True)

    def __unicode__(self):
        return self.name

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

    def slots_passed_and_failed(self):
        return self.voiceslots().filter(status=VoiceSlot.PASS).count() + self.voiceslots().filter(status=VoiceSlot.FAIL).count()

    def slots_ready(self):
        """
        Returns count of voiceslots in "Ready" status

        Primarily a convenience method for templates
        """
        return self.voiceslots().filter(status=VoiceSlot.READY).count()

    def slots_ready_percent(self):
        """
        Percent of voiceslots in "Ready" status

        Controls width of progress bars
        """
        if self.slots_total() != 0:
            return float(self.slots_ready()) / self.slots_total() * 100
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
        """
        Returns count of voiceslots in "New" status

        Primarily a convenience method for templates
        """
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
                a = Action.objects.filter(scope__voiceslot=slot, type=Action.TESTER_PASS_SLOT).order_by('-time')[0]
                Action.log(a.actor, Action.AUTO_PASS_SLOT, 'Slot passed as identical to {0}'.format(slot.name), s)

            elif s.status == VoiceSlot.FAIL:
                a = Action.objects.filter(scope__voiceslot=slot, type=Action.TESTER_FAIL_SLOT).order_by('-time')[0]
                Action.log(a.actor,
                           Action.AUTO_FAIL_SLOT,
                           u'{0} (duplicate of {1})'.format(a.description, a.scope.voiceslot.name),
                           s)
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

    def created_date(self):
        vuids = VUID.objects.filter(project=self)
        if vuids.count() == 1:
            upload_date = vuids[0].upload_date
        elif vuids.count() > 1:
            upload_date = vuids[0].upload_date
            for vuid in vuids:
                if vuid.upload_date < upload_date:
                    upload_date = vuid.upload_date
        else:
            upload_date = None

        return upload_date

    def last_modified_date(self):
        if self.actions().count() > 0:
            return self.actions().latest('time').time
        else:
            return None

    def update_file_status_last_time(self):
        return self.actions().filter(type=Action.UPDATE_FILE_STATUSES).latest('time').time

    def status_as_of(self, timestamp):
        """Based on actions, determine the status of voiceslots on this project as of the passed timestamp"""
        timestamp = int(timestamp)  # Protection against SQL injection
        query = """select action.type, count(action.voiceslot_id) from
            (
            select scope.voiceslot_id, action.time as time, action.type
            from activity_scope as scope
            inner join activity_action as action
            on action.scope_id = scope.id
            where scope.project_id = {0}
            and action.type in (1, 2, 3, 4, 5, 6)
            ) as action
            inner join
            (
            select scope.voiceslot_id, max(action.time) as time
            from activity_scope as scope
            inner join activity_action as action
            on action.scope_id = scope.id
            where scope.project_id = {0}
            and action.type in (1, 2, 3, 4, 5, 6)
            and action.time < (timestamp 'epoch' + {1} * interval '1 second')
            group by scope.voiceslot_id) as max
            on action.voiceslot_id = max.voiceslot_id
            and action.time = max.time
            group by action.type
            order by action.type;""".format(self.id, timestamp)
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        dict_result = defaultdict(int)
        for row in result:
            dict_result[row[0]] = row[1]
        return dict_result


class VoiceSlot(models.Model):
    """Represents a .wav file and its associated verbiage and testing status"""
    NEW = 'New'
    READY = 'Ready'
    PASS = 'Pass'
    FAIL = 'Fail'
    MISSING = 'Missing'
    VOICESLOT_STATUS_CHOICES = ((NEW, 'New'), (READY, 'Ready'), (PASS, 'Pass'),
                                (FAIL, 'Fail'), (MISSING, 'Missing'))
    vuid = models.ForeignKey('VUID', null=True, on_delete=models.SET_NULL)
    vuid_initial = models.IntegerField(null=True, blank=True)
    vuid_previous = models.IntegerField(null=True, blank=True)
    language = models.ForeignKey('Language')
    name = models.TextField()
    path = models.TextField()
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    status = models.TextField(choices=VOICESLOT_STATUS_CHOICES, default=NEW)
    verbiage = models.TextField(blank=True, null=True)
    verbiage_previous = models.TextField(blank=True, null=True, default="")
    checked_out = models.BooleanField(default=False)
    checked_out_time = models.DateTimeField(blank=True, null=True)
    bravo_checksum = models.TextField(blank=True, null=True, default="")
    bravo_time = models.DateTimeField(blank=True, null=True)
    vuid_time = models.DateField(blank=True, null=True)
    vuid_time_previous = models.DateField(blank=True, null=True)
    check_in_time = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return '{0}: {1}'.format(self.name, self.language.project.name)

    def check_in(self, user, forced=False):
        if self.checked_out is True:
            self.checked_out = False
            self.check_in_time = datetime.now()
            self.user = None
            self.save()

    def check_out(self, user, forced=False):
        if self.checked_out is False:
            self.checked_out = True
            self.checked_out_time = datetime.now()
            self.user = user
            self.save()

    def filepath(self):
        return "{0}/{1}.wav".format(self.path, self.name)

    def history_list(self):
        return Action.objects.filter(scope__voiceslot=self)

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
            last_modified = int(conn.execute('stat -c %Y {0}'.format(remote_path.replace('(', r'\(').replace(')', r'\)')))[0])
        return filepath


class VUID(models.Model):
    """Represents the uploaded file used to generate VoiceSlot object"""
    project = models.ForeignKey('Project')
    filename = models.TextField()
    upload_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=vuid_location)
    upload_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return '{0}: {1}'.format(self.filename, self.project.name)


class Language(models.Model):
    """Represents an available language in one project"""
    project = models.ForeignKey('Project')
    name = models.TextField()

    def voiceslot_count(self):
        return VoiceSlot.objects.filter(language=self).count()

    def voiceslots(self):
        return VoiceSlot.objects.filter(language=self)

    def voiceslot_missing(self):
        return VoiceSlot.objects.filter(language=self, status=VoiceSlot.MISSING).count()

    def voiceslot_defective(self):
        return VoiceSlot.objects.filter(language=self, status=VoiceSlot.FAIL).count()

    def __unicode__(self):
        return '{0}: {1}'.format(self.name, self.project.name)


class UpdateStatus(models.Model):
    project = models.ForeignKey('projects.Project')
    last_run = models.DateTimeField(auto_now=True)
    running = models.BooleanField(default=False)
    query_id = models.TextField(default='')

    def __unicode__(self):
        return '{0}: {1}'.format(self.project.name, self.running)
