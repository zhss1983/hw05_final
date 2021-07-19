from tempfile import mkdtemp

from django.conf import settings
from django.core.cache import cache
from django.test import Client, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Follow, Group, Post, User
from posts.views import my_paginator
from yatube.settings import DELTA_PAGE_COUNT, MAX_PAGE_COUNT
from .test_basetestcase import BaseTestCase


class PostsTestsCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=f'user_{cls.__name__}')
        cls.url_profile = reverse(
            'profile',
            kwargs={'username': cls.user.username}
        )
        group = Group.objects.create(
            title=f'Тест_{cls.__name__}',
            slug=f'test_{cls.__name__}',
            description=f'Текст_{cls.__name__}',
        )
        cls.url_group = reverse('group', kwargs={'slug': group.slug})
        post = Post.objects.create(
            text=f'Тест_{cls.__name__}',
            author=cls.user,
            group=group,
        )
        cls.url_post = reverse(
            'post',
            kwargs={
                'username': cls.user.username,
                'post_id': post.pk
            }
        )
        cls.url_post_edit = reverse(
            'post_edit',
            kwargs={
                'username': cls.user.username,
                'post_id': post.pk
            }
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.__class__.user)

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
        auth_url_list = (
            (cls.url_new_post, 'posts/manage_post.html'),
            (cls.url_post_edit, 'posts/manage_post.html'),
            (cls.url_follow_index, 'posts/follow.html'),
        )
        for url, template_name in auth_url_list:
            response = self.authorized_client.get(url)
            with self.subTest(url=url):
                self.assertTemplateUsed(response, template_name=template_name)

    def test_posts_contain_in_correct_group(self):
        """Check correct access by group."""
        cls = self.__class__
        post = Post.objects.first()
        in_list_url = (
            cls.url_index,
            cls.url_group,
        )
        for url in in_list_url:
            response = self.authorized_client.get(url)
            with self.subTest(url=url):
                self.assertIn(post, response.context['page'].object_list)

    def test_posts_not_contain_in_wrong_group(self):
        """Check correct access by group."""
        cls = self.__class__
        new_group = Group.objects.create(
            title=f'Group {cls.__name__} №2',
            slug=f'test_group_{cls.__name__}_2',
            description=f'Тестовая группа {cls.__name__} №2',
        )
        post = Post.objects.first()
        url_new_group = reverse('group', kwargs={'slug': new_group.slug})
        response = self.authorized_client.get(url_new_group)
        self.assertNotIn(post, response.context['page'].object_list)


@override_settings(MEDIA_ROOT=mkdtemp(dir=settings.BASE_DIR))
class PostsContextTestsCase(BaseTestCase):

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
            image=cls.img_upload()
        )
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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.__class__.user)

    def test_posts_contain_form(self):
        """Check templates on form context containing."""
        cls = self.__class__
        url_post_edit = reverse(
            'post_edit',
            kwargs={
                'username': cls.user.username,
                'post_id': cls.post.pk
            }
        )
        url_list = (cls.url_new_post, url_post_edit)
        for url in url_list:
            response = self.authorized_client.get(url)
            with self.subTest(url=url):
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], PostForm)

    def test_profile_shows_correct_context(self):
        """Check profile view context."""
        cls = self.__class__
        url = cls.url_profile
        response = self.authorized_client.get(url)
        self.assertIn('author', response.context)
        author = response.context['author']
        self.assertEqual(cls.user, author)
        self.assertEqual(cls.user.username, author.username)

    def test_group_shows_correct_context(self):
        """Check group view context."""
        cls = self.__class__
        url = cls.url_group
        response = self.authorized_client.get(url)
        self.assertIn('group', response.context)
        content = {
            'pk': response.context['group'].pk,
            'title': response.context['group'].title,
            'slug': response.context['group'].slug,
            'description': response.context['group'].description
        }
        self.assert_group(cls.group, content)

    def test_post_shows_correct_context(self):
        """Check post view context"""
        cls = self.__class__
        response = self.authorized_client.get(cls.url_post)
        self.assertIn('post', response.context)
        content = {
            'pk': response.context['post'].pk,
            'text': response.context['post'].text,
            'author': response.context['post'].author,
            'group': response.context['post'].group,
            'pub_date': response.context['post'].pub_date
        }
        self.assert_post(cls.post, content)

    def test_posts_shows_images(self):
        """Check image context in multiposts pages."""
        cls = self.__class__
        url_list = (
            cls.url_index,
            cls.url_profile,
            cls.url_group,
        )
        cache.clear()
        for url in url_list:
            response = self.authorized_client.get(url)
            with self.subTest(url=url):
                self.assert_image_in_post(
                    response.context['page'][-1].image.path,
                    cls.image_file_name
                )

    def test_post_show_image(self):
        """Check image context in post."""
        cls = self.__class__
        response = self.authorized_client.get(cls.url_post)
        self.assert_image_in_post(
            response.context['post'].image.path,
            cls.image_file_name
        )


class PaginatorViewsTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=f'user_{cls.__name__}')
        cls.group = Group.objects.create(
            title=f'Тест {cls.__name__}',
            slug=f'test_{cls.__name__}',
            description=f'Текст_{cls.__name__}',
        )
        """MAX_PAGE_COUNT - Число постов на странице. (по умолчанию 10)
        DELTA_PAGE_COUNT - Число страниц отображаемых в пагинаторе относительно
        текущей. (DELTA_PAGE_COUNT = 1 if DEBUG else 10)
        """
        cls.less_ten = 3  # количество постов на последней странице
        # Вычисляю количество полных страниц.
        cls.page_count = DELTA_PAGE_COUNT * 2 + 3
        # Создаю необходимое количество постов,
        cls.posts = tuple(
            Post.objects.create(text=f'Тест {count}', author=cls.user,
                                group=cls.group) for count in
            range(cls.page_count * MAX_PAGE_COUNT + cls.less_ten)
        )
        cls.url_group = reverse('group', kwargs={'slug': cls.group.slug})
        cls.url_profile = reverse(
            'profile',
            kwargs={'username': cls.user.username}
        )

    def test_my_paginator_return_context(self):
        """Check my_paginator function on correct return"""
        pages = self.page_count + 1  # Полное число страниц
        check_context = (
            # (
            #     page_number, - Номер страници для демонстрацыи
            #     from_page, - Нчинать отображение номеров страниц с этой
            #     to_page, - Отображать страницы до этой
            #     page_count - Число постов на отображаемой страние.
            # ),
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
                2 + DELTA_PAGE_COUNT,
                2,
                min(pages - 1, 2 + 2 * DELTA_PAGE_COUNT),
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
                pages - 2 - DELTA_PAGE_COUNT,
                max(2, pages - 2 - 2 * DELTA_PAGE_COUNT),
                pages - 2,
                MAX_PAGE_COUNT
            ),
            (  # Предыдущая, 1, 2, _3_, 4, ..., 6, Следующая
                pages // 2,
                max(2, pages // 2 - DELTA_PAGE_COUNT),
                min(pages - 1, pages // 2 + DELTA_PAGE_COUNT),
                MAX_PAGE_COUNT
            ),
        )
        """Я тестирую свою функцию пагинатора на то что при любом поступающем
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
        """Checks the pass of the paginator's parameters to the context

        It is not the test of the paginator's work, but the test that
        it is in the context. Also it is checked that something else is not
        transmitted under the guise of a paginator.
        """
        cls = self.__class__
        check_context = (
            cls.url_index,
            cls.url_group,
            cls.url_profile,
            cls.url_follow_index,
        )
        cache.clear()
        for url in check_context:
            authorized_client = Client()
            authorized_client.force_login(cls.user)
            response = authorized_client.get(url)
            with self.subTest(url=url):
                self.assertIn('page', response.context)
                self.assertIn('from_page', response.context)
                self.assertIn('to_page', response.context)


class CacheViewsTestCase(BaseTestCase):

    def test_index_page_cache(self):
        """Check caching of the index.html (url '/')."""
        cls = self.__class__
        user = User.objects.create(username=f'user_{cls.__name__}')
        cache.clear()
        response = self.client.get(cls.url_index)
        content_start = response.content
        Post.objects.create(
            text=f'Тест {cls.__name__}',
            author=user,
        )
        response = self.client.get(cls.url_index)
        self.assertEqual(content_start, response.content)
        cache.clear()
        response = self.client.get(cls.url_index)
        self.assertNotEqual(content_start, response.content)


class FollowTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=f'user_{cls.__name__}')
        cls.user_follow = User.objects.create(
            username=f'user_follow_{cls.__name__}'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.__class__.user)

    def test_auth_user_follow(self):
        """Check subscribe function."""
        cls = self.__class__
        url_profile_follow = reverse(
            'profile_follow',
            kwargs={'username': cls.user_follow.username}
        )
        count = Follow.objects.count()
        self.authorized_client.post(url_profile_follow)
        self.assertEqual(count + 1, Follow.objects.count())
        follow = Follow.objects.last()
        self.assertEqual(follow.user, cls.user)
        self.assertEqual(follow.author, cls.user_follow)

    def test_auth_user_follow_show(self):
        """Check subscribe function."""
        cls = self.__class__
        Follow.objects.create(user=cls.user, author=cls.user_follow)
        post = Post.objects.create(text='test_follow.', author=cls.user_follow)
        response = self.authorized_client.get(cls.url_follow_index)
        self.assertIn(post, response.context['page'])

    def test_auth_user_unfollow(self):
        """Check unsubscribe function."""
        cls = self.__class__
        Follow.objects.create(author=cls.user_follow, user=cls.user)
        url_profile_unfollow = reverse(
            'profile_unfollow',
            kwargs={'username': cls.user_follow.username}
        )
        count = Follow.objects.count()
        self.authorized_client.post(url_profile_unfollow)
        self.assertEqual(count - 1, Follow.objects.count())

    def test_auth_user_unfollow_show(self):
        """Check unsubscribe function."""
        cls = self.__class__
        post = Post.objects.create(
            text='test_follow.',
            author=cls.user_follow,
        )
        response = self.authorized_client.get(cls.url_follow_index)
        self.assertNotIn(post, response.context['page'])
