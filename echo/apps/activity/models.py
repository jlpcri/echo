from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Scope(models.Model):
    """Defines project objects impacted by Action"""
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
    project = models.ForeignKey('projects.Project', blank=True, null=True)
    language = models.ForeignKey('projects.Language', blank=True, null=True)
    voiceslot = models.ForeignKey('projects.VoiceSlot', blank=True, null=True)

    def __unicode__(self):
        if self.scope == self.UNIVERSAL:
            return u'Universal'
        elif self.scope == self.PROJECT:
            return u'Project ' + self.project.name
        elif self.scope == self.LANGUAGE:
            return self.language.name + u' ' + self.project.name
        return u'{0} in {1} {2}'.format(self.voiceslot.name, self.language.name, self.project.name)


class Action(models.Model):
    """Entry for activity feed"""
    TESTER_PASS_SLOT = 1
    TESTER_FAIL_SLOT = 2
    AUTO_NEW_SLOT = 3
    AUTO_PASS_SLOT = 4
    AUTO_FAIL_SLOT = 5
    AUTO_MISSING_SLOT = 6
    UPLOAD_VUID = 7
    UPDATE_FILE_STATUSES = 8
    CREATE_PROJECT = 9
    REPORT_GENERATION = 10
    ELPIS_RUN = 11
    UPDATE_ROOT_PATH = 12
    UPDATE_BRAVO_SERVER = 13
    TESTER_JOIN_PROJECT = 14
    TESTER_LEAVE_PROJECT = 15
    ARCHIVE_PROJECT = 16
    UN_ARCHIVE_PROJECT = 17
    TYPE_CHOICES = (
        (TESTER_PASS_SLOT, 'Tester passed slot'),
        (TESTER_FAIL_SLOT, 'Tester failed slot'),
        (AUTO_NEW_SLOT, 'Automatically marked slot for testing'),
        (AUTO_PASS_SLOT, 'Automatically passed slot'),
        (AUTO_FAIL_SLOT, 'Automatically failed slot'),
        (AUTO_MISSING_SLOT, 'Automatically marked slot as missing'),
        (UPLOAD_VUID, 'Prompt list upload'),
        (UPDATE_FILE_STATUSES, 'Ran file status update'),
        (CREATE_PROJECT, 'Project created'),
        (REPORT_GENERATION, 'Report generated'),
        (ELPIS_RUN, 'Elpis run'),
        (UPDATE_ROOT_PATH, 'Project root path updated'),
        (UPDATE_BRAVO_SERVER, 'Bravo server changed'),
        (TESTER_JOIN_PROJECT, 'Tester joined project'),
        (TESTER_LEAVE_PROJECT, 'Tester left project'),
        (ARCHIVE_PROJECT, 'Archive project'),
        (UN_ARCHIVE_PROJECT, 'Un archive project')
    )

    actor = models.ForeignKey(User)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, blank=False, null=False)
    description = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    scope = models.ForeignKey(Scope)

    def __unicode__(self):
        return u'{0} on {1}'.format(self.description, self.time.strftime("%c"))

    @classmethod
    def log(cls, actor, action_type, description, scope=None):
        """Convenience method to create Action items"""
        SLOT_TYPES = (cls.TESTER_PASS_SLOT,
                      cls.TESTER_FAIL_SLOT,
                      cls.AUTO_PASS_SLOT,
                      cls.AUTO_FAIL_SLOT,
                      cls.AUTO_MISSING_SLOT,
                      cls.AUTO_NEW_SLOT)
        LANGUAGE_TYPES = (cls.REPORT_GENERATION, )
        PROJECT_TYPES = (cls.UPLOAD_VUID, cls.UPDATE_FILE_STATUSES, cls.CREATE_PROJECT, cls.REPORT_GENERATION,
                         cls.ELPIS_RUN, cls.UPDATE_ROOT_PATH, cls.UPDATE_BRAVO_SERVER, cls.TESTER_JOIN_PROJECT,
                         cls.TESTER_LEAVE_PROJECT, cls.ARCHIVE_PROJECT, cls.UN_ARCHIVE_PROJECT)
        UNIVERSAL_TYPES = ()

        from echo.apps.projects.models import VoiceSlot, Language, Project

        if scope is None:
            if action_type not in UNIVERSAL_TYPES:
                raise ValueError('Invalid action type for given scope')
            sc = Scope.objects.create(scope=Scope.UNIVERSAL, project=None, language=None, voiceslot=None)
        elif type(scope) is Project:
            if action_type not in PROJECT_TYPES:
                raise ValueError('Invalid action type for given scope')
            sc = Scope.objects.create(scope=Scope.PROJECT, project=scope, language=None, voiceslot=None)
        elif type(scope) is Language:
            if action_type not in LANGUAGE_TYPES:
                raise ValueError('Invalid action type for given scope')
            sc = Scope.objects.create(scope=Scope.PROJECT, project=scope.project, language=scope, voiceslot=None)
        elif type(scope) is VoiceSlot:
            if action_type not in SLOT_TYPES:
                raise ValueError('Invalid action type for given scope')
            sc = Scope.objects.create(scope=Scope.PROJECT, project=scope.language.project, language=scope.language,
                                      voiceslot=scope)
        else:
            raise ValueError('Invalid scope object')
        cls.objects.create(actor=actor, type=action_type, description=description, scope=sc)

