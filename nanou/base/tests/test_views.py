from django.test import Client, TestCase
from django.urls import reverse


class NanouViewCorrcetPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user has the required permissions."""
    csrf_client = Client(enforce_csrf_checks=True)

    def test_get_landing_page(self):
        response = self.client.get(reverse('base:landingpage'))
        self.assertEqual(response.status_code, 200)


class NanouViewWrongPermissionMixin(object):
    """Mixins for user testing the views is logged if the user lacks the required permissions."""

    def test_get_landing_page(self):
        url = reverse('base:landingpage')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)


class NanouViewManagerTests(TestCase, NanouViewCorrcetPermissionsMixin):
    """User testing the views is logged in as manager and therefore has the required permissions."""
    fixtures = ['users_testdata']

    def setUp(self):
        self.client.login(username='manager', password='admin')


class NanouViewSocialUserTests(TestCase, NanouViewWrongPermissionMixin):
    """User testing the views is logged in as social user and therefore lacking the required permissions."""
    fixtures = ['users_testdata']

    def setUp(self):
        self.client.login(username='socialuser', password='admin')


class NanouViewNoPermissionTests(TestCase, NanouViewWrongPermissionMixin):
    """User testing the views is not logged and therefore lacking the required permissions."""
    fixtures = ['users_testdata']
