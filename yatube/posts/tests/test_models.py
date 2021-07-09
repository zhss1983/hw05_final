from django.test import TestCase

from .test_setups import MySetupTestCase


class ModelTest(TestCase, MySetupTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        MySetupTestCase.setUpClass()

    @classmethod
    def tearDownClass(cls):
        MySetupTestCase.tearDownClass()
        super().tearDownClass()

    def test_post_object_text_field(self):
        """Check __str__, it must return self.text[:15]."""
        cls = self.__class__
        result_str = cls.post.text[:15]
        self.assertEqual(result_str, str(cls.post))

    def test_group_object_title_field(self):
        """Check __str__, it must return self.title."""
        cls = self.__class__
        result_str = cls.group.title
        self.assertEqual(result_str, str(cls.group))
