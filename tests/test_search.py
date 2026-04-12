import pytest
from rest_framework.test import APIClient
from apps.users.models import User


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


@pytest.mark.django_db
def test_search_by_username(auth_client, create_user):
    client, user = auth_client
    create_user(email='other@test.com', username='otheruser')
    response = client.get('/api/search/users/?q=other')
    assert response.status_code == 200
    assert len(response.data['data']) == 1


@pytest.mark.django_db
def test_search_empty_query(auth_client):
    client, user = auth_client
    response = client.get('/api/search/users/?q=')
    assert response.status_code == 200
    assert response.data['data'] == []


@pytest.mark.django_db
def test_search_excludes_self(auth_client):
    client, user = auth_client
    response = client.get(f'/api/search/users/?q={user.username}')
    assert response.status_code == 200
    assert len(response.data['data']) == 0


@pytest.mark.django_db
def test_search_requires_auth(client):
    response = client.get('/api/search/users/?q=test')
    assert response.status_code == 401


@pytest.mark.django_db
def test_search_no_results(auth_client):
    client, user = auth_client
    response = client.get('/api/search/users/?q=xyz123')
    assert response.status_code == 200
    assert len(response.data['data']) == 0