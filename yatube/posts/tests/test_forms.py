from os import path

from django.test import TestCase

from .test_setups import MySetupTestCase
from posts.forms import PostForm
from posts.models import Post


class PostsSaveTests(TestCase, MySetupTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        MySetupTestCase.setUpClass()

    @classmethod
    def tearDownClass(cls):
        MySetupTestCase.tearDownClass()
        super().tearDownClass()

    def test_posts_contain_form(self):
        """Check templates on form context containing."""
        cls = self.__class__
        url_list = (
            cls.url_new_post,
            cls.url_post_edit,
        )
        for url in url_list:
            response = cls.authorized_client.get(url)
            self.assertIn('form', response.context)
            form = response.context['form']
            for field, value in PostForm().fields.items():
                with self.subTest(form_field=field):
                    self.assertIsInstance(form.fields[field], type(value))

    def test_auth_user_save_post_and_correct_redirect(self):
        """Check save post and correct redirect."""
        cls = self.__class__
        img1 = cls.img_upload()
        img2 = cls.img_upload()
        context_list = (
            {
                'group': cls.group.pk,
                'text': ('Save new post (group = '
                         f'{cls.group.pk}). {id(cls.group)}'),
                'image': img1
            },
            {
                'group': '',
                'text': f'Save new post without group. {id(cls.group)}',
                'image': img2
            },
        )
        for context in context_list:
            count = Post.objects.count()
            with self.subTest(url=cls.url_new_post, context=context):
                response = cls.authorized_client.post(
                    cls.url_new_post,
                    data=context
                )
                count += 1
                post = Post.objects.filter(text=context['text']).last()
                self.assertRedirects(response, cls.url_index)
                self.assertEqual(post.author, cls.user)
                if context['group']:
                    self.assertEqual(post.group.pk, context['group'])
                else:
                    self.assertIsNone(post.group)
                self.assertEqual(Post.objects.count(), count)
                self.assertTrue(path.exists(post.image.path))
        img1.close()
        img2.close()

    def test_auth_user_edit_post_and_correct_redirect(self):
        """Check edit post and correct redirect."""
        cls = self.__class__
        img1 = cls.img_upload()
        img2 = cls.img_upload()
        context_list = (
            {
                'group': cls.group.pk,
                'text': ('Edit post (group = '
                         f'{cls.group.pk}).  {id(cls.group)}'),
                'image': img1
            },
            {
                'group': '',
                'text': f'Edit post without group. {id(cls.group)}',
                'image': img2
            },
        )
        for context in context_list:
            count = Post.objects.count()
            with self.subTest(url=cls.url_post_edit, context=context):
                cur_img = cls.post.image
                response = cls.authorized_client.post(
                    cls.url_post_edit,
                    data=context
                )
                post = Post.objects.filter(text=context['text']).last()
                self.assertRedirects(response, cls.url_post)
                self.assertEqual(post.author, cls.user)
                if context['group']:
                    self.assertEqual(post.group.pk, context['group'])
                else:
                    self.assertIsNone(post.group)
                self.assertTrue(post.image)
                self.assertNotEqual(post.image, cur_img)
                self.assertEqual(Post.objects.count(), count)
        img1.close()
        img2.close()
