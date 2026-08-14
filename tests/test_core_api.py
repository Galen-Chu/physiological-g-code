"""Core resource API tests: management commands + endpoints."""
import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from api.models import Codon, Hexagram

pytestmark = pytest.mark.django_db


@pytest.fixture(scope='class')
def loaded_data(django_db_setup, django_db_blocker):
    """Load the 64 codons + 64 hexagrams once per class-run."""
    with django_db_blocker.unblock():
        call_command('load_codons', verbosity=0)
        call_command('load_hexagrams', verbosity=0)


@pytest.mark.usefixtures('loaded_data')
class TestCoreResources:
    def test_sixty_four_codons_loaded(self):
        assert Codon.objects.count() == 64

    def test_sixty_four_hexagrams_loaded(self):
        assert Hexagram.objects.count() == 64

    def test_codons_endpoint_public(self):
        client = APIClient()
        resp = client.get('/api/codons/')
        assert resp.status_code == 200
        assert resp.data['count'] == 64

    def test_hexagrams_endpoint_public(self):
        client = APIClient()
        resp = client.get('/api/hexagrams/')
        assert resp.status_code == 200
        assert resp.data['count'] == 64

    def test_analyze_sequence_endpoint(self):
        from django.contrib.auth import get_user_model
        client = APIClient()
        user = get_user_model().objects.create_user(username='analyst', password='pw-12345678')
        client.force_authenticate(user=user)
        resp = client.post('/api/analysis/analyze_sequence/', {
            'sequence': 'ATGCGATAA',
            'sequence_name': 'Test',
            'sequence_type': 'DNA',
            'mapping_scheme': 'scheme_1',
        }, format='json')
        assert resp.status_code == 200

    def test_swagger_schema_renders(self):
        client = APIClient()
        assert client.get('/api/schema/').status_code == 200
