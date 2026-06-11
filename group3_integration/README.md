# Integrated Project — AI-Powered NBA Syllabus Generation System

**G.B. Pant Institute of Engineering & Technology, Pauri Garhwal**
Final Year Project | Computer Science and Engineering

---

## Overview

This project integrates three independent AI systems to automate NBA-compliant syllabus generation for engineering courses. Group 1 generates the syllabus and programme outcomes using a local LLM, Group 2 maps Course Outcomes to Programme Outcomes using ML-based semantic similarity, and Group 3 acts as the integration layer that connects both systems into a single unified pipeline.

---

## System Architecture

```
Faculty Input
      |
      v
Group 1 (port 8000)              Group 3 (integration layer)         Group 2 (port 8001)
AI-Syllabus-Generator    --->    main.py + adapter + validator  --->  MAPPING_SEQUENCER
  - Generates COs                  - Validates G1 output               - CO x PO mapping
  - Generates Units                - Transforms data format            - CO x PSO mapping
  - Generates POs/PSOs/PEOs        - Calls both APIs                   - PO x PEO mapping
  - Calls Ollama LLM               - Handles timeouts/fallback         - Semester sequencer
      |                                      |
      v                                      v
Saved JSON output              Final CO-PO Matrix + Semester Plan
```

---

## Folder Structure

```
integrated-project/
|
|-- group1-syllabus-generator/          Group 1 repo (cloned)
|   |-- app/
|   |   |-- generator/
|   |   |   |-- syllabus_generator.py   4-call AI pipeline
|   |   |   |-- programme_generator.py  PO/PSO/PEO generator
|   |   |-- schemas/
|   |   |   |-- models.py               SyllabusRequest/Response
|   |   |   |-- contracts.py            official data contracts
|   |   |-- prompts/                    Ollama prompt builders
|   |   |-- rules/                      Bloom's taxonomy engine
|   |   |-- config.py                   Ollama URL and model
|   |   |-- main.py                     FastAPI app (port 8000)
|   |-- outputs/                        saved syllabus JSON files
|   |-- data/bloom_verbs.json
|
|-- group2-mapping-sequencer/           Group 2 repo (cloned)
|   |-- api/
|   |   |-- main.py                     FastAPI app (port 8001)
|   |   |-- models.py                   SQLAlchemy models
|   |   |-- database.py                 SQLite setup
|   |-- mapping/
|   |   |-- similarity.py               BERT + SVM hybrid scorer
|   |   |-- embeddings.py               sentence-transformers
|   |   |-- classifier.py               SVM classifier
|   |-- sequencer/
|   |   |-- topo_sort.py                topological sort
|   |   |-- graph_model.py              NetworkX DAG
|   |-- schemas/                        JSON schemas
|   |-- data/                           training data + accreditation defs
|
|-- group3_integration/                 Group 3 code (our integration layer)
|   |-- __init__.py
|   |-- definitions.py                  fallback PO/PSO/PEO definitions
|   |-- adapter/
|   |   |-- __init__.py
|   |   |-- transformer.py              converts G1 output to G2 format
|   |   |-- validator.py                validates data at each boundary
|   |   |-- g2_integration.py           calls Group 2 endpoints
|   |-- schemas/
|   |   |-- __init__.py
|   |   |-- validator.py                schema validators
|   |-- utils/
|   |   |-- __init__.py
|   |   |-- logger.py                   terminal logging helpers
|   |-- tests/
|       |-- test_transformer.py         integration tests
|
|-- main.py                             entry point - runs full pipeline
|-- requirements.txt                    Group 3 dependencies
|-- README.md                           this file
```

---

## Prerequisites

| Requirement | Version | Purpose |
|---|---|---|
| Python | 3.9+ | all services |
| Ollama | 0.30+ | local LLM for Group 1 |
| curriculum-ai model | latest | syllabus generation |
| sentence-transformers | latest | Group 2 CO-PO mapping |

---

## Installation

**Step 1 — Install Ollama**

Download from https://ollama.com/download and install. Then pull the model:

```powershell
ollama pull curriculum-ai
```

**Step 2 — Install Group 1 dependencies**

```powershell
cd group1-syllabus-generator
pip install -r requirements.txt
cd ..
```

**Step 3 — Install Group 2 dependencies**

```powershell
cd group2-mapping-sequencer
pip install fastapi uvicorn sqlalchemy python-multipart sentence-transformers scikit-learn numpy networkx reportlab pypdf requests
cd ..
```

**Step 4 — Install Group 3 dependencies**

```powershell
pip install -r requirements.txt
```

**Step 5 — Verify integration setup**

```powershell
python -c "
from group3_integration.definitions import PO_DEFINITIONS, PSO_DEFINITIONS, PEO_DEFINITIONS
from group3_integration.adapter.transformer import transform_syllabus_to_sequencer_input
from group3_integration.adapter.validator import validate_syllabus_response
from group3_integration.adapter.g2_integration import resolve_definitions
print('All imports OK')
print('POs:', len(PO_DEFINITIONS), '| PSOs:', len(PSO_DEFINITIONS), '| PEOs:', len(PEO_DEFINITIONS))
"
```

---

## Running the Pipeline

Open **3 separate terminals** inside `integrated-project/`.

**Terminal 1 — Start Ollama (if not already running)**

```powershell
ollama serve
```

Verify: `curl http://localhost:11434 -UseBasicParsing`
Expected: `Ollama is running`

**Terminal 2 — Start Group 1**

```powershell
cd group1-syllabus-generator
python -m uvicorn app.main:app --port 8000 --reload
```

Wait for: `Uvicorn running on http://127.0.0.1:8000`

**Terminal 3 — Start Group 2**

```powershell
cd group2-mapping-sequencer
python -m uvicorn api.main:app --port 8001 --reload
```

Wait for: `Uvicorn running on http://127.0.0.1:8001`

Note: First startup takes 30-60 seconds — downloads the sentence-transformer model (400MB).

**Terminal 4 — Run the pipeline**

```powershell
cd integrated-project
python main.py "Computer Organization and Architecture" COA-401
```

**Custom course:**

```powershell
python main.py "Data Structures and Algorithms" CS301
python main.py "Operating Systems" CS401
python main.py "Machine Learning" CS601
```

---

## How the Pipeline Works

```
Step 1   main.py calls Group 1 POST /generate/syllabus
         Group 1 runs 4 Ollama calls:
           Call 1 -> COs + objectives
           Call 2 -> unit-wise syllabus
           Call 3 -> CO-PO matrix (discarded - replaced by Group 2)
           Call 4 -> textbooks + resources

Step 2   main.py validates Group 1 output
         Checks: units exist, COs have co_id/text/bloom_level

Step 3   transformer.py converts units to Group 2 sequencer format
         Group 1: unit_id, unit_title, satisfied_cos[]
         Group 2: id, credits, prerequisites[]
         Prerequisites inferred from shared Course Outcomes between units

Step 4   main.py calls Group 1 POST /programme/generate-all
         Gets: POs (12), PSOs (3), PEOs (5)
         If Group 1 times out: uses fallback from definitions.py

Step 5   g2_integration.py calls Group 2 POST /map/matrix three times:
           CO x PO  -> mapping levels 0-3
           CO x PSO -> mapping levels 0-3
           PO x PEO -> mapping levels 0-3
         Group 2 scoring: 0.55 x BERT + 0.35 x SVM + 0.10 x keywords
         Levels: <0.2=0(none), <0.4=1(low), <0.6=2(medium), >=0.6=3(high)

Step 6   transformer.py calls Group 2 POST /sequencer/plan
         Builds a semester plan using topological sort on unit dependencies

Step 7   Final output printed with CO-PO matrix and semester plan
```

---

## Data Ownership

| Data | Owner | Notes |
|---|---|---|
| Course Outcomes (COs) | Group 1 | generated by Ollama LLM |
| Units and Topics | Group 1 | generated by Ollama LLM |
| Textbooks and Resources | Group 1 | generated by Ollama LLM |
| Programme Outcomes (POs) | Group 1 (with G3 fallback) | 12 NBA standard POs |
| Programme Specific Outcomes (PSOs) | Group 1 (with G3 fallback) | 3 PSOs |
| Programme Educational Objectives (PEOs) | Group 1 (with G3 fallback) | 5 PEOs |
| CO-PO Matrix | Group 2 | ML-based, replaces Group 1's matrix |
| CO-PSO Matrix | Group 2 | ML-based |
| PO-PEO Matrix | Group 2 | ML-based |
| Semester Plan | Group 2 | topological sort |

---

## Override Definitions

To force Group 3's own PO/PSO/PEO definitions instead of Group 1's generated values, open `group3_integration/definitions.py` and set:

```python
OVERRIDE_POS  = True   # use Group 3's PO list
OVERRIDE_PSOS = True   # use Group 3's PSO list
OVERRIDE_PEOS = True   # use Group 3's PEO list
```

Set to `False` to use Group 1's generated values (default).

---

## Timeout Handling

Group 1 uses Ollama which can be slow (4.9GB model). The pipeline handles this automatically:

```
Call Group 1
    |-- timeout? --> wait 60 seconds --> retry
                         |-- timeout again? --> check saved files
                                                   |-- no saved file? --> exit with error
                                                   |-- saved file found? --> continue
```

Saved syllabi are stored in `group1-syllabus-generator/outputs/` and are picked up automatically by course name.

---

## API Quick Reference

### Group 1 (port 8000)

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /health | check server + Ollama status |
| POST | /generate/syllabus | generate full syllabus |
| POST | /programme/generate-all | generate POs, PSOs, PEOs |
| POST | /export/docx | export syllabus as Word document |
| GET | /docs | Swagger UI |

### Group 2 (port 8001)

| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | health check |
| POST | /map/matrix | CO x PO/PSO/PEO mapping matrix |
| POST | /map/auto | simple CO to PO top-k mapping |
| POST | /sequencer/plan | semester plan from prerequisites |
| POST | /attainment/calculate | CO and PO attainment from marks |
| GET | /docs | Swagger UI |

---

## Testing

**Test Group 1 is alive:**
```powershell
curl http://localhost:8000/ -UseBasicParsing
```

**Test Group 2 is alive:**
```powershell
curl http://localhost:8001/ -UseBasicParsing
```

**Test Group 3 imports:**
```powershell
python -c "from group3_integration.adapter.g2_integration import run_integration; print('OK')"
```

**Run integration tests:**
```powershell
python group3_integration/tests/test_transformer.py
```

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `uvicorn not recognized` | uvicorn not in PATH | use `python -m uvicorn` instead |
| `No module named mapping` | wrong main.py at root | replace root main.py with Group 3 version |
| `No module named group3_integration` | hyphen folder name | run `Copy-Item -Recurse group3-integration group3_integration` |
| `Read timed out` | Ollama busy or slow | wait for current generation to finish |
| `No module named sentence_transformers` | missing dependency | run `pip install sentence-transformers` |
| `No module named sqlalchemy` | missing dependency | run `pip install sqlalchemy` |
| `Connection refused port 8000` | Group 1 not running | start Group 1 server |
| `Connection refused port 8001` | Group 2 not running | start Group 2 server |

---

## Group Responsibilities

**Group 1 — AI-Syllabus-Generator**
Builds an AI-powered syllabus generator using FastAPI and Ollama. Takes course details as input and produces NBA-compliant syllabus with COs, units, CO-PO matrix, textbooks and programme outcomes.

**Group 2 — MAPPING_SEQUENCER**
Builds a semantic mapping engine using sentence-transformers and SVM classifier. Takes COs and POs as input and produces accurate mapping levels (0-3) using hybrid scoring. Also includes a topological course sequencer.

**Group 3 — Integration Layer**
Connects Group 1 and Group 2 into a single pipeline. Responsible for data validation, format transformation, API orchestration, timeout handling, and producing the final merged output.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Group 1 API | FastAPI, Pydantic, Uvicorn |
| Group 1 AI | Ollama, curriculum-ai model |
| Group 2 API | FastAPI, SQLAlchemy, SQLite |
| Group 2 ML | sentence-transformers, scikit-learn SVM, NetworkX |
| Group 3 | Python, requests |
| All | Python 3.9+ |

---

## University

G.B. Pant Institute of Engineering and Technology, Pauri Garhwal, Uttarakhand
Department of Computer Science and Engineering
