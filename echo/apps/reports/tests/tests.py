from django.test import Client, TestCase
from django.core.urlresolvers import resolve, reverse

from django.contrib.auth import get_user_model

from echo.apps.projects.models import Project, Language, VoiceSlot, VUID
from echo.apps.activity.models import Action
from echo.apps.reports.views import report_project

User = get_user_model()


class ReportsViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_accout = {
            'username': 'test_user',
            'password': 'test'
        }

        self.user = User.objects.create_user(username=self.user_accout['username'],
                                             password=self.user_accout['password'])
        self.client.login(
            username=self.user_accout['username'],
            password=self.user_accout['password']
        )
        self.project = Project.objects.create(name='Test Project')
        self.vuid = VUID.objects.create(filename='hi.xlsx',
                                        project=self.project,
                                        upload_by=self.user)
        self.language = Language.objects.create(name='Pig Latin',
                                                project=self.project)
        self.voiceslot = VoiceSlot.objects.create(name='greeting.wav',
                                                  path='/voice/audio/testproject',
                                                  language=self.language,
                                                  vuid=self.vuid)

    def test_project_report_url_resolve_to_view(self):
        found = resolve(reverse('reports:report_project',
                                args=[self.project.id, ]))
        self.assertEqual(found.func, report_project)

    def test_project_voiceslots_pass(self):
        Action.log(self.user,
                   Action.AUTO_PASS_SLOT,
                   u"'sup?",
                   self.voiceslot)
        self.action = Action.objects.get(actor=self.user)
        print 'test: ', self.action.time.date()

        response = self.client.get(reverse('reports:report_project',
                                           args=[self.project.id, ]),)

        #print self.vuid.upload_date
        #print response

        self.assertContains(response, 'pass : 1')
