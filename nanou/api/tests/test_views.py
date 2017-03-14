import json
from datetime import datetime

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

    def assertJSONDataVideoNames(self, response, video_names):
        json_response = self.load_response_content(response)
        self.assertIn('data', json_response)
        self.assertTrue(all('attributes' in item for item in json_response['data']))
        self.assertTrue(all('name' in item['attributes'] for item in json_response['data']))
        self.assertTrue(all('url' in item['attributes'] for item in json_response['data']))
        self.assertTrue(all('stream_url' in item['attributes'] for item in json_response['data']))
        self.assertTrue(all('provider_name' in item['attributes'] for item in json_response['data']))
        self.assertTrue(all('tags' in item['attributes'] for item in json_response['data']))
        response_names = [item['attributes']['name'] for item in json_response['data']]
        self.assertEqual(video_names, response_names)

    def assertJSONDataSurveyLink(self, response, survey_link):
        json_response = self.load_response_content(response)
        self.assertIn('data', json_response)
        self.assertTrue('attributes' in json_response['data'])
        link = json_response['data']['attributes'].get('link', None)
        self.assertEqual(link, survey_link)

    def watch_and_next_videos(self, video_name, next_videos):
        with NeoGraph() as graph:
            obj = Video.select(graph).where('_.name = "{}"'.format(video_name)).first()
            response = self.client.post(
                reverse('api:watch_videos'),
                json.dumps({'data': {
                    'type': 'watches',
                    'attributes': {
                        'video_id': obj.id,
                        'date': datetime.now().isoformat(),
                        'rating': 1,
                        'progress': 1,
                    }
                }}),
                content_type='application/vnd.api+json',
            )
            self.assertEqual(response.status_code, 204)
            response = self.client.get(reverse('api:next_videos'))
            self.assertEqual(response.status_code, 200)
            self.assertJSONDataVideoNames(response, next_videos)

    def dismiss_and_next_videos(self, video_name, next_videos):
        with NeoGraph() as graph:
            obj = Video.select(graph).where('_.name = "{}"'.format(video_name)).first()
            response = self.client.post(
                reverse('api:watch_videos'),
                json.dumps({'data': {
                    'type': 'watches',
                    'attributes': {
                        'video_id': obj.id,
                        'date': datetime.now().isoformat(),
                        'rating': -1,
                        'progress': 0,
                    }
                }}),
                content_type='application/vnd.api+json',
            )
            self.assertEqual(response.status_code, 204)
            response = self.client.get(reverse('api:next_videos'))
            self.assertEqual(response.status_code, 200)
            self.assertJSONDataVideoNames(response, next_videos)

    def watch_and_history(self, video_name, history_videos):
        with NeoGraph() as graph:
            obj = Video.select(graph).where('_.name = "{}"'.format(video_name)).first()
            response = self.client.post(
                reverse('api:watch_videos'),
                json.dumps({'data': {
                    'type': 'watches',
                    'attributes': {
                        'video_id': obj.id,
                        'date': datetime.now().isoformat(),
                        'rating': 1,
                        'progress': 1,
                    }
                }}),
                content_type='application/vnd.api+json',
            )
            self.assertEqual(response.status_code, 204)
            response = self.client.get(reverse('api:history'))
            self.assertEqual(response.status_code, 200)
            self.assertJSONDataVideoNames(response, history_videos)

    def dismiss_and_history(self, video_name, history_videos):
        with NeoGraph() as graph:
            obj = Video.select(graph).where('_.name = "{}"'.format(video_name)).first()
            response = self.client.post(
                reverse('api:watch_videos'),
                json.dumps({'data': {
                    'type': 'watches',
                    'attributes': {
                        'video_id': obj.id,
                        'date': datetime.now().isoformat(),
                        'rating': -1,
                        'progress': 0,
                    }
                }}),
                content_type='application/vnd.api+json',
            )
            self.assertEqual(response.status_code, 204)
            response = self.client.get(reverse('api:history'))
            self.assertEqual(response.status_code, 200)
            self.assertJSONDataVideoNames(response, history_videos)

    def watch_and_survey(self, video_name, survey_link):
        with NeoGraph() as graph:
            obj = Video.select(graph).where('_.name = "{}"'.format(video_name)).first()
            response = self.client.post(
                reverse('api:watch_videos'),
                json.dumps({'data': {
                    'type': 'watches',
                    'attributes': {
                        'video_id': obj.id,
                        'date': datetime.now().isoformat(),
                        'rating': 1,
                        'progress': 1,
                    }
                }}),
                content_type='application/vnd.api+json',
            )
            self.assertEqual(response.status_code, 204)
            response = self.client.get(reverse('api:survey_latest'))
            self.assertEqual(response.status_code, 200)
            self.assertJSONDataSurveyLink(response, survey_link)

    def complete_survey(self, survey_id):
        response = self.client.post(reverse('api:survey_complete', kwargs={'pk': survey_id}))
        self.assertEqual(response.status_code, 204)

    # GET /api/next/
    def test_next_videos_view(self):
        response = self.client.get(reverse('api:next_videos'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONDataVideoNames(response, ['A'])

    def test_next_videos_view_workflow(self):
        response = self.client.get(reverse('api:next_videos'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONDataVideoNames(response, ['A'])

        self.watch_and_next_videos('A', ['C'])
        self.watch_and_next_videos('C', ['B'])
        self.watch_and_next_videos('B', [])

    def test_next_videos_view_workflow_dimiss(self):
        response = self.client.get(reverse('api:next_videos'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONDataVideoNames(response, ['A'])

        self.dismiss_and_next_videos('A', ['C'])
        self.dismiss_and_next_videos('C', [])

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
                    'type': 'watches',
                    'attributes': {
                        'video_id': obj.id,
                        'date': datetime.now().isoformat(),
                        'rating': 1,
                        'progress': 1,
                    }
                }}),
                content_type='application/vnd.api+json',
            )
            self.assertEqual(response.status_code, 204, response.content)

    def test_post_watch_video_again(self):
        with NeoGraph() as graph:
            obj = Video.select(graph).where('_.name = "{}"'.format('A')).first()
            response = self.client.post(
                reverse('api:watch_videos'),
                json.dumps({'data': {
                    'type': 'watches',
                    'attributes': {
                        'video_id': obj.id,
                        'date': datetime.now().isoformat(),
                        'rating': 1,
                        'progress': 1,
                    }
                }}),
                content_type='application/vnd.api+json',
            )

            self.assertEqual(response.status_code, 204, response.content)
            response = self.client.post(
                reverse('api:watch_videos'),
                json.dumps({'data': {
                    'type': 'watches',
                    'attributes': {
                        'video_id': obj.id,
                        'date': datetime.now().isoformat(),
                        'rating': 0.5,
                        'progress': 1,
                    }
                }}),
                content_type='application/vnd.api+json',
            )
            self.assertEqual(response.status_code, 204, response.content)

    def test_post_watch_video_missing_data(self):
        response = self.client.post(
            reverse('api:watch_videos'),
            content_type='application/vnd.api+json',
        )
        self.assertEqual(response.status_code, 400)

    def test_post_watch_video_missing_date(self):
        with NeoGraph() as graph:
            obj = Video.select(graph).where('_.name = "{}"'.format('A')).first()
            response = self.client.post(
                reverse('api:watch_videos'),
                json.dumps({'data': {
                    'type': 'watches',
                    'attributes': {
                        'video_id': obj.id,
                        'rating': 1,
                        'progress': 1,
                    }
                }}),
                content_type='application/vnd.api+json',
            )
            self.assertEqual(response.status_code, 400)

    def test_post_watch_video_missing_rating(self):
        with NeoGraph() as graph:
            obj = Video.select(graph).where('_.name = "{}"'.format('A')).first()
            response = self.client.post(
                reverse('api:watch_videos'),
                json.dumps({'data': {
                    'type': 'watches',
                    'attributes': {
                        'video_id': obj.id,
                        'date': datetime.now().isoformat(),
                        'progress': 1,
                    }
                }}),
                content_type='application/vnd.api+json',
            )
            self.assertEqual(response.status_code, 400)

    def test_post_watch_video_missing_progress(self):
        with NeoGraph() as graph:
            obj = Video.select(graph).where('_.name = "{}"'.format('A')).first()
            response = self.client.post(
                reverse('api:watch_videos'),
                json.dumps({'data': {
                    'type': 'watches',
                    'attributes': {
                        'video_id': obj.id,
                        'date': datetime.now().isoformat(),
                        'rating': 1,
                    }
                }}),
                content_type='application/vnd.api+json',
            )
            self.assertEqual(response.status_code, 400)

    def test_post_watch_video_wrong_id(self):
        response = self.client.post(
            reverse('api:watch_videos'),
            json.dumps({'data': {
                'type': 'watches',
                'attributes': {
                    'video_id': '1234567',
                }
            }}),
            content_type='application/vnd.api+json',
        )
        self.assertEqual(response.status_code, 400)

    # GET /api/history
    def test_get_history(self):
        response = self.client.get(reverse('api:history'))
        self.assertEqual(response.status_code, 200)
        json_content = self.assertJSONDataVideoNames(response, [])

    def test_get_history_workflow(self):
        response = self.client.get(reverse('api:history'))
        self.assertEqual(response.status_code, 200)
        json_content = self.assertJSONDataVideoNames(response, [])

        self.watch_and_history('C', ['C'])
        self.watch_and_history('A', ['A', 'C'])
        self.watch_and_history('B', ['B', 'A', 'C'])

    def test_get_history_workflow_dismiss(self):
        response = self.client.get(reverse('api:history'))
        self.assertEqual(response.status_code, 200)
        json_content = self.assertJSONDataVideoNames(response, [])

        self.dismiss_and_history('C', [])
        self.dismiss_and_history('A', [])

    # GET /api/preferences/
    def test_get_preferences(self):
        response = self.client.get(reverse('api:preferences'))
        self.assertEqual(response.status_code, 200)
        json = self.load_response_content(response)
        self.assertEqual(json.get('data'), [{
            u'type': u'preferences',
            u'id': u'2',
            u'attributes': {
                u'name': u'aMusic',
                u'weight': 0.5,
            }
        }, {
            u'type': u'preferences',
            u'id': u'1',
            u'attributes': {
                u'name': u'Category',
                u'weight': 0.75,
            }
        }])

    # PATCH /api/preferences/<pk>/
    def test_patch_preferences(self):
        response = self.client.patch(
            reverse('api:preference_update', kwargs={'pk': 1}),
            json.dumps({u'data': {
                u'type': 'preferences',
                u'id': u'1',
                u'attributes': {
                    u'weight': 0.25,
                },
            }}),
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 204, response.content)

    def test_patch_preferences_new(self):
        response = self.client.patch(
            reverse('api:preference_update', kwargs={'pk': 2}),
            json.dumps({u'data': {
                u'type': 'preferences',
                u'id': u'2',
                u'attributes': {
                    u'weight': 0.1,
                },
            }}),
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 204, response.content)

    def test_patch_preferences_missing_id(self):
        response = self.client.patch(
            reverse('api:preference_update', kwargs={'pk': 1}),
            json.dumps({u'data': {
                u'type': 'preferences',
                u'attributes': {
                    u'weight': 0.25,
                },
            }}),
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 400)

    def test_patch_preferences_missing_weight(self):
        response = self.client.patch(
            reverse('api:preference_update', kwargs={'pk': 1}),
            json.dumps({u'data': {
                u'type': 'preferences',
                u'id': u'1',
                u'attributes': {},
            }}),
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 400)
        json_response = self.load_response_content(response)
        self.assertEqual(json_response.get('errors'), {u'title': u'Invalid preference updates'})

    def test_patch_preferences_id_mismatch(self):
        response = self.client.patch(
            reverse('api:preference_update', kwargs={'pk': 1}),
            json.dumps({u'data': {
                u'type': 'preferences',
                u'id': u'0',
                u'attributes': {
                    u'weight': 0.25,
                },
            }}),
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 400)
        json_response = self.load_response_content(response)
        self.assertEqual(json_response.get('errors'), {u'title': u'Invalid preference updates'})

    def test_patch_preferences_not_existing(self):
        response = self.client.patch(
            reverse('api:preference_update', kwargs={'pk': 0}),
            json.dumps({u'data': {
                u'type': 'preferences',
                u'id': u'0',
                u'attributes': {
                    u'weight': 0.25,
                },
            }}),
            content_type='application/vnd.api+json'
        )
        self.assertEqual(response.status_code, 400, response.content)
        json_response = self.load_response_content(response)
        self.assertEqual(json_response.get('errors'), {u'id': u'0', u'title': u'Found non-existing category id'})

    # GET /api/surveys/latest
    def test_get_latest_survey(self):
        response = self.client.get(reverse('api:survey_latest'))
        self.assertEqual(response.status_code, 200)
        json = self.load_response_content(response)
        self.assertEqual(json, {
            'data': {
                'type': 'surveys',
                'id': None,
                'attributes': {
                }
            }
        })

    def test_get_survey_workflow(self):
        response = self.client.get(reverse('api:survey_latest'))
        self.assertEqual(response.status_code, 200)
        json_content = self.assertJSONDataSurveyLink(response, None)

        self.watch_and_survey('C', 'https://www.google.com/')
        self.watch_and_survey('A', 'https://www.github.com/')
        self.watch_and_survey('B', 'https://www.github.com/')

    def test_get_survey_workflow_complete_1(self):
        response = self.client.get(reverse('api:survey_latest'))
        self.assertEqual(response.status_code, 200)
        json_content = self.assertJSONDataSurveyLink(response, None)

        self.watch_and_survey('C', 'https://www.google.com/')
        self.complete_survey(1)
        self.watch_and_survey('A', 'https://www.facebook.com/')
        self.complete_survey(2)
        self.watch_and_survey('B', None)

    def test_get_survey_workflow_complete_2(self):
        response = self.client.get(reverse('api:survey_latest'))
        self.assertEqual(response.status_code, 200)
        json_content = self.assertJSONDataSurveyLink(response, None)

        self.watch_and_survey('C', 'https://www.google.com/')
        self.watch_and_survey('A', 'https://www.github.com/')
        self.complete_survey(2)
        self.watch_and_survey('B', None)

    # PATCH /api/surveys/<pk>/complete
    def test_post_complete_survey(self):
        response = self.client.post(reverse('api:survey_complete', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 204)


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
                json.dumps({'data': {
                    'type': 'watches',
                    'attributes': {
                        'video_id': obj.id,
                        'date': datetime.now().isoformat(),
                        'rating': 1,
                        'progress': 1,
                    }
                }}),
                content_type='application/vnd.api+json',
            )
            self.assertEqual(response.status_code, 401)

    # GET /api/history
    def test_get_history(self):
        response = self.client.get(reverse('api:history'))
        self.assertEqual(response.status_code, 401)

    # GET /api/preferences/
    def test_get_preferences(self):
        response = self.client.get(reverse('api:preferences'))
        self.assertEqual(response.status_code, 401)

    # PATCH /api/preferences/<pk>/
    def test_patch_preferences(self):
        response = self.client.post(reverse('api:preference_update', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 401)

    # GET /api/surveys/latest
    def test_get_latest_survey(self):
        response = self.client.get(reverse('api:survey_latest'))
        self.assertEqual(response.status_code, 401)

    # PATCH /api/surveys/<pk>/complete
    def test_post_complete_survey(self):
        response = self.client.post(reverse('api:survey_complete', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 401)


class ApiViewManagerTests(NeoTestCase, ApiViewWrongPermissionsMixin):
    """User testing the views is logged in as manager and therefore has the required permissions."""
    fixtures = ['users_testdata.json']
    neo_fixtures = ['api/fixtures/neo_watched_video_testdata.json']

    def setUp(self):
        self.client.login(username='manager', password='admin')


class ApiViewSocialUserests(NeoTestCase, ApiViewWrongPermissionsMixin):
    """User testing the views is logged in as social user and therefore lacking the required permissions."""
    fixtures = ['users_testdata.json', 'surveys_testdata.json']
    neo_fixtures = ['api/fixtures/neo_watched_video_testdata.json']

    def setUp(self):
        self.client.login(username='socialuser', password='admin')


class ApiViewTokenTests(NeoTestCase, ApiViewCorrectPermissionsMixin):
    """User testing the views is not logged and therefore lacking the required permissions."""
    fixtures = ['users_testdata', 'surveys_testdata.json']
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
    fixtures = ['users_testdata.json', 'surveys_testdata.json']
    neo_fixtures = ['api/fixtures/neo_watched_video_testdata.json']
