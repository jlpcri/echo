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
        self.voiceslot = VoiceSlot.objects.create(name='greeting',
                                                  path='/voice/audio/testproject',
                                                  language=self.language,
                                                  vuid=self.vuid)
        self.voiceslot_missing = VoiceSlot.objects.create(name='missing',
                                                          path='/voice/audio/testproject',
                                                          language=self.language,
                                                          vuid=self.vuid,
                                                          status=VoiceSlot.MISSING)
        self.voiceslot_fail = VoiceSlot.objects.create(name='fail',
                                                       path='/voice/audio/testproject',
                                                       language=self.language,
                                                       vuid=self.vuid,
                                                       status=VoiceSlot.FAIL)
        self.description = 'Action Description notes'

    def test_project_report_url_resolve_to_view(self):
        found = resolve(reverse('reports:report_project',
                                args=[self.project.id, ]))
        self.assertEqual(found.func, report_project)

    def test_project_progress_voiceslots_auto_pass(self):
        Action.log(self.user,
                   Action.AUTO_PASS_SLOT,
                   self.description,
                   self.voiceslot)
        self.action = Action.objects.get(actor=self.user)

        response = self.client.get(reverse('reports:report_project',
                                           args=[self.project.id, ]),
                                   follow=True)

        self.assertEqual(response.status_code, 200)

    def test_project_progress_voiceslots_tester_pass(self):
        Action.log(self.user,
                   Action.TESTER_PASS_SLOT,
                   self.description,
                   self.voiceslot)
        self.action = Action.objects.get(actor=self.user)

        response = self.client.get(reverse('reports:report_project',
                                           args=[self.project.id, ]),
                                   follow=True)

        self.assertEqual(response.status_code, 200)

    def test_project_progress_voiceslots_auto_fail(self):
        Action.log(self.user,
                   Action.AUTO_FAIL_SLOT,
                   self.description,
                   self.voiceslot)
        self.action = Action.objects.get(actor=self.user)

        response = self.client.get(reverse('reports:report_project',
                                           args=[self.project.id, ]),
                                   follow=True)
        self.assertEqual(response.status_code, 200)

    def test_project_progress_voiceslots_tester_fail(self):
        Action.log(self.user,
                   Action.TESTER_FAIL_SLOT,
                   self.description,
                   self.voiceslot)
        self.action = Action.objects.get(actor=self.user)

        response = self.client.get(reverse('reports:report_project',
                                           args=[self.project.id, ]),
                                   follow=True)

        self.assertEqual(response.status_code, 200)

    def test_project_progress_voiceslots_auto_new(self):
        Action.log(self.user,
                   Action.AUTO_NEW_SLOT,
                   self.description,
                   self.voiceslot)
        self.action = Action.objects.get(actor=self.user)

        response = self.client.get(reverse('reports:report_project',
                                           args=[self.project.id, ]),
                                   follow=True)

        self.assertEqual(response.status_code, 200)

    def test_project_progress_voiceslots_auto_missing(self):
        Action.log(self.user,
                   Action.AUTO_MISSING_SLOT,
                   self.description,
                   self.voiceslot)
        self.action = Action.objects.get(actor=self.user)

        response = self.client.get(reverse('reports:report_project',
                                           args=[self.project.id, ]),
                                   follow=True)

        self.assertEqual(response.status_code, 200)

    def test_project_voiceslots_missing(self):
        response = self.client.get(reverse('reports:missing',
                                           args=[self.project.id, ]), )

        self.assertContains(response, self.voiceslot_missing.path + '/' + self.voiceslot_missing.name)

    def test_project_voiceslots_fail(self):
        Action.log(self.user,
                   Action.TESTER_FAIL_SLOT,
                   self.description,
                   self.voiceslot_fail)
        response = self.client.get(reverse('reports:failed',
                                           args=[self.project.id, ]), )

        self.assertContains(response, self.voiceslot_fail.name)
        self.assertContains(response, self.description)

