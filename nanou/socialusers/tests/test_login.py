import json

from django.test import TestCase
from django.urls import reverse
from django.utils import six

from rest_framework.authtoken.models import Token


class SocialLoginCorrectPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user has the required permissions."""

    # /social/status
    def test_get_authstatus(self):
        response = self.client.get(reverse('sociallogin:status'))
        self.assertEqual(response.status_code, 200)
        response_content = response.content
        if six.PY3:
            response_content = str(response_content, encoding='utf8')
        json_content = json.loads(response_content)
        self.assertTrue('token' in json_content)


class SocialLoginWrongPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user lacks the required permissions."""

    # /social/status
    def test_get_authstatus(self):
        response = self.client.get(reverse('sociallogin:status'))
        self.assertRedirects(response, reverse('sociallogin:login_providers'))


class SocialLoginManagerTests(TestCase, SocialLoginWrongPermissionsMixin):
    """User testing the views is logged in as manager and therefore has the required permissions."""
    fixtures = ['users_testdata']

    def setUp(self):
        self.client.login(username='manager', password='admin')


class SocialLoginSocialUserTests(TestCase, SocialLoginCorrectPermissionsMixin):
    """User testing the views is logged in as social user and therefore lacking the required permissions."""
    fixtures = ['users_testdata']

    def setUp(self):
        self.client.login(username='socialuser', password='admin')


class SocialLoginTokenTests(TestCase, SocialLoginCorrectPermissionsMixin):
    """User testing the views is not logged and therefore lacking the required permissions."""
    fixtures = ['users_testdata']

    def setUp(self):
        token = Token.objects.first()
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token ' + token.key


class SocialLoginNoPermissionTests(TestCase, SocialLoginWrongPermissionsMixin):
    """User testing the views is not logged and therefore lacking the required permissions."""
    fixtures = ['users_testdata']

    # GET /social/login-providers
    def test_get_login_providers(self):
        response = self.client.get(reverse('sociallogin:login_providers'))
        self.assertEqual(response.status_code, 200)
        response_content = response.content
        if six.PY3:
            response_content = str(response_content, encoding='utf8')
        json_content = json.loads(response_content)
        self.assertTrue('data' in json_content)
