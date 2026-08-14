"""UserProfile views: public profiles + own-profile read/update."""
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.models import UserProfile
from api.serializers.user_profile import PublicProfileSerializer, OwnProfileSerializer


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public profiles are readable by anyone; the owner additionally has
    GET/PATCH /api/profiles/me/ for the full profile and preferences.
    """

    queryset = UserProfile.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'me':
            return OwnProfileSerializer
        return PublicProfileSerializer

    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        # get-or-create so pre-existing users (createsuperuser, fixtures) also
        # have a profile without needing the register endpoint
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if request.method == 'PATCH':
            serializer = OwnProfileSerializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = OwnProfileSerializer(profile)
        return Response(serializer.data)
