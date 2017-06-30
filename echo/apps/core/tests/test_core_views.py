from django.test import Client, TestCase
from django.core.urlresolvers import reverse, resolve
from django.contrib.auth.models import User

from echo.apps.core.views import home, form, signin, signout


class CoreViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url_form = reverse('core:form')
        self.url_home = reverse('core:home')

    def test_home_url_resolve_to_view(self):
        found = resolve(self.url_home)
        self.assertEqual(found.func, home)

    def test_home_url_returns_status_200(self):
        response = self.client.get(self.url_home, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_form_url_resolve_to_view(self):
        found = resolve(self.url_form)
        self.assertEqual(found.func, form)

    def test_form_url_returns_status_200(self):
        response = self.client.get(self.url_form)
        self.assertEqual(response.status_code, 200)


class TestUserAuthenticationSignIn(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_account_correct = {
            'username': 'correctName',
            'password': 'correctPassword'
        }
        self.user = User.objects.create_user(
            username=self.user_account_correct['username'],
            password=self.user_account_correct['password']
        )
        self.user_account_incorrect_username = {
            'username': 'incorrectName',
            'password': 'correctPassword'
        }
        self.user_account_incorrect_password = {
            'username': 'correctName',
            'password': 'incorrectPassword'
        }

    def test_user_sign_in_resolve_to_view(self):
        found = resolve(reverse('core:signin'))
        self.assertEqual(found.func, signin)

    def test_user_sign_in_successfully_redirect(self):
        response = self.client.post(
            reverse('core:signin'),
            self.user_account_correct,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('core:home'))

    def test_user_sign_in_unsuccessfully_with_incorrect_username_redirect(self):
        response = self.client.post(
            reverse('core:signin'),
            self.user_account_incorrect_username
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:form'))

    def test_user_sign_in_unsuccessfully_with_incorrect_password_redirect(self):
        response = self.client.post(
            reverse('core:signin'),
            self.user_account_incorrect_password
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:form'))

    def test_user_sign_in_successfully(self):
        response = self.client.post(
            reverse('core:signin'),
            self.user_account_correct,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(self.client.session['_auth_user_id'], self.user.pk)

    def test_user_sign_in_unsuccessfully_with_incorrect_username(self):
        response = self.client.post(
            reverse('core:signin'),
            self.user_account_incorrect_username,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        message = list(response.context['messages'])
        self.assertEqual(str(message[0]), 'Invalid username or password.')

    def test_user_sign_in_unsuccessfully_with_incorrect_password(self):
        response = self.client.post(
            reverse('core:signin'),
            self.user_account_incorrect_password,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        message = list(response.context['messages'])
        self.assertEqual(str(message[0]), 'Invalid username or password.')

    def test_user_sign_in_unsuccessfully_without_post_method(self):
        response = self.client.get(
            reverse('core:signin'),
            self.user_account_correct
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)


class TestUsersAuthenticationSignOut(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_account_correct = {
            'username': 'correctName',
            'password': 'correctPassword'
        }
        self.user = User.objects.create_user(
            username=self.user_account_correct['username'],
            password=self.user_account_correct['password']
        )
        self.client.login(
            username=self.user_account_correct['username'],
            password=self.user_account_correct['password']
        )

    def test_user_sign_out_resolve_to_view(self):
        found = resolve(reverse('core:signout'))
        self.assertEqual(found.func, signout)

    def test_user_sign_out_redirect(self):
        response = self.client.get(
            reverse('core:signout')
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:form'))

    def test_user_sign_out_successfully(self):
        response = self.client.get(
            reverse('core:signout'),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('auth_user_id', self.client.session)


