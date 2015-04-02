from django.test import Client, TestCase
from django.core.urlresolvers import reverse, resolve
from django.contrib.auth.models import User

from echo.apps.settings.models import Server, PreprodServer
from echo.apps.settings.views import index, servers, servers_preprod, users


class SettingsViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user_account_superuser = {
            'username': 'superUserName',
            'password': 'superUserPassword'
        }
        self.user_account_normaluser = {
            'username': 'normalUserName',
            'password': 'normalUserPassword'
        }
        self.user_superuser = User.objects.create_superuser(
            username=self.user_account_superuser['username'],
            password=self.user_account_superuser['password'],
            email=''
        )
        self.user_normaluser = User.objects.create(
            username=self.user_account_normaluser['username'],
            password=self.user_account_normaluser['password']
        )

        self.url_index = reverse('settings:index')
        self.url_servers = reverse('settings:servers')
        self.url_servers_preprod = reverse('settings:servers_preprod')
        self.url_users = reverse('settings:users')

    def test_index_url_resolve_to_view(self):
        found = resolve(reverse('settings:index'))
        self.assertEqual(found.func, index)

    def test_index_url_returns_status_200(self):
        response = self.client.get(self.url_index, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_servers_url_resolve_to_view(self):
        found = resolve(reverse('settings:servers'))
        self.assertEqual(found.func, servers)

    def test_servers_url_returns_status_200(self):
        response = self.client.get(self.url_servers, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_servers_view_contains_servers_list_with_superuser(self):
        self.client.login(
            username=self.user_account_superuser['username'],
            password=self.user_account_superuser['password']
        )
        server1 = Server.objects.create(name='Server1',
                                        address='10.0.0.1',
                                        account='server_account',
                                        active=True)
        server2 = Server.objects.create(name='Server2',
                                        address='10.0.0.2',
                                        account='server_account')
        response = self.client.get(self.url_servers, follow=True)
        self.assertContains(response, server1.name, 1)
        self.assertContains(response, server1.address, 1)
        self.assertContains(response, server1.account, 2)
        self.assertContains(response, server1.name, 1)
        self.assertContains(response, server2.address, 1)

    def test_servers_preprod_url_resolve_to_view(self):
        found = resolve(reverse('settings:servers_preprod'))
        self.assertEqual(found.func, servers_preprod)

    def test_servers_preprod_url_returns_status_200(self):
        response = self.client.get(self.url_servers_preprod, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_users_url_resolve_to_view(self):
        found = resolve(reverse('settings:users'))
        self.assertEqual(found.func, users)

    def test_users_url_returns_status_200(self):
        response = self.client.get(self.url_users, follow=True)
        self.assertEqual(response.status_code, 200)
