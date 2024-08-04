from http import HTTPStatus

from django.urls import reverse

import pytest
from pytest_django.asserts import assertRedirects


ADMIN_CLIENT = pytest.lazy_fixture('admin_client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
NEWS_DELETE_URL = 'news:delete'
NEWS_DETAIL_URL = 'news:detail'
NEWS_EDIT_URL = 'news:edit'
NEWS_HOME_URL = 'news:home'
USERS_LOGIN_URL = 'users:login'
USERS_LOGOUT_URL = 'users:logout'
USERS_SIGNUP_URL = 'users:signup'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, note_object',
    (
        (NEWS_HOME_URL, None),
        (NEWS_DETAIL_URL, pytest.lazy_fixture('id_for_args')),
        (USERS_LOGIN_URL, None),
        (USERS_LOGOUT_URL, None),
        (USERS_SIGNUP_URL, None),
    ),
)
def test_pages_availability_anonymous_user(name, note_object, client):
    url = reverse(name, args=note_object)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (ADMIN_CLIENT, HTTPStatus.NOT_FOUND),
        (AUTHOR_CLIENT, HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    (NEWS_EDIT_URL, NEWS_DELETE_URL),
)
def test_availability_for_comment_edit_and_delete(
        parametrized_client, name, comment, expected_status
):
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    (NEWS_EDIT_URL, NEWS_DELETE_URL),
)
def test_redirects(client, name, comment):
    login_url = reverse(USERS_LOGIN_URL)
    url = reverse(name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
