from django.test import Client
from django.urls import reverse

from neo.tests import NeoTestCase
from socialusers.models import SocialUser


class SocialUserViewCorrcetPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user has the required permissions."""
    csrf_client = Client(enforce_csrf_checks=True)

    # List
    def test_get_list_view(self):
        response = self.client.get(reverse('socialusers:list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('socialusers', response.context)
        socialusers = list(response.context['socialusers'])
        all_socialusers = SocialUser.all()
        self.assertTrue(all(user in all_socialusers for user in socialusers))

    def test_post_list_view_not_allowed(self):
        response = self.client.post(reverse('socialusers:list'))
        self.assertEqual(response.status_code, 405)

    # Detail
    def test_get_detail_view(self):
        user = SocialUser.first()
        response = self.client.get(reverse('socialusers:detail', kwargs={'pk': user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('socialuser', response.context)
        self.assertEqual(response.context['socialuser'], user)

    def test_get_detail_view_not_existant(self):
        response = self.client.get(reverse('socialusers:detail', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_detail_view_not_allowed(self):
        user = SocialUser.first()
        response = self.client.post(reverse('socialusers:detail', kwargs={'pk': user.id}))
        self.assertEqual(response.status_code, 405)

    # Update
    def test_get_update_view(self):
        user = SocialUser.first()
        response = self.client.get(reverse('socialusers:update', kwargs={'pk': user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_get_update_view_not_existant(self):
        response = self.client.get(reverse('socialusers:update', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_update_view(self):
        user = SocialUser.first()
        data = {
            'watched_videos': [],
        }
        response = self.client.post(reverse('socialusers:update', kwargs={'pk': user.id}), data, follow=True)
        self.assertRedirects(response, reverse('socialusers:list'))

    # def test_post_update_view_no_data(self):
    #     user = SocialUser.first()
    #     response = self.client.post(reverse('socialusers:update', kwargs={'pk': user.id}))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('form', response.context)  # shows form again
    #
    # def test_post_update_view_incomplete_data(self):
    #     data = {}
    #     user = SocialUser.first()
    #     response = self.client.post(reverse('socialusers:update', kwargs={'pk': user.id}), data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('form', response.context)  # shows form again

    def test_post_update_view_not_existant(self):
        response = self.client.post(reverse('socialusers:update', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_update_view_without_csrf_token(self):
        user = SocialUser.first()
        response = self.csrf_client.post(reverse('socialusers:update', kwargs={'pk': user.id}))
        self.assertEqual(response.status_code, 403)

    # has_preference
    def assertRelationContext(self, response, data=None):
        for key in ['start_node', 'end_node', 'relationship']:
            self.assertIn(key, response.context)

    def test_get_has_preference_view(self):
        response = self.client.get(reverse('socialusers:has_preference', kwargs={'pk1': 1, 'pk2': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)

    def test_get_has_preference_view_not_existant(self):
        for pk1, pk2 in [(1, 1000), (1000, 1), (1000, 1000)]:
            response = self.client.get(reverse('socialusers:has_preference', kwargs={'pk1': pk1, 'pk2': pk2}))
            self.assertEqual(response.status_code, 404)

    def test_post_has_preference_view(self):
        data = {
            'weight': '0.7',
        }
        response = self.client.post(reverse('socialusers:has_preference', kwargs={'pk1': 1, 'pk2': 1}),
                                    data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)
        self.assertIn('messages', response.context)
        for key in data:
            props = response.context['relationship']['props']
            self.assertIn(key, props)
            self.assertEqual(props[key], data[key])
        self.assertIn('success', response.context['messages'])

    def test_post_has_preference_view_no_data(self):
        response = self.client.post(reverse('socialusers:has_preference', kwargs={'pk1': 1, 'pk2': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)
        self.assertIn('messages', response.context)
        self.assertIn('error', response.context['messages'])

    def test_post_has_preference_view_incomplete_data(self):
        data = {}
        response = self.client.post(reverse('socialusers:has_preference', kwargs={'pk1': 1, 'pk2': 1}), data)
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)
        self.assertIn('messages', response.context)
        self.assertIn('error', response.context['messages'])

    def test_post_has_preference_view_too_much_data(self):
        data = {
            'weight': 0.7,
            'foo': 'baz',
            'asdf': 1,
        }
        response = self.client.post(reverse('socialusers:has_preference', kwargs={'pk1': 1, 'pk2': 1}), data)
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)
        self.assertIn('messages', response.context)
        self.assertIn('error', response.context['messages'])

    def test_post_has_preference_view_not_existant(self):
        for pk1, pk2 in [(1, 1000), (1000, 1), (1000, 1000)]:
            response = self.client.post(reverse('socialusers:has_preference', kwargs={'pk1': pk1, 'pk2': pk2}))
            self.assertEqual(response.status_code, 404)

    def test_post_has_preference_view_without_csrf_token(self):
        response = self.csrf_client.post(reverse('socialusers:has_preference', kwargs={'pk1': 1, 'pk2': 1}))
        self.assertEqual(response.status_code, 403)

    # belongs_to
    def test_get_watched_view(self):
        response = self.client.get(reverse('socialusers:watched', kwargs={'pk1': 1, 'pk2': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)

    def test_get_watched_view_not_existant(self):
        for pk1, pk2 in [(1, 1000), (1000, 1), (1000, 1000)]:
            response = self.client.get(reverse('socialusers:watched', kwargs={'pk1': pk1, 'pk2': pk2}))
            self.assertEqual(response.status_code, 404)

    def test_post_watched_view(self):
        data = {
            'date': 'now',
            'rating': '1.0',
            'progress': '1.0',
        }
        response = self.client.post(reverse('socialusers:watched', kwargs={'pk1': 1, 'pk2': 1}), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)
        self.assertIn('messages', response.context)
        for key in data:
            props = response.context['relationship']['props']
            self.assertIn(key, props)
            self.assertEqual(props[key], data[key])
        self.assertIn('success', response.context['messages'])

    def test_post_watched_view_no_data(self):
        response = self.client.post(reverse('socialusers:watched', kwargs={'pk1': 1, 'pk2': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)
        self.assertIn('messages', response.context)
        self.assertIn('error', response.context['messages'])

    def test_post_watched_view_incomplete_data(self):
        data = {}
        response = self.client.post(reverse('socialusers:watched', kwargs={'pk1': 1, 'pk2': 1}), data)
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)
        self.assertIn('messages', response.context)
        self.assertIn('error', response.context['messages'])

    def test_post_watched_view_too_much_data(self):
        data = {
            'date': 'now',
            'rating': '1.0',
            'progress': '1.0',
            'foo': 'baz',
            'asdf': 1,
        }
        response = self.client.post(reverse('socialusers:watched', kwargs={'pk1': 1, 'pk2': 1}), data)
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)
        self.assertIn('messages', response.context)
        self.assertIn('error', response.context['messages'])

    def test_post_watched_view_not_existant(self):
        for pk1, pk2 in [(1, 1000), (1000, 1), (1000, 1000)]:
            response = self.client.post(reverse('socialusers:watched', kwargs={'pk1': pk1, 'pk2': pk2}))
            self.assertEqual(response.status_code, 404)

    def test_post_watched_view_without_csrf_token(self):
        response = self.csrf_client.post(reverse('socialusers:watched', kwargs={'pk1': 1, 'pk2': 1}))
        self.assertEqual(response.status_code, 403)


class SocialUserViewWrongPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user lacks the required permissions."""

    # List
    def test_get_list_view(self):
        url = reverse('socialusers:list')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Detail
    def test_get_detail_view(self):
        user = SocialUser.first()
        url = reverse('socialusers:detail', kwargs={'pk': user.id})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Update
    def test_get_update_view(self):
        user = SocialUser.first()
        url = reverse('socialusers:update', kwargs={'pk': user.id})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # has_preference
    def test_get_preference_view(self):
        url = reverse('socialusers:has_preference', kwargs={'pk1': 1, 'pk2': 1})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # watched
    def test_get_watched_view(self):
        url = reverse('socialusers:watched', kwargs={'pk1': 1, 'pk2': 1})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)


class SocialUserViewManagerTests(NeoTestCase, SocialUserViewCorrcetPermissionsMixin):
    """User testing the views is logged in as manager and therefore has the required permissions."""
    fixtures = ['users_testdata']
    neo_fixtures = ['socialusers/fixtures/neo_socialuser_testdata.json']

    def setUp(self):
        self.client.login(username='manager', password='admin')


class SocialUserViewSocialUserTests(NeoTestCase, SocialUserViewWrongPermissionsMixin):
    """User testing the views is logged in as social user and therefore lacking the required permissions."""
    fixtures = ['users_testdata']
    neo_fixtures = ['socialusers/fixtures/neo_socialuser_testdata.json']

    def setUp(self):
        self.client.login(username='socialuser', password='admin')


class SocialUserViewNoPermissionTests(NeoTestCase, SocialUserViewWrongPermissionsMixin):
    """User testing the views is not logged and therefore lacking the required permissions."""
    fixtures = ['users_testdata']
    neo_fixtures = ['socialusers/fixtures/neo_socialuser_testdata.json']
