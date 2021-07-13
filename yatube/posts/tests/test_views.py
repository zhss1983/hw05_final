from datetime import datetime as dt
from os import path
import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.core.paginator import Page
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Follow, Group, Post, User
from posts.views import my_paginator
from yatube.settings import DELTA_PAGE_COUNT, MAX_PAGE_COUNT

User = get_user_model()


class PostsURLTestsCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user_PostsURLTestsCase_1')
        cls.group = Group.objects.create(
            title='Тест_PostsURLTestsCase_1',
            slug='test_PostsURLTestsCase_1',
            description='Текст_PostsURLTestsCase',
        )
        cls.post = Post.objects.create(
            text='Тест_PostsURLTestsCase',
            author=cls.user,
            group=cls.group,
        )
        cls.url_index = reverse('index')
        cls.url_group = reverse('group', kwargs={'slug': cls.group.slug})
        cls.url_profile = reverse(
            'profile',
            kwargs={'username': cls.user.username}
        )
        cls.url_post = reverse(
            'post',
            kwargs={
                'username': cls.user.username,
                'post_id': cls.post.pk
            }
        )
        cls.url_follow_index = reverse('follow_index')
        cls.url_new_post = reverse('new_post')
        cls.url_post_edit = reverse(
            'post_edit',
            kwargs={
                'username': cls.user.username,
                'post_id': cls.post.pk
            }
        )

    def setUp(self):
        cache.clear()

    def test_url_uses_correct_template_by_guest(self):
        """Check matching of template name and URL address."""
        cls = self.__class__
        url_list = (
            (cls.url_index, 'posts/index.html'),
            (cls.url_profile, 'posts/profile.html'),
            (cls.url_post, 'posts/post.html'),
            (cls.url_group, 'posts/group.html'),
        )
        cache.clear()
        for url, template_name in url_list:
            response = self.client.get(url)
            with self.subTest(url=url):
                self.assertTemplateUsed(response, template_name=template_name)

    def test_url_uses_correct_template_auth_user(self):
        """Check matching of template name and URL address."""
        cls = self.__class__
        authorized_client = Client()
        authorized_client.force_login(cls.user)
        auth_url_list = (
            (cls.url_new_post, 'posts/manage_post.html'),
            (cls.url_post_edit, 'posts/manage_post.html'),
            (cls.url_follow_index, 'posts/follow.html'),
        )
        for url, template_name in auth_url_list:
            response = authorized_client.get(url)
            with self.subTest(url=url):
                self.assertTemplateUsed(response, template_name=template_name)

    def test_posts_contain_in_correct_group(self):
        """Check correct access by group."""
        cls = self.__class__
        authorized_client = Client()
        authorized_client.force_login(cls.user)
        new_group = Group.objects.create(
            title='Group №2',
            slug='test_group_2',
            description='Тестовая группа № 2',
        )
        #print('Число постов после создания', Post.objects.count())
        #my_post = Post.objects.last()
        #print('Последний пост:', my_post.pk, my_post.text, my_post.group_id, my_post.pub_date)
        my_post = Post.objects.first()
        #print('Первый пост:', my_post.pk, my_post.text, my_post.group_id, my_post.pub_date)
        #print('Ожидаемый пост:', cls.post.pk, cls.post.text, cls.post.group_id, cls.post.pub_date)
        in_list_url = (
            cls.url_group,
            cls.url_index,
        )
        for url in in_list_url:
            with self.subTest(url=url):
                cache.clear()
                response = authorized_client.get(url)
                self.assertIn(my_post, response.context['page'].object_list)
        url_new_group = reverse('group', kwargs={'slug': new_group.slug})
        response = authorized_client.get(url_new_group)
        self.assertNotIn(my_post, response.context['page'].object_list)


class PostsContextTestsCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = 'tempfile_media'
        cls.url_list = (
            ('about:author', 'about/author.html', '/about/author/'),
            ('about:tech', 'about/tech.html', '/about/tech/'),
        )
        cls.user = User.objects.create(username='user_PostsContextTestsCase')
        cls.group = Group.objects.create(
            title='Тест_PostsContextTestsCase',
            slug='test_PostsContextTestsCase',
            description='Текст_PostsContextTestsCase',
        )
        img = cls.img_upload()
        cls.post = Post.objects.create(
            text='Тест_PostsContextTestsCase',
            author=cls.user,
            group=cls.group,
            image=img
        )
        img.close()
        cls.url_post_edit = reverse(
            'post_edit',
            kwargs={
                'username': cls.user.username,
                'post_id': cls.post.pk
            }
        )
        cls.url_new_post = reverse('new_post')
        cls.url_follow_index = reverse('follow_index')
        cls.url_group = reverse('group', kwargs={'slug': cls.group.slug})
        cls.url_profile = reverse(
            'profile',
            kwargs={'username': cls.user.username}
        )
        cls.url_post = reverse(
            'post',
            kwargs={
                'username': cls.user.username,
                'post_id': cls.post.pk
            }
        )
        cls.url_index = reverse('index')

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

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.__class__.user)

    def test_url_uses_correct_template(self):
        """Check matching of template name and URL address."""
        for url, template_name, abs_url in self.__class__.url_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(reverse(url))
                self.assertTemplateUsed(response, template_name=template_name)

    def test_posts_contain_form(self):
        """Check templates on form context containing."""
        cls = self.__class__
        url_list = (
            cls.url_new_post,
            cls.url_post_edit,
        )
        for url in url_list:
            response = self.authorized_client.get(url)
            with self.subTest(url=url):
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], PostForm)

    def test_posts_shows_correct_context(self):
        """Check specific context, not paginator context.

        Checking that the corresponding variables are passed into the context
        and their value is as expected. In cases where a group, author or post
        is passed, it is checked that this is the correct group, author or post
        from database.
        """
        cls = self.__class__
        year = dt.today().year
        url_list = (
            (
                cls.url_new_post,
                ('year', year),
            ),
            (
                cls.url_post_edit,
                ('year', year),
            ),
            (
                cls.url_profile,
                ('author', cls.user),
                ('year', year),
            ),
            (
                cls.url_group,
                ('group', cls.group),
                ('year', year),
            ),
            (
                cls.url_post,
                ('post', cls.post),
                ('year', year),
            ),
            (
                cls.url_follow_index,
                ('year', year),
            ),
        )
        for url, *context in url_list:
            response = self.authorized_client.get(url)
            for name, value in context:
                with self.subTest(url=url, name=name):
                    self.assertIn(name, response.context)
                    self.assertEqual(value, response.context[name])

    def test_posts_shows_images(self):
        """Check image context in multiposts pages."""
        cls = self.__class__
        url_list = (
            cls.url_profile,
            cls.url_group,
            cls.url_index,
        )
        for url in url_list:
            cache.clear()
            response = self.authorized_client.get(url)
            with self.subTest(url=url):
                post_img = response.context['page'][-1].image
                self.assertTrue(path.exists(post_img.path))

    def test_post_show_image(self):
        """Check image context in post."""
        cls = self.__class__
        url = cls.url_post
        response = self.authorized_client.get(url)
        post_img = response.context['post'].image
        self.assertTrue(path.exists(post_img.path))


class PaginatorViewsTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user_PaginatorViewsTestCase')
        cls.group = Group.objects.create(
            title='Тест PaginatorViewsTestCase',
            slug='test_PaginatorViewsTestCase',
            description='Текст_PaginatorViewsTestCase',
        )
        # MAX_PAGE_COUNT - Число постов на странице. (по умолчанию 10)
        # DELTA_PAGE_COUNT - Число страниц отображаемых в пагинаторе
        # относительно текущей.  (по умолчанию 1)
        cls.less_ten = 3  # количество постов на последней странице
        # Вычисляю количество полных страниц.
        cls.page_count = DELTA_PAGE_COUNT * 2 + 3
        # Создаю необходимое количество постов,
        cls.posts = tuple(
            Post.objects.create(text=f'Тест {count}', author=cls.user,
                                group=cls.group) for count in
            range(cls.page_count * MAX_PAGE_COUNT + cls.less_ten)
        )
        cls.url_index = reverse('index')
        cls.url_group = reverse('group', kwargs={'slug': cls.group.slug})
        cls.url_profile = reverse(
            'profile',
            kwargs={'username': cls.user.username}
        )
        cls.url_follow_index = reverse('follow_index')

    def setUp(self):
        cache.clear()

    def test_my_paginator_return_context(self):
        """Check my_paginator function on correct return"""
        pages = self.page_count + 1  # Полное число страниц
        check_context = (
            #(
            #    page_number, - Номер страници для демонстрацыи
            #    from_page, - Нчинать отображение номеров страниц с этой
            #    to_page, - Отображать страницы до этой
            #    page_count - Число постов на отображаемой страние.
            #),
            (  # Предыдущая, _1_, 2, ..., 6, Следующая
                1,
                2,
                min(pages - 1, DELTA_PAGE_COUNT + 1),
                MAX_PAGE_COUNT
            ),
            (  # Предыдущая, 1, _2_, 3, ..., 6, Следующая
                2,
                max(2, 2 - DELTA_PAGE_COUNT),
                min(pages - 1, 2 + DELTA_PAGE_COUNT),
                MAX_PAGE_COUNT
            ),
            (  # Предыдущая, 1, 2, _3_, 4, ..., 6, Следующая
                3,
                max(2, 3 - DELTA_PAGE_COUNT),
                min(pages - 1, 3 + DELTA_PAGE_COUNT),
                MAX_PAGE_COUNT
            ),
            (  # Предыдущая, 1, ..., 5, _6_, Следующая
                pages,
                max(2, pages - DELTA_PAGE_COUNT),
                pages - 1,
                self.less_ten  # На странице только 3 поста вместо 10
            ),
            (  # Предыдущая, 1, ..., 4, _5_, 6, Следующая
                pages - 1,
                max(2, pages - 1 - DELTA_PAGE_COUNT),
                min(pages - 1, pages - 1 + DELTA_PAGE_COUNT),
                MAX_PAGE_COUNT
            ),
            (  # Предыдущая, 1, ..., 3, _4_, 5, 6, Следующая
                pages - 2,
                max(2, pages - 2 - DELTA_PAGE_COUNT),
                min(pages - 1, pages - 2 + DELTA_PAGE_COUNT),
                MAX_PAGE_COUNT
            ),
            (  # Предыдущая, 1, 2, _3_, 4, ..., 6, Следующая
                pages // 2,
                max(2, pages // 2 - DELTA_PAGE_COUNT),
                min(pages - 1, pages // 2 + DELTA_PAGE_COUNT),
                MAX_PAGE_COUNT
            ),
        )
        """
        Я тестирую свою функцию пагинатора на то что при любом поступающем 
        наборе данных она передаст правильные значения в ответ. После этого не
        будет необходимости тестировать то что пагинатор передаёт корректный
        контекст в каждую функцию, а только что соответствующий контекст в
        принципе передаётся. 
        """
        for page_number, from_page, to_page, page_count in check_context:
            if 1 <= page_number <= pages:
                with self.subTest(page_number=page_number):
                    paginator = my_paginator(self.__class__.posts, page_number)
                    self.assertEqual(
                        len(paginator.get('page')),
                        page_count
                    )
                    self.assertEqual(
                        paginator.get('from_page'),
                        from_page
                    )
                    self.assertEqual(
                        paginator.get('to_page'),
                        to_page
                    )

    def test_paginator_in_context(self):
        """Checks the pass of the paginator's parameters to the context"""
        cls = self.__class__
        check_context = (
            cls.url_index,
            cls.url_group,
            cls.url_profile,
            cls.url_follow_index,
        )
        for url in check_context:
            cache.clear()
            authorized_client = Client()
            authorized_client.force_login(cls.user)
            response = authorized_client.get(url)
            with self.subTest(url=url):
                self.assertIn('page', response.context)
                self.assertIn('from_page', response.context)
                self.assertIn('to_page', response.context)
                # Проверяем значения для 1_ой страницы
                self.assertIsInstance(response.context['page'], Page)
                self.assertEqual(response.context['from_page'], 2)
                count = min(response.context['page'].paginator.num_pages-1,
                            DELTA_PAGE_COUNT+1)
                self.assertEqual(
                    response.context['to_page'],
                    count
                )


class CacheViewsTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user_CacheViewsTestCase')
        cls.post = Post.objects.create(
            text='Тест CacheViewsTestCase',
            author=cls.user,
        )
        cls.url_index = reverse('index')

    def setUp(self):
        cache.clear()

    def test_index_page_cache(self):
        """Check caching of the index.html (url '/')."""
        cls = self.__class__
        # Базовое значение поста
        post_start = Post.objects.get(id=cls.post.pk)
        # Получаем страницу, создаём кеш
        self.client.get(cls.url_index)
        # Меняем пост
        cls.post.text = f'Edit post chash. {id(cls.post)}'
        cls.post.save()
        # Убеждаемся что кэш работает, страница кэширована
        post_edit = Post.objects.get(id=cls.post.pk)
        response = self.client.get(cls.url_index)
        content = response.content.decode(errors='xmlcharrefreplace')
        self.assertIn(post_start.text, content)
        self.assertNotIn(post_edit.text, content)
        # Имитируем тайм аут для кэша
        cache.clear()
        # Убеждаемся что страница обновилась.
        response = self.client.get(cls.url_index)
        content = response.content.decode(errors='xmlcharrefreplace')
        self.assertNotIn(post_start.text, content)
        self.assertIn(post_edit.text, content)


class FollowTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user_FollowTestCase')
        cls.user_follow = User.objects.create(
            username='user_follow FollowTestCase',
        )
        cls.post_follow = Post.objects.create(
            text=f'test_follow. {id(cls.user_follow)}',
            author=cls.user_follow,
        )
        cls.url_follow_index = reverse('follow_index')
        cls.post = Post.objects.create(
            text='Тест ' * 100,
            author=cls.user,
        )
        cls.follow = Follow.objects.create(user=cls.user,
                                           author=cls.user_follow)

    def setUp(self):
        cache.clear()

    def test_auth_user_follow_index(self):
        """Check correct showing posts on follow_index url.

        Checks that the user sees his posts."""
        cls = self.__class__
        authorized_client = Client()
        authorized_client.force_login(cls.user)
        response = authorized_client.post(cls.url_follow_index)
        self.assertIn(cls.post_follow, response.context['page'])

    def test_wrong_auth_user_follow_index(self):
        """Check correct showing posts on follow_index url.

        Checks that the user doesn't see some other posts."""
        cls = self.__class__
        authorized_client = Client()
        authorized_client.force_login(cls.user_follow)
        response = authorized_client.post(cls.url_follow_index)
        self.assertNotIn(cls.post, response.context['page'])
