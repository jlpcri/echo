import json

from django import test
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from echo.apps.projects.models import Project
from echo.apps.settings.models import Server, PreprodServer
from echo.apps.elpis.utils.directory_tree import DirectoryTree, FileNotOnPathError
from echo.apps.elpis.models import ElpisStatus

User = get_user_model()

class TestDashboardView(test.TestCase):
    def setUp(self):
        p = Project.objects.create(name='Test Project')
        User.objects.create_user(username='test_user', password='test')
        self.client = test.Client()
        self.client.login(username='test_user', password='test')
        self.url = reverse('elpis:dashboard', args=(p.id, ))


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
        p = Project.objects.create(name='Test Project', bravo_server=Server.objects.first())
        self.client.login(username='test_user', password='test')
        self.url = reverse('elpis:set_server', args=(p.id,))

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
        p = Project.objects.create(name='Test Project', bravo_server=Server.objects.first())
        self.client.login(username='test_user', password='test')
        self.set_server_url = reverse('elpis:set_server', args=(p.id,))
        self.set_path_url = reverse('elpis:set_path', args=(p.id,))

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
        p = Project.objects.create(name='Test Project', preprod_server=pps,
                               preprod_path='/usr/local/tuvox/public/Projects/21cent')
        self.client.login(username='test_user', password='test')
        self.url = reverse('elpis:verify', args=(p.id,))

    def test_verify_get_apps(self):
        """GET on URL should return a JSON list of applications for client"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        response_body = json.loads(response.content)
        self.assertTrue(response_body['apps'])


class TestCheckRunningView(test.TestCase):
    def setUp(self):
        self.client = test.Client()
        User.objects.create_user(username='test_user', password='test')
        pps = PreprodServer.objects.create(name='linux4095', address='linux4095.wic.west.com', account='wicqacip',
                                           application_type=PreprodServer.PRODUCER)
        p = Project.objects.create(name='Test Project', preprod_server=pps,
                               preprod_path='/usr/local/tuvox/public/Projects/21cent')
        self.es = ElpisStatus.objects.create(project=p)
        self.client.login(username='test_user', password='test')
        self.url = reverse('elpis:check', args=(p.id,))

    def test_running(self):
        """If running, return JSON {running: True}"""
        self.es.running = True
        self.es.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        response_body = json.loads(response.content)
        self.assertTrue(response_body['running'])

    def test_not_running(self):
        """If not running, return JSON {running: False}"""
        self.es.running = False
        self.es.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        response_body = json.loads(response.content)
        self.assertFalse(response_body['running'])


class TestFetchView(test.TestCase):
    def setUp(self):
        self.client = test.Client()
        User.objects.create_user(username='test_user', password='test')
        pps = PreprodServer.objects.create(name='linux4095', address='linux4095.wic.west.com', account='wicqacip',
                                           application_type=PreprodServer.PRODUCER)
        p = Project.objects.create(name='Test Project', preprod_server=pps,
                               preprod_path='/usr/local/tuvox/public/Projects/21cent')
        self.es = ElpisStatus.objects.create(project=p)
        self.client.login(username='test_user', password='test')
        self.url = reverse('elpis:fetch', args=(p.id,))

    def test_response_when_not_run(self):
        """Empty response if no content has been set by a previous run"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.content, '')


    def test_response_when_run(self):
        """If previously run, return a page view to render"""
        last_run = "<html>Some stuff here</html>"
        self.es.response = last_run
        self.es.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.content, last_run)

class TestDirectoryTree(test.TestCase):
    """Test suite for DirectoryTree"""

    def test_without_path(self):
        """Tests DirectoryTree with no path specified"""
        dt = DirectoryTree()
        self.assertEqual(dt.entries, [])
        dt.add('/path/to/some/file.wav')
        self.assertEqual(dt.entries, ['/', ['path/', ['to/', ['some/', ['file.wav']]]]])
        dt.add('/path/to/some/other.wav')
        self.assertEqual(dt.entries, ['/', ['path/', ['to/', ['some/', ['file.wav', 'other.wav']]]]])
        dt.add('/path/to/another/place.wav')
        self.assertEqual(dt.entries, ['/', ['path/', ['to/', ['some/', ['file.wav', 'other.wav'],
                                                              'another/', ['place.wav']]]]])

    def test_with_path(self):
        """Tests DirectoryTree with a root path specified"""
        dt = DirectoryTree('/path/to/')
        dt.add('/path/to/some/file.wav')
        self.assertEqual(dt.entries, ['some/', ['file.wav']])
        dt.add('/path/to/some/other.wav')
        self.assertEqual(dt.entries, ['some/', ['file.wav', 'other.wav']])
        dt.add('/path/to/another/place.wav')
        self.assertEqual(dt.entries, ['some/', ['file.wav', 'other.wav'], 'another/', ['place.wav']])

    def test_bad_path(self):
        """DirectoryTree raises an exception if a file is added off the init path"""
        dt = DirectoryTree('/path/to/')
        self.assertRaises(FileNotOnPathError, dt.add, '/wrong/path/to/some/file.wav')

    def test_contains_without_path(self):
        """'if filepath in DirectoryTree' functionality"""
        dt = DirectoryTree()
        dt.add('/path/to/some/file.txt')
        self.assertTrue('/path/to/some/file.txt' in dt)
        self.assertFalse('/path/leading/nowhere' in dt)