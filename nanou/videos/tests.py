from django.test import Client
from django.urls import reverse

from neo.tests import NeoTestCase
from videos.models import Video


class VideoViewLoggedInTests(NeoTestCase):
    fixtures = ['users_views_testdata']
    neo_fixtures = ['videos/fixtures/neo_video_group_testdata.json']
    csrf_client = Client(enforce_csrf_checks=True)

    def setUp(self):
        self.client.login(username='admin', password='admin')

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
        video = Video.first()
        response = self.client.get(reverse('videos:detail', kwargs={'pk': video.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('video', response.context)
        self.assertEqual(response.context['video'], video)

    def test_get_detail_view_not_existant(self):
        response = self.client.get(reverse('videos:detail', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_detail_view_not_allowed(self):
        video = Video.first()
        response = self.client.post(reverse('videos:detail', kwargs={'pk': video.id}))
        self.assertEqual(response.status_code, 405)

    # Create
    def test_get_create_view(self):
        response = self.client.get(reverse('videos:create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_post_create_view(self):
        data = {
            'name': 'Random Video',
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
        video = Video.first()
        response = self.client.get(reverse('videos:update', kwargs={'pk': video.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_get_update_view_not_existant(self):
        response = self.client.get(reverse('videos:update', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_update_view(self):
        video = Video.first()
        data = {
            'name': 'Updated Video',
        }
        response = self.client.post(reverse('videos:update', kwargs={'pk': video.id}), data, follow=True)
        self.assertRedirects(response, reverse('videos:list'))

    def test_post_update_view_no_data(self):
        video = Video.first()
        response = self.client.post(reverse('videos:update', kwargs={'pk': video.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_update_view_incomplete_data(self):
        data = {}
        video = Video.first()
        response = self.client.post(reverse('videos:update', kwargs={'pk': video.id}), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_update_view_not_existant(self):
        response = self.client.post(reverse('videos:update', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_update_view_without_csrf_token(self):
        video = Video.first()
        response = self.csrf_client.post(reverse('videos:update', kwargs={'pk': video.id}))
        self.assertEqual(response.status_code, 403)

    # Delete
    def test_get_delete_view(self):
        video = Video.first()
        response = self.client.get(reverse('videos:delete', kwargs={'pk': video.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('video', response.context)
        self.assertEqual(response.context['video'], video)

    def test_get_delete_view_not_existant(self):
        response = self.client.get(reverse('videos:delete', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_delete_view(self):
        video = Video.first()
        response = self.client.post(reverse('videos:delete', kwargs={'pk': video.id}), follow=True)
        self.assertRedirects(response, reverse('videos:list'))
        self.assertNotIn(video, Video.all())

    def test_post_delete_view_not_existant(self):
        response = self.client.post(reverse('videos:delete', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_delete_view_without_csrf_token(self):
        video = Video.first()
        response = self.csrf_client.post(reverse('videos:delete', kwargs={'pk': video.id}))
        self.assertEqual(response.status_code, 403)


class VideoViewwNoPermissionTests(NeoTestCase):
    """User testing the views is not logged and therefore lacking the required permissions."""
    neo_fixtures = ['videos/fixtures/neo_video_group_testdata.json']

    # List
    def test_get_list_view(self):
        url = reverse('videos:list')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Detail
    def test_get_detail_view(self):
        video = Video.first()
        url = reverse('videos:detail', kwargs={'pk': video.id})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Create
    def test_get_create_view(self):
        url = reverse('videos:create')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Update
    def test_get_update_view(self):
        video = Video.first()
        url = reverse('videos:update', kwargs={'pk': video.id})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Delete
    def test_get_delete_view(self):
        video = Video.first()
        url = reverse('videos:delete', kwargs={'pk': video.id})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)
