import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

NEWS_DETAIL_URL = 'news:detail'
NEWS_HOME_URL = 'news:home'


@pytest.mark.django_db
@pytest.mark.usefixtures('all_news')
def test_news_count(client):
    url = reverse(NEWS_HOME_URL)
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
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
def test_form_availability_for_client(news, client):
    url = reverse(NEWS_DETAIL_URL, args=(news.id,))
    response = client.get(url)
    assert ('form' in response.context) is False


@pytest.mark.django_db
def test_form_availability_for_author_client(news, author_client):
    url = reverse(NEWS_DETAIL_URL, args=(news.id,))
    response = author_client.get(url)
    assert ('form' in response.context) is True
    assert isinstance(response.context['form'], CommentForm)
