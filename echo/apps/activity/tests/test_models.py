from django import test
from django.contrib.auth import get_user_model

from echo.apps.projects.models import Project, Language, VoiceSlot
from echo.apps.activity.models import Action

User = get_user_model()

class TestActionLogging(test.TestCase):
    def setUp(self):
        User.objects.create_user(username='test_user', password='test')
        Project.objects.create(name='Test Project')
        Language.objects.create(name='Pig Latin', project=Project.objects.first())
        VoiceSlot.objects.create(name='greeting.wav', path='/voice/audio/testproject', language=Language.objects.first())

    def test_voiceslot_action_success(self):
        user = User.objects.first()
        Action.log(user, Action.TESTER_PASS_SLOT, u"'sup?", VoiceSlot.objects.first())
        a = Action.objects.get(description=u"'sup?")
        self.assertEqual(a.scope.voiceslot, VoiceSlot.objects.first())
        self.assertEqual(a.scope.language, Language.objects.first())
        self.assertEqual(a.scope.project, Project.objects.first())