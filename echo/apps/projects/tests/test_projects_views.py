from django.test import Client, TestCase
from django.core.urlresolvers import reverse, resolve
from django.contrib.auth.models import User

from echo.apps.projects.models import Project
from echo.apps.projects.views import certify, projects
from echo.apps.settings.models import UserSettings


class TestViewCertify(TestCase):
    def setUp(self):
        self.client = Client()
        self.project = Project.objects.create(name='Test Project')
        self.url = reverse('projects:certify', args=(self.project.pk, ))
        self.user = {
            'username': 'TestUsername',
            'password': 'TestPassword',
        }
        User.objects.create_user(username=self.user['username'], password=self.user['password'], email='')
        self.client.login(
            username=self.user['username'],
            password=self.user['password']
        )

    def test_certify_url_resolve_to_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func, certify)

    def test_get_certify_url_as_user_returns_404(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)


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


