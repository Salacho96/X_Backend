import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User, Follow


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        'email': 'test@test.com',
        'username': 'testuser',
        'password': 'testpass123'
    }


@pytest.fixture
def create_user(db):
    def make_user(email='test@test.com', username='testuser', password='testpass123'):
        return User.objects.create_user(
            email=email,
            username=username,
            password=password
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


# --- AUTH TESTS ---

@pytest.mark.django_db
def test_register_success(client, user_data):
    response = client.post('/api/auth/register/', user_data, format='json')
    assert response.status_code == 201
    assert response.data['success'] is True
    assert 'access' in response.data['data']
    assert 'refresh' in response.data['data']


@pytest.mark.django_db
def test_register_duplicate_email(client, create_user, user_data):
    create_user()
    response = client.post('/api/auth/register/', user_data, format='json')
    assert response.status_code == 400
    assert response.data['success'] is False


@pytest.mark.django_db
def test_register_short_password(client):
    response = client.post('/api/auth/register/', {
        'email': 'test@test.com',
        'username': 'testuser',
        'password': '123'
    }, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_login_success(client, create_user):
    create_user()
    response = client.post('/api/auth/login/', {
        'email': 'test@test.com',
        'password': 'testpass123'
    }, format='json')
    assert response.status_code == 200
    assert response.data['success'] is True
    assert 'access' in response.data['data']


@pytest.mark.django_db
def test_login_wrong_password(client, create_user):
    create_user()
    response = client.post('/api/auth/login/', {
        'email': 'test@test.com',
        'password': 'wrongpass'
    }, format='json')
    assert response.status_code == 400
    assert response.data['success'] is False


@pytest.mark.django_db
def test_login_wrong_email(client):
    response = client.post('/api/auth/login/', {
        'email': 'noexiste@test.com',
        'password': 'testpass123'
    }, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_logout_success(auth_client):
    client, user = auth_client
    login_response = client.post('/api/auth/login/', {
        'email': 'test@test.com',
        'password': 'testpass123'
    }, format='json')
    refresh = login_response.data['data']['refresh']
    response = client.post('/api/auth/logout/', {'refresh': refresh}, format='json')
    assert response.status_code == 200
    assert response.data['success'] is True


@pytest.mark.django_db
def test_profile_get_success(auth_client):
    client, user = auth_client
    response = client.get(f'/api/auth/profile/{user.username}/')
    assert response.status_code == 200
    assert response.data['data']['username'] == user.username


@pytest.mark.django_db
def test_profile_requires_auth(client):
    response = client.get('/api/auth/profile/testuser/')
    assert response.status_code == 401


# --- FOLLOW TESTS ---

@pytest.mark.django_db
def test_follow_user(auth_client, create_user):
    client, user = auth_client
    other = create_user(email='other@test.com', username='otheruser')
    response = client.post(f'/api/auth/profile/{other.username}/follow/')
    assert response.status_code == 201
    assert Follow.objects.filter(follower=user, following=other).exists()


@pytest.mark.django_db
def test_unfollow_user(auth_client, create_user):
    client, user = auth_client
    other = create_user(email='other@test.com', username='otheruser')
    Follow.objects.create(follower=user, following=other)
    response = client.post(f'/api/auth/profile/{other.username}/follow/')
    assert response.status_code == 200
    assert not Follow.objects.filter(follower=user, following=other).exists()


@pytest.mark.django_db
def test_cannot_follow_yourself(auth_client):
    client, user = auth_client
    response = client.post(f'/api/auth/profile/{user.username}/follow/')
    assert response.status_code == 400


@pytest.mark.django_db
def test_followers_list(auth_client, create_user):
    client, user = auth_client
    other = create_user(email='other@test.com', username='otheruser')
    Follow.objects.create(follower=other, following=user)
    response = client.get(f'/api/auth/profile/{user.username}/followers/')
    assert response.status_code == 200
    assert len(response.data['data']) == 1


@pytest.mark.django_db
def test_following_list(auth_client, create_user):
    client, user = auth_client
    other = create_user(email='other@test.com', username='otheruser')
    Follow.objects.create(follower=user, following=other)
    response = client.get(f'/api/auth/profile/{user.username}/following/')
    assert response.status_code == 200
    assert len(response.data['data']) == 1
