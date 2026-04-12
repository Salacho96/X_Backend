import pytest
from rest_framework.test import APIClient
from apps.users.models import User, Follow
from apps.tweets.models import Tweet, Like


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def make_user(email='test@test.com', username='testuser', password='testpass123'):
        return User.objects.create_user(
            email=email, username=username, password=password
        )
    return make_user


@pytest.fixture
def auth_client(client, create_user):
    user = create_user()
    response = client.post('/api/auth/login/', {
        'email': 'test@test.com',
        'password': 'testpass123'
    }, format='json')
    token = response.data['data']['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client, user


# --- TWEET TESTS ---

@pytest.mark.django_db
def test_create_tweet(auth_client):
    client, user = auth_client
    response = client.post('/api/tweets/', {'content': 'Hola mundo!'}, format='json')
    assert response.status_code == 201
    assert response.data['success'] is True
    assert Tweet.objects.filter(author=user).count() == 1


@pytest.mark.django_db
def test_create_tweet_empty_content(auth_client):
    client, user = auth_client
    response = client.post('/api/tweets/', {'content': '   '}, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_tweet_exceeds_280_chars(auth_client):
    client, user = auth_client
    response = client.post('/api/tweets/', {'content': 'x' * 281}, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_delete_own_tweet(auth_client):
    client, user = auth_client
    tweet = Tweet.objects.create(author=user, content='Tweet a eliminar')
    response = client.delete(f'/api/tweets/{tweet.id}/')
    assert response.status_code == 200
    assert not Tweet.objects.filter(id=tweet.id).exists()


@pytest.mark.django_db
def test_cannot_delete_other_tweet(auth_client, create_user):
    client, user = auth_client
    other = create_user(email='other@test.com', username='otheruser')
    tweet = Tweet.objects.create(author=other, content='Tweet ajeno')
    response = client.delete(f'/api/tweets/{tweet.id}/')
    assert response.status_code == 403


@pytest.mark.django_db
def test_timeline_shows_followed_tweets(auth_client, create_user):
    client, user = auth_client
    other = create_user(email='other@test.com', username='otheruser')
    Follow.objects.create(follower=user, following=other)
    Tweet.objects.create(author=other, content='Tweet del seguido')
    response = client.get('/api/tweets/timeline/')
    assert response.status_code == 200
    assert len(response.data['data']['tweets']) == 1


@pytest.mark.django_db
def test_timeline_excludes_unfollowed_tweets(auth_client, create_user):
    client, user = auth_client
    other = create_user(email='other@test.com', username='otheruser')
    Tweet.objects.create(author=other, content='Tweet de no seguido')
    response = client.get('/api/tweets/timeline/')
    assert response.status_code == 200
    assert len(response.data['data']['tweets']) == 0


@pytest.mark.django_db
def test_like_tweet(auth_client):
    client, user = auth_client
    tweet = Tweet.objects.create(author=user, content='Tweet a likear')
    response = client.post(f'/api/tweets/{tweet.id}/like/')
    assert response.status_code == 201
    assert Like.objects.filter(user=user, tweet=tweet).exists()


@pytest.mark.django_db
def test_unlike_tweet(auth_client):
    client, user = auth_client
    tweet = Tweet.objects.create(author=user, content='Tweet a unlikear')
    Like.objects.create(user=user, tweet=tweet)
    response = client.post(f'/api/tweets/{tweet.id}/like/')
    assert response.status_code == 200
    assert not Like.objects.filter(user=user, tweet=tweet).exists()


@pytest.mark.django_db
def test_tweet_requires_auth(client):
    response = client.post('/api/tweets/', {'content': 'Sin auth'}, format='json')
    assert response.status_code == 401