import shutil
import tempfile


from django.contrib.auth import get_user_model
from django.http import response
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache

from ..models import Follow, Group, Post
from django import forms

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.author_group = Group.objects.create(
            title='Тестовый заголовок 2',
            description='Тестовое описание 2',
            slug='author-slug'
        )
        cls.user = User.objects.create_user(username='UserHasNoName')
        cls.author_с = User.objects.create_user(username='TestAuthor')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )
        cls.small_gif = (            
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif',
        )
        cls.follow = Follow.objects.create(author=cls.author_с, user=cls.user)
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        posts_count = Post.objects.count()
        response = self.authorized_client.get(reverse('posts:index')).content
        Post.objects.create(
            text='Тестовый текст для проверки кэша',
            author=self.user,
            group=self.group
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            response,
            self.authorized_client.get(reverse('posts:index')).content
        )
        cache.clear()
        self.assertNotEqual(
            response,
            self.authorized_client.get(reverse('posts:index')).content
        )

    def test_pages_uses_correct_template(self):
        template_page_names = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.post.author.username}
            ):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
        }
        for reverse_name, template in template_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_home_page(self):
        response = self.authorized_client.get(
            reverse('posts:index'))
        for post in response.context['page_obj']:
            self.assertIsInstance(post, Post)

    def test_context_group_page(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        for post in response.context['page_obj']:
            self.assertEqual(post.group, self.group)

    def test_context_profile_page(self):
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.post.author.username}))
        for post in response.context['page_obj']:
            self.assertEqual(post.author, self.user)

    def test_context_post_detail_page(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        test_post = response.context['post'].id
        self.assertEqual(test_post, self.post.id)

    def test_create_post_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_home_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_pud_date_0 = first_object.pub_date
        post_text_0 = first_object.text
        post_slug_0 = first_object.group.slug
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_pud_date_0, self.post.pub_date)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_slug_0, self.group.slug)
        self.assertIsNotNone(self.post)
        self.assertIsNotNone(post_image_0)

    def test_posts_group_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_pud_date_0 = first_object.pub_date
        post_text_0 = first_object.text
        post_slug_0 = first_object.group.slug
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_pud_date_0, self.post.pub_date)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_slug_0, self.group.slug)
        self.assertIsNotNone(self.post)
        self.assertIsNotNone(post_image_0)

    def test_posts_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.post.author.username}))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_pud_date_0 = first_object.pub_date
        post_text_0 = first_object.text
        post_slug_0 = first_object.group.slug
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_pud_date_0, self.post.pub_date)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_slug_0, self.group.slug)
        self.assertIsNotNone(self.post)
        self.assertIsNotNone(post_image_0)

    def test_posts_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        first_object = response.context['post']
        post_author_0 = first_object.author.username
        post_pud_date_0 = first_object.pub_date
        post_text_0 = first_object.text
        post_slug_0 = first_object.group.slug
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_pud_date_0, self.post.pub_date)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_slug_0, self.group.slug)
        self.assertIsNotNone(self.post)
        self.assertIsNotNone(post_image_0)
    
    def test_posts_follow_page_show_correct_context(self):
        author_post = Post.objects.create(
            author=self.author_с,
            text='Тестовый',
            group=self.author_group
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_pud_date_0 = first_object.pub_date
        post_text_0 = first_object.text
        post_slug_0 = first_object.group.slug
        self.assertEqual(post_author_0, author_post.author.username)
        self.assertEqual(post_pud_date_0, author_post.pub_date)
        self.assertEqual(post_text_0, author_post.text)
        self.assertEqual(post_slug_0, author_post.group.slug)
        self.assertIsNotNone(self.post)
