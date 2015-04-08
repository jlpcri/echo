import json

from django.test import Client, TestCase
from django.core.urlresolvers import reverse, resolve
from django.contrib.auth.models import User

from echo.apps.projects.models import Project
from echo.apps.projects.views import certify, projects
from echo.apps.settings.models import UserSettings


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
        self.assertEqual(json.loads(response.content)['reason'], 'Project not initial')
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
        self.assertEqual(json.loads(response.content)['reason'], 'Project not initial')
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
        self.assertEqual(json.loads(response.content)['reason'], 'Project not initial')
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


