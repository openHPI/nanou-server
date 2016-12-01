from django.test import Client
from django.urls import reverse

from neo.tests import NeoTestCase
from videos.models import Video


class VideoViewCorrcetPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user has the required permissions."""
    csrf_client = Client(enforce_csrf_checks=True)

    # List
    def test_get_list_view(self):
        response = self.client.get(reverse('videos:list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('videos', response.context)
        videos = list(response.context['videos'])
        all_videos = Video.all()
        self.assertTrue(all(video in all_videos for video in videos))

    def test_post_list_view_not_allowed(self):
        response = self.client.post(reverse('videos:list'))
        self.assertEqual(response.status_code, 405)

    # Detail
    def test_get_detail_view(self):
        video = Video.get(1)
        response = self.client.get(reverse('videos:detail', kwargs={'pk': video.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('video', response.context)
        self.assertEqual(response.context['video'], video)

    def test_get_detail_view_not_existant(self):
        response = self.client.get(reverse('videos:detail', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_detail_view_not_allowed(self):
        response = self.client.post(reverse('videos:detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 405)

    # Create
    def test_get_create_view(self):
        response = self.client.get(reverse('videos:create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_post_create_view(self):
        data = {
            'name': 'Random Video',
            'url': 'https://www.youtube.com/watch?v=DLzxrzFCyOs',
        }
        response = self.client.post(reverse('videos:create'), data, follow=True)
        self.assertRedirects(response, reverse('videos:list'))

    def test_post_create_view_no_data(self):
        response = self.client.post(reverse('videos:create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_create_view_incomplete_data(self):
        data = {}
        response = self.client.post(reverse('videos:create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_create_view_without_csrf_token(self):
        response = self.csrf_client.post(reverse('videos:create'))
        self.assertEqual(response.status_code, 403)

    # Update
    def test_get_update_view(self):
        response = self.client.get(reverse('videos:update', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_get_update_view_not_existant(self):
        response = self.client.get(reverse('videos:update', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_update_view(self):
        data = {
            'name': 'Updated Video',
            'url': 'https://www.youtube.com/watch?v=DLzxrzFCyOs',
        }
        response = self.client.post(reverse('videos:update', kwargs={'pk': 1}), data, follow=True)
        self.assertRedirects(response, reverse('videos:list'))

    def test_post_update_view_no_data(self):
        response = self.client.post(reverse('videos:update', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_update_view_incomplete_data(self):
        data = {}
        response = self.client.post(reverse('videos:update', kwargs={'pk': 1}), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_update_view_not_existant(self):
        response = self.client.post(reverse('videos:update', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_update_view_without_csrf_token(self):
        response = self.csrf_client.post(reverse('videos:update', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)

    # Delete
    def test_get_delete_view(self):
        video = Video.get(1)
        response = self.client.get(reverse('videos:delete', kwargs={'pk': video.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('video', response.context)
        self.assertEqual(response.context['video'], video)

    def test_get_delete_view_not_existant(self):
        response = self.client.get(reverse('videos:delete', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_delete_view(self):
        video = Video.get(1)
        response = self.client.post(reverse('videos:delete', kwargs={'pk': video.id}), follow=True)
        self.assertRedirects(response, reverse('videos:list'))
        self.assertNotIn(video, Video.all())

    def test_post_delete_view_not_existant(self):
        response = self.client.post(reverse('videos:delete', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_delete_view_without_csrf_token(self):
        response = self.csrf_client.post(reverse('videos:delete', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)

    # belongs_to
    def assertRelationContext(self, response, data=None):
        for key in ['start_node', 'end_node', 'relationship']:
            self.assertIn(key, response.context)

    def test_get_belongs_to_view(self):
        response = self.client.get(reverse('videos:belongs_to', kwargs={'pk1': 1, 'pk2': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)

    def test_get_belongs_to_view_not_existant(self):
        for pk1, pk2 in [(1, 1000), (1000, 1), (1000, 1000)]:
            response = self.client.get(reverse('videos:belongs_to', kwargs={'pk1': pk1, 'pk2': pk2}))
            self.assertEqual(response.status_code, 404)

    def test_post_belongs_to_view(self):
        data = {
            'weight': '0.7',
        }
        response = self.client.post(reverse('videos:belongs_to', kwargs={'pk1': 1, 'pk2': 1}), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)
        self.assertIn('messages', response.context)
        for key in data:
            props = response.context['relationship']['props']
            self.assertIn(key, props)
            self.assertEqual(props[key], data[key])
        self.assertIn('success', response.context['messages'])

    def test_post_belongs_to_view_no_data(self):
        response = self.client.post(reverse('videos:belongs_to', kwargs={'pk1': 1, 'pk2': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)
        self.assertIn('messages', response.context)
        self.assertIn('error', response.context['messages'])

    def test_post_belongs_to_view_incomplete_data(self):
        data = {}
        response = self.client.post(reverse('videos:belongs_to', kwargs={'pk1': 1, 'pk2': 1}), data)
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)
        self.assertIn('messages', response.context)
        self.assertIn('error', response.context['messages'])

    def test_post_belongs_to_view_too_much_data(self):
        data = {
            'weight': 0.7,
            'foo': 'baz',
            'asdf': 1,
        }
        response = self.client.post(reverse('videos:belongs_to', kwargs={'pk1': 1, 'pk2': 1}), data)
        self.assertEqual(response.status_code, 200)
        self.assertRelationContext(response)
        self.assertIn('messages', response.context)
        self.assertIn('error', response.context['messages'])

    def test_post_belongs_to_view_not_existant(self):
        for pk1, pk2 in [(1, 1000), (1000, 1), (1000, 1000)]:
            response = self.client.post(reverse('videos:belongs_to', kwargs={'pk1': pk1, 'pk2': pk2}))
            self.assertEqual(response.status_code, 404)

    def test_post_belongs_to_view_without_csrf_token(self):
        response = self.csrf_client.post(reverse('videos:belongs_to', kwargs={'pk1': 1, 'pk2': 1}))
        self.assertEqual(response.status_code, 403)


class VideoViewWrongPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user lacks the required permissions."""

    # List
    def test_get_list_view(self):
        url = reverse('videos:list')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Detail
    def test_get_detail_view(self):
        url = reverse('videos:detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Create
    def test_get_create_view(self):
        url = reverse('videos:create')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Update
    def test_get_update_view(self):
        url = reverse('videos:update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Delete
    def test_get_delete_view(self):
        url = reverse('videos:delete', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # belongs_to
    def test_get_belongs_to_view(self):
        url = reverse('videos:belongs_to', kwargs={'pk1': 1, 'pk2': 1})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)


class VideoViewManagerTests(NeoTestCase, VideoViewCorrcetPermissionsMixin):
    """User testing the views is logged in as manager and therefore has the required permissions."""
    fixtures = ['users_testdata']
    neo_fixtures = ['videos/fixtures/neo_video_group_testdata.json']

    def setUp(self):
        self.client.login(username='manager', password='admin')


class VideoViewSocialUserests(NeoTestCase, VideoViewWrongPermissionsMixin):
    """User testing the views is logged in as social user and therefore lacking the required permissions."""
    fixtures = ['users_testdata']
    neo_fixtures = ['videos/fixtures/neo_video_group_testdata.json']

    def setUp(self):
        self.client.login(username='socialuser', password='admin')


class VideoViewNoPermissionTests(NeoTestCase, VideoViewWrongPermissionsMixin):
    """User testing the views is not logged and therefore lacking the required permissions."""
    fixtures = ['users_testdata']
    neo_fixtures = ['videos/fixtures/neo_video_group_testdata.json']
