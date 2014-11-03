from django.db import models
from django.contrib.auth import get_user_model

from echo.apps.projects.models import VoiceSlot, Language, Project

User = get_user_model()

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
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, blank=False, null=False)
    description = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    scope = models.ForeignKey(Scope)

    @classmethod
    def log(cls, actor, action_type, description, scope=None):
        SLOT_TYPES = (cls.TESTER_PASS_SLOT, cls.TESTER_FAIL_SLOT, cls.AUTO_PASS_SLOT, cls.AUTO_FAIL_SLOT)
        LANGUAGE_TYPES = (cls.REPORT_GENERATION, )
        PROJECT_TYPES = (cls.UPLOAD_VUID, cls.UPDATE_FILE_STATUSES, cls.CREATE_PROJECT, cls.REPORT_GENERATION,
                         cls.ELPIS_RUN, cls.UPDATE_ROOT_PATH, cls.UPDATE_BRAVO_SERVER, cls.TESTER_JOIN_PROJECT,
                         cls.TESTER_LEAVE_PROJECT)
        UNIVERSAL_TYPES = ()

        if scope is None:
            if action_type not in UNIVERSAL_TYPES:
                raise ValueError('Invalid action type for given scope')
            sc = Scope.create(scope=Scope.UNIVERSAL, project=None, language=None, voiceslot=None)
        elif type(scope) is Project:
            if action_type not in PROJECT_TYPES:
                raise ValueError('Invalid action type for given scope')
            sc = Scope.create(scope=Scope.PROJECT, project=scope, language=None, voiceslot=None)
        elif type(scope) is Language:
            if action_type not in LANGUAGE_TYPES:
                raise ValueError('Invalid action type for given scope')
            sc = Scope.create(scope=Scope.PROJECT, project=scope.project, language=scope, voiceslot=None)
        elif type(scope) is VoiceSlot:
            if action_type not in SLOT_TYPES:
                raise ValueError('Invalid action type for given scope')
            sc = Scope.create(scope=Scope.PROJECT, project=scope.language.project, language=scope.language,
                              voiceslot=scope)
        else:
            raise ValueError('Invalid scope object')
        cls.create(actor=actor, type=action_type, description=description, scope=sc)

