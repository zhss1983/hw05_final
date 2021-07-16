from datetime import datetime as dt
from os import path
from shutil import rmtree
from tempfile import mkdtemp

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post

User = get_user_model()


class PostsTestsCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(username=f'user_{cls.__name__}')
        cls.group = Group.objects.create(
            title=f'Group Тест_{cls.__name__}',
            slug=f'test_{cls.__name__}',
            description=f'Текст_{cls.__name__}',
        )
        cls.url_new_post = reverse('new_post')
        cls.url_index = reverse('index')
        cls.url_login = reverse('login')

    @classmethod
    def tearDownClass(cls):
        rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def img_upload(self):
        return SimpleUploadedFile(
            name='small.gif',
            content=(
                b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
            ),
            content_type='image/gif'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.__class__.user)

    def test_list_url_redirect_anonymous(self):
        """Check redirect for an unauthorized user."""
        cls = self.__class__
        now = dt.now()
        post = Post.objects.create(
            text=f'Delete Post Тест_{cls.__name__} ({now})',
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
        now = dt.now()
        context = {
            'group': cls.group.pk,
            'text': (f'Save new post {cls.__name__} ({now}).'),
            'image': self.img_upload()
        }
        self.assertFalse(Post.objects.filter(text=context['text']).exists())
        count = Post.objects.count()
        response = self.authorized_client.post(
            cls.url_new_post,
            data=context
        )
        self.assertEqual(Post.objects.count(), count + 1)
        self.assertRedirects(response, cls.url_index)
        post = Post.objects.last()
        self.assertEqual(post.text, context['text'])
        self.assertEqual(post.author, cls.user)
        self.assertEqual(post.group, cls.group)
        self.assertTrue(path.exists(post.image.path))
        context['image'].close()

    def test_auth_user_edit_post_and_correct_redirect(self):
        """Check edit post and correct redirect."""
        cls = self.__class__
        now = dt.now()
        post = Post.objects.create(
            text=f'test_forms.py Тест_{cls.__name__} ({now})',
            author=cls.user,
            group=cls.group,
        )
        group2 = Group.objects.create(
            title=f'Group Тест_{cls.__name__} №2',
            slug=f'test_{cls.__name__}_n2',
            description=f'Текст_{cls.__name__} №2',
        )
        context = {
            'group': group2.pk,
            'text': (f'Edit post ({now}).'),
        }
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
        post.refresh_from_db()
        self.assertEqual(Post.objects.count(), count)
        self.assertRedirects(response, url_post)
        self.assertEqual(post.author, cls.user)
        self.assertEqual(post.group, group2)
        self.assertEqual(post.text, context['text'])

    def test_auth_wrong_user_edit_post_and_correct_redirect(self):
        """Check wrong user could'nt edit post and correct redirect."""
        cls = self.__class__
        now = dt.now()
        wrong_user = User.objects.create(
            username='wrong_user',
        )
        post = Post.objects.create(
            text=f'test_forms.py Тест_{cls.__name__}',
            author=wrong_user,
            group=cls.group,
        )
        group3 = Group.objects.create(
            title=f'Group Тест_{cls.__name__} №3',
            slug=f'test_{cls.__name__}_n3',
            description=f'Текст_{cls.__name__} №3',
        )
        context = {
            'group': group3.pk,
            'text': (f'Edit post {cls.__name__} ({now}).'),
        }
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
        response = self.authorized_client.post(
            url_post_edit,
            data=context
        )
        self.assertEqual(count, Post.objects.count())
        post.refresh_from_db()
        self.assertRedirects(response, url_post)
        self.assertNotEqual(post.text, context['text'])
        self.assertEqual(post.author, wrong_user)
        self.assertEqual(post.group, cls.group)

    def test_not_auth_user_add_post(self):
        """Check wrong user could'nt add post and correct redirect."""
        cls = self.__class__
        now = dt.now()
        group4 = Group.objects.create(
            title=f'Group Тест_{cls.__name__} №4',
            slug=f'test_{cls.__name__}_n4',
            description=f'Текст_{cls.__name__} №4',
        )
        context = {
            'group': group4.pk,
            'text': (f'Save new post {cls.__name__} by wrong user ({now}).'),
        }
        count = Post.objects.count()
        response = self.client.post(
            cls.url_new_post,
            data=context
        )
        self.assertEqual(Post.objects.count(), count)
        self.assertRedirects(
            response,
            f'{cls.url_login}?next={cls.url_new_post}'
        )

    def test_delete_url_redirect_post(self):
        """Check redirect for an authorized user."""
        cls = self.__class__
        now = dt.now()
        post = Post.objects.create(
            text=f'Delete Post {cls.__name__} ({now})',
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
        response = self.authorized_client.post(
            url_post_delete,
            {'this_url': cls.url_index}
        )
        self.assertRedirects(response, cls.url_index)


class CommentsTestCase(TestCase):

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
        cls.url_login = reverse('login')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.__class__.user)

    def test_auth_user_add_comment(self):
        """Checking the addition of a comment."""
        cls = self.__class__
        now = dt.now()
        context = {
            'text': f'Текст комментария для posta {cls.__name__} ({now})'
        }
        count = Comment.objects.count()
        resp = self.authorized_client.post(cls.url_add_comment, data=context)
        self.assertRedirects(resp, cls.url_post)
        self.assertEqual(count + 1, Comment.objects.count())
        comment = Comment.objects.last()
        self.assertEqual(comment.text, context['text'])
        self.assertEqual(comment.author, cls.user)
        self.assertEqual(comment.post, cls.post)

    def test_not_auth_user_add_comment(self):
        """Checking the addition of a comment from not authorise user."""
        cls = self.__class__
        now = dt.now()
        context = {
            'text': f'Текст комментария для posta {cls.__name__} ({now}).'
        }
        count = Comment.objects.count()
        response = self.client.post(cls.url_add_comment, data=context)
        self.assertEqual(count, Comment.objects.count())
        self.assertRedirects(
            response,
            f'{cls.url_login}?next={cls.url_add_comment}'
        )
