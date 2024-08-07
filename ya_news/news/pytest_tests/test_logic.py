from http import HTTPStatus
from random import choice

import pytest
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertRedirects

NEWS_DELETE_URL = 'news:delete'
NEWS_DETAIL_URL = 'news:detail'
NEWS_EDIT_URL = 'news:edit'
NEWS_HOME_URL = 'news:home'
COMMENT_TEXT = 'Новый текст комментария'


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    comments_count_before = Comment.objects.count()
    url = reverse(NEWS_DETAIL_URL, args=(news.id,))
    client.post(url, data={'text': COMMENT_TEXT})
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


def test_user_can_create_comment(author_client, author, news):
    comments_count_before = Comment.objects.count()
    url = reverse(NEWS_DETAIL_URL, args=(news.id,))
    response = author_client.post(url, data={'text': COMMENT_TEXT})
    assertRedirects(response, f'{url}#comments')
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before + 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    comments_count_before = Comment.objects.count()
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
    assert comments_count_after == comments_count_before


def test_author_can_edit_comment(
    author_client, comment, news, author
):
    url = reverse(NEWS_EDIT_URL, args=(comment.id,))
    response = author_client.post(url, data={'text': COMMENT_TEXT})
    assertRedirects(response, reverse(
        'news:detail',
        args=(news.id,)) + '#comments'
    )
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_author_can_delete_comment(author_client, comment, news):
    comments_count_before = Comment.objects.count()
    url = reverse(NEWS_DELETE_URL, args=(comment.id,))
    response = author_client.delete(url)
    assertRedirects(response, reverse(
        'news:detail',
        args=(news.id,)) + '#comments'
    )
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before - 1


def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    comments_count_before = Comment.objects.count()
    url = reverse(NEWS_DELETE_URL, args=(comment.id,))
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


def test_user_cant_edit_comment_of_another_user(
    admin_client, comment, news, author
):
    url = reverse(NEWS_EDIT_URL, args=(comment.id,))
    response = admin_client.post(url, data={'text': COMMENT_TEXT})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author
