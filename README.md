# 🧬 Physiological G-Code

> **Where genetics meets philosophy** - A platform for exploring the connections between DNA/RNA codons and I Ching hexagrams

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 What is Physiological G-Code?

**Physiological G-Code** is an interdisciplinary platform that bridges molecular biology and Chinese philosophy by exploring the fascinating parallel between two 64-state systems:

- **64 DNA Codons** - All possible combinations of 4 nucleotides (A, T, G, C) in triplets
- **64 I Ching Hexagrams** - All combinations of 6 yin/yang lines

Both systems encode fundamental information - one for biological life, the other for philosophical wisdom. This platform enables you to translate genetic sequences into hexagram sequences and discover emergent patterns.

---

## 🎯 Features

### 1. **Sequence Analysis** 🧬
- Upload DNA/RNA sequences for translation
- Automatic codon-to-hexagram mapping
- Amino acid translation
- GC content calculation
- Dominant hexagram identification

### 2. **Multiple Mapping Schemes** 🔄
- **Binary**: Direct nucleotide-to-binary-to-hexagram conversion
- **Structural**: Based on molecular properties (purine/pyrimidine)
- **Hydrogen Bond**: Based on bond count (2 vs 3)
- **AI-Induced**: Machine learning discovers optimal associations

### 3. **AI-Powered Interpretations** 🤖
- Google Gemini integration for generating interpretations
- Biological significance analysis
- Traditional I Ching meanings
- Synthesis of ancient and modern wisdom

### 4. **Advanced Pattern Analysis** 📊 (Phase 3)
- Position-specific hexagram distribution analysis
- Sliding window pattern detection
- Motif discovery with configurable parameters
- Conservation analysis across sequences
- Information theory metrics (entropy, diversity)
- Hexagram run detection
- Autocorrelation analysis

### 5. **Comparative Analysis** ⚖️ (Phase 3)
- Side-by-side sequence comparison
- Mapping scheme comparison
- Statistical significance tests (chi-square, Fisher's exact, KS test)
- Similarity metrics (Jaccard, cosine, overlap)
- Multi-sequence alignment
- Conserved region detection

### 6. **Interactive Visualizations** 📈 (Phase 3)
- Frequency distribution charts (bar, pie, donut)
- Transition network visualization
- Position vs hexagram heatmaps
- 3D relationship projections
- Radar chart comparisons
- Sunburst hierarchical views
- Real-time interactive charts with Plotly.js

### 7. **Export Functionality** 💾 (Phase 3)
- Export to CSV, JSON, FASTA formats
- PDF report generation
- Image export (PNG/SVG)
- Batch export to multiple formats

### 8. **RESTful API** 🔌
- Complete CRUD operations for all entities
- Authentication support
- OpenAPI/Swagger documentation
- Webhook support for real-time updates

### 9. **Community Features** 👥 (Phase 4)
- User profiles with reputation system
- Discussion threads with voting
- Threaded comments with mentions
- Notification system
- API key management for third-party integrations
- Webhook system for event notifications
- Badge system and achievements

---

## 🛠️ Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.11+ |
| **Framework** | Django 5.0 |
| **API** | Django REST Framework |
| **Database** | PostgreSQL 15+ / SQLite |
| **Cache** | Redis |
| **Task Queue** | Celery |

### AI/ML
| Component | Technology |
|-----------|-----------|
| **AI Model** | Google Gemini API |
| **BioPython** | Sequence analysis |

### Frontend
| Component | Technology |
|-----------|-----------|
| **Styling** | Custom CSS (Terminal-Chic theme) |
| **JavaScript** | Vanilla ES6+ |
| **Charts** | Plotly.js (interactive visualizations) |
| **Aesthetic** | Dark + Neon Green |

### Analysis & ML
| Component | Technology |
|-----------|-----------|
| **Bio** | BioPython |
| **Stats** | SciPy, scikit-learn |
| **Charts** | Plotly.js |
| **PDF** | ReportLab |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (optional, can use SQLite)
- Redis 7+ (optional)
- Google Gemini API Key (optional)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/Galen-Chu/physiological-g-code.git
cd physiological-g-code
```

#### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your configuration
```

#### 5. Database Setup

```bash
python manage.py migrate
python manage.py createsuperuser
```

#### 6. Load Initial Data

```bash
# Load all 64 hexagrams
python manage.py load_hexagrams

# Load all 64 codons
python manage.py load_codons
```

#### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

---

## 📖 API Documentation

### Authentication
```
POST   /api/auth/register/
POST   /api/auth/login/
```

### Analysis
```
POST   /api/analysis/analyze_codon/
POST   /api/analysis/analyze_sequence/
POST   /api/analysis/translate_codons/
GET    /api/analysis/mapping_schemes/
```

### Codons
```
GET    /api/codons/
GET    /api/codons/{id}/
GET    /api/codons/start_codons/
GET    /api/codons/stop_codons/
GET    /api/codons/by_amino_acid/?code=M
```

### Hexagrams
```
GET    /api/hexagrams/
GET    /api/hexagrams/{id}/
GET    /api/hexagrams/{id}/codons/
GET    /api/hexagrams/{id}/complementary/
GET    /api/hexagrams/balanced/
```

### Sequences
```
GET    /api/sequences/
POST   /api/sequences/analyze/
GET    /api/sequences/{id}/statistics/
```

### Mappings
```
GET    /api/mappings/
GET    /api/mappings/active/
POST   /api/mappings/induce/
POST   /api/mappings/{id}/activate/
```

### Pattern Analysis (Phase 3)
```
POST   /api/patterns/position_analysis/
POST   /api/patterns/sliding_window/
POST   /api/patterns/motif_discovery/
POST   /api/patterns/conservation/
POST   /api/patterns/entropy/
POST   /api/patterns/runs/
POST   /api/patterns/correlation/
```

### Comparative Analysis (Phase 3)
```
POST   /api/comparative/side_by_side/
POST   /api/comparative/mapping_comparison/
POST   /api/comparative/statistical_test/
POST   /api/comparative/multiple_sequences/
POST   /api/comparative/conserved_regions/
```

### Export (Phase 3)
```
POST   /api/export/csv/
POST   /api/export/json/
POST   /api/export/fasta/
POST   /api/export/pdf_data/
POST   /api/export/batch/
```

### Visualizations (Phase 3)
```
POST   /api/visualizations/frequency/
POST   /api/visualizations/transitions/
POST   /api/visualizations/heatmap/
POST   /api/visualizations/3d_relations/
POST   /api/visualizations/radar/
```

Interactive documentation available at:
- Swagger UI: `/api/schema/swagger/`
- ReDoc: `/api/schema/redoc/`

---

## 🧪 Usage Examples

### Analyze a DNA Sequence

```python
from genetic_engine.genetic_analysis_service import GeneticAnalysisService

service = GeneticAnalysisService()

results = service.analyze_sequence(
    sequence="ATGCGATAA",
    sequence_name="Sample Gene",
    sequence_type="DNA",
    mapping_scheme="scheme_1"
)

print(f"Hexagram sequence: {results['hexagram_sequence']}")
print(f"Dominant hexagram: {results['dominant_hexagram']}")
print(f"Amino acids: {results['amino_acid_sequence']}")
```

### Get Hexagram for Codon

```python
from genetic_engine.codon_translator import CodonTranslator

translator = CodonTranslator(mapping_scheme='scheme_1')
hexagram_num = translator.translate_codon('ATG')
print(f"ATG -> Hexagram {hexagram_num}")
```

### Generate AI Interpretation

```python
from genetic_engine.genetic_ai_client import GeneticGeminiClient

client = GeneticGeminiClient(api_key='your-api-key')

interpretation = client.generate_hexagram_interpretation(
    hexagram_number=1,
    hexagram_name="The Creative",
    hexagram_binary="111111",
    codon="ATG",
    amino_acid="M"
)
```

---

## 📊 Data Models

### Codon
- DNA/RNA triplet sequences
- Amino acid mappings
- Start/stop codon flags
- Binary representation

### Hexagram
- Binary representation (6 lines)
- Chinese name and pinyin
- English translation
- Lower/upper trigrams
- Nuclear and complementary relationships

### CodonSequence
- User-submitted sequences
- Analysis results (cached)
- Hexagram sequences
- Statistics (GC content, diversity)

### CodonHexagramMapping
- Multiple mapping schemes
- AI-induced mappings
- Validation metrics
- Version tracking

---

## 🎨 Project Structure

```
physiological_g_code/
├── core/                  # Django project settings
│   ├── settings/         # Environment configs
│   └── urls.py
│
├── api/                   # REST API app
│   ├── models/           # Database models
│   ├── serializers/      # DRF serializers
│   ├── views/            # API views
│   └── urls.py
│
├── genetic_engine/        # Core analysis engine
│   ├── codon_translator.py
│   ├── hexagram_mapper.py
│   ├── genetic_ai_client.py
│   ├── genetic_analysis_service.py
│   ├── pattern_analyzer.py       # Phase 3: Pattern detection
│   ├── comparative_analyzer.py   # Phase 3: Comparative analysis
│   ├── export_service.py         # Phase 3: Export functionality
│   ├── visualization_data_builder.py  # Phase 3: Visualization data
│   └── prompts/          # AI prompt templates
│
├── templates/             # HTML templates
├── static/                # CSS, JavaScript
│   ├── css/
│   └── js/
│       ├── components/
│       │   ├── sequence-analyzer.js
│       │   ├── hexagram-grid.js
│       │   ├── charts/              # Phase 3: Chart components
│       │   │   ├── frequency-chart.js
│       │   │   ├── transition-network.js
│       │   │   ├── heatmap.js
│       │   │   └── 3d-relations.js
│       │   └── analysis-dashboard.js  # Phase 3: Main dashboard
│       └── utils/
│           ├── api-client.js
│           ├── hexagram-renderer.js
│           └── plotly-wrapper.js     # Phase 3: Plotly.js wrapper
│
├── scripts/               # Utility scripts
├── tests/                 # Test suite
├── docs/                  # Documentation
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov=genetic_engine

# Run specific test
pytest tests/test_genetic_engine.py
```

---

## 📈 Roadmap

### ✅ Phase 1: Foundation (Completed)
- [x] Django project setup
- [x] Database models (codons, hexagrams)
- [x] Core translation algorithms
- [x] REST API endpoints
- [x] Basic frontend UI

### ✅ Phase 2: AI Integration (Completed)
- [x] Google Gemini integration
- [x] Interpretation generation
- [x] AI-induced mapping
- [x] Prompt templates

### ✅ Phase 3: Enhanced Analysis (Completed)
- [x] Advanced pattern detection (position analysis, sliding window, motifs)
- [x] Comparative analysis tools (sequence comparison, statistical tests)
- [x] Export to various formats (CSV, JSON, FASTA, PDF)
- [x] Interactive hexagram visualizations (Plotly.js charts)

### ✅ Phase 4: Community (Completed)
- [x] User authentication with profiles
- [x] Community discussion system with threaded comments
- [x] Notification system
- [x] Shared mapping schemes with voting
- [x] API key system for third-party integrations
- [x] Webhook system for event notifications

### 🔮 Phase 5: Future Enhancements
- [ ] Mobile application
- [ ] Real-time collaborative analysis
- [ ] Advanced ML-based pattern recognition
- [ ] Integration with genomic databases

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Galen Chu**

- GitHub: [@Galen-Chu](https://github.com/Galen-Chu)

---

## 🙏 Acknowledgments

- **Google Gemini** - AI-powered content generation
- **BioPython** - Biological sequence analysis
- **Django & DRF** - Robust web framework
- **I Ching tradition** - Ancient wisdom system

---

## 📞 Contact & Support

- 🐛 Issues: [GitHub Issues](https://github.com/Galen-Chu/physiological-g-code/issues)
- 💡 Discussions: [GitHub Discussions](https://github.com/Galen-Chu/physiological-g-code/discussions)

---

<div align="center">

**🧬 Welcome to the crossroads of biology and philosophy.**

**Welcome to Physiological G-Code.**

Made with ⚡ by Galen Chu

</div>
