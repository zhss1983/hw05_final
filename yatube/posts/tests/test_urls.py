from http import HTTPStatus

from django.core.cache import cache
from django.test import Client
from django.urls import reverse

from posts.models import Group, Post, User
from .test_basetestcase import BaseTestCase


class PostURLTestsCase(BaseTestCase):

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
            text=f'Тест_{cls.__name__}',
            author=cls.user,
            group=cls.group,
        )
        cls.url_group = reverse('group', kwargs={'slug': cls.group.slug})
        cls.url_profile = reverse(
            'profile',
            kwargs={'username': cls.user.username}
        )
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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.__class__.user)
        cache.clear()

    def test_page_not_found(self):
        response = self.client.get('/some_strange_404_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_absolute_path_by_name(self):
        """Check absolute url paths."""
        cls = self.__class__
        urls_by_name = (
            (cls.url_index, '/'),
            (cls.url_new_post, '/new/'),
            (cls.url_profile, f'/{cls.user.username}/'),
            (cls.url_group, f'/group/{cls.group.slug}/'),
            (cls.url_post, f'/{cls.user.username}/{cls.post.pk}/'),
            (cls.url_post_edit, f'/{cls.user.username}/{cls.post.pk}/edit/'),
            (cls.url_post_delete,
             f'/{cls.user.username}/{cls.post.pk}/delete/'),
        )
        for name, url in urls_by_name:
            with self.subTest(name=name):
                self.assertEqual(name, url)

    def test_url_exists_at_desired_location(self):
        """Check addres available."""
        cls = self.__class__
        url_list = (
            cls.url_index,
            cls.url_profile,
            cls.url_group,
            cls.url_post,
        )
        for url in url_list:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_url_exists_at_desired_location(self):
        """Check addres available."""
        cls = self.__class__
        auth_url_list = (
            cls.url_new_post,
            cls.url_post_edit,
        )
        for url in auth_url_list:
            response = self.authorized_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_list_url_redirect_anonymous(self):
        """Check redirect for an unauthorized user."""
        cls = self.__class__
        url_login = reverse('login')
        url_list = (
            cls.url_new_post,
            cls.url_post_edit,
        )
        for url in url_list:
            response = self.client.get(url)
            with self.subTest(url=url):
                self.assertRedirects(response, f'{url_login}?next={url}')

    def test_auth_wrong_user_try_edit_post_and_correct_redirect(self):
        """Check wrong user could'nt edit post and correct redirect."""
        cls = self.__class__
        wrong_user = User.objects.create(
            username='wrong_user',
        )
        post = Post.objects.create(
            text=f'Edit wrong user {cls.__name__}',
            author=wrong_user,
        )
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
        response = self.authorized_client.get(url_post_edit)
        self.assertRedirects(response, url_post)


class CommentURLTestCase(BaseTestCase):

    def test_absolute_path_by_name(self):
        """Check absolute url paths."""
        user, post = 'user', 1
        url_add_comment = reverse(
            'add_comment',
            kwargs={
                'username': user,
                'post_id': post
            }
        )
        self.assertEqual(url_add_comment, f'/{user}/{post}/comment/')


class FollowURLTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user_FollowTestCase')
        cls.user_follow = User.objects.create(username='user_follow_test')
        cls.url_following_profile = reverse(
            'profile',
            kwargs={'username': cls.user_follow.username}
        )
        cls.url_profile_unfollow = reverse(
            'profile_unfollow',
            kwargs={'username': cls.user_follow.username}
        )
        cls.url_profile_follow = reverse(
            'profile_follow',
            kwargs={'username': cls.user_follow.username}
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.__class__.user)

    def test_auth_user_follow_redirect(self):
        """Check subscribe function."""
        cls = self.__class__
        response = self.authorized_client.get(cls.url_profile_follow)
        self.assertRedirects(response, cls.url_following_profile)

    def test_auth_user_unfollow_redirect(self):
        """Check unsubscribe function."""
        cls = self.__class__
        response = self.authorized_client.get(cls.url_profile_unfollow)
        self.assertRedirects(response, cls.url_following_profile)

    def test_list_url_redirect_anonymous(self):
        """Check redirect for an unauthorized user."""
        cls = self.__class__
        url_login = reverse('login')
        url_list = (
            cls.url_follow_index,
            cls.url_profile_follow,
            cls.url_profile_unfollow,
        )
        for url in url_list:
            response = self.client.get(url)
            with self.subTest(url=url):
                self.assertRedirects(response, f'{url_login}?next={url}')

    def test_for_auth_user_exists_url_at_desired_location(self):
        """Check addres available."""
        cls = self.__class__
        response = self.authorized_client.get(cls.url_follow_index)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_absolute_path_by_name(self):
        """Check absolute url paths."""
        cls = self.__class__
        urls_by_name = (
            (cls.url_follow_index, '/follow/'),
            (cls.url_profile_follow, f'/{cls.user_follow.username}/follow/'),
            (cls.url_profile_unfollow,
             f'/{cls.user_follow.username}/unfollow/'),
        )
        for name, url in urls_by_name:
            with self.subTest(name=name):
                self.assertEqual(name, url)
