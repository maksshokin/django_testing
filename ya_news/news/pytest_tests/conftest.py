from datetime import timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import Client
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model: type[get_user_model()]) -> get_user_model():
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author: User, client: Client) -> Client:
    client.force_login(author)
    return client


@pytest.fixture
def news() -> News:
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def comment(author: User, news: News) -> Comment:
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст'
    )


@pytest.fixture
def all_news() -> News:
    today = timezone.localdate()
    all_news: list[News] = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def all_comment(news: News, author: User) -> Comment:
    now = timezone.now()
    for index in range(2):
        comment: Comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
