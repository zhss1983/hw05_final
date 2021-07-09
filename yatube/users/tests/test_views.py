from django.test import TestCase
from django.urls import reverse


class UsersViewsTests(TestCase):

    def test_url_correct_template_name(self):
        """Check matching of template name and URL address."""
        url = reverse('signup')
        template_name = 'users/signup.html'
        response = self.client.get(url)
        self.assertTemplateUsed(response, template_name=template_name)
