from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.test import Client

from posts.forms import PostForm
from posts.models import Follow, Group, Post

User = get_user_model()

class PostsURLTestsCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user_PostsURLTestsCase')
        cls.user_follow = User.objects.create(
            username='user_follow_PostsURLTestsCase',
        )
        cls.group = Group.objects.create(
            title='Тест_PostsURLTestsCase',
            slug='test_PostsURLTestsCase',
            description='Текст_PostsURLTestsCase',
        )
        cls.post = Post.objects.create(
            text='Тест_PostsURLTestsCase',
            author=cls.user,
            group=cls.group,
        )
        cls.post_follow = Post.objects.create(
            text=f'test_follow. {id(cls.user_follow)}',
            author=cls.user_follow,
            group=cls.group,
        )
        cls.follow = Follow.objects.create(user=cls.user,
                                           author=cls.user_follow)
        cls.form = PostForm
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.url_index = reverse('index')
        cls.url_new_post = reverse('new_post')
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
        cls.url_post_delete = reverse(
            'post_delete',
            kwargs={
                'username': cls.user.username,
                'post_id': cls.post.pk
            }
        )

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_not_found(self):
        response = self.client.get('/some_strange_404_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_absolute_path_by_name(self):
        """Check absolute url paths."""
        cls = self.__class__
        urls_by_name = (
            (cls.url_index, '/'),
            (cls.url_new_post, '/new/'),
            (cls.url_follow_index, '/follow/'),
            (cls.url_profile, f'/{cls.user.username}/'),
            (cls.url_group, f'/group/{cls.group.slug}/'),
            (cls.url_post, f'/{cls.user.username}/{cls.post.pk}/'),
            (cls.url_profile_follow, f'/{cls.user_follow.username}/follow/'),
            (cls.url_post_edit, f'/{cls.user.username}/{cls.post.pk}/edit/'),
            (cls.url_profile_unfollow,
             f'/{cls.user_follow.username}/unfollow/'),
            (cls.url_add_comment,
             f'/{cls.user.username}/{cls.post.pk}/comment/'),
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
        cache.clear()
        for url in url_list:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_url_exists_at_desired_location(self):
        """Check addres available."""
        cls = self.__class__
        authorized_client = Client()
        authorized_client.force_login(cls.user)
        auth_url_list = (
            cls.url_new_post,
            cls.url_post_edit,
            cls.url_follow_index,
        )
        for url in auth_url_list:
            response = authorized_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(response.status_code, HTTPStatus.OK)

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
            response = self.client.get(url)
            with self.subTest(url=url):
                self.assertRedirects(response, f'{url_login}?next={url}')
