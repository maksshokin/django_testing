from http import HTTPStatus
from random import choice

from django.urls import reverse

import pytest
from conftest import COMMENT_TEXT
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

NEWS_DELETE_URL = 'news:delete'
NEWS_DETAIL_URL = 'news:detail'
NEWS_EDIT_URL = 'news:edit'
NEWS_HOME_URL = 'news:home'


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    comments_count_before = Comment.objects.count()
    assert comments_count_before == 0
    url = reverse(NEWS_DETAIL_URL, args=(news.id,))
    client.post(url, data=form_data)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == 0


def test_user_can_create_comment(author_client, author, news, form_data):
    comments_count_before = Comment.objects.count()
    assert comments_count_before == 0
    url = reverse(NEWS_DETAIL_URL, args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count_after = Comment.objects.count()
    assert comments_count_after == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    comments_count_before = Comment.objects.count()
    assert comments_count_before == 0
    bad_words_data = {
        'text': f'Какой-то текст, {choice(BAD_WORDS)}, еще текст'
    }
    url = reverse(NEWS_DETAIL_URL, args=(news.id,))
    response = author_client.post(url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    form = response.context['form']
    assert 'text' in form.errors
    assert WARNING in form.errors['text']
    comments_count_after = Comment.objects.count()
    assert comments_count_after == 0


def test_author_can_edit_comment(
    author_client, form_data, comment, url_to_comments, news, author
):
    url = reverse(NEWS_EDIT_URL, args=(comment.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_author_can_delete_comment(author_client, comment, url_to_comments):
    comments_count_before = Comment.objects.count()
    assert comments_count_before == 1
    url = reverse(NEWS_DELETE_URL, args=(comment.id,))
    response = author_client.delete(url)
    assertRedirects(response, url_to_comments)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == 0


def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    comments_count_before = Comment.objects.count()
    assert comments_count_before == 1
    url = reverse(NEWS_DELETE_URL, args=(comment.id,))
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_after = Comment.objects.count()
    assert comments_count_after == 1


def test_user_cant_edit_comment_of_another_user(
    admin_client, comment, form_data, news, author
):
    url = reverse(NEWS_EDIT_URL, args=(comment.id,))
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author
