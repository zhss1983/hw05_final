from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_list = (
            (reverse('about:author'), 'about/author.html', '/about/author/'),
            (reverse('about:tech'), 'about/tech.html', '/about/tech/'),
        )

    def test_url_exists_at_desired_location(self):
        """Check addres available."""
        for url, tmp, abs_url in self.__class__.url_list:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_name_correct(self):
        """Check corresponds of absolur url and url by name."""
        for url, tmp, abs_url in self.__class__.url_list:
            with self.subTest(url=url):
                self.assertEqual(url, abs_url)

    def test_url_uses_correct_template(self):
        """Check matching of template name and URL address."""
        for url, template_name, abs_url in self.__class__.url_list:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template_name=template_name)
