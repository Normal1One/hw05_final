from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок ',
            description='Тестовое описание ',
            slug='test-slug',
        )
        cls.user = User.objects.create_user(username='NoName')
        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый текст {i}',
                group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_main_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_main_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_group_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_group_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_first_profile_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.post.author.username})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_profile_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={
                'username': self.post.author.username
            }) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)
