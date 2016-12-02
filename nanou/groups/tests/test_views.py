from django.test import Client
from django.urls import reverse

from groups.models import Group
from neo.tests import NeoTestCase


class GroupViewCorrcetPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user has the required permissions."""
    csrf_client = Client(enforce_csrf_checks=True)

    # List
    def test_get_list_view(self):
        response = self.client.get(reverse('groups:list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('groups', response.context)
        groups = list(response.context['groups'])
        all_groups = Group.all()
        self.assertTrue(all(group in all_groups for group in groups))

    def test_post_list_view_not_allowed(self):
        response = self.client.post(reverse('groups:list'))
        self.assertEqual(response.status_code, 405)

    # Detail
    def test_get_detail_view(self):
        group = Group.get(1)
        response = self.client.get(reverse('groups:detail', kwargs={'pk': group.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('group', response.context)
        self.assertEqual(response.context['group'], group)

    def test_get_detail_view_not_existant(self):
        response = self.client.get(reverse('groups:detail', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_detail_view_not_allowed(self):
        response = self.client.post(reverse('groups:detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 405)

    # Create
    def test_get_create_view(self):
        response = self.client.get(reverse('groups:create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_post_create_view(self):
        data = {
            'name': 'Random Group',
        }
        response = self.client.post(reverse('groups:create'), data, follow=True)
        self.assertRedirects(response, reverse('groups:list'))

    def test_post_create_view_no_data(self):
        response = self.client.post(reverse('groups:create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_create_view_incomplete_data(self):
        data = {}
        response = self.client.post(reverse('groups:create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_create_view_without_csrf_token(self):
        response = self.csrf_client.post(reverse('groups:create'))
        self.assertEqual(response.status_code, 403)

    # Update
    def test_get_update_view(self):
        response = self.client.get(reverse('groups:update', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_get_update_view_not_existant(self):
        response = self.client.get(reverse('groups:update', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_update_view(self):
        data = {
            'name': 'Updated Group',
        }
        response = self.client.post(reverse('groups:update', kwargs={'pk': 1}), data, follow=True)
        self.assertRedirects(response, reverse('groups:list'))

    def test_post_update_view_no_data(self):
        response = self.client.post(reverse('groups:update', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_update_view_incomplete_data(self):
        data = {}
        response = self.client.post(reverse('groups:update', kwargs={'pk': 1}), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_update_view_not_existant(self):
        response = self.client.post(reverse('groups:update', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_update_view_without_csrf_token(self):
        response = self.csrf_client.post(reverse('groups:update', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)

    # Delete
    def test_get_delete_view(self):
        group = Group.get(1)
        response = self.client.get(reverse('groups:delete', kwargs={'pk': group.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('group', response.context)
        self.assertEqual(response.context['group'], group)

    def test_get_delete_view_not_existant(self):
        response = self.client.get(reverse('groups:delete', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_delete_view(self):
        group = Group.get(1)
        response = self.client.post(reverse('groups:delete', kwargs={'pk': group.id}), follow=True)
        self.assertRedirects(response, reverse('groups:list'))
        self.assertNotIn(group, Group.all())

    def test_post_delete_view_not_existant(self):
        response = self.client.post(reverse('groups:delete', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_delete_view_without_csrf_token(self):
        response = self.csrf_client.post(reverse('groups:delete', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)


class GroupViewWrongPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user lacks the required permissions."""

    # List
    def test_get_list_view(self):
        url = reverse('groups:list')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Detail
    def test_get_detail_view(self):
        url = reverse('groups:detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Create
    def test_get_create_view(self):
        url = reverse('groups:create')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Update
    def test_get_update_view(self):
        url = reverse('groups:update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Delete
    def test_get_delete_view(self):
        url = reverse('groups:delete', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)


class GroupViewManagerTests(NeoTestCase, GroupViewCorrcetPermissionsMixin):
    """User testing the views is logged in as manager and therefore has the required permissions."""
    fixtures = ['users_testdata']
    neo_fixtures = ['videos/fixtures/neo_video_group_testdata.json']

    def setUp(self):
        self.client.login(username='manager', password='admin')


class GroupViewSocialUserests(NeoTestCase, GroupViewWrongPermissionsMixin):
    """User testing the views is logged in as social user and therefore lacking the required permissions."""
    fixtures = ['users_testdata']
    neo_fixtures = ['videos/fixtures/neo_video_group_testdata.json']

    def setUp(self):
        self.client.login(username='socialuser', password='admin')


class GroupViewNoPermissionTests(NeoTestCase, GroupViewWrongPermissionsMixin):
    """User testing the views is not logged and therefore lacking the required permissions."""
    fixtures = ['users_testdata']
    neo_fixtures = ['videos/fixtures/neo_video_group_testdata.json']
