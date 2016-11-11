from django.test import Client
from django.urls import reverse
from django.utils import six

from neo.tests import NeoTestCase
from groups.models import Group


def get_valid_kwargs():
    group = Group.first()
    rel_type = group.required_by_videos._RelatedObjects__match_args[1]
    video = list(group.required_by_videos)[0]
    return {
        'pk1': video.id,
        'rel_type': rel_type,
        'pk2': group.id,
    }


def get_invalid_kwargs_options():
    valid_kwargs = get_valid_kwargs()
    for key, value in valid_kwargs.items():
        option = valid_kwargs.copy()
        if isinstance(value, int):
            option[key] = 0
        elif isinstance(value, six.string_types):
            option[key] = 'foobarbaz'
        yield option


class NeoExtrasViewCorrcetPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user has the required permissions."""
    csrf_client = Client(enforce_csrf_checks=True)

    def assertRelationContext(self, response, data=None):
        for key in ['start_node', 'end_node', 'relationship']:
            self.assertIn(key, response.context)

    # Update
    def test_get_update_view(self):
        response = self.client.get(reverse('neoextras:relation', kwargs=get_valid_kwargs()))
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)

    def test_get_update_view_not_existant(self):
        for option in get_invalid_kwargs_options():
            response = self.client.get(reverse('neoextras:relation', kwargs=option))
            self.assertEqual(response.status_code, 404)

    def test_post_update_view(self):
        data = {
            'weight': '0.7',
            'foo': 'baz',
        }
        response = self.client.post(reverse('neoextras:relation', kwargs=get_valid_kwargs()), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)
        self.assertIn('messages', response.context)
        for key in data:
            props = response.context['relationship']['props']
            self.assertIn(key, props)
            self.assertEqual(props[key], data[key])
        self.assertIn('success', response.context['messages'])

    def test_post_update_view_no_data(self):
        response = self.client.post(reverse('neoextras:relation', kwargs=get_valid_kwargs()))
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)
        self.assertIn('messages', response.context)
        self.assertIn('error', response.context['messages'])

    def test_post_update_view_incomplete_data(self):
        data = {
            'weight': 0.7,
        }
        response = self.client.post(reverse('neoextras:relation', kwargs=get_valid_kwargs()), data)
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)
        self.assertIn('messages', response.context)
        self.assertIn('error', response.context['messages'])

    def test_post_update_view_too_much_data(self):
        data = {
            'weight': 0.7,
            'foo': 'baz',
            'asdf': 1,
        }
        response = self.client.post(reverse('neoextras:relation', kwargs=get_valid_kwargs()), data)
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)
        self.assertIn('messages', response.context)
        self.assertIn('error', response.context['messages'])

    def test_post_update_view_not_existant(self):
        for option in get_invalid_kwargs_options():
            response = self.client.post(reverse('neoextras:relation', kwargs=option))
            self.assertEqual(response.status_code, 404)

    def test_post_update_view_without_csrf_token(self):
        response = self.csrf_client.post(reverse('neoextras:relation', kwargs=get_valid_kwargs()))
        self.assertEqual(response.status_code, 403)


class NeoExtrasViewWrongPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user lacks the required permissions."""

    # Update
    def test_get_update_view(self):
        url = reverse('neoextras:relation', kwargs=get_valid_kwargs())
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)


class NeoExtrasViewManagerTests(NeoTestCase, NeoExtrasViewCorrcetPermissionsMixin):
    """User testing the views is logged in as manager and therefore has the required permissions."""
    fixtures = ['users_testdata']
    neo_fixtures = ['videos/fixtures/neo_video_group_testdata.json']

    def setUp(self):
        self.client.login(username='manager', password='admin')


class NeoExtrasViewSocialUserests(NeoTestCase, NeoExtrasViewWrongPermissionsMixin):
    """User testing the views is logged in as social user and therefore lacking the required permissions."""
    fixtures = ['users_testdata']
    neo_fixtures = ['videos/fixtures/neo_video_group_testdata.json']

    def setUp(self):
        self.client.login(username='socialuser', password='admin')


class NeoExtrasViewNoPermissionTests(NeoTestCase, NeoExtrasViewWrongPermissionsMixin):
    """User testing the views is not logged and therefore lacking the required permissions."""
    fixtures = ['users_testdata']
    neo_fixtures = ['videos/fixtures/neo_video_group_testdata.json']
