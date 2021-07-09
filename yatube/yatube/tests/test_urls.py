from http import HTTPStatus

from django.test import TestCase


class StaticURLTests(TestCase):

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_not_found(self):
        response = self.client.get('/some_strange_404_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
