"""Webhook views: CRUD + secret regeneration (secret shown once)."""
import secrets

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import Webhook
from api.serializers.webhook import WebhookSerializer


class WebhookViewSet(viewsets.ModelViewSet):
    serializer_class = WebhookSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'head', 'options', 'delete']

    def get_queryset(self):
        return Webhook.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        secret = f'whk_{secrets.token_hex(24)}'
        webhook = serializer.save(user=request.user, secret=secret)

        data = WebhookSerializer(webhook).data
        data['secret'] = secret  # the only time the plaintext secret is returned
        return Response(data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Never let a plain update overwrite the stored secret."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = {k: v for k, v in request.data.items() if k != 'secret'}
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def regenerate_secret(self, request, pk=None):
        webhook = self.get_object()
        secret = f'whk_{secrets.token_hex(24)}'
        webhook.secret = secret
        webhook.save(update_fields=['secret'])
        data = WebhookSerializer(webhook).data
        data['secret'] = secret
        return Response(data)
