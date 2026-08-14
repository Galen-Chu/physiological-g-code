"""Community API tests: profiles, discussions, comments, votes,
notifications, API keys, webhooks."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from api.models import Discussion, Comment, Notification, APIKey, Webhook

User = get_user_model()

pytestmark = pytest.mark.django_db


def make_user(username, password='a-secure-password-123'):
    user = User.objects.create_user(username=username, password=password)
    from api.models import UserProfile
    UserProfile.objects.get_or_create(user=user)
    return user


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def alice():
    return make_user('alice')


@pytest.fixture
def bob():
    return make_user('bob')


class TestProfiles:
    def test_own_profile_get_and_patch(self, alice):
        client = auth_client(alice)
        resp = client.get('/api/profiles/me/')
        assert resp.status_code == 200
        assert resp.data['username'] == 'alice'

        resp = client.patch('/api/profiles/me/', {'bio': 'hello'}, format='json')
        assert resp.status_code == 200
        assert resp.data['bio'] == 'hello'

    def test_public_profile_is_readable_without_auth(self, alice):
        client = APIClient()
        resp = client.get(f'/api/profiles/{alice.profile.id}/')
        assert resp.status_code == 200
        assert 'email' not in resp.data  # private fields hidden publicly


class TestDiscussionsAndComments:
    def create_discussion(self, user, title='First post'):
        client = auth_client(user)
        resp = client.post('/api/discussions/', {
            'title': title, 'content': 'body text',
            'discussion_type': 'question', 'tags': ['test'],
        }, format='json')
        assert resp.status_code == 201
        return resp.data

    def test_create_list_and_retrieve_discussion(self, alice):
        created = self.create_discussion(alice)
        assert created['author'] == 'alice'
        assert created['slug']

        client = APIClient()  # public read
        assert client.get('/api/discussions/').status_code == 200
        assert client.get(f"/api/discussions/{created['id']}/").status_code == 200

    def test_comment_and_threaded_reply(self, alice, bob):
        discussion = self.create_discussion(alice)
        client = auth_client(bob)
        top = client.post(f"/api/discussions/{discussion['id']}/comments/",
                          {'content': 'nice post'}, format='json')
        assert top.status_code == 201
        assert top.data['author'] == 'bob'

        reply = client.post(f"/api/discussions/{discussion['id']}/comments/",
                            {'content': 'reply', 'parent': top.data['id']}, format='json')
        assert reply.status_code == 201
        assert reply.data['parent'] == top.data['id']

        listing = client.get(f"/api/discussions/{discussion['id']}/comments/")
        assert listing.data['count'] == 2

    def test_comment_notifies_discussion_author(self, alice, bob):
        discussion = self.create_discussion(alice)
        client = auth_client(bob)
        client.post(f"/api/discussions/{discussion['id']}/comments/",
                    {'content': 'hello'}, format='json')
        assert Notification.objects.filter(recipient=alice, actor=bob).exists()

    def test_only_author_may_edit_comment(self, alice, bob):
        discussion = self.create_discussion(alice)
        client = auth_client(alice)
        comment = client.post(f"/api/discussions/{discussion['id']}/comments/",
                              {'content': 'mine'}, format='json').data

        intruder = auth_client(bob)
        resp = intruder.patch(f"/api/comments/{comment['id']}/",
                              {'content': 'hacked'}, format='json')
        assert resp.status_code == 403

        owner = auth_client(alice)
        resp = owner.patch(f"/api/comments/{comment['id']}/",
                           {'content': 'edited'}, format='json')
        assert resp.status_code == 200 and resp.data['content'] == 'edited'

    def test_discussion_vote_updates_score(self, alice, bob):
        discussion = self.create_discussion(alice)
        client = auth_client(bob)
        resp = client.post(f"/api/discussions/{discussion['id']}/vote/",
                           {'vote_type': 'up'}, format='json')
        assert resp.status_code == 200 and resp.data['vote_score'] == 1

        # re-vote down updates instead of double counting
        resp = client.post(f"/api/discussions/{discussion['id']}/vote/",
                           {'vote_type': 'down'}, format='json')
        assert resp.data['vote_score'] == -1

    def test_comment_vote_updates_counts(self, alice, bob):
        discussion = self.create_discussion(alice)
        comment = auth_client(alice).post(
            f"/api/discussions/{discussion['id']}/comments/",
            {'content': 'vote on me'}, format='json').data

        resp = auth_client(bob).post(f"/api/comments/{comment['id']}/vote/",
                                     {'vote_type': 'up'}, format='json')
        assert resp.status_code == 200 and resp.data['vote_score'] == 1


class TestNotifications:
    def test_list_and_mark_read(self, alice, bob):
        Notification.objects.create(
            recipient=alice, notification_type='system',
            title='t1', message='m1', url='https://example.com',
        )
        Notification.objects.create(
            recipient=alice, notification_type='system',
            title='t2', message='m2', url='https://example.com',
        )
        client = auth_client(alice)
        listing = client.get('/api/notifications/')
        assert listing.status_code == 200

        first_id = listing.data['results'][0]['id']
        assert client.post(f'/api/notifications/{first_id}/mark_read/').status_code == 200

        marked = client.post('/api/notifications/mark_all_read/')
        assert marked.data['marked_read'] == 1  # the remaining unread one

    def test_isolated_between_users(self, alice, bob):
        Notification.objects.create(
            recipient=bob, notification_type='system',
            title='private', message='m', url='https://example.com',
        )
        listing = auth_client(alice).get('/api/notifications/')
        assert listing.data['count'] == 0


class TestAPIKeys:
    def test_create_shows_plaintext_once_then_only_prefix(self, alice):
        client = auth_client(alice)
        created = client.post('/api/api-keys/', {'name': 'my key'}, format='json')
        assert created.status_code == 201
        assert created.data['key'].startswith('pgc_')
        assert created.data['prefix'] == created.data['key'][:12]

        # list shows metadata only — never the plaintext again
        listing = client.get('/api/api-keys/')
        assert 'key' not in listing.data['results'][0]
        assert listing.data['results'][0]['prefix'] == created.data['prefix']

    def test_revoke_and_rotate(self, alice):
        client = auth_client(alice)
        created = client.post('/api/api-keys/', {'name': 'my key'}, format='json').data

        revoked = client.post(f"/api/api-keys/{created['id']}/revoke/")
        assert revoked.status_code == 200 and revoked.data['is_active'] is False

        rotated = client.post(f"/api/api-keys/{created['id']}/rotate/")
        assert rotated.status_code == 200
        assert rotated.data['key'].startswith('pgc_') and rotated.data['is_active'] is True

    def test_keys_are_per_user(self, alice, bob):
        created = auth_client(alice).post('/api/api-keys/', {'name': 'k'}, format='json').data
        assert auth_client(bob).get(f"/api/api-keys/{created['id']}/").status_code == 404


class TestWebhooks:
    def test_webhook_crud_and_secret(self, alice):
        client = auth_client(alice)
        created = client.post('/api/webhooks/', {
            'name': 'hook', 'url': 'https://example.com/hook',
            'events': ['analysis.completed'],
        }, format='json')
        assert created.status_code == 201
        assert created.data['secret'].startswith('whk_')

        # list must NOT reveal the secret again
        listing = client.get('/api/webhooks/')
        assert 'secret' not in listing.data['results'][0]

        regenerated = client.post(f"/api/webhooks/{created.data['id']}/regenerate_secret/")
        assert regenerated.status_code == 200
        assert regenerated.data['secret'].startswith('whk_')

        assert client.delete(f"/api/webhooks/{created.data['id']}/").status_code == 204

    def test_webhooks_are_per_user(self, alice, bob):
        created = auth_client(alice).post('/api/webhooks/', {
            'name': 'hook', 'url': 'https://example.com/hook', 'events': [],
        }, format='json').data
        assert auth_client(bob).get(f"/api/webhooks/{created['id']}/").status_code == 404
