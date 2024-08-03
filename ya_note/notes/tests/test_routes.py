from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

NOTES_ADD_URL = 'notes:add'
NOTES_DELETE_URL = 'notes:delete'
NOTES_DETAIL_URL = 'notes:detail'
NOTES_EDIT_URL = 'notes:edit'
NOTES_HOME_URL = 'notes:home'
NOTES_LIST_URL = 'notes:list'
NOTES_SUCCESS_URL = 'notes:success'
USERS_LOGIN_URL = 'users:login'
USERS_LOGOUT_URL = 'users:logout'
USERS_SIGNUP_URL = 'users:signup'


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Иван Иванов')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Сергей Петров')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug-text',
            author=cls.author
        )

    def test_pages_availability(self):
        urls = (
            NOTES_HOME_URL,
            USERS_LOGIN_URL,
            USERS_LOGOUT_URL,
            USERS_SIGNUP_URL,
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = (
            NOTES_LIST_URL,
            NOTES_ADD_URL,
            NOTES_SUCCESS_URL,
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in (NOTES_DETAIL_URL, NOTES_EDIT_URL, NOTES_DELETE_URL):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect(self):
        urls = (
            (NOTES_DETAIL_URL, (self.note.slug,)),
            (NOTES_EDIT_URL, (self.note.slug,)),
            (NOTES_DELETE_URL, (self.note.slug,)),
            (NOTES_ADD_URL, None),
            (NOTES_SUCCESS_URL, None),
            (NOTES_LIST_URL, None),
        )
        login_url = reverse(USERS_LOGIN_URL)
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
