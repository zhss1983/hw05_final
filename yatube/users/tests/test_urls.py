from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class UsersURLTests(TestCase):

    def test_absolute_url_path_by_name(self):
        """Check absolute url paths."""
        name = reverse('signup')
        url = '/auth/signup/'
        self.assertEqual(name, url)

    def test_url_exists_at_desired_location(self):
        """Check addres available."""
        url = reverse('signup')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
