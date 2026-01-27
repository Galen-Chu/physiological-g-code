# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Mobile application
- Real-time collaborative analysis
- Advanced ML-based pattern recognition
- Integration with genomic databases

## [1.2.0] - 2026-01-26

### Phase 4: Community Features

### Added
- **User Profiles**
  - User profile system with reputation tracking
  - Badge and achievement system
  - User statistics and activity tracking
  - Profile customization

- **Community Discussion**
  - Discussion thread system with upvoting/downvoting
  - Threaded comment system with nested replies
  - Mention system (@username) for community interaction
  - Comment moderation and flagging
  - Thread categorization and tagging

- **Notification System**
  - Real-time notifications for community activity
  - Email notifications for important updates
  - Notification preferences and settings
  - Notification history and mark-as-read functionality

- **API Key Management**
  - API key generation and management
  - Scoped API keys with specific permissions
  - API key usage tracking and rate limiting
  - API key rotation and revocation

- **Webhook System**
  - Webhook configuration for external integrations
  - Event-driven webhook triggers
  - Webhook authentication and security
  - Webhook delivery status and retry logic
  - Support for multiple webhook endpoints

### Phase 3: Enhanced Analysis

### Added
- **Advanced Pattern Detection**
  - Position-specific hexagram distribution analysis
  - Sliding window pattern detection with configurable window sizes
  - Motif discovery algorithms
  - Conservation analysis across multiple sequences
  - Information theory metrics (entropy, diversity indices)
  - Hexagram run detection and analysis
  - Autocorrelation analysis for pattern identification

- **Comparative Analysis**
  - Side-by-side sequence comparison
  - Mapping scheme comparison and validation
  - Statistical significance tests:
    - Chi-square test
    - Fisher's exact test
    - Kolmogorov-Smirnov test
  - Similarity metrics (Jaccard, cosine, overlap coefficients)
  - Multiple sequence alignment support
  - Conserved region detection across sequences

- **Export Functionality**
  - Export analysis results to CSV format
  - Export to JSON for data interchange
  - Export to FASTA format for sequence data
  - PDF report generation with visualizations
  - Batch export to multiple formats simultaneously
  - Customizable export templates and layouts

- **Interactive Visualizations**
  - Frequency distribution charts (bar, pie, donut)
  - Transition network visualization for hexagram sequences
  - Position vs hexagram heatmaps
  - 3D relationship projections using Plotly.js
  - Radar chart comparisons for multiple sequences
  - Sunburst hierarchical views
  - Real-time interactive chart updates
  - Export charts as PNG/SVG

### New API Endpoints
- `/api/patterns/position_analysis/` - Position-specific analysis
- `/api/patterns/sliding_window/` - Sliding window pattern detection
- `/api/patterns/motif_discovery/` - Motif discovery
- `/api/patterns/conservation/` - Conservation analysis
- `/api/patterns/entropy/` - Entropy calculation
- `/api/patterns/runs/` - Hexagram run detection
- `/api/patterns/correlation/` - Autocorrelation analysis
- `/api/comparative/side_by_side/` - Side-by-side comparison
- `/api/comparative/mapping_comparison/` - Mapping scheme comparison
- `/api/comparative/statistical_test/` - Statistical significance testing
- `/api/comparative/multiple_sequences/` - Multiple sequence alignment
- `/api/comparative/conserved_regions/` - Conserved region detection
- `/api/export/csv/` - CSV export
- `/api/export/json/` - JSON export
- `/api/export/fasta/` - FASTA export
- `/api/export/pdf_data/` - PDF report generation
- `/api/export/batch/` - Batch export
- `/api/visualizations/frequency/` - Frequency chart data
- `/api/visualizations/transitions/` - Transition network data
- `/api/visualizations/heatmap/` - Heatmap data
- `/api/visualizations/3d_relations/` - 3D relationship data
- `/api/visualizations/radar/` - Radar chart data

### New Backend Services
- `genetic_engine/pattern_analyzer.py` - Pattern detection algorithms (675 lines)
- `genetic_engine/comparative_analyzer.py` - Comparative analysis logic (666 lines)
- `genetic_engine/export_service.py` - Multi-format export service (480 lines)
- `genetic_engine/visualization_data_builder.py` - Chart data preparation (656 lines)

### New Data Models
- `api/models/analysis_pattern.py` - AnalysisPattern, PatternMatch, PositionAnalysis
- `api/models/comparative_analysis.py` - ComparativeAnalysis, ComparisonCache, StatisticalTest
- `api/models/user_profile.py` - UserProfile, Badge, Achievement
- `api/models/discussion.py` - DiscussionThread, ThreadCategory
- `api/models/comment.py` - Comment, CommentModeration
- `api/models/vote.py` - Vote (generic voting system)
- `api/models/notification.py` - Notification, NotificationPreference
- `api/models/api_key.py` - APIKey with scopes and rate limiting
- `api/models/webhook.py` - Webhook, WebhookEvent, WebhookDelivery

### New Frontend Components
- `static/js/utils/plotly-wrapper.js` - Standardized Plotly.js wrapper (331 lines)
- `static/js/components/charts/frequency-chart.js` - Frequency distribution charts
- `static/js/components/charts/transition-network.js` - Transition network visualizations
- `static/js/components/charts/heatmap.js` - Heatmap visualizations
- `static/js/components/charts/3d-relations.js` - 3D relationship projections
- `static/js/components/analysis-dashboard.js` - Main analysis dashboard (673 lines)

### Dependencies Added
- scipy - Scientific computing for statistical tests
- scikit-learn - Machine learning utilities
- reportlab - PDF generation
- matplotlib - Additional plotting capabilities

### Changed
- Updated `api/models/mapping.py` - Added vote_score, fork_count, usage_count fields
- Enhanced `api/urls.py` - Registered new ViewSets for patterns, comparative, export, visualizations
- Updated `static/js/utils/api-client.js` - Extended API client methods (186 lines)
- Enhanced `templates/index.html` - Added Plotly.js CDN and new JavaScript components

### Documentation
- Added `PHASE_3_4_IMPLEMENTATION_SUMMARY.md` - Complete implementation guide (383 lines)
- Updated README.md with new features and API documentation

### Technical Details
- **Files Changed**: 35 files
- **Lines Added**: 8,327+ lines
- **Test Coverage**: Test structure in place (tests/test_api/, tests/test_genetic_engine/)

## [1.0.0] - 2026-01-21

### Phase 1: Foundation

### Added
- **Django Project Setup**
  - Django 5.0 framework with Django REST Framework
  - PostgreSQL 15+ support with SQLite fallback
  - Redis caching layer
  - Celery task queue integration
  - Environment-based configuration (base/development/production)

- **Core Data Models**
  - Codon model - DNA/RNA triplet sequences with amino acid mappings
  - Hexagram model - 64 hexagrams with binary representation and metadata
  - CodonSequence model - User-submitted sequences with analysis results
  - HexagramInterpretation model - AI-generated interpretations
  - CodonHexagramMapping model - Multiple mapping schemes with validation
  - Start/stop codon identification
  - GC content calculation
  - Binary representation system

- **Translation Algorithms**
  - Binary mapping scheme - Direct nucleotide-to-binary-to-hexagram
  - Structural mapping scheme - Based on molecular properties (purine/pyrimidine)
  - Hydrogen bond mapping scheme - Based on bond count (2 vs 3)

- **REST API Endpoints**
  - `/api/codons/` - Codon CRUD operations
  - `/api/codons/start_codons/` - Get start codons
  - `/api/codons/stop_codons/` - Get stop codons
  - `/api/codons/by_amino_acid/?code=M` - Filter by amino acid
  - `/api/hexagrams/` - Hexagram CRUD operations
  - `/api/hexagrams/{id}/complementary/` - Get complementary hexagram
  - `/api/hexagrams/balanced/` - Get balanced hexagrams
  - `/api/sequences/` - Sequence management
  - `/api/sequences/analyze/` - Analyze sequences
  - `/api/sequences/{id}/statistics/` - Get sequence statistics
  - `/api/mappings/` - Mapping scheme management
  - `/api/mappings/active/` - Get active mapping
  - `/api/mappings/induce/` - AI-induced mapping
  - `/api/mappings/{id}/activate/` - Activate a mapping scheme

- **Management Commands**
  - `python manage.py load_hexagrams` - Load all 64 hexagrams
  - `python manage.py load_codons` - Load all 64 codons

- **Frontend**
  - Terminal-Chic theme with dark + neon green aesthetic
  - Sequence analyzer component
  - Hexagram grid visualization
  - API client utility
  - Hexagram renderer utility

### Phase 2: AI Integration

### Added
- **Google Gemini Integration**
  - AI-powered hexagram interpretations
  - Biological significance analysis
  - Traditional I Ching meaning generation
  - Synthesis of ancient and modern wisdom

- **AI Analysis Features**
  - Codon-to-hexagram interpretation
  - Sequence-level pattern analysis
  - AI-induced mapping discovery
  - Contextual interpretation based on biological data

- **Prompt Templates**
  - `genetic_engine/prompts/hexagram_interpretation.txt` - Single hexagram interpretation
  - `genetic_engine/prompts/mapping_induction.txt` - Mapping scheme optimization
  - `genetic_engine/prompts/sequence_analysis.txt` - Sequence-level analysis

- **AI Services**
  - `genetic_engine/genetic_ai_client.py` - Google Gemini API client (358 lines)
  - `genetic_engine/genetic_analysis_service.py` - Main analysis service (335 lines)
  - `genetic_engine/codon_translator.py` - Codon translation logic (256 lines)
  - `genetic_engine/hexagram_mapper.py` - Hexagram mapping (296 lines)

### API Endpoints Added
- `/api/analysis/analyze_codon/` - Analyze single codon
- `/api/analysis/analyze_sequence/` - Analyze DNA/RNA sequence
- `/api/analysis/translate_codons/` - Translate codons to amino acids
- `/api/analysis/mapping_schemes/` - List available mapping schemes
- `/api/hexagram_interpretations/` - Hexagram interpretation CRUD

### Deployment
- Dockerfile with multi-stage build
- docker-compose.yml for local development
- Environment configuration via .env files
- Production-ready settings

### Documentation
- Comprehensive README.md (408 lines)
- API documentation with Swagger/OpenAPI support
- Usage examples and code samples
- Quick start guide

### Technical Details
- **Files Created**: 60 files
- **Lines of Code**: 5,439 lines
- **Python Version**: 3.11+
- **Django Version**: 5.0
- **License**: MIT

### Test Structure
- pytest configuration (pytest.ini)
- Test directories: tests/test_api/, tests/test_genetic_engine/
- Ready for comprehensive test coverage

---

## Version Summary

- **[Unreleased]** - Planned Phase 5 features
- **[1.2.0]** - Phase 3 & 4: Enhanced Analysis + Community (2026-01-26)
- **[1.0.0]** - Phase 1 & 2: Foundation + AI Integration (2026-01-21)

---

## Links

- [GitHub Repository](https://github.com/Galen-Chu/physiological-g-code)
- [Issue Tracker](https://github.com/Galen-Chu/physiological-g-code/issues)
- [Documentation](https://github.com/Galen-Chu/physiological-g-code/blob/main/README.md)

---

**Note**: This project follows Semantic Versioning. Major version 1 indicates stable, production-ready functionality.
