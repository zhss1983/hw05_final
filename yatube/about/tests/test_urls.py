from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_list = (
            ('about:author', '/about/author/'),
            ('about:tech', '/about/tech/'),
        )

    def test_url_exists_at_desired_location(self):
        """Check addres available."""
        for url, abs_url in self.__class__.url_list:
            with self.subTest(url=url):
                response = self.client.get(reverse(url))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_name_correct(self):
        """Check corresponds of absolur url and url by name."""
        for url, abs_url in self.__class__.url_list:
            with self.subTest(url=url):
                self.assertEqual(reverse(url), abs_url)
