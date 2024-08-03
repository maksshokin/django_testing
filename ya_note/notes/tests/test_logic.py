from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()

NOTES_ADD_URL = 'notes:add'
NOTES_DELETE_URL = 'notes:delete'
NOTES_EDIT_URL = 'notes:edit'
NOTES_SUCCESS_URL = 'notes:success'
USERS_LOGIN_URL = 'users:login'


class TestLogic(TestCase):
    COMMENT_TEXT = 'Текст комментария'
    NEW_COMMENT_TEXT = 'Обновлённый комментарий'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Иван Иванов')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Сергей Петров')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_user_can_create_note(self):
        url = reverse(NOTES_ADD_URL)
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse(NOTES_SUCCESS_URL))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.exclude(id=self.note.id).get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        url = reverse(NOTES_ADD_URL)
        response = self.client.post(url, data=self.form_data)
        login_url = reverse(USERS_LOGIN_URL)
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        assert Note.objects.count() == 1

    def test_not_unique_slug(self):
        url = reverse(NOTES_ADD_URL)
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(url, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        url = reverse(NOTES_ADD_URL)
        self.form_data.pop('slug')
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse(NOTES_SUCCESS_URL))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.exclude(id=self.note.id).get()
        expected_slug = slugify(self.form_data['title'])
        assert new_note.slug == expected_slug

    def test_author_can_edit_note(self):
        url = reverse(NOTES_EDIT_URL, args=(self.note.slug,))
        response = self.author_client.post(url, self.form_data)
        self.assertRedirects(response, reverse(NOTES_SUCCESS_URL))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        url = reverse(NOTES_EDIT_URL, args=(self.note.slug,))
        response = self.reader_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        url = reverse(NOTES_DELETE_URL, args=(self.note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse(NOTES_SUCCESS_URL))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        url = reverse(NOTES_DELETE_URL, args=(self.note.slug,))
        response = self.reader_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
