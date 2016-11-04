import json

from django.test import Client
from django.urls import reverse
from django.utils import six

from neo.tests import NeoTestCase
from neo.utils import NeoGraph
from videos.models import Video


class ApiViewCorrectPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user has the required permissions."""
    csrf_client = Client(enforce_csrf_checks=True)

    def assertJSONResponse(self, response, json):
        response_content = response.content
        if six.PY3:
            response_content = str(response_content, encoding='utf8')
        self.assertJSONEqual(response_content, json)

    def watch_and_next_videos(self, video_name, next_videos):
        with NeoGraph() as graph:
            obj = Video.select(graph).where('_.name = "{}"'.format(video_name)).first()
            response = self.client.post(
                reverse('api:watched_videos'),
                json.dumps({'videos': [obj.id]}),
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 200)
            response = self.client.get(reverse('api:next_videos'))
            self.assertEqual(response.status_code, 200)
            self.assertJSONResponse(response, next_videos)

    # GET /api/next_videos
    def test_next_videos_view(self):
        response = self.client.get(reverse('api:next_videos'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONResponse(response, ['A', 'C'])

    def test_next_videos_view_workflow(self):
        response = self.client.get(reverse('api:next_videos'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONResponse(response, ['A', 'C'])

        self.watch_and_next_videos('A', ['B', 'C'])
        self.watch_and_next_videos('C', ['B'])
        self.watch_and_next_videos('B', [])

    # GET /api/watched/<video_id>
    def test_get_watch_video(self):
        response = self.client.get(reverse('api:watched_videos'))
        self.assertEqual(response.status_code, 405)

    # POST /api/watched/<video_id>
    def test_post_watch_video(self):
        with NeoGraph() as graph:
            obj = Video.select(graph).where('_.name = "{}"'.format('A')).first()
            response = self.client.post(
                reverse('api:watched_videos'),
                json.dumps({'videos': [obj.id]}),
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 200)

    def test_post_watch_video_missing_data(self):
        response = self.client.post(
            reverse('api:watched_videos'),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_post_watch_video_wrong_data(self):
        response = self.client.post(
            reverse('api:watched_videos'),
            json.dumps({'videos': 'foobar'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)


class ApiViewWrongPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user lacks the required permissions."""

    # /api/next_videos
    def test_next_videos_view(self):
        response = self.client.get(reverse('api:next_videos'))
        self.assertEqual(response.status_code, 403)

    # GET /api/watched/<video_id>
    def test_get_watch_video(self):
        response = self.client.get(reverse('api:watched_videos'))
        self.assertEqual(response.status_code, 405)

    # POST /api/watched/<video_id>
    def test_post_watch_video(self):
        with NeoGraph() as graph:
            obj = Video.select(graph).where('_.name = "{}"'.format('A')).first()
            response = self.client.post(
                reverse('api:watched_videos'),
                json.dumps({'videos': [obj.id]}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 403)


class ApiViewManagerTests(NeoTestCase, ApiViewWrongPermissionsMixin):
    """User testing the views is logged in as manager and therefore has the required permissions."""
    fixtures = ['users_testdata.json']
    neo_fixtures = ['api/fixtures/neo_watched_video_testdata.json']

    def setUp(self):
        self.client.login(username='manager', password='admin')


class ApiViewSocialUserests(NeoTestCase, ApiViewCorrectPermissionsMixin):
    """User testing the views is logged in as social user and therefore lacking the required permissions."""
    fixtures = ['users_testdata.json']
    neo_fixtures = ['api/fixtures/neo_watched_video_testdata.json']

    def setUp(self):
        self.client.login(username='socialuser', password='admin')


class ApiViewNoPermissionTests(NeoTestCase, ApiViewWrongPermissionsMixin):
    """User testing the views is not logged and therefore lacking the required permissions."""
    fixtures = ['users_testdata.json']
    neo_fixtures = ['api/fixtures/neo_watched_video_testdata.json']
