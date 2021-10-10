from django.contrib.auth import get_user_model
from django.http import response
from django.test import TestCase, Client
from django.urls import reverse


from ..models import Group, Post

User = get_user_model()


class PostsAndStaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.user = User.objects.create_user(username='HasNoName')
        cls.author_c = User.objects.create_user(username='TestAuthor')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        templates_uls_names = {
            'posts/index.html': '/',
            'posts/create_post.html': '/create/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
            'posts/profile.html': f'/profile/{self.post.author.username}/',
            'posts/follow.html': '/follow/',
        }
        for template, adress in templates_uls_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_post_create_page_authorized_user(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_post_create_page_guest_user(self):
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)

    def test_group_page(self):
        response = self.authorized_client.get(f'/group/{self.group.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_profile_page(self):
        response = self.authorized_client.get(
            f'/profile/{self.post.author.username}/')
        self.assertEqual(response.status_code, 200)

    def test_post_detail(self):
        response = self.authorized_client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_guest_user_post_edit(self):
        response = self.guest_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_authorized_user_post_edit(self):
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_comment_page(self):
        response = self.guest_client.get(f'/posts/{self.post.id}/comment/')
        self.assertEqual(response.status_code, 302)
    
    def test_unexcisting_page(self):
        response = self.authorized_client.get('/unexcisting_page/')
        self.assertEqual(response.status_code, 404)
