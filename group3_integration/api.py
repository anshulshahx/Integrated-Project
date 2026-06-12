"""
group3_integration/api.py
Group 3 — Integration Bridge API (port 9000)

Run: python -m uvicorn group3_integration.api:app --port 9000 --reload

Endpoints:
  POST /pipeline/generate  - full pipeline: G1 syllabus + programme -> G2 mapping + sequencer + attainment
  POST /pipeline/approve   - regenerate / finalize full syllabus via G1
  POST /pipeline/reject    - regenerate with rejection reason, remap via G2
  GET  /pipeline/status    - health of G1, G2, Ollama
"""

import requests
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

GROUP1_URL = "http://localhost:8000"
GROUP2_URL = "http://localhost:8001"
OLLAMA_URL = "http://localhost:11434"

G1_TIMEOUT = 900   # Ollama generation is slow
G2_TIMEOUT = 120

app = FastAPI(
    title="Group 3 - Integration Bridge API",
    description="Connects Group 1 (AI Syllabus Generator) and Group 2 (Mapping Sequencer)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request models ────────────────────────────────────────────────────────────

class AttainmentQuestion(BaseModel):
    id: str
    name: str
    max_marks: float
    co_id: str


class StudentMark(BaseModel):
    student_id: str
    student_name: str
    marks: Dict[str, Any] = {}


class AttainmentSettings(BaseModel):
    target_score_percent: float = 60.0
    threshold_l1: float = 50.0
    threshold_l2: float = 60.0
    threshold_l3: float = 70.0
    questions: List[AttainmentQuestion] = []
    students: List[StudentMark] = []


class GenerateRequest(BaseModel):
    course_name: str
    course_description: str
    course_code: str = ""
    num_units: int = 5
    education_level: str = "undergraduate"
    programme: str = "btech"
    year_of_study: int = 2
    semester: int = 3
    branch: str = "Computer Science and Engineering"
    credits: int = 4
    ltp: str = "3:1:0"
    university_name: str = "G.B. Pant Institute of Engineering and Technology, Pauri Garhwal"
    programme_name: str = ""
    programme_description: str = ""
    attainment_settings: Optional[AttainmentSettings] = None


class RejectRequest(GenerateRequest):
    rejection_reason: str
    custom_prompt: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _call_g1_syllabus(req: GenerateRequest, regenerate: bool = False,
                      rejection_reason: str = None, custom_prompt: str = None) -> dict:
    payload = {
        "course_name":        req.course_name,
        "course_description": req.course_description,
        "course_code":        req.course_code or None,
        "num_units":          req.num_units,
        "education_level":    req.education_level,
        "programme":          req.programme,
        "year_of_study":      req.year_of_study,
        "semester":           req.semester,
        "branch":             req.branch,
        "credits":            req.credits,
        "ltp":                req.ltp,
        "university_name":    req.university_name,
    }
    if regenerate:
        payload["regenerate"] = True
        payload["rejection_reason"] = rejection_reason or ""
        if custom_prompt:
            payload["custom_prompt"] = custom_prompt
    try:
        r = requests.post(f"{GROUP1_URL}/generate/syllabus", json=payload, timeout=G1_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        raise HTTPException(503, "Group 1 unreachable at port 8000. Start it with: python -m uvicorn app.main:app --port 8000")
    except requests.exceptions.ReadTimeout:
        raise HTTPException(504, "Group 1 timed out. Ollama is busy or slow — wait and retry.")
    except requests.exceptions.HTTPError as e:
        raise HTTPException(502, f"Group 1 error: {e}")


def _call_g1_programme(req: GenerateRequest) -> dict:
    try:
        r = requests.post(f"{GROUP1_URL}/programme/generate-all", json={
            "programme_name":        req.programme_name or f"{req.programme.upper()} {req.branch}",
            "programme_description": req.programme_description or
                                     f"A {req.programme.upper()} programme in {req.branch} covering {req.course_name}.",
            "course_list":           [req.course_name],
            "n_peos":                5,
            "n_psos":                3,
        }, timeout=G1_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception:
        # Fall back to Group 3 definitions — never block the pipeline on this
        return {}


def _fallback_definitions():
    from group3_integration.definitions import PO_DEFINITIONS, PSO_DEFINITIONS, PEO_DEFINITIONS
    return PO_DEFINITIONS, PSO_DEFINITIONS, PEO_DEFINITIONS


def _resolve_pos_psos_peos(programme: dict):
    pos  = [{"id": p["po_id"],  "text": p.get("text", "")} for p in programme.get("pos",  []) if p.get("po_id")]
    psos = [{"id": p["pso_id"], "text": p.get("text", "")} for p in programme.get("psos", []) if p.get("pso_id")]
    peos = [{"id": p["peo_id"], "text": p.get("text", "")} for p in programme.get("peos", []) if p.get("peo_id")]
    fb_pos, fb_psos, fb_peos = _fallback_definitions()
    return (pos or fb_pos), (psos or fb_psos), (peos or fb_peos)


def _g2_matrix(cos: list, pos: list, psos: list = None) -> dict:
    payload = {"cos": cos, "pos": pos, "top_k": max(len(pos), 1)}
    if psos:
        payload["psos"] = psos
    try:
        r = requests.post(f"{GROUP2_URL}/map/matrix", json=payload, timeout=G2_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        raise HTTPException(503, "Group 2 unreachable at port 8001. Start it with: python -m uvicorn api.main:app --port 8001")
    except Exception as e:
        raise HTTPException(502, f"Group 2 mapping error: {e}")


def _g2_sequencer(syllabus: dict) -> dict:
    from group3_integration.adapter.transformer import transform_syllabus_to_sequencer_input
    try:
        seq = transform_syllabus_to_sequencer_input(syllabus)
        if not seq["courses"]:
            return {}
        r = requests.post(f"{GROUP2_URL}/sequencer/plan", json={
            "courses":             seq["courses"],
            "max_credits_per_sem": seq["max_credits_per_sem"],
        }, timeout=30)
        r.raise_for_status()
        return r.json()
    except HTTPException:
        raise
    except Exception:
        return {}


def _g2_attainment(cos_ids: list, pos_ids: list, psos_ids: list,
                   matrix: dict, settings: AttainmentSettings) -> dict:
    if not settings or not settings.questions or not settings.students:
        return {}
    try:
        r = requests.post(f"{GROUP2_URL}/attainment/calculate", json={
            "cos":  cos_ids,
            "pos":  pos_ids,
            "psos": psos_ids,
            "matrix": matrix,
            "questions": [q.dict() for q in settings.questions],
            "students":  [s.dict() for s in settings.students],
            "target_score_percent": settings.target_score_percent,
            "threshold_l1": settings.threshold_l1,
            "threshold_l2": settings.threshold_l2,
            "threshold_l3": settings.threshold_l3,
        }, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}


def _clean_cos(syllabus: dict) -> list:
    return [
        {
            "co_id":       co.get("co_id"),
            "text":        (co.get("text") or "").replace("[VERB_WARNING]", "").strip(),
            "bloom_level": co.get("bloom_level", ""),
            "bloom_verb":  co.get("bloom_verb", ""),
        }
        for co in syllabus.get("course_outcomes", [])
        if co.get("co_id") and co.get("text")
    ]


def _run_full_pipeline(req: GenerateRequest, syllabus: dict) -> dict:
    cos_full = _clean_cos(syllabus)
    g2_cos   = [{"id": c["co_id"], "text": c["text"]} for c in cos_full]

    programme = _call_g1_programme(req)
    pos, psos, peos = _resolve_pos_psos_peos(programme)

    # CO x PO (+PSO in one call — Group 2 supports psos param)
    co_resp = _g2_matrix(g2_cos, pos, psos)
    full_matrix = co_resp.get("matrix", {})

    # Split combined matrix into CO-PO and CO-PSO
    po_ids  = [p["id"] for p in pos]
    pso_ids = [p["id"] for p in psos]
    co_po_matrix  = {co: {k: v for k, v in row.items() if k in po_ids}  for co, row in full_matrix.items()}
    co_pso_matrix = {co: {k: v for k, v in row.items() if k in pso_ids} for co, row in full_matrix.items()}

    # PO x PEO
    peo_resp = _g2_matrix(pos, peos)
    po_peo_matrix = peo_resp.get("matrix", {})

    # Sequencer
    plan = _g2_sequencer(syllabus)

    # Attainment (uses combined CO-PO+PSO matrix)
    attainment = _g2_attainment(
        cos_ids=[c["co_id"] for c in cos_full],
        pos_ids=po_ids,
        psos_ids=pso_ids,
        matrix=full_matrix,
        settings=req.attainment_settings,
    )

    return {
        "course_name":    syllabus.get("course_name", req.course_name),
        "course_code":    syllabus.get("course_code", req.course_code),
        "cos":            cos_full,
        "pos":            [{"po_id":  p["id"], "text": p["text"]} for p in pos],
        "psos":           [{"pso_id": p["id"], "text": p["text"]} for p in psos],
        "peos":           [{"peo_id": p["id"], "text": p["text"]} for p in peos],
        "co_po_matrix":   co_po_matrix,
        "co_pso_matrix":  co_pso_matrix,
        "po_peo_matrix":  po_peo_matrix,
        "semester_plan":  plan.get("plan", []),
        "total_semesters": plan.get("total_semesters", 0),
        "units":          syllabus.get("units", []),
        "attainment": {
            "co_stats":       attainment.get("co_stats", {}),
            "po_stats":       attainment.get("po_stats", {}),
            "pso_stats":      attainment.get("pso_stats", {}),
            "question_stats": attainment.get("question_stats", {}),
        },
        "syllabus_raw":   syllabus,
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "Group 3 Integration Bridge running", "version": "1.0.0"}


@app.get("/pipeline/status")
def pipeline_status():
    def check(url, timeout=5):
        try:
            return requests.get(url, timeout=timeout).status_code == 200
        except Exception:
            return False
    return {
        "group1": "running" if check(f"{GROUP1_URL}/") else "unreachable",
        "group2": "running" if check(f"{GROUP2_URL}/") else "unreachable",
        "ollama": "running" if check(OLLAMA_URL) else "unreachable",
    }


@app.post("/pipeline/generate")
def pipeline_generate(req: GenerateRequest):
    syllabus = _call_g1_syllabus(req)
    if not syllabus.get("course_outcomes"):
        raise HTTPException(502, "Group 1 returned no course outcomes")
    return _run_full_pipeline(req, syllabus)


@app.post("/pipeline/approve")
def pipeline_approve(req: GenerateRequest):
    # Final full syllabus generation with the approved inputs
    syllabus = _call_g1_syllabus(req)
    if not syllabus.get("units"):
        raise HTTPException(502, "Group 1 returned no units")
    return _run_full_pipeline(req, syllabus)


@app.post("/pipeline/reject")
def pipeline_reject(req: RejectRequest):
    syllabus = _call_g1_syllabus(
        req, regenerate=True,
        rejection_reason=req.rejection_reason,
        custom_prompt=req.custom_prompt,
    )
    if not syllabus.get("course_outcomes"):
        raise HTTPException(502, "Group 1 regeneration returned no course outcomes")
    return _run_full_pipeline(req, syllabus)