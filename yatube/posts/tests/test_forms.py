import shutil
import tempfile


from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.user = User.objects.create_user(username='UserHasNoName')
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
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
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )
        cls.cache_text = []
        Follow.objects.create(author=cls.author, user=cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif',
        )
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'UserHasNoName'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data.get('text'),
                group=self.group.id,
                image='posts/small.gif'
            ).exists()
        )
        post = Post.objects.first()
        self.assertEqual(Post.objects.get(
            text=form_data.get('text')).text, form_data.get('text'))
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertIn(self.uploaded.name, post.image.name)

    def test_edit_post(self):
        form_data = {
            'text': 'Тесвый текст',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data.get('text'),
                group=self.group.id,
            ).exists()
        )

    def test_guest_client_cannot_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст для теста',
            'group': self.group.id,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        login_reverse = reverse('users:login')
        create_reverse = reverse('posts:post_create')
        self.assertRedirects(
            response, f'{login_reverse}?next={create_reverse}')
        self.assertEqual(Post.objects.count(), posts_count)

    def text_comment_create_post(self):
        Comment.objects.create(
            post=self.post,
            author=self.user,
            text='Тестовый комментарий под тестовым постом'
        )
        self.assertTrue(
            Comment.objects.filter(
                text=self.comment.text
            ).exists()
        )
