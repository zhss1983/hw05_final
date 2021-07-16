from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Comment, Group, Post


class ModelTestCase(TestCase):

    def test_object_text_field(self):
        """Check __str__"""
        cls = self.__class__
        user = get_user_model().objects.create(username=f'user_{cls.__name__}')
        group = Group.objects.create(
            title=f'Тест_{cls.__name__}',
            slug=f'test_{cls.__name__}',
            description=f'Текст_{cls.__name__}',
        )
        post = Post.objects.create(
            text=f'Тест_{cls.__name__}',
            author=user,
            group=group,
        )
        comment = Comment.objects.create(
            post=post,
            author=user,
            text=f'Тест_{cls.__name__}'
        )
        models_strings = (
            (comment.text[:15], comment),
            (group.title, group),
            (post.text[:15], post),
        )
        for my_model, model in models_strings:
            with self.subTest(exept_str=my_model, model=model):
                self.assertEqual(my_model, str(model))
