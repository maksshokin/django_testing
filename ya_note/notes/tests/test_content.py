from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

NOTES_ADD_URL = 'notes:add'
NOTES_EDIT_URL = 'notes:edit'
NOTES_LIST_URL = 'notes:list'


class TestContent(TestCase):
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
            slug='slug-text',
            author=cls.author
        )

    def test_notes_list_for_different_users(self):
        response = self.author_client.get(reverse(NOTES_LIST_URL))
        notes = response.context['object_list']
        self.assertIn(self.note, notes)

    def test_note_not_in_list_for_another_user(self):
        response = self.reader_client.get(reverse(NOTES_LIST_URL))
        notes = response.context['object_list']
        self.assertNotIn(self.note, notes)

    def test_create_edit_note_page_contains_form(self):
        urls = (
            (NOTES_ADD_URL, None),
            (NOTES_EDIT_URL, (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
