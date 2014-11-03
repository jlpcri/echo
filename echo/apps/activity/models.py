from django.db import models
from django.contrib.auth import get_user_model

from echo.apps.projects.models import VoiceSlot, Language, Project

User = get_user_model()

class Action(models.Model):
    TESTER_PASS_SLOT = 1
    TESTER_FAIL_SLOT = 2
    AUTO_PASS_SLOT = 3
    AUTO_FAIL_SLOT = 4
    UPLOAD_VUID = 5
    UPDATE_FILE_STATUSES = 6
    CREATE_PROJECT = 7
    REPORT_GENERATION = 8
    ELPIS_RUN = 9
    UPDATE_ROOT_PATH = 10
    UPDATE_BRAVO_SERVER = 11
    TESTER_JOIN_PROJECT = 12
    TESTER_LEAVE_PROJECT = 13
    TYPE_CHOICES = (
        (TESTER_PASS_SLOT, 'Tester passed slot'),
        (TESTER_FAIL_SLOT, 'Tester failed slot'),
        (AUTO_PASS_SLOT, 'Automatically passed slot'),
        (AUTO_FAIL_SLOT, 'Automatically failed slot'),
        (UPLOAD_VUID, 'Prompt list upload'),
        (UPDATE_FILE_STATUSES, 'Ran file status update'),
        (CREATE_PROJECT, 'Project created'),
        (REPORT_GENERATION, 'Report generated'),
        (ELPIS_RUN, 'Elpis run'),
        (UPDATE_ROOT_PATH, 'Project root path updated'),
        (UPDATE_BRAVO_SERVER, 'Bravo server changed'),
        (TESTER_JOIN_PROJECT, 'Tester joined project'),
        (TESTER_LEAVE_PROJECT, 'Tester left project')
    )

    actor = models.ForeignKey(User)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
    description = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    scope = models.ForeignKey(Scope)


class Scope(models.Model):
    UNIVERSAL = 1
    PROJECT = 2
    LANGUAGE = 3
    VOICESLOT = 4
    SCOPE_CHOICES = (
        (UNIVERSAL, 'Universal'),
        (PROJECT, 'Project'),
        (LANGUAGE, 'Language'),
        (VOICESLOT, 'Voice slot')
    )

    scope = models.PositiveSmallIntegerField(choices=SCOPE_CHOICES)
    project = models.ForeignKey(Project, blank=True, null=True)
    language = models.ForeignKey(Language, blank=True, null=True)
    voiceslot = models.ForeignKey(VoiceSlot, blank=True, null=True)