from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


class ModelTestCase(TestCase):

    def test_object_text_field(self):
        """Check __str__"""
        user = get_user_model().objects.create(username='user_ModelTestCase')
        group = Group.objects.create(
            title='Тест_ModelTestCase',
            slug='test_ModelTestCase',
            description='Текст_ModelTestCase',
        )
        post = Post.objects.create(
            text='Тест_ModelTestCase',
            author=user,
            group=group,
        )
        model_string = (
            (post.text[:15], str(post)),
            (group.title, str(group)),
        )
        for my_model, str_model in model_string:
            with self.subTest(exept_str=post.text[:15], chk_str=str_model):
                self.assertEqual(my_model, str_model)
