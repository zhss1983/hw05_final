from http import HTTPStatus
from os import path
import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class PostsTestsCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = 'tempfile_media'
        cls.user = User.objects.create(username='user_PostsTestsCase')
        cls.user_follow = User.objects.create(
            username='user_follow',
        )
        cls.group = Group.objects.create(
            title='Group Тест_PostsTestsCase',
            slug='test_PostsTestsCase',
            description='Текст_PostsTestsCase',
        )
        img = cls.img_upload()
        cls.post = Post.objects.create(
            text='test_forms.py Тест_PostsTestsCase',
            author=cls.user,
            group=cls.group,
            image=img
        )
        img.close()
        cls.url_new_post = reverse('new_post')
        cls.url_index = reverse('index')
        cls.url_post_edit = reverse(
            'post_edit',
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
        cls.url_post_delete = reverse(
            'post_delete',
            kwargs={
                'username': cls.user.username,
                'post_id': cls.post.pk
            }
        )
        cls.url_profile_follow = reverse(
            'profile_follow',
            kwargs={'username': cls.user_follow.username}
        )
        cls.url_profile_unfollow = reverse(
            'profile_unfollow',
            kwargs={'username': cls.user_follow.username}
        )
        cls.url_follow_index = reverse('follow_index')
        cls.url_add_comment = reverse(
            'add_comment',
            kwargs={
                'username': cls.user.username,
                'post_id': cls.post.pk
            }
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def img_upload(cls):
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

    def test_auth_user_save_post_and_correct_redirect(self):
        """Check save post and correct redirect."""
        cls = self.__class__
        authorized_client = Client()
        authorized_client.force_login(cls.user)
        context = {
            'group': cls.group.pk,
            'text': ('Save new post (group = '
                     f'{cls.group.pk}). {id(cls.group)}'),
            'image': cls.img_upload()
        }
        self.assertFalse(Post.objects.filter(text=context['text']).exists())
        count = Post.objects.count()
        response = authorized_client.post(
            cls.url_new_post,
            data=context
        )
        self.assertTrue(Post.objects.filter(text=context['text']).exists())
        self.assertEqual(Post.objects.count(), count+1)
        post = Post.objects.first()
        self.assertRedirects(response, cls.url_index)
        self.assertEqual(post.author, cls.user)
        self.assertEqual(post.group, cls.group)
        self.assertTrue(path.exists(post.image.path))
        context['image'].close()

    def test_auth_user_edit_post_and_correct_redirect(self):
        """Check edit post and correct redirect."""
        cls = self.__class__
        authorized_client = Client()
        authorized_client.force_login(cls.user)
        context = {
            'group': cls.group.pk,
            'text': ('Edit post (group = '
                     f'{cls.group.pk}).  {id(cls.group)}'),
            'image': cls.img_upload()
        }
        count = Post.objects.count()
        cur_img = cls.post.image
        response = authorized_client.post(
            cls.url_post_edit,
            data=context
        )
        post = Post.objects.first()
        self.assertEqual(Post.objects.count(), count)
        self.assertRedirects(response, cls.url_post)
        self.assertEqual(post.author, cls.user)
        self.assertEqual(post.group, cls.group)
        self.assertTrue(post.image)
        self.assertNotEqual(post.image, cur_img)
        self.assertTrue(path.exists(post.image.path))
        context['image'].close()

    def test_auth_wrong_user_edit_post_and_correct_redirect(self):
        """Check wrong user could'nt edit post and correct redirect."""
        cls = self.__class__
        wrong_user = User.objects.create(
            username='wrong_user',
        )
        wrong_client = Client()
        wrong_client.force_login(wrong_user)
        context = {
            'group': cls.group.pk,
            'text': ('Edit post (group = '
                     f'{cls.group.pk}).  {id(cls.group)}'),
            'image': cls.img_upload()
        }
        cur_img = cls.post.image
        response = wrong_client.post(
            cls.url_post_edit,
            data=context
        )
        post = Post.objects.get(pk=cls.post.pk)
        self.assertRedirects(response, cls.url_post)
        self.assertNotEqual(post.text, context['text'])
        self.assertNotEqual(post.author, wrong_user)
        self.assertTrue(post.image)
        self.assertEqual(post.image, cur_img)
        self.assertNotEqual(post.image, context['image'])
        context['image'].close()

    def test_not_auth_user_edit_post(self):
        """Check wrong user could'nt edit post and correct redirect."""
        cls = self.__class__
        context = {
            'group': cls.group.pk,
            'text': ('Edit post (group = '
                     f'{cls.group.pk}).  {id(cls.group)}'),
            'image': cls.img_upload()
        }
        cur_img = cls.post.image
        count = Post.objects.count()
        self.client.post(
            cls.url_post_edit,
            data=context
        )
        post = Post.objects.get(pk=cls.post.pk)
        self.assertEqual(Post.objects.count(), count)
        self.assertNotEqual(post.text, context['text'])
        self.assertNotEqual(post.author, AnonymousUser)
        self.assertTrue(post.image)
        self.assertEqual(post.image, cur_img)
        context['image'].close()

    def test_delete_url_redirect_post(self):
        """Check redirect for an authorized user."""
        cls = self.__class__
        this_url = f'/some_strange_DELETE_URL/'
        authorized_client = Client()
        authorized_client.force_login(cls.user)
        response = authorized_client.post(cls.url_post_delete,
                                          {'this_url': this_url})
        """
        Не применяю assertRedirects т.к. далее происходит переброска на
        страницу поиска профиля пользователя и после - 404. Мне необходимо
        проверить что редирект будет произведён именно по адресу из контекста
        хранящемуся в this_url
        """
        self.assertEqual(response.url, this_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_list_url_redirect_anonymous(self):
        """Check redirect for an unauthorized user."""
        cls = self.__class__
        url_login = reverse('login')
        url_list = (
            cls.url_new_post,
            cls.url_post_edit,
            cls.url_add_comment,
            cls.url_post_delete,
            cls.url_follow_index,
            cls.url_profile_follow,
            cls.url_profile_unfollow,
        )
        for url in url_list:
            response = self.client.post(url)
            with self.subTest(url=url):
                self.assertRedirects(response, f'{url_login}?next={url}')


class CommentsTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user_CommentsTestCase')
        cls.group = Group.objects.create(
            title='Тест_CommentsTestCase',
            slug='test_CommentsTestCase',
            description='Текст_CommentsTestCase',
        )
        cls.post = Post.objects.create(
            text='Тест CommentsTestCase',
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

    def test_auth_user_add_comment(self):
        """Checking the addition of a comment."""
        cls = self.__class__
        context = {
            'text': f'Текст комментария для posta {cls.post.pk} {id(cls.post)}'
        }
        count = Comment.objects.count()
        authorized_client = Client()
        authorized_client.force_login(cls.user)
        resp = authorized_client.post(cls.url_add_comment, data=context)
        self.assertRedirects(resp, cls.url_post)
        self.assertEqual(count+1, Comment.objects.count())
        comment = Comment.objects.first()
        self.assertEqual(comment.text, context['text'])
        response = self.client.get(cls.url_post)
        comments = response.context['post'].comments.all()
        self.assertIn(comment, comments)

    def test_not_auth_user_add_comment(self):
        """Checking the addition of a comment from not authorise user."""
        cls = self.__class__
        context = {
            'text': f'Текст комментария для posta {cls.post.pk} {id(cls.post)}'
        }
        count = Comment.objects.count()
        self.client.post(cls.url_add_comment, data=context)
        self.assertEqual(count, Comment.objects.count())
        comment = Comment.objects.first()
        self.assertFalse(comment,
                         Comment.objects.filter(text=context['text']).exists())

        if comment is not None:
            self.assertNotEqual(comment.text, context['text'])
        response = self.client.get(cls.url_post)
        comments = response.context['post'].comments.all()
        self.assertNotIn(comment, comments)


class FollowTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user_FollowTestCase')
        cls.user_follow = User.objects.create(
            username='user_follow_FollowTestCase'
        )
        cls.post_follow = Post.objects.create(
            text=f'test_follow. {id(cls.user_follow)}',
            author=cls.user_follow,
        )
        cls.post = Post.objects.create(
            text=f'test_follow. {id(cls.user)}',
            author=cls.user,
        )
        cls.url_profile_follow = reverse(
            'profile_follow',
            kwargs={'username': cls.user_follow.username}
        )
        cls.url_profile_unfollow = reverse(
            'profile_unfollow',
            kwargs={'username': cls.user.username}
        )
        cls.url_follow_index = reverse('follow_index')

    def test_auth_user_follow(self):
        """Check unsubscribe and subscribe function.

        Tests first subscribing to the author, and then unsubscribing from him.
        """
        cls = self.__class__
        authorized_client = Client()
        authorized_client.force_login(cls.user)
        following_profile = reverse(
            'profile',
            kwargs={'username': cls.user_follow.username}
        )
        # Подписываюсь
        count = Follow.objects.count() + 1
        response = authorized_client.post(cls.url_profile_follow)
        self.assertRedirects(response, following_profile)
        # Проверяю подписка
        follow = Follow.objects.first()
        self.assertEqual(follow.user, cls.user)
        self.assertEqual(follow.author, cls.user_follow)
        self.assertEqual(count, Follow.objects.count())
        # Проверяю что результат подписки выводится на странице
        response = authorized_client.post(cls.url_follow_index)
        self.assertIn(cls.post_follow, response.context['page'])

    def test_auth_user_unfollow(self):
        """Check unsubscribe and subscribe function.

        Tests first subscribing to the author, and then unsubscribing from him.
        """
        cls = self.__class__
        authorized_client = Client()
        authorized_client.force_login(cls.user_follow)
        follow = Follow.objects.create(author=cls.user, user=cls.user_follow)
        following_profile = reverse(
            'profile',
            kwargs={'username': cls.user.username}
        )
        count = Follow.objects.count() - 1
        # Отписываюсь
        response = authorized_client.post(cls.url_profile_unfollow)
        self.assertRedirects(response, following_profile)
        # Проверяю удаление подписки
        self.assertFalse(Follow.objects.filter(pk=follow.pk).exists())
        self.assertEqual(count, Follow.objects.count())
        # Проверка что более указанного поста нет в выводе
        response = authorized_client.post(cls.url_follow_index)
        self.assertNotIn(cls.post_follow, response.context['page'])
