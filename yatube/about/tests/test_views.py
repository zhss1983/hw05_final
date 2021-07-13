from django.test import TestCase
from django.urls import reverse


class TemplateTestCase(TestCase):

    def test_url_uses_correct_template(self):
        """Check matching of template name and URL address."""
        url_list = (
            ('about:author', 'about/author.html', '/about/author/'),
            ('about:tech', 'about/tech.html', '/about/tech/'),
        )
        for url, template_name in url_list:
            with self.subTest(url=url):
                response = self.client.get(reverse(url))
                self.assertTemplateUsed(response,
                                        template_name=template_name)
