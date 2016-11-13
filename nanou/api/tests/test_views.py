import json

from django.test import Client
from django.urls import reverse
from django.utils import six

from rest_framework.authtoken.models import Token

from neo.tests import NeoTestCase
from neo.utils import NeoGraph
from videos.models import Video


class ApiViewCorrectPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user has the required permissions."""
    csrf_client = Client(enforce_csrf_checks=True)

    def load_response_content(self, response):
        response_content = response.content
        if six.PY3:
            response_content = str(response_content, encoding='utf8')
        return json.loads(response_content)

    def assertVideoCount(self, response, count):
        json_response = self.load_response_content(response)
        self.assertIn('meta', json_response)
        self.assertIn('count', json_response['meta'])
        self.assertEqual(count, json_response['meta']['count'])

    def assertJSONDataVideoNames(self, response, video_names):
        json_response = self.load_response_content(response)
        self.assertIn('data', json_response)
        self.assertTrue(all('attributes' in item for item in json_response['data']))
        self.assertTrue(all('name' in item['attributes'] for item in json_response['data']))
        response_names = [item['attributes']['name'] for item in json_response['data']]
        self.assertTrue(all(response_name in video_names for response_name in response_names))
        self.assertTrue(all(video_name in response_names for video_name in video_names))

    def watch_and_next_videos(self, video_name, next_videos):
        with NeoGraph() as graph:
            obj = Video.select(graph).where('_.name = "{}"'.format(video_name)).first()
            response = self.client.post(
                reverse('api:watch_videos'),
                json.dumps({'data': {
                    'type': 'videos',
                    'id': obj.id,
                }}),
                content_type='application/vnd.api+json',
            )
            self.assertEqual(response.status_code, 200)
            response = self.client.get(reverse('api:next_videos'))
            self.assertEqual(response.status_code, 200)
            self.assertJSONDataVideoNames(response, next_videos)

    # GET /api/next_videos
    def test_next_videos_view(self):
        response = self.client.get(reverse('api:next_videos'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONDataVideoNames(response, ['A', 'C'])

    def test_next_videos_view_workflow(self):
        response = self.client.get(reverse('api:next_videos'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONDataVideoNames(response, ['A', 'C'])

        self.watch_and_next_videos('A', ['B', 'C'])
        self.watch_and_next_videos('C', ['B'])
        self.watch_and_next_videos('B', [])

    # GET /api/watch/
    def test_get_watch_video(self):
        response = self.client.get(reverse('api:watch_videos'))
        self.assertEqual(response.status_code, 405)

    # POST /api/watch/
    def test_post_watch_video(self):
        with NeoGraph() as graph:
            obj = Video.select(graph).where('_.name = "{}"'.format('A')).first()
            response = self.client.post(
                reverse('api:watch_videos'),
                json.dumps({'data': {
                    'type': 'videos',
                    'id': obj.id,
                }}),
                content_type='application/vnd.api+json',
            )
            self.assertEqual(response.status_code, 200)
            self.assertVideoCount(response, 1)

    def test_post_watch_video_again(self):
        with NeoGraph() as graph:
            obj = Video.select(graph).where('_.name = "{}"'.format('A')).first()
            response = self.client.post(
                reverse('api:watch_videos'),
                json.dumps({'data': {
                    'type': 'videos',
                    'id': obj.id,
                }}),
                content_type='application/vnd.api+json',
            )
            self.assertEqual(response.status_code, 200)
            self.assertVideoCount(response, 1)
            response = self.client.post(
                reverse('api:watch_videos'),
                json.dumps({'data': {
                    'type': 'videos',
                    'id': obj.id,
                }}),
                content_type='application/vnd.api+json',
            )
            self.assertEqual(response.status_code, 200)
            self.assertVideoCount(response, 0)

    def test_post_watch_video_missing_data(self):
        response = self.client.post(
            reverse('api:watch_videos'),
            content_type='application/vnd.api+json',
        )
        self.assertEqual(response.status_code, 400)

    def test_post_watch_video_wrong_data(self):
        response = self.client.post(
            reverse('api:watch_videos'),
            json.dumps({'data': {
                'type': 'videos',
                'id': '1234567',
            }}),
            content_type='application/vnd.api+json',
        )
        self.assertEqual(response.status_code, 400)


class ApiViewWrongPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user lacks the required permissions."""

    # /api/next_videos
    def test_next_videos_view(self):
        response = self.client.get(reverse('api:next_videos'))
        self.assertEqual(response.status_code, 401)

    # GET /api/watch/
    def test_get_watch_video(self):
        response = self.client.get(reverse('api:watch_videos'))
        self.assertEqual(response.status_code, 401)

    # POST /api/watch/
    def test_post_watch_video(self):
        with NeoGraph() as graph:
            obj = Video.select(graph).where('_.name = "{}"'.format('A')).first()
            response = self.client.post(
                reverse('api:watch_videos'),
                json.dumps({'videos': [obj.id]}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 401)


class ApiViewManagerTests(NeoTestCase, ApiViewWrongPermissionsMixin):
    """User testing the views is logged in as manager and therefore has the required permissions."""
    fixtures = ['users_testdata.json']
    neo_fixtures = ['api/fixtures/neo_watched_video_testdata.json']

    def setUp(self):
        self.client.login(username='manager', password='admin')


class ApiViewSocialUserests(NeoTestCase, ApiViewWrongPermissionsMixin):
    """User testing the views is logged in as social user and therefore lacking the required permissions."""
    fixtures = ['users_testdata.json']
    neo_fixtures = ['api/fixtures/neo_watched_video_testdata.json']

    def setUp(self):
        self.client.login(username='socialuser', password='admin')


class ApiViewTokenTests(NeoTestCase, ApiViewCorrectPermissionsMixin):
    """User testing the views is not logged and therefore lacking the required permissions."""
    fixtures = ['users_testdata']
    neo_fixtures = ['api/fixtures/neo_watched_video_testdata.json']

    def setUp(self):
        token = Token.objects.first()
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token ' + token.key


class ApiViewNoPermissionTests(NeoTestCase, ApiViewWrongPermissionsMixin):
    """User testing the views is not logged and therefore lacking the required permissions."""
    fixtures = ['users_testdata.json']
    neo_fixtures = ['api/fixtures/neo_watched_video_testdata.json']
