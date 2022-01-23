from django.test import TestCase

from ..models import Comment, Group, Post, User


class ModelTestCase(TestCase):

    def test_object_text_field(self):
        """Check __str__"""
        cls = self.__class__
        user = User.objects.create(username=f'user_{cls.__name__}')
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
        models_string_presentations = (
            (comment.text[:15], comment),
            (group.title, group),
            (post.text[:15], post),
        )
        for string_presentation, model in models_string_presentations:
            with self.subTest(exept_str=string_presentation, model=model):
                self.assertEqual(string_presentation, str(model))
