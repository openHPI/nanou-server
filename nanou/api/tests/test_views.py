import json

from django.test import Client
from django.urls import reverse
from django.utils import six
from rest_framework.authtoken.models import Token

from categories.models import Category
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
        self.assertTrue(all('url' in item['attributes'] for item in json_response['data']))
        response_names = [item['attributes']['name'] for item in json_response['data']]
        self.assertEqual(video_names, response_names)

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

    # GET /api/next/
    def test_next_videos_view(self):
        response = self.client.get(reverse('api:next_videos'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONDataVideoNames(response, ['C'])

    def test_next_videos_view_workflow(self):
        response = self.client.get(reverse('api:next_videos'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONDataVideoNames(response, ['C'])

        self.watch_and_next_videos('C', ['A', 'B'])
        self.watch_and_next_videos('B', ['A'])
        self.watch_and_next_videos('A', [])

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

    # GET /api/preferences/
    def test_get_preferences(self):
        category = Category.first()
        response = self.client.get(reverse('api:preferences'))
        self.assertEqual(response.status_code, 200)
        json = self.load_response_content(response)
        self.assertEqual(json.get('data'), [{
            u'type': u'preferences',
            u'id': u'%s' % category.id,
            u'attributes': {
                u'name': u'Category',
                u'weight': 0.75,
            },
        }])

    # POST /api/preferences/
    def test_post_preferences(self):
        category = Category.first()
        response = self.client.post(
            reverse('api:preferences'),
            json.dumps({u'data': {u'type': u'preferences',  u'attributes': {u'updates': [{
                u'type': 'preferences',
                u'id': u'%s' % category.id,
                u'attributes': {
                    u'weight': 0.25,
                },
            }]}}}),
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 200, response.content)
        json_response = self.load_response_content(response)
        self.assertEqual(json_response.get('meta'), {u'count': 1})

    def test_post_preferences_missing_updates(self):
        response = self.client.post(
            reverse('api:preferences'),
            json.dumps({u'data': {u'type': u'preferences', u'attributes': {}}}),
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 400)
        json_response = self.load_response_content(response)
        self.assertEqual(json_response.get('errors'), {u'title': u'Found no preference updates'})

    def test_post_preferences_wrong_updates_format(self):
        response = self.client.post(
            reverse('api:preferences'),
            json.dumps({u'data': {u'type': u'preferences', u'updates': 1}}),
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 400)
        json_response = self.load_response_content(response)
        self.assertEqual(json_response.get('errors'), {u'title': u'Found no preference updates'})

    def test_post_preferences_missing_id(self):
        response = self.client.post(
            reverse('api:preferences'),
            json.dumps({u'data': {u'type': u'preferences', u'attributes': {u'updates': [{
                u'type': 'preferences',
                u'attributes': {
                    u'weight': 0.25,
                },
            }]}}}),
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 400)
        json_response = self.load_response_content(response)
        self.assertEqual(json_response.get('errors'), {u'title': u'Invalid preference updates'})

    def test_post_preferences_missing_attributes(self):
        category = Category.first()
        response = self.client.post(
            reverse('api:preferences'),
            json.dumps({u'data': {u'type': u'preferences', u'attributes': {u'updates': [{
                u'type': 'preferences',
                u'id': u'%s' % category.id,
            }]}}}),
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 400)
        json_response = self.load_response_content(response)
        self.assertEqual(json_response.get('errors'), {u'title': u'Invalid preference updates'})

    def test_post_preferences_missing_weight(self):
        category = Category.first()
        response = self.client.post(
            reverse('api:preferences'),
            json.dumps({u'data': {u'type': u'preferences', u'attributes': {u'updates': [{
                u'type': 'preferences',
                u'id': u'%s' % category.id,
                u'attributes': {},
            }]}}}),
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 400)
        json_response = self.load_response_content(response)
        self.assertEqual(json_response.get('errors'), {u'title': u'Invalid preference updates'})

    def test_post_preferences_invalid_id(self):
        response = self.client.post(
            reverse('api:preferences'),
            json.dumps({u'data': {u'type': u'preferences', u'attributes': {u'updates': [{
                u'type': 'preferences',
                u'id': u'0',
                u'attributes': {
                    u'weight': 0.25,
                },
            }]}}}),
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 400, response.content)
        json_response = self.load_response_content(response)
        self.assertEqual(json_response.get('errors'), {u'id': u'0', u'title': u'Found non-existing category id'})


class ApiViewWrongPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user lacks the required permissions."""

    # GET /api/next/
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
                content_type='application/vnd.api+json'
            )
            self.assertEqual(response.status_code, 401)

    # GET /api/preferences/
    def test_get_preferences(self):
        response = self.client.get(reverse('api:preferences'))
        self.assertEqual(response.status_code, 401)

    # POST /api/preferences/
    def test_post_preferences(self):
        response = self.client.post(reverse('api:preferences'))
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
        # Delete SocialUser object that is created by the Djangos post_save signal.
        # We need the node created by us because we want to create some relationships.
        with NeoGraph() as graph:
            graph.run('MATCH (a:SocialUser) WHERE NOT (a)-[:HAS_PREFERENCE]->() DELETE a')


class ApiViewNoPermissionTests(NeoTestCase, ApiViewWrongPermissionsMixin):
    """User testing the views is not logged and therefore lacking the required permissions."""
    fixtures = ['users_testdata.json']
    neo_fixtures = ['api/fixtures/neo_watched_video_testdata.json']
