"""Auth API tests: register → login → authenticated request."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


def test_register_returns_tokens_and_creates_profile(client):
    resp = client.post('/api/auth/register/', {
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'a-secure-password-123',
    }, format='json')
    assert resp.status_code == 201
    assert 'access' in resp.data and 'refresh' in resp.data
    assert resp.data['user']['username'] == 'alice'

    user = User.objects.get(username='alice')
    assert hasattr(user, 'profile')  # profile auto-created


def test_register_rejects_weak_password(client):
    resp = client.post('/api/auth/register/', {
        'username': 'bob',
        'email': 'bob@example.com',
        'password': '123',
    }, format='json')
    assert resp.status_code == 400


def test_register_rejects_duplicate_username(client):
    User.objects.create_user(username='carol', password='a-secure-password-123')
    resp = client.post('/api/auth/register/', {
        'username': 'carol',
        'email': 'carol@example.com',
        'password': 'a-secure-password-123',
    }, format='json')
    assert resp.status_code == 400


def test_login_returns_token_pair(client):
    User.objects.create_user(username='dave', password='a-secure-password-123')
    resp = client.post('/api/auth/login/', {
        'username': 'dave',
        'password': 'a-secure-password-123',
    }, format='json')
    assert resp.status_code == 200
    assert 'access' in resp.data


def test_login_rejects_wrong_password(client):
    User.objects.create_user(username='erin', password='a-secure-password-123')
    resp = client.post('/api/auth/login/', {
        'username': 'erin',
        'password': 'wrong-password',
    }, format='json')
    assert resp.status_code == 401


def test_jwt_authenticates_protected_endpoint(client):
    User.objects.create_user(username='frank', password='a-secure-password-123')
    login = client.post('/api/auth/login/', {
        'username': 'frank', 'password': 'a-secure-password-123',
    }, format='json')
    token = login.data['access']

    resp = client.get('/api/notifications/', HTTP_AUTHORIZATION=f'Bearer {token}')
    assert resp.status_code == 200

    # ...and anonymously it must be rejected
    anon = APIClient()
    assert anon.get('/api/notifications/').status_code == 401
