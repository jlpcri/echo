import json

from django.test import Client, TestCase
from django.core.urlresolvers import reverse, resolve
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from django.core.files.base import ContentFile

from echo.apps.projects.models import Project, VUID, Language, VoiceSlot
from echo.apps.projects.views import certify, projects
from echo.apps.settings.models import UserSettings
from echo.apps.projects import helpers

from openpyxl import Workbook

class TestViewCertify(TestCase):
    """
    Tests projects.views.certify
    """
    def setUp(self):
        self.client = Client()
        self.project = Project.objects.create(name='Test Project')
        self.url = reverse('projects:certify', args=(self.project.pk, ))
        self.credentials = {
            'username': 'TestUsername',
            'password': 'TestPassword',
        }
        self.user = User.objects.create_user(username=self.credentials['username'], password=self.credentials['password'], email='')
        self.client.login(
            username=self.credentials['username'],
            password=self.credentials['password']
        )
        UserSettings.objects.get_or_create(user=self.user)

    def test_certify_url_resolve_to_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func, certify)

    def test_get_certify_url_as_user_returns_404(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_get_certify_url_as_superuser_returns_404(self):
        self.user.is_superuser = True
        self.user.save()
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.user.is_superuser = False
        self.user.save()

    def test_get_certify_url_as_creative_services_returns_404(self):
        self.user.usersettings.creative_services = True
        self.user.usersettings.save()
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.user.usersettings.creative_services = False
        self.user.usersettings.save()

    def test_get_certify_url_as_project_manager_returns_404(self):
        self.user.usersettings.project_manager = True
        self.user.usersettings.save()
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.user.usersettings.project_manager = False
        self.user.usersettings.save()

    def test_post_certify_url_as_user_returns_success_false(self):
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['success'], False)
        self.assertEqual(json.loads(response.content)['reason'], 'Invalid user permissions')

    def test_post_certify_url_as_superuser_returns_success_false_not_initial(self):
        self.user.is_superuser = True
        self.user.save()
        self.project.status = Project.TESTING
        self.project.save()
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['success'], False)
        self.assertEqual(json.loads(response.content)['reason'], 'Project status is not Initial')
        self.user.is_superuser = False
        self.user.save()

    def test_post_certify_url_as_creative_services_returns_success_false_not_initial(self):
        self.user.usersettings.creative_services = True
        self.user.usersettings.save()
        self.project.status = Project.TESTING
        self.project.save()
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['success'], False)
        self.assertEqual(json.loads(response.content)['reason'], 'Project status is not Initial')
        self.user.usersettings.creative_services = False
        self.user.usersettings.save()

    def test_post_certify_url_as_project_manager_returns_success_false_not_initial(self):
        self.user.usersettings.project_manager = True
        self.user.usersettings.save()
        self.project.status = Project.TESTING
        self.project.save()
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['success'], False)
        self.assertEqual(json.loads(response.content)['reason'], 'Project status is not Initial')
        self.user.usersettings.project_manager = False
        self.user.usersettings.save()

    # def test_post_certify_url_as_superuser_returns_success_false_missing_files(self):
    #     self.user.is_superuser = True
    #     self.user.save()
    #     response = self.client.post(self.url, follow=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(json.loads(response.content)['success'], False)
    #     self.assertEqual(json.loads(response.content)['reason'], 'Project missing files')
    #     self.user.is_superuser = False
    #     self.user.save()
    #
    # def test_post_certify_url_as_creative_services_returns_success_false_missing_files(self):
    #     self.user.usersettings.creative_services = True
    #     self.user.usersettings.save()
    #     response = self.client.post(self.url, follow=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(json.loads(response.content)['success'], False)
    #     self.assertEqual(json.loads(response.content)['reason'], 'Project missing files')
    #     self.user.usersettings.creative_services = False
    #     self.user.usersettings.save()
    #
    # def test_post_certify_url_as_project_manager_returns_success_false_missing_files(self):
    #     self.user.usersettings.project_manager = True
    #     self.user.usersettings.save()
    #     response = self.client.post(self.url, follow=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(json.loads(response.content)['success'], False)
    #     self.assertEqual(json.loads(response.content)['reason'], 'Project missing files')
    #     self.user.usersettings.project_manager = False
    #     self.user.usersettings.save()

    def test_post_certify_url_as_superuser_returns_success_true_sets_testing(self):
        self.user.is_superuser = True
        self.user.save()
        self.project.status = Project.INITIAL
        self.project.save()
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['success'], True)
        p = Project.objects.get(pk=self.project.pk)
        self.assertEqual(p.status, Project.TESTING)
        self.user.is_superuser = False
        self.user.save()

    def test_post_certify_url_as_creative_services_returns_success_true_sets_testing(self):
        self.user.usersettings.creative_services = True
        self.user.usersettings.save()
        self.project.status = Project.INITIAL
        self.project.save()
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['success'], True)
        p = Project.objects.get(pk=self.project.pk)
        self.assertEqual(p.status, Project.TESTING)
        self.user.usersettings.creative_services = False
        self.user.usersettings.save()

    def test_post_certify_url_as_project_manager_returns_success_true_sets_testing(self):
        self.user.usersettings.project_manager = True
        self.user.usersettings.save()
        self.project.status = Project.INITIAL
        self.project.save()
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['success'], True)
        p = Project.objects.get(pk=self.project.pk)
        self.assertEqual(p.status, Project.TESTING)
        self.user.usersettings.project_manager = False
        self.user.usersettings.save()


class ProjectsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url_projects = reverse('projects:projects')

        self.project1 = {
            'name': 'Test Project 1'
        }
        self.project2 = {
            'name': 'Test Project 2'
        }

        self.user_account_superuser = {
            'username': 'superUserName',
            'password': 'superUserPassword'
        }
        self.user_superuser = User.objects.create_superuser(
            username=self.user_account_superuser['username'],
            password=self.user_account_superuser['password'],
            email=''
        )
        self.client.login(
            username=self.user_account_superuser['username'],
            password=self.user_account_superuser['password']
        )


    def test_projects_url_resolve_to_view(self):
        found = resolve(self.url_projects)
        self.assertEqual(found.func, projects)

    def test_projects_url_return_200(self):
        response = self.client.get(self.url_projects, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_projects_views_with_no_projects(self):
        response = self.client.get(self.url_projects, follow=True)
        self.assertContains(response, 'There are no initial projects currently.')
        self.assertQuerysetEqual(response.context['projects'], [])
        self.assertEqual(response.context['tab'], 'csp')
        self.assertEqual(response.context['sort'], 'project_name')

    def test_projects_view_contains_projects_list(self):
        project1 = Project.objects.create(name=self.project1['name'])
        project2 = Project.objects.create(name=self.project2['name'])
        response = self.client.get(self.url_projects)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project1.name)
        self.assertContains(response, project2.name)


class ProjectsViewsFileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url_projects = reverse('projects:projects')

        self.pj1 = {
            'name': 'Test Project 1',
            'root_path' : '/voice/audio/american_express/plenti'
        }

        self.user_account_superuser = {
            'username': 'superUserName',
            'password': 'superUserPassword'
        }
        self.user_superuser = User.objects.create_superuser(
            username=self.user_account_superuser['username'],
            password=self.user_account_superuser['password'],
            email=''
        )
        self.client.login(
            username=self.user_account_superuser['username'],
            password=self.user_account_superuser['password']
        )
        UserSettings.objects.create(user=self.user_superuser)
        excel_data_array = [
            ['Page Name', 'Prompt Name', 'Prompt Text', 'State Name', 'Date Changed'],
            ['Bravo path: /voice/audio/american_express/plenti'],
            ['Welcome', 'Greeting', 'Thank you for calling Plenti.', 'say_Greeting', '10 / 20 / 2014'],
            ['Welcome', 'LanguagePrompt', 'Para Espanol, oprima el numero nueve.', 'prompt_LanguagePrompt',
             '10 / 27 / 2014'],
            ['Welcome', 'LanguagePromptNI1', 'N / A', 'prompt_LanguagePrompt', '10 / 27 / 2014'],
            ['Welcome', 'LanguagePromptNI2', 'N / A', 'prompt_LanguagePrompt', '10 / 27 / 2014'],
            ['Welcome', 'LanguagePromptNM1', 'N / A', 'prompt_LanguagePrompt', '10 / 27 / 2014'],
            ['Welcome', 'LanguagePromptNM2', 'N / A', 'prompt_LanguagePrompt', '10 / 27 / 2014']
        ]
        self.wb1 = Workbook()
        self.wb2 = Workbook()
        self.wb1.name = 'hi'
        self.wb2.name = 'hi.xlsx'
        self.wb1.filename = 'hi'
        self.wb2.filename = 'hi.xlsx'
        self.ws1 = self.wb1.active
        self.ws2 = self.wb2.active
        for line in excel_data_array:
            self.ws1.append(line)
            self.ws2.append(line)
        self.wb1.save(filename='hi')
        self.wb2.save(filename='hi.xlsx')



    def test_projects_upload_no_file(self):
        project = Project.objects.create(name=self.pj1['name'], root_path=self.pj1['root_path'])
        response = self.client.post(reverse('projects:project', kwargs={'pid': project.pk}), {'upload_file': ''},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unable to upload file')

    def test_projects_upload_bad_filename(self):
        project = Project.objects.create(name=self.pj1['name'], root_path=self.pj1['root_path'])
        response = self.client.post(reverse('projects:project', kwargs={'pid': project.pk}),
                                    {'file': open(self.wb1.filename, 'r'),
                                     'upload_file': self.wb1.filename}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid file type, unable to upload')

    def test_projects_upload_valid_script(self):
        project = Project.objects.create(name=self.pj1['name'], root_path=self.pj1['root_path'])
        response = self.client.post(reverse('projects:project', kwargs={'pid': project.pk}),
                                    {'file': open(self.wb2.filename, 'r'),
                                     'upload_file': self.wb2.filename}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'hi.xlsx')
        self.assertContains(response, 'vuidid')

    def test_projects_rollback(self):
        project = Project.objects.create(name=self.pj1['name'], root_path=self.pj1['root_path'])
        response = self.client.post(reverse('projects:project', kwargs={'pid': project.pk}),
                                    {'file': open(self.wb2.filename, 'r'),
                                     'upload_file': self.wb2.filename}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'hi.xlsx')
        response = self.client.post(reverse('projects:rollback_vuid', kwargs={'vuid_id': '1'}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response, 'hi.xlsx')
        self.assertNotEqual(response, 'vuidid')