import json

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.utils import six
from rest_framework.authtoken.models import Token

from neo.tests import NeoTestCase
from socialusers.models import SocialUser


class SocialLoginCorrectPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user has the required permissions."""

    # /api/auth-status
    def test_get_authstatus(self):
        response = self.client.get(reverse('sociallogin:status'))
        self.assertEqual(response.status_code, 200)
        response_content = response.content
        if six.PY3:
            response_content = str(response_content, encoding='utf8')
        json_content = json.loads(response_content)
        self.assertIn('authenticated', json_content)
        self.assertEqual(json_content['authenticated'], True)
        self.assertIn('token', json_content)
        self.assertIn('preferencesInitialized', json_content)


class SocialLoginWrongPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user lacks the required permissions."""

    # /api/auth-status
    def test_get_authstatus(self):
        response = self.client.get(reverse('sociallogin:status'))
        self.assertEqual(response.status_code, 200)
        response_content = response.content
        if six.PY3:
            response_content = str(response_content, encoding='utf8')
        json_content = json.loads(response_content)
        self.assertIn('authenticated', json_content)
        self.assertEqual(json_content['authenticated'], False)

    # GET /api/combine
    def test_get_combine(self):
        response = self.client.get(reverse('sociallogin:combine_accounts'))
        self.assertEqual(response.status_code, 401)


class SocialLoginTestCase(NeoTestCase):
    # GET /api/login-providers
    def test_get_login_providers(self):
        response = self.client.get(reverse('sociallogin:login_providers'))
        self.assertEqual(response.status_code, 200)
        response_content = response.content
        if six.PY3:
            response_content = str(response_content, encoding='utf8')
        json_content = json.loads(response_content)
        self.assertTrue('data' in json_content)

    # GET /api/test_login
    def test_get_test_login(self):
        user_count = User.objects.count()
        socialuser_count = len(list(SocialUser.all()))

        response = self.client.get(reverse('sociallogin:test_login'), {'vendorId': '1234'})
        self.assertEqual(response.status_code, 200)
        response_content = response.content
        if six.PY3:
            response_content = str(response_content, encoding='utf8')
        json_content = json.loads(response_content)
        self.assertIn('authenticated', json_content)
        self.assertEqual(json_content['authenticated'], True)
        self.assertEqual(User.objects.count(), user_count+1)
        self.assertEqual(len(list(SocialUser.all())), socialuser_count+1)
        self.assertIn('preferencesInitialized', json_content)
        self.assertIn('token', json_content)
        token = json_content['token']

        # login again
        response = self.client.get(reverse('sociallogin:test_login'), {'vendorId': '1234'})
        self.assertEqual(response.status_code, 200)
        response_content = response.content
        if six.PY3:
            response_content = str(response_content, encoding='utf8')
        json_content = json.loads(response_content)
        self.assertIn('authenticated', json_content)
        self.assertEqual(json_content['authenticated'], True)
        self.assertEqual(User.objects.count(), user_count+1)
        self.assertEqual(len(list(SocialUser.all())), socialuser_count+1)
        self.assertIn('token', json_content)
        self.assertEqual(json_content['token'], token)


    def test_get_test_login_missing_vendor_id(self):
        response = self.client.get(reverse('sociallogin:test_login'))
        self.assertEqual(response.status_code, 400)

class SocialLoginManagerTests(SocialLoginWrongPermissionsMixin, SocialLoginTestCase):
    """User testing the views is logged in as manager and therefore has the required permissions."""
    fixtures = ['users_testdata']

    def setUp(self):
        self.client.login(username='manager', password='admin')


class SocialLoginSocialUserTests(SocialLoginCorrectPermissionsMixin, SocialLoginTestCase):
    """User testing the views is logged in as social user and therefore lacking the required permissions."""
    fixtures = ['users_testdata']

    def setUp(self):
        self.client.login(username='socialuser', password='admin')


class SocialLoginTokenTests(SocialLoginCorrectPermissionsMixin, SocialLoginTestCase):
    """User testing the views is not logged and therefore lacking the required permissions."""
    fixtures = ['users_testdata']
    neo_fixtures = ['api/fixtures/neo_login_testdata.json']

    def setUp(self):
        user = User.objects.get(pk=3)
        token = Token.objects.get(user=user)
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token ' + token.key

    # GET /api/combine
    def test_get_combine(self):
        user = User.objects.get(pk=3)
        test_user = User.objects.get(pk=4)

        socialuser = SocialUser.get(1)
        test_socialuser = SocialUser.get(2)

        self.assertEqual(test_user.username, 'abcd')
        self.assertEqual(socialuser.user_id, 3)
        self.assertEqual(test_socialuser.user_id, 4)
        self.assertEqual(sorted([video.name for video in SocialUser.next_videos(user.id)]), [u'B'])
        self.assertEqual(sorted([video.name for video in SocialUser.next_videos(test_user.id)]), [u'A'])

        # combine
        response = self.client.get(reverse('sociallogin:combine_accounts'), {'vendorId': 'abcd'})
        self.assertEqual(response.status_code, 200)

        self.assertTrue(test_user.username.endswith('abcd'))
        self.assertEqual(socialuser.user_id, 3)
        self.assertEqual(test_socialuser.user_id, 3)
        self.assertEqual(sorted([video.name for video in SocialUser.next_videos(user.id)]), [u'C'])

        # do it again
        response = self.client.get(reverse('sociallogin:combine_accounts'), {'vendorId': 'abcd'})
        self.assertEqual(response.status_code, 400)


    def test_get_combine_missing_vendor_id(self):
        response = self.client.get(reverse('sociallogin:combine_accounts'))
        self.assertEqual(response.status_code, 400)

    def test_get_combine_invalid_vendor_id(self):
        response = self.client.get(reverse('sociallogin:combine_accounts'), {'vendorId': 'dcba'})
        self.assertEqual(response.status_code, 400)


class SocialLoginInvalidTokenTests(SocialLoginWrongPermissionsMixin, SocialLoginTestCase):
    """User testing the views is not logged and therefore lacking the required permissions."""
    fixtures = ['users_testdata']

    def setUp(self):
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token 12345abcdef'


class SocialLoginNoPermissionTests(SocialLoginWrongPermissionsMixin, SocialLoginTestCase):
    """User testing the views is not logged and therefore lacking the required permissions."""
    fixtures = ['users_testdata']
