from django.test import TestCase

from django.contrib.auth import get_user_model

from echo.apps.projects.models import Project, Language, VoiceSlot, VUID
from echo.apps.activity.models import Action

User = get_user_model()


class ReportsViewsTests(TestCase):
    def setUp(self):
        User.objects.create_user(username='test_user', password='test')
        Project.objects.create(name='Test Project')
        VUID.objects.create(filename='hi.xlsx',
                            project=Project.objects.first(),
                            upload_by=User.objects.first(),
                            upload_date='2014-11-05')
        Language.objects.create(name='Pig Latin', project=Project.objects.first())
        VoiceSlot.objects.create(name='greeting.wav', path='/voice/audio/testproject',
                                 language=Language.objects.first(), vuid=VUID.objects.first())

    def test_project_voiceslots_missing(self):
        user = User.objects.first()
        Action.log(user, Action.TESTER_PASS_SLOT, u"'sup?", VoiceSlot.objects.first())
        a = Action.objects.get(description=u"'sup?")
        print a
        print a.scope.language.name
        print a.scope.project.name
        print a.scope.project.vuid_set.all()[0].upload_date
        self.assertEqual(a.scope.voiceslot, VoiceSlot.objects.first())
        self.assertEqual(a.scope.language, Language.objects.first())
        self.assertEqual(a.scope.project, Project.objects.first())
