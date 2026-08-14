"""
URL configuration for Physiological G-Code API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from api.views import (
    CodonViewSet,
    HexagramViewSet,
    CodonSequenceViewSet,
    HexagramInterpretationViewSet,
    CodonHexagramMappingViewSet,
    AnalysisViewSet,
)
# Phase 3: Enhanced Analysis
from api.views.pattern_analysis import PatternAnalysisViewSet
from api.views.comparative_analysis import ComparativeAnalysisViewSet
from api.views.export_views import ExportViewSet
from api.views.visualization_views import VisualizationViewSet

from api.views.analysis import api_root
# Phase 4: Auth + Community
from api.views.auth import RegisterView, LoginView
from api.views.user_profile import UserProfileViewSet
from api.views.discussion import DiscussionViewSet, CommentViewSet
from api.views.notification import NotificationViewSet
from api.views.api_key import APIKeyViewSet
from api.views.webhook import WebhookViewSet

# Create router
router = DefaultRouter()
router.register(r'codons', CodonViewSet, basename='codon')
router.register(r'hexagrams', HexagramViewSet, basename='hexagram')
router.register(r'sequences', CodonSequenceViewSet, basename='codonsequence')
router.register(r'interpretations', HexagramInterpretationViewSet, basename='hexagraminterpretation')
router.register(r'mappings', CodonHexagramMappingViewSet, basename='codonhexagrammapping')
router.register(r'analysis', AnalysisViewSet, basename='analysis')

# Phase 3: Enhanced Analysis
router.register(r'patterns', PatternAnalysisViewSet, basename='pattern')
router.register(r'comparative', ComparativeAnalysisViewSet, basename='comparative')
router.register(r'export', ExportViewSet, basename='export')
router.register(r'visualizations', VisualizationViewSet, basename='visualization')

# Phase 4: Community
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'discussions', DiscussionViewSet, basename='discussion')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'api-keys', APIKeyViewSet, basename='api-key')
router.register(r'webhooks', WebhookViewSet, basename='webhook')

urlpatterns = [
    # API root
    path('', api_root, name='api-root'),

    # Router endpoints
    path('', include(router.urls)),

    # Authentication
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),

    # Schema and documentation (drf-spectacular; the legacy coreapi
    # docs route was removed — coreapi is deprecated and uninstalled)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-schema'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc-schema'),
]
