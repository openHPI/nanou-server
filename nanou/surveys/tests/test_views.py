from django.test import Client, TestCase
from django.urls import reverse

from surveys.models import Survey


class SurveyViewCorrcetPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user has the required permissions."""
    csrf_client = Client(enforce_csrf_checks=True)

    # List
    def test_get_list_view(self):
        response = self.client.get(reverse('surveys:list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('surveys', response.context)
        surveys = list(response.context['surveys'])
        all_surveys = Survey.objects.all()
        self.assertTrue(all(survey in all_surveys for survey in surveys))

    def test_post_list_view_not_allowed(self):
        response = self.client.post(reverse('surveys:list'))
        self.assertEqual(response.status_code, 405)

    # Detail
    def test_get_detail_view(self):
        survey = Survey.objects.get(pk=1)
        response = self.client.get(reverse('surveys:detail', kwargs={'pk': survey.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('survey', response.context)
        self.assertEqual(response.context['survey'], survey)

    def test_get_detail_view_not_existant(self):
        response = self.client.get(reverse('surveys:detail', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_detail_view_not_allowed(self):
        response = self.client.post(reverse('surveys:detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 405)

    # Create
    def test_get_create_view(self):
        response = self.client.get(reverse('surveys:create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_post_create_view(self):
        data = {
            'name': 'Random Survey',
            'link': 'https://www.facebook.com',
            'secondary_lin': 'https://www.github.com',
            'watch_minimum' : 2,
        }
        response = self.client.post(reverse('surveys:create'), data, follow=True)
        self.assertRedirects(response, reverse('surveys:list'))

    def test_post_create_view_no_data(self):
        response = self.client.post(reverse('surveys:create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_create_view_incomplete_data(self):
        data = {}
        response = self.client.post(reverse('surveys:create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_create_view_without_csrf_token(self):
        response = self.csrf_client.post(reverse('surveys:create'))
        self.assertEqual(response.status_code, 403)

    # Update
    def test_get_update_view(self):
        response = self.client.get(reverse('surveys:update', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_get_update_view_not_existant(self):
        response = self.client.get(reverse('surveys:update', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_update_view(self):
        data = {
            'name': 'Updated Survey',
            'link': 'https://www.facebook.com',
            'secondary_lin': 'https://www.github.com',
            'watch_minimum' : 2,
        }
        response = self.client.post(reverse('surveys:update', kwargs={'pk': 1}), data, follow=True)
        self.assertRedirects(response, reverse('surveys:list'))

    def test_post_update_view_no_data(self):
        response = self.client.post(reverse('surveys:update', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_update_view_incomplete_data(self):
        data = {}
        response = self.client.post(reverse('surveys:update', kwargs={'pk': 1}), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_update_view_not_existant(self):
        response = self.client.post(reverse('surveys:update', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_update_view_without_csrf_token(self):
        response = self.csrf_client.post(reverse('surveys:update', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)

    # Delete
    def test_get_delete_view(self):
        survey = Survey.objects.get(pk=1)
        response = self.client.get(reverse('surveys:delete', kwargs={'pk': survey.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('survey', response.context)
        self.assertEqual(response.context['survey'], survey)

    def test_get_delete_view_not_existant(self):
        response = self.client.get(reverse('surveys:delete', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_delete_view(self):
        survey = Survey.objects.get(pk=1)
        response = self.client.post(reverse('surveys:delete', kwargs={'pk': survey.id}), follow=True)
        self.assertRedirects(response, reverse('surveys:list'))
        self.assertNotIn(survey, Survey.objects.all())

    def test_post_delete_view_not_existant(self):
        response = self.client.post(reverse('surveys:delete', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_delete_view_without_csrf_token(self):
        response = self.csrf_client.post(reverse('surveys:delete', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)


class SurveyViewWrongPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user lacks the required permissions."""

    # List
    def test_get_list_view(self):
        url = reverse('surveys:list')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Detail
    def test_get_detail_view(self):
        url = reverse('surveys:detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Create
    def test_get_create_view(self):
        url = reverse('surveys:create')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Update
    def test_get_update_view(self):
        url = reverse('surveys:update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Delete
    def test_get_delete_view(self):
        url = reverse('surveys:delete', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)


class SurveyViewManagerTests(TestCase, SurveyViewCorrcetPermissionsMixin):
    """User testing the views is logged in as manager and therefore has the required permissions."""
    fixtures = ['users_testdata', 'surveys_testdata']

    def setUp(self):
        self.client.login(username='manager', password='admin')


class SurveyViewSocialUserTests(TestCase, SurveyViewWrongPermissionsMixin):
    """User testing the views is logged in as social user and therefore lacking the required permissions."""
    fixtures = ['users_testdata', 'surveys_testdata']

    def setUp(self):
        self.client.login(username='socialuser', password='admin')


class SurveyViewNoPermissionTests(TestCase, SurveyViewWrongPermissionsMixin):
    """User testing the views is not logged and therefore lacking the required permissions."""
    fixtures = ['users_testdata', 'surveys_testdata']
