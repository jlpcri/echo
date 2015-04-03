from django.test import Client, TestCase
from django.core.urlresolvers import reverse, resolve
from django.contrib.auth.models import User

from echo.apps.projects.models import Project
from echo.apps.projects.views import projects


class ProjectsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url_projects = reverse('projects:projects')

        self.project1 = Project.objects.create(name='Test Project 1')
        self.project2 = Project.objects.create(name='Test Project 2')

    def test_projects_url_resolve_to_view(self):
        found = resolve(self.url_projects)
        self.assertEqual(found.func, projects)

    def test_projects_url_return_200(self):
        response = self.client.get(self.url_projects, follow=True)
        self.assertEqual(response.status_code, 200)
