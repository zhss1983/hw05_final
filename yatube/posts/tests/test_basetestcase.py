from os import path
from shutil import rmtree

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse


class BaseTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_media_dir = None
        super().setUpClass()
        cls.image_file_name = 'small.gif'
        cls.url_new_post = reverse('new_post')
        cls.url_index = reverse('index')
        cls.url_login = reverse('login')
        cls.url_follow_index = reverse('follow_index')

    @classmethod
    def tearDownClass(cls):
        if cls.temp_media_dir:
            rmtree(cls.temp_media_dir, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def img_upload(cls):
        cls.temp_media_dir = settings.MEDIA_ROOT
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

    def assert_image_in_post(self, img, filename):
        _, head = path.split(img)
        self.assertEqual(head, filename)

    def assert_comment(self, comment, context):
        pk = context.get('pk')
        if pk:
            self.assertEqual(comment.pk, pk)
        created = context.get('created')
        if created:
            self.assertEqual(comment.created, created)
        text = context.get('text')
        if text:
            self.assertEqual(comment.text, text)
        author = context.get('author')
        if author:
            self.assertEqual(comment.author, author)
        post = context.get('post')
        if post:
            self.assertEqual(comment.post, post)

    def assert_post(self, post, context):
        pk = context.get('pk')
        if pk:
            self.assertEqual(post.pk, pk)
        text = context.get('text')
        if text:
            self.assertEqual(post.text, text)
        pub_date = context.get('pub_date')
        if pub_date:
            self.assertEqual(post.pub_date, pub_date)
        author = context.get('author')
        if author:
            self.assertEqual(post.author, author)
        group = context.get('group')
        if group:
            self.assertEqual(post.group, group)
        image_file_name = context.get('image')
        if image_file_name:
            self.assert_image_in_post(post.image.path, image_file_name)

    def assert_group(self, group, context):
        pk = context.get('pk')
        if pk:
            self.assertEqual(group.pk, pk)
        title = context.get('title')
        if title:
            self.assertEqual(group.title, title)
        slug = context.get('slug')
        if slug:
            self.assertEqual(group.slug, slug)
        description = context.get('description')
        if description:
            self.assertEqual(group.description, description)
