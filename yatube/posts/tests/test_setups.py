import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Follow, Group, Post

User = get_user_model()


class MySetupTestCase():

    @classmethod
    def setUpClass(cls):
        settings.MEDIA_ROOT = 'tempfile_media'
        cls.user = User.objects.create(
            username='user',
        )
        cls.user_follow = User.objects.create(
            username='user_follow',
        )
        cls.group = Group.objects.create(
            title='Тест ' * 40,
            slug='test_' * 30,
            description='Текст ' * 50,
        )
        img = cls.img_upload()
        cls.post = Post.objects.create(
            text='Тест ' * 100,
            author=cls.user,
            group=cls.group,
            image=img
        )
        img.close()
        img = cls.img_upload()
        cls.post_follow = Post.objects.create(
            text=f'test_follow. {id(cls.user_follow)}',
            author=cls.user_follow,
            group=cls.group,
            image=img
        )
        img.close()
        cls.follow = Follow.objects.create(user=cls.user,
                                           author=cls.user_follow)
        cls.form = PostForm
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.url_index = reverse('index')
        cls.url = reverse('index')
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

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

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
