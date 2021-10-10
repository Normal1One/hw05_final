from django.test import TestCase, Client
from django.urls import reverse


guest_client = Client()


class AboutPagesTests(TestCase):
    def test_author_page(self):
        response = guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_tech_page(self):
        response = guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_page_author_uses_correct_template(self):
        response = guest_client.get(reverse('about:author'))
        self.assertTemplateUsed(response, 'about/author.html')

    def test_page_tech_uses_correct_template(self):
        response = guest_client.get(reverse('about:tech'))
        self.assertTemplateUsed(response, 'about/tech.html')
