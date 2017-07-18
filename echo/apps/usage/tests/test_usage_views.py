from django.test import Client, TestCase
from django.core.urlresolvers import reverse, resolve
from django.contrib.auth.models import User

from echo.apps.projects.models import Project
from echo.apps.usage.views import project, projects, user, users, usage


class UsageViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.project = Project.objects.create(name='Usage Project')

        self.user_account_staffuser = {
            'username': 'staffUserName',
            'password': 'staffUserPassword'
        }

        self.user_staffuser = User.objects.create(
            username=self.user_account_staffuser['username'],
            password=self.user_account_staffuser['password'],
            is_staff=True
        )

        self.client.login(
            username=self.user_account_staffuser['username'],
            password=self.user_account_staffuser['password']
        )

        self.url_project = reverse('usage:project', args=[self.project.id, ])
        self.url_projects = reverse('usage:projects')
        self.url_user = reverse('usage:user', args=[self.user_staffuser.id, ])
        self.url_users = reverse('usage:users')
        self.url_usage = reverse('usage:usage')

    def test_projects_url_resolve_to_view(self):
        found = resolve(self.url_projects)
        self.assertEqual(found.func, projects)

    def test_projects_url_returns_200(self):
        response = self.client.get(self.url_projects, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_project_url_resolve_to_view(self):
        found = resolve(self.url_project)
        self.assertEqual(found.func, project)

    def test_project_url_returns_200(self):
        response = self.client.get(self.url_project, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_users_url_resolve_to_view(self):
        found = resolve(self.url_users)
        self.assertEqual(found.func, users)

    def test_users_url_returns_200(self):
        response = self.client.get(self.url_users, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_user_url_resolve_to_view(self):
        found = resolve(self.url_user)
        self.assertEqual(found.func, user)

    def test_user_url_returns_200(self):
        response = self.client.get(self.url_user, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_usage_url_resolve_to_view(self):
        found = resolve(self.url_usage)
        self.assertEqual(found.func, usage)

    def test_usage_url_returns_200(self):
        response = self.client.get(self.url_usage, follow=True)
        self.assertEqual(response.status_code, 200)

