from django.test import Client
from django.urls import reverse

from categories.models import Category
from neo.tests import NeoTestCase


class CategoryViewCorrcetPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user has the required permissions."""
    csrf_client = Client(enforce_csrf_checks=True)

    # List
    def test_get_list_view(self):
        response = self.client.get(reverse('categories:list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('categories', response.context)
        categories = list(response.context['categories'])
        all_categories = Category.all()
        self.assertTrue(all(category in all_categories for category in categories))

    def test_post_list_view_not_allowed(self):
        response = self.client.post(reverse('categories:list'))
        self.assertEqual(response.status_code, 405)

    # Detail
    def test_get_detail_view(self):
        category = Category.get(1)
        response = self.client.get(reverse('categories:detail', kwargs={'pk': category.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('category', response.context)
        self.assertEqual(response.context['category'], category)

    def test_get_detail_view_not_existant(self):
        response = self.client.get(reverse('categories:detail', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_detail_view_not_allowed(self):
        response = self.client.post(reverse('categories:detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 405)

    # Create
    def test_get_create_view(self):
        response = self.client.get(reverse('categories:create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_post_create_view(self):
        data = {
            'name': 'Random Category',
        }
        response = self.client.post(reverse('categories:create'), data, follow=True)
        self.assertRedirects(response, reverse('categories:list'))

    def test_post_create_view_no_data(self):
        response = self.client.post(reverse('categories:create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_create_view_incomplete_data(self):
        data = {}
        response = self.client.post(reverse('categories:create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_create_view_without_csrf_token(self):
        response = self.csrf_client.post(reverse('categories:create'))
        self.assertEqual(response.status_code, 403)

    # Update
    def test_get_update_view(self):
        response = self.client.get(reverse('categories:update', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_get_update_view_not_existant(self):
        response = self.client.get(reverse('categories:update', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_update_view(self):
        data = {
            'name': 'Updated Category',
        }
        response = self.client.post(reverse('categories:update', kwargs={'pk': 1}), data, follow=True)
        self.assertRedirects(response, reverse('categories:list'))

    def test_post_update_view_no_data(self):
        response = self.client.post(reverse('categories:update', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_update_view_incomplete_data(self):
        data = {}
        response = self.client.post(reverse('categories:update', kwargs={'pk': 1}), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)  # shows form again

    def test_post_update_view_not_existant(self):
        response = self.client.post(reverse('categories:update', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_update_view_without_csrf_token(self):
        response = self.csrf_client.post(reverse('categories:update', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)

    # Delete
    def test_get_delete_view(self):
        category = Category.get(1)
        response = self.client.get(reverse('categories:delete', kwargs={'pk': category.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('category', response.context)
        self.assertEqual(response.context['category'], category)

    def test_get_delete_view_not_existant(self):
        response = self.client.get(reverse('categories:delete', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_delete_view(self):
        category = Category.get(1)
        response = self.client.post(reverse('categories:delete', kwargs={'pk': category.id}), follow=True)
        self.assertRedirects(response, reverse('categories:list'))
        self.assertNotIn(category, Category.all())

    def test_post_delete_view_not_existant(self):
        response = self.client.post(reverse('categories:delete', kwargs={'pk': 1000}))
        self.assertEqual(response.status_code, 404)

    def test_post_delete_view_without_csrf_token(self):
        response = self.csrf_client.post(reverse('categories:delete', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)


class CategoryViewWrongPermissionsMixin(object):
    """Mixins for user testing the views is logged if the user lacks the required permissions."""

    # List
    def test_get_list_view(self):
        url = reverse('categories:list')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Detail
    def test_get_detail_view(self):
        url = reverse('categories:detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Create
    def test_get_create_view(self):
        url = reverse('categories:create')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Update
    def test_get_update_view(self):
        url = reverse('categories:update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)

    # Delete
    def test_get_delete_view(self):
        url = reverse('categories:delete', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + '?next=' + url)


class CategoryViewManagerTests(NeoTestCase, CategoryViewCorrcetPermissionsMixin):
    """User testing the views is logged in as manager and therefore has the required permissions."""
    fixtures = ['users_testdata']
    neo_fixtures = ['categories/fixtures/neo_category_testdata.json']

    def setUp(self):
        self.client.login(username='manager', password='admin')


class CategoryViewSocialUserests(NeoTestCase, CategoryViewWrongPermissionsMixin):
    """User testing the views is logged in as social user and therefore lacking the required permissions."""
    fixtures = ['users_testdata']
    neo_fixtures = ['categories/fixtures/neo_category_testdata.json']

    def setUp(self):
        self.client.login(username='socialuser', password='admin')


class CategoryViewNoPermissionTests(NeoTestCase, CategoryViewWrongPermissionsMixin):
    """User testing the views is not logged and therefore lacking the required permissions."""
    fixtures = ['users_testdata']
    neo_fixtures = ['categories/fixtures/neo_category_testdata.json']
