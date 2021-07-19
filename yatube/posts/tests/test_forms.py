from tempfile import mkdtemp

from django.conf import settings
from django.test import Client, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User
from .test_basetestcase import BaseTestCase


@override_settings(MEDIA_ROOT=mkdtemp(dir=settings.BASE_DIR))
class PostsTestsCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=f'user_{cls.__name__}')
        cls.group = Group.objects.create(
            title=f'Group Тест_{cls.__name__}',
            slug=f'test_{cls.__name__}',
            description=f'Текст_{cls.__name__}',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.__class__.user)

    def test_list_url_redirect_anonymous(self):
        """Check redirect for an unauthorized user."""
        cls = self.__class__
        post = Post.objects.create(
            text=f'Delete Post Тест_{cls.__name__}',
            author=cls.user,
            group=cls.group,
        )
        url_post_delete = reverse(
            'post_delete',
            kwargs={
                'username': cls.user.username,
                'post_id': post.pk
            }
        )
        url_post_edit = reverse(
            'post_edit',
            kwargs={
                'username': cls.user.username,
                'post_id': post.pk
            }
        )
        url_list = (
            cls.url_new_post,
            url_post_edit,
            url_post_delete,
        )
        for url in url_list:
            response = self.client.post(url)
            with self.subTest(url=url):
                self.assertRedirects(response, f'{cls.url_login}?next={url}')

    def test_auth_user_add_post_and_correct_redirect(self):
        """Check save post and correct redirect."""
        cls = self.__class__
        context = {
            'group': cls.group.pk,
            'text': f'Save new post {cls.__name__}.',
            'image': cls.img_upload()
        }
        self.assertFalse(Post.objects.filter(text=context['text']).exists())
        count = Post.objects.count()
        response = self.authorized_client.post(cls.url_new_post, data=context)
        self.assertRedirects(response, cls.url_index)
        self.assertEqual(Post.objects.count(), count + 1)
        post = Post.objects.last()
        content = {
            'text': context['text'],
            'author': cls.user,
            'group': cls.group,
            'image': cls.image_file_name
        }
        self.assert_post(post, content)

    def test_auth_user_edit_post_and_correct_redirect(self):
        """Check edit post and correct redirect."""
        cls = self.__class__
        post = Post.objects.create(
            text=f'test_forms.py Тест_{cls.__name__}',
            author=cls.user,
            group=cls.group,
        )
        pub_date = post.pub_date
        pk = post.pk
        group2 = Group.objects.create(
            title=f'Group Тест_{cls.__name__} №2',
            slug=f'test_{cls.__name__}_n2',
            description=f'Текст_{cls.__name__} №2',
        )
        context = {'group': group2.pk, 'text': 'Edit post.'}
        url_post_edit = reverse(
            'post_edit',
            kwargs={
                'username': cls.user.username,
                'post_id': post.pk
            }
        )
        url_post = reverse(
            'post',
            kwargs={
                'username': cls.user.username,
                'post_id': post.pk
            }
        )
        count = Post.objects.count()
        response = self.authorized_client.post(url_post_edit, data=context)
        self.assertRedirects(response, url_post)
        self.assertEqual(Post.objects.count(), count)
        post.refresh_from_db()
        content = {
            'pk': pk,
            'text': context['text'],
            'author': cls.user,
            'group': group2,
            'pub_date': pub_date,
        }
        self.assert_post(post, content)

    def test_auth_wrong_user_edit_post_and_correct_redirect(self):
        """Check wrong user could'nt edit post and correct redirect."""
        cls = self.__class__
        wrong_user = User.objects.create(username='wrong_user')
        post = Post.objects.create(
            text=f'test_forms.py Тест_{cls.__name__}',
            author=wrong_user,
            group=cls.group,
        )
        pub_date = post.pub_date
        pk = post.pk
        base_text = post.text
        group3 = Group.objects.create(
            title=f'Group Тест_{cls.__name__} №3',
            slug=f'test_{cls.__name__}_n3',
            description=f'Текст_{cls.__name__} №3',
        )
        context = {'group': group3.pk, 'text': f'Edit post {cls.__name__}.'}
        url_post_edit = reverse(
            'post_edit',
            kwargs={
                'username': wrong_user.username,
                'post_id': post.pk
            }
        )
        url_post = reverse(
            'post',
            kwargs={
                'username': wrong_user.username,
                'post_id': post.pk
            }
        )
        count = Post.objects.count()
        response = self.authorized_client.post(url_post_edit, data=context)
        self.assertRedirects(response, url_post)
        self.assertEqual(count, Post.objects.count())
        post.refresh_from_db()
        content = {
            'pk': pk,
            'text': base_text,
            'author': wrong_user,
            'group': cls.group,
            'pub_date': pub_date
        }
        self.assert_post(post, content)

    def test_not_auth_user_add_post(self):
        """Check wrong user could'nt add post and correct redirect."""
        cls = self.__class__
        context = {
            'group': cls.group.pk,
            'text': f'Save new post {cls.__name__} by wrong user.',
        }
        count = Post.objects.count()
        response = self.client.post(
            cls.url_new_post,
            data=context
        )
        self.assertRedirects(
            response,
            f'{cls.url_login}?next={cls.url_new_post}'
        )
        self.assertEqual(Post.objects.count(), count)

    def test_delete_url_redirect_post(self):
        """Check redirect for an authorized user."""
        cls = self.__class__
        post = Post.objects.create(
            text=f'Delete Post {cls.__name__} ',
            author=cls.user,
            group=cls.group,
        )
        url_post_delete = reverse(
            'post_delete',
            kwargs={
                'username': cls.user.username,
                'post_id': post.pk
            }
        )
        count = Post.objects.count()
        response = self.authorized_client.post(
            url_post_delete,
            {'this_url': cls.url_index}
        )
        self.assertRedirects(response, cls.url_index)
        self.assertEqual(count - 1, Post.objects.count())


class CommentsTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=f'user_{cls.__name__}')
        cls.group = Group.objects.create(
            title=f'Тест_{cls.__name__}',
            slug=f'test_{cls.__name__}',
            description=f'Текст_{cls.__name__}',
        )
        cls.post = Post.objects.create(
            text=f'Тест {cls.__name__}',
            author=cls.user,
            group=cls.group,
        )
        cls.url_add_comment = reverse(
            'add_comment',
            kwargs={
                'username': cls.user.username,
                'post_id': cls.post.pk
            }
        )
        cls.url_post = reverse(
            'post',
            kwargs={
                'username': cls.user.username,
                'post_id': cls.post.pk
            }
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.__class__.user)

    def test_auth_user_add_comment(self):
        """Checking the addition of a comment."""
        cls = self.__class__
        context = {'text': f'Текст комментария для posta {cls.__name__}'}
        count = Comment.objects.count()
        resp = self.authorized_client.post(cls.url_add_comment, data=context)
        self.assertRedirects(resp, cls.url_post)
        self.assertEqual(count + 1, Comment.objects.count())
        comment = Comment.objects.last()
        content = {
            'text': context['text'],
            'author': cls.user,
            'post': cls.post
        }
        self.assert_comment(comment, content)

    def test_not_auth_user_add_comment(self):
        """Checking the addition of a comment from not authorise user."""
        cls = self.__class__
        context = {'text': f'Текст комментария для posta {cls.__name__}.'}
        count = Comment.objects.count()
        response = self.client.post(cls.url_add_comment, data=context)
        self.assertRedirects(
            response,
            f'{cls.url_login}?next={cls.url_add_comment}'
        )
        self.assertEqual(count, Comment.objects.count())
