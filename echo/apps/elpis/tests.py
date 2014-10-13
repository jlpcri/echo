from django import test
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from echo.apps.projects.models import Project

User = get_user_model()

class TestSetServerView(test.TestCase):
    def setUp(self):
        self.client = test.Client()
        User.objects.create_user(username='test_user', password='test')
        Project.objects.create(name='Test Project',)
        self.client.login(username='test_user', password='test')
        self.url = reverse('elpis:set_server', args=(1,))

    def test_dashboard_load(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_matching_confirm_screen(self):
        response = self.client.post(self.url, {})
        self.assertTrue(False)

    def test_match_disconfirm(self):
        self.assertTrue(False)

    def test_match_confirmed(self):
        self.assertTrue(False)

    def test_project_select_screen(self):
        self.assertTrue(False)

class TestVerifyView(test.TestCase):
    def setUp(self):
        self.client = test.Client()
        User.objects.create_user(username='test_user', password='test')
        Project.objects.create(name='Test Project',)
        self.client.login(username='test_user', password='test')
        self.url = reverse('elpis:verify', args=(1,))

    def test_verify_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)