# AI-Driven Platform for Outcome-Based Curriculum Design

> Final Year Project — B.Tech Computer Science Engineering (AI & ML)
> G.B. Pant Institute of Engineering & Technology, Pauri Garhwal
> VIII Semester | AIP-109 | 2025–2026

---

## Overview

This platform automates the generation of accreditation-ready curriculum artifacts using a locally hosted Large Language Model (LLM) and a deterministic rule-based validation engine. It is designed to support Outcome-Based Education (OBE) as mandated by NBA, AICTE, UGC-LOCF, NAAC, and IQAC for Indian universities.

The system eliminates the manual effort involved in writing Course Outcomes, mapping them to Program Outcomes, generating unit-wise syllabi, and producing NBA-compliant documentation — reducing a weeks-long process to minutes.

---

## Team

| Name | Role |
|------|------|
| Member 1 | LLM Integration + Rules Engine |
| Member 2 | Syllabus Generator + DOCX Exporter |
| Member 3 | Programme Generator + Review System |
| Member 4 | API Design + Testing + Data Contracts |

**Faculty Guide:** Project Supervisor, Department of CSE

---

## Key Features

- Automated generation of Course Outcomes (COs) with Bloom's taxonomy classification
- Full unit-wise syllabus generation following Indian university format
- CO-PO mapping matrix (5 COs × 12 NBA POs) with correlation levels 1/2/3
- CO-PSO mapping matrix with correlation levels
- Bloom's level declared per CO (L1 to L6) with action verb
- NBA attainment targets and attainment levels (0/1/2/3)
- Direct and indirect assessment planning per CO
- Indian university exam pattern (30 internal + 70 end semester)
- Continuous Quality Improvement (CQI) plan generation
- NAAC and IQAC compliance documentation
- Programme Educational Objectives (PEOs), Program Outcomes (POs), Programme Specific Outcomes (PSOs)
- Human-in-the-loop faculty review system with training label export
- DOCX Word document export in Indian university format with red footer bar
- BERT training label export for semantic mapping integration
- JSON data contracts for inter-group API integration

---

## Standards Compliance

| Standard | Coverage |
|----------|----------|
| NBA GAPC v4.0 | CO-PO mapping, attainment calculation, CQI |
| AICTE | Programme structure, credit framework |
| UGC-LOCF | Course objectives, credit hours |
| NAAC | Quality assurance documentation |
| IQAC | Internal quality cell requirements |
| Bloom's Taxonomy | 6-level classification with action verbs |
| Washington Accord | 12 Programme Outcomes framework |

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| LLM | Ollama + LLaMA 3.1 8B (local, offline, free) |
| API Framework | FastAPI + Uvicorn |
| Data Validation | Pydantic v2 |
| Rules Engine | Custom 8-rule deterministic engine |
| Document Export | python-docx (Indian university format) |
| Middleware | CORS + GZip compression |
| Testing | Custom test suites — 158/158 passing |

---

## Project Structure

```
AI-Syllabus-Generator/
│
├── app/                              # Core application
│   ├── main.py                       # FastAPI app — 12 REST endpoints
│   ├── config.py                     # Ollama model configuration
│   │
│   ├── generator/                    # AI generation modules
│   │   ├── llm_client.py             # Course outcome generation
│   │   ├── syllabus_generator.py     # Unit-wise syllabus generation
│   │   ├── programme_generator.py    # PEO / PO / PSO generation
│   │   └── review_manager.py         # Faculty review and feedback system
│   │
│   ├── prompts/                      # LLM prompt engineering
│   │   ├── outcome_prompt.py         # Outcome generation prompts
│   │   ├── syllabus_prompt.py        # Syllabus generation prompts (NBA compliant)
│   │   └── peo_prompt.py             # Programme artifact prompts
│   │
│   ├── rules/
│   │   └── engine.py                 # 8-rule deterministic validation engine
│   │
│   ├── schemas/                      # Data models and contracts
│   │   ├── models.py                 # Pydantic request/response models
│   │   ├── review_models.py          # Faculty review models
│   │   ├── programme_models.py       # PEO / PO / PSO models
│   │   ├── contracts.py              # JSON data contracts for integration
│   │   └── validator.py              # Schema validation utilities
│   │
│   ├── exporter/
│   │   └── docx_exporter.py          # Word document generation (Indian format)
│   │
│   └── utils/
│       └── helpers.py                # Logging, file I/O, response wrappers
│
├── data/
│   └── bloom_verbs.json              # Bloom's taxonomy verbs — all 6 levels
│
├── tests/                            # Automated test suites
│   ├── test_engine.py                # Rules engine tests       (35 tests)
│   ├── test_pipeline.py              # Integration tests         (40 tests)
│   ├── test_contracts.py             # JSON contract tests       (24 tests)
│   ├── test_30_courses.py            # QA benchmark — 30 courses (30 tests)
│   └── test_polish.py                # Edge cases and polish     (29 tests)
│
├── outputs/                          # Generated JSON files (auto-created)
│   └── exports/                      # Generated DOCX files (auto-created)
│
├── feedback/
│   └── reviews.json                  # Faculty review logs and training labels
│
├── logs/
│   └── app.log                       # Application logs (auto-created)
│
├── requirements.txt                  # Python dependencies
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.10 or above
- [Ollama](https://ollama.com/download) installed on your system

### Installation

```bash
# Clone the repository
git clone https://github.com/anshulshahx/AI-Syllabus-Generator
cd AI-Syllabus-Generator

# Install dependencies
pip install -r requirements.txt

# Pull the LLM model
ollama pull llama3.1:8b
```

### Running the Application

```bash
# Terminal 1 — Start Ollama (if not running)
ollama serve

# Terminal 2 — Start the API server
python -m uvicorn app.main:app --reload
```

Open the interactive API documentation:
```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | System status |
| GET | `/health` | Health check + Ollama connection status |
| POST | `/generate/outcomes` | Generate COs with Bloom's classification |
| POST | `/generate/syllabus` | Generate full NBA-compliant unit syllabus |
| POST | `/export/docx` | Export syllabus as Word document |
| POST | `/review/submit` | Submit faculty review (accept/reject/edit) |
| GET | `/review/all` | Retrieve all faculty reviews |
| GET | `/review/training-labels` | Export BERT training labels |
| POST | `/programme/peos` | Generate Program Educational Objectives |
| POST | `/programme/pos` | Generate all 12 NBA Program Outcomes |
| POST | `/programme/psos` | Generate Programme Specific Outcomes |
| POST | `/programme/generate-all` | Generate PEOs + POs + PSOs in one call |

---

## The 8-Rule Validation Engine

Every AI-generated outcome is passed through 8 deterministic rules before being returned:

| Rule | Name | Action |
|------|------|--------|
| 1 | Bloom Verb Check | Flags outcome if first word is not a valid Bloom action verb |
| 2 | Measurability Check | Flags compound verbs like "understand and apply" |
| 3 | Deduplication | Removes outcomes with Jaccard similarity above 0.8 |
| 4 | Domain Tagging | Extracts subject-domain keywords automatically |
| 5 | Length Check | Enforces 8–30 word range per outcome |
| 6 | Profanity Filter | Blocks inappropriate language |
| 7 | Bias Filter | Warns on gendered or ability-biased language |
| 8 | Academic Tone | Warns on informal or colloquial language |

---

## NBA OBE Framework Implementation

### Course Outcomes (COs)

Each CO includes:
- Bloom's taxonomy level (Remember / Understand / Apply / Analyze / Evaluate / Create)
- Bloom's level number (L1 to L6) and action verb
- Mapping to minimum 2 NBA Program Outcomes (PO1–PO12)
- CO-PO correlation strength (1 = Low, 2 = Medium, 3 = High)
- Mapping to Programme Specific Outcomes (PSOs)
- Attainment target and attainment level (0/1/2/3)
- Direct assessment tools (Unit Tests, Assignments, End Semester Exam)
- Indirect assessment tools (Course End Survey, Exit Survey)

### CO-PO Mapping Matrix

Full 5 × 12 matrix with color-coded correlation levels:
- Green — High correlation (3)
- Yellow — Medium correlation (2)
- Red — Low correlation (1)
- Empty — No correlation (-)

### Attainment Calculation

```
CO Attainment = (Direct Assessment × 0.8) + (Indirect Assessment × 0.2)
PO Attainment = Σ(CO_Attainment × CO-PO_Strength) / Σ(CO-PO_Strength)
```

NBA Attainment Levels:
- Level 3 — 80% or more students score above 60% threshold
- Level 2 — 70–79% students score above 60% threshold
- Level 1 — 60–69% students score above 60% threshold
- Level 0 — Less than 60% students score above threshold

### Indian University Exam Pattern

```
Internal Assessment    30 marks
  Unit Test I          10 marks
  Unit Test II         10 marks
  Assignments           5 marks
  Attendance            5 marks
End Semester Exam      70 marks
Total                 100 marks
```

---

## Supported Programmes

| Category | Programmes |
|----------|-----------|
| Engineering | B.Tech, M.Tech, Diploma |
| Science | B.Sc, M.Sc |
| Commerce | B.Com, M.Com |
| Arts | B.A, M.A |
| Computer Applications | BCA, MCA |
| Management | MBA |
| Medical | MBBS, B.Pharm, M.Pharm |
| Law | LLB |
| Education | B.Ed |
| Architecture | B.Arch |
| Research | Ph.D |

---

## Sample API Request

### Generate NBA-Compliant Syllabus

```json
POST /generate/syllabus
{
  "course_name": "Data Structures and Algorithms",
  "course_description": "Arrays, linked lists, stacks, queues, trees, graphs, sorting and searching algorithms",
  "num_units": 5,
  "education_level": "undergraduate",
  "programme": "btech",
  "year_of_study": 2,
  "semester": 3,
  "branch": "Computer Science and Engineering",
  "credits": 4,
  "ltp": "3:1:0",
  "university_name": "G.B. Pant Institute of Engineering and Technology, Pauri Garhwal"
}
```

### Regenerate on Rejection

```json
POST /generate/syllabus
{
  "course_name": "Data Structures and Algorithms",
  "course_description": "Arrays, linked lists, stacks, queues, trees, graphs",
  "num_units": 5,
  "programme": "btech",
  "year_of_study": 2,
  "regenerate": true,
  "rejection_reason": "Insufficient practical content. Need more implementation topics.",
  "custom_prompt": "Focus on algorithm implementation and real-world applications."
}
```

---

## Test Results

```
Test Suite                Tests    Status
─────────────────────────────────────────
Rules Engine              35/35    PASS
Pipeline Integration      40/40    PASS
JSON Data Contracts       24/24    PASS
30-Course QA Benchmark    30/30    PASS
Polish and Edge Cases     29/29    PASS
─────────────────────────────────────────
Total                    158/158   ALL PASSING
```

Run tests:

```bash
python tests/test_engine.py
python tests/test_pipeline.py
python tests/test_contracts.py
python tests/test_30_courses.py
python tests/test_polish.py
```

---

## Data Contracts

```
GET /contracts
```

| Contract | Description |
|----------|-------------|
| OutcomeObject | AI-generated CO with Bloom level, flags, domain tags |
| CourseUnits | Full syllabus with unit-wise breakdown |
| MappingResponse | CO-to-PO semantic mapping format |
| TrainingLabel | Faculty-verified BERT retraining labels |
| Programme | PEOs + POs + PSOs combined |

---

## System Architecture

This platform forms the Generation Layer of a three-component system:

```
Generation Layer (This Project)
        │  REST API / JSON Contracts
        ▼
Semantic Mapping Layer
  BERT classifier, sentence embeddings, CO-PO articulation matrix
        │  Mapped curriculum data
        ▼
UI and Integration Layer
  React dashboard, mapping canvas, SCORM/LTI export, faculty portal
```

---

## Requirements

```
fastapi
uvicorn
pydantic
requests
python-docx
```

---

## Repository

[https://github.com/anshulshahx/AI-Syllabus-Generator](https://github.com/anshulshahx/AI-Syllabus-Generator)

---

*Final Year Project | B.Tech CSE (AI & ML) | G.B. Pant Institute of Engineering & Technology, Pauri Garhwal | 2025–2026*
