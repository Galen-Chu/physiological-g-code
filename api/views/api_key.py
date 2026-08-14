"""APIKey views: create (plaintext shown once), list, revoke, delete."""
import hashlib
import secrets

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import APIKey
from api.serializers.api_key import APIKeySerializer


def _generate_key():
    """Return (plaintext, prefix, sha256-hash) for a new key."""
    plaintext = f'pgc_{secrets.token_hex(24)}'
    prefix = plaintext[:12]
    digest = hashlib.sha256(plaintext.encode()).hexdigest()
    return plaintext, prefix, digest


class APIKeyViewSet(viewsets.ModelViewSet):
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options', 'delete']

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plaintext, prefix, digest = _generate_key()
        api_key = serializer.save(user=request.user, key=digest, prefix=prefix)

        data = APIKeySerializer(api_key).data
        data['key'] = plaintext  # the only time the plaintext is returned
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        api_key = self.get_object()
        api_key.is_active = False
        api_key.save(update_fields=['is_active'])
        return Response(APIKeySerializer(api_key).data)

    @action(detail=True, methods=['post'])
    def rotate(self, request, pk=None):
        """Revoke the old key and return a fresh plaintext key."""
        api_key = self.get_object()
        plaintext, prefix, digest = _generate_key()
        api_key.key = digest
        api_key.prefix = prefix
        api_key.is_active = True
        api_key.save(update_fields=['key', 'prefix', 'is_active'])

        data = APIKeySerializer(api_key).data
        data['key'] = plaintext
        return Response(data)
