"""
URL configuration for Physiological G-Code API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
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

urlpatterns = [
    # API root
    path('', api_root, name='api-root'),

    # Router endpoints
    path('', include(router.urls)),

    # Authentication (to be added in Phase 4)
    # path('auth/', include('rest_framework.urls')),

    # Schema and documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-schema'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc-schema'),
    path('docs/', include_docs_urls(title='Physiological G-Code API')),
]
