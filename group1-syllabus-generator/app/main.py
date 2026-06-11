import requests
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.schemas.models import OutcomeRequest, OutcomeResponse, SyllabusRequest, SyllabusResponse
from app.schemas.review_models import ReviewRequest, ReviewSummary
from app.schemas.programme_models import PEORequest, PEOResponse, PORequest, POResponse, PSORequest, PSOResponse, ProgrammeRequest, ProgrammeResponse
from app.generator.llm_client import generate_outcomes
from app.generator.syllabus_generator import generate_syllabus
from app.generator.review_manager import process_reviews, get_all_reviews, get_training_labels
from app.generator.programme_generator import generate_peos, generate_pos, generate_psos, generate_programme
from app.exporter.docx_exporter import export_syllabus_to_docx
from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL

app = FastAPI(
    title       = "Group 1 - Curriculum AI",
    description = "AI-Driven Platform for Outcome-Based Curriculum Design",
    version     = "2.0.0"
)

app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.get("/")
def root():
    return {"status": "Group 1 API is running", "version": "2.0.0"}

@app.get("/health")
def health():
    try:
        r      = requests.get(f"{OLLAMA_BASE_URL}", timeout=5)
        ollama = "connected" if r.status_code == 200 else "unreachable"
    except Exception:
        ollama = "unreachable"
    return {
        "api": "running", "version": "2.0.0",
        "ollama": ollama, "model": OLLAMA_MODEL,
        "endpoints": [
            "GET  /", "GET  /health",
            "POST /generate/outcomes",
            "POST /generate/syllabus",
            "POST /export/docx",
            "POST /review/submit",
            "GET  /review/all",
            "GET  /review/training-labels",
            "POST /programme/peos",
            "POST /programme/pos",
            "POST /programme/psos",
            "POST /programme/generate-all",
        ]
    }

@app.post("/generate/outcomes", response_model=OutcomeResponse)
def generate(request: OutcomeRequest):
    outcomes = generate_outcomes(request)
    return OutcomeResponse(
        course_name=request.course_name,
        education_level=request.education_level or "undergraduate",
        programme=request.programme or "btech",
        year_of_study=request.year_of_study,
        outcomes=outcomes
    )

@app.post("/generate/syllabus", response_model=SyllabusResponse)
def syllabus(request: SyllabusRequest):
    return generate_syllabus(request)

@app.post("/export/docx")
def export_docx(request: SyllabusRequest):
    syllabus_data = generate_syllabus(request)
    if not syllabus_data.units:
        raise HTTPException(status_code=500, detail="Syllabus generation failed")
    file_path = export_syllabus_to_docx(syllabus_data)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="DOCX export failed")
    safe  = request.course_name.replace(" ", "_")
    code  = f"_{request.course_code}"       if request.course_code   else ""
    prog  = request.programme.upper()       if request.programme     else "general"
    yr    = f"_Year{request.year_of_study}" if request.year_of_study else ""
    sem   = f"_S{request.semester}"         if request.semester      else ""
    fname = f"{safe}{code}_{prog}{yr}{sem}_syllabus.docx"
    return FileResponse(
        path=file_path, filename=fname,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@app.post("/review/submit", response_model=ReviewSummary)
def submit_review(request: ReviewRequest):
    return process_reviews(request)

@app.get("/review/all")
def all_reviews():
    return get_all_reviews()

@app.get("/review/training-labels")
def training_labels():
    return get_training_labels()

@app.post("/programme/peos", response_model=PEOResponse)
def peos(request: PEORequest):
    return generate_peos(request)

@app.post("/programme/pos", response_model=POResponse)
def pos(request: PORequest):
    return generate_pos(request)

@app.post("/programme/psos", response_model=PSOResponse)
def psos(request: PSORequest):
    return generate_psos(request)

@app.post("/programme/generate-all", response_model=ProgrammeResponse)
def programme_all(request: ProgrammeRequest):
    return generate_programme(request)