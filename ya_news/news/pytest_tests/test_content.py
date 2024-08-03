from django.conf import settings
from django.urls import reverse

import pytest

AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
CLIENT = pytest.lazy_fixture('client')
NEWS_DETAIL_URL = 'news:detail'
NEWS_HOME_URL = 'news:home'


@pytest.mark.django_db
@pytest.mark.usefixtures('all_news')
def test_news_count(client):
    url = reverse(NEWS_HOME_URL)
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('all_news')
def test_news_order(client):
    url = reverse(NEWS_HOME_URL)
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert sorted_dates == all_dates


@pytest.mark.django_db
@pytest.mark.usefixtures('all_comment')
def test_comments_order(client, news):
    url = reverse(NEWS_DETAIL_URL, args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_dates = [comment.created for comment in news.comment_set.all()]
    sorted_dates = sorted(all_dates)
    assert sorted_dates == all_dates


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, note_in_list',
    (
        (AUTHOR_CLIENT, True),
        (CLIENT, False),
    )
)
def test_form_availability_for_different_clients(
    parametrized_client, note_in_list, news
):
    url = reverse(NEWS_DETAIL_URL, args=(news.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is note_in_list
