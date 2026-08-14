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

## 🎯 Key Features

- **Sequence Analysis** - Upload DNA/RNA sequences for automatic codon-to-hexagram mapping, amino acid translation, and GC content calculation
- **Multiple Mapping Schemes** - Binary, structural, hydrogen bond, and AI-induced mappings
- **AI-Powered Interpretations** - Google Gemini integration for biological and philosophical insights
- **Advanced Pattern Detection** - Position analysis, sliding windows, motif discovery, entropy metrics, and autocorrelation
- **Comparative Analysis** - Statistical tests (chi-square, Fisher's exact, KS test), similarity metrics, and conservation analysis
- **Interactive Visualizations** - Real-time Plotly.js charts (frequency, transitions, heatmaps, 3D, radar)
- **Export Functionality** - CSV, JSON, FASTA, PDF reports, and batch exports
- **RESTful API** - Complete CRUD with authentication, OpenAPI/Swagger documentation, and webhooks
- **Community Features** - User profiles, discussions with voting, threaded comments, notifications, and API key management

📖 **See [CHANGELOG.md](CHANGELOG.md) for detailed version history and feature releases.**

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

Interactive API documentation is available at:
- **Swagger UI**: `/api/schema/swagger/`
- **ReDoc**: `/api/schema/redoc/`

### Key Endpoints

```bash
# Authentication
POST   /api/auth/register/
POST   /api/auth/login/

# Core Resources
GET    /api/codons/
GET    /api/hexagrams/
GET    /api/sequences/
POST   /api/sequences/analyze/
GET    /api/mappings/

# Analysis
POST   /api/analysis/analyze_sequence/
POST   /api/analysis/analyze_codon/

# Pattern Analysis
POST   /api/patterns/position_analysis/
POST   /api/patterns/sliding_window/
POST   /api/patterns/motif_discovery/

# Comparative Analysis
POST   /api/comparative/side_by_side/
POST   /api/comparative/statistical_test/

# Export & Visualizations
POST   /api/export/{format}/
POST   /api/visualizations/{type}/
```

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
├── tests/                 # Test suite (35 tests: genetic engine + API + community)
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

## 📈 Version History

- **[1.3.0]** (2026-08-14) - Phase 4 Community API + auth endpoints + migrations + 35 tests + multiple critical fixes
- **[1.2.0]** (2026-01-26) - Enhanced Analysis + Community data models
- **[1.0.0]** (2026-01-21) - Foundation + AI Integration

📖 **See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.**

---

## 🔮 What's Next?

Planned features for future releases:
- Mobile application
- Real-time collaborative analysis
- Advanced ML-based pattern recognition
- Integration with genomic databases

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
- LinkedIn: [Galen Chu](https://www.linkedin.com/in/galen-chu-203590b5/)

---

## 🙏 Acknowledgments

- **Google Gemini** - AI-powered content generation
- **Django & DRF** - Robust web framework
- **The Open Source Community** - For all the amazing tools and libraries

---

## 📞 Contact & Support

- 📧 Email: (coming soon)
- 💬 Discord: (coming soon)
- 🐛 Issues: [GitHub Issues](https://github.com/Galen-Chu/spiritual-g-code/issues)

---

## 🌟 Star History

If you find this project interesting, please consider giving it a ⭐ star!

[![Star History Chart](https://api.star-history.com/svg?repos=Galen-Chu/spiritual-g-code&type=Date)](https://star-history.com/#Galen-Chu/spiritual-g-code&Date)

---

<div align="center">

**🔮 Welcome to the source code.**

**Welcome to G-Code.**

**Welcome home, Galen.**

Made with ⚡ by Galen Chu

</div>
