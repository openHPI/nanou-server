from django.test import Client
from django.urls import reverse

from neo.tests import NeoTestCase
from groups.models import Group


class GroupViewTests(NeoTestCase):
    neo_fixtures = ['videos/fixtures/neo_video_group_testdata.json']
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
        group = Group.first()
        response = self.client.get(reverse('groups:detail', kwargs={'pk': group.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('group', response.context)
        self.assertEqual(response.context['group'], group)

    def test_get_detail_view_not_existant(self):
        response = self.client.get(reverse('groups:detail', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_detail_view_not_allowed(self):
        group = Group.first()
        response = self.client.post(reverse('groups:detail', kwargs={'pk': group.id}))
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
        group = Group.first()
        response = self.client.get(reverse('groups:update', kwargs={'pk': group.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_get_update_view_not_existant(self):
        response = self.client.get(reverse('groups:update', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_update_view(self):
        group = Group.first()
        data = {
            'name': 'Updated Group',
        }
        response = self.client.post(reverse('groups:update', kwargs={'pk': group.id}), data, follow=True)
        self.assertRedirects(response, reverse('groups:list'))

    def test_post_update_view_no_data(self):
        group = Group.first()
        response = self.client.post(reverse('groups:update', kwargs={'pk': group.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_update_view_incomplete_data(self):
        data = {}
        group = Group.first()
        response = self.client.post(reverse('groups:update', kwargs={'pk': group.id}), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_update_view_not_existant(self):
        response = self.client.post(reverse('groups:update', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_update_view_without_csrf_token(self):
        group = Group.first()
        response = self.csrf_client.post(reverse('groups:update', kwargs={'pk': group.id}))
        self.assertEqual(response.status_code, 403)

    # Delete
    def test_get_delete_view(self):
        group = Group.first()
        response = self.client.get(reverse('groups:delete', kwargs={'pk': group.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('group', response.context)
        self.assertEqual(response.context['group'], group)

    def test_get_delete_view_not_existant(self):
        response = self.client.get(reverse('groups:delete', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_delete_view(self):
        group = Group.first()
        response = self.client.post(reverse('groups:delete', kwargs={'pk': group.id}), follow=True)
        self.assertRedirects(response, reverse('groups:list'))
        self.assertNotIn(group, Group.all())

    def test_post_delete_view_not_existant(self):
        response = self.client.post(reverse('groups:delete', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_delete_view_without_csrf_token(self):
        group = Group.first()
        response = self.csrf_client.post(reverse('groups:delete', kwargs={'pk': group.id}))
        self.assertEqual(response.status_code, 403)
