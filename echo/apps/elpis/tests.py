import json

from django import test
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from echo.apps.projects.models import Project
from echo.apps.settings.models import Server, PreprodServer

User = get_user_model()

class TestDashboardView(test.TestCase):
    def setUp(self):
        self.client = test.Client()
        User.objects.create_user(username='test_user', password='test')
        self.client.login(username='test_user', password='test')
        self.url = reverse('elpis:dashboard', args=(1,))
        Project.objects.create(name='Test Project')

    def test_dashboard_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class TestSetServerView(test.TestCase):
    def setUp(self):
        self.client = test.Client()
        User.objects.create_user(username='test_user', password='test')

        Server.objects.create(name='Fake Bravo')
        # TODO: Mock preprod servers
        PreprodServer.objects.create(name='linux4095', address='linux4095.wic.west.com', account='wicqacip',
                                     application_type=PreprodServer.PRODUCER)
        PreprodServer.objects.create(name='Prompt Store Placeholder', application_type=PreprodServer.NATIVE_VXML)
        Project.objects.create(name='Test Project', bravo_server=Server.objects.first())
        self.client.login(username='test_user', password='test')
        self.url = reverse('elpis:set_server', args=(1,))

    def test_set_producer(self):
        """Test that the Producer server returns success and a list of paths"""
        producer_pk = PreprodServer.objects.get(application_type=PreprodServer.PRODUCER).pk
        response = self.client.post(self.url, {'preprod-server': producer_pk})
        self.assertEqual(response.status_code, 200)
        response_body = json.loads(response.content)
        self.assertTrue(response_body['success'])
        self.assertTrue(response_body['paths'])
        self.assertEqual(Project.objects.first().preprod_server.pk, producer_pk)

class TestSetPathView(test.TestCase):
    def setUp(self):
        self.client = test.Client()
        User.objects.create_user(username='test_user', password='test')

        Server.objects.create(name='Fake Bravo')
        # TODO: Mock preprod servers
        PreprodServer.objects.create(name='linux4095', address='linux4095.wic.west.com', account='wicqacip',
                                     application_type=PreprodServer.PRODUCER)
        PreprodServer.objects.create(name='Prompt Store Placeholder', application_type=PreprodServer.NATIVE_VXML)
        Project.objects.create(name='Test Project', bravo_server=Server.objects.first())
        self.client.login(username='test_user', password='test')
        self.set_server_url = reverse('elpis:set_server', args=(1,))
        self.set_path_url = reverse('elpis:set_path', args=(1,))

    def test_set_producer_path(self):
        """Fetch paths for the producer server, then set one"""
        producer_pk = PreprodServer.objects.get(application_type=PreprodServer.PRODUCER).pk
        response = self.client.post(self.set_server_url, {'preprod-server': producer_pk})
        self.assertEqual(response.status_code, 200)
        response_body = json.loads(response.content)
        self.assertTrue(response_body['success'])
        self.assertTrue(response_body['paths'])

        path = response_body['paths'][0]
        response = self.client.post(self.set_path_url, {'preprod-path': path})
        self.assertEqual(response.status_code, 200)
        response_body = json.loads(response.content)
        self.assertTrue(response_body['success'])
        self.assertEqual(response_body['path'], '/usr/local/tuvox/public/Projects/' + path)
        self.assertEqual(response_body['path'], Project.objects.first().preprod_path)



class TestVerifyView(test.TestCase):
    def setUp(self):
        self.client = test.Client()
        User.objects.create_user(username='test_user', password='test')
        # TODO: Mock preprod servers
        pps = PreprodServer.objects.create(name='linux4095', address='linux4095.wic.west.com', account='wicqacip',
                                           application_type=PreprodServer.PRODUCER)
        Project.objects.create(name='Test Project', preprod_server=pps,
                               preprod_path='/usr/local/tuvox/public/Projects/21cent')
        self.client.login(username='test_user', password='test')
        self.url = reverse('elpis:verify', args=(1,))

    def test_verify_get_apps(self):
        """GET on URL should return a JSON list of applications for client"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        response_body = json.loads(response.content)
        self.assertTrue(response_body['apps'])