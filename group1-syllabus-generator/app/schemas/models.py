from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict

VALID_BLOOM_LEVELS = ["remember", "understand", "apply", "analyze", "evaluate", "create"]

VALID_PROGRAMMES = [
    "btech", "bsc", "bcom", "ba", "mtech", "msc", "mcom", "ma",
    "bca", "mca", "mbbs", "bpharm", "mpharm", "diploma", "phd",
    "barch", "mba", "llb", "bed"
]

# ── NBA 12 POs — Indian Universities Standard ────────────────────
NBA_12_POS = {
    "PO1":  "Engineering Knowledge",
    "PO2":  "Problem Analysis",
    "PO3":  "Design/Development of Solutions",
    "PO4":  "Conduct Investigations of Complex Problems",
    "PO5":  "Modern Tool Usage",
    "PO6":  "The Engineer and Society",
    "PO7":  "Environment and Sustainability",
    "PO8":  "Ethics",
    "PO9":  "Individual and Team Work",
    "PO10": "Communication",
    "PO11": "Project Management and Finance",
    "PO12": "Life Long Learning",
}

# ── Attainment levels as per NBA SAR ────────────────────────────
ATTAINMENT_LEVELS = {
    3: "80% or more students score above threshold",
    2: "70-79% students score above threshold",
    1: "60-69% students score above threshold",
    0: "Less than 60% students score above threshold"
}

class OutcomeRequest(BaseModel):
    course_name: str = Field(..., min_length=3, max_length=100)
    course_description: str = Field(..., min_length=10, max_length=1000)
    target_bloom_levels: Optional[List[str]] = ["remember","understand","apply"]
    n_candidates: int = Field(default=3, ge=1, le=10)
    education_level: Optional[str] = "undergraduate"
    programme: Optional[str] = "btech"
    year_of_study: Optional[int] = Field(default=None, ge=1, le=6)
    custom_prompt: Optional[str] = None

    @validator("course_name")
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("course_name cannot be empty")
        return v.strip()

    @validator("target_bloom_levels")
    def valid_bloom_levels(cls, v):
        if v:
            for level in v:
                if level.lower() not in VALID_BLOOM_LEVELS:
                    raise ValueError(f"Invalid bloom level: '{level}'")
        return v

    @validator("course_description")
    def description_not_empty(cls, v):
        if not v.strip():
            raise ValueError("course_description cannot be empty")
        return v.strip()

class OutcomeObject(BaseModel):
    text: str
    bloom_level: str
    assessment_suggestion: str
    confidence_est: float
    flags: List[str] = []
    domain_tags: List[str] = []

class OutcomeResponse(BaseModel):
    course_name: str
    education_level: str = "undergraduate"
    programme: str = "btech"
    year_of_study: Optional[int] = None
    outcomes: List[OutcomeObject]

# ── CO Object — Full NBA Indian format ──────────────────────────
class COObject(BaseModel):
    co_id: str
    text: str
    bloom_level: str
    bloom_verb: str
    bloom_level_number: str             # L1 to L6
    mapped_pos: List[str] = []
    po_correlation: Dict[str, int] = {}
    mapped_psos: List[str] = []
    pso_correlation: Dict[str, int] = {}
    attainment_target: str = "60% of students score above 60%"
    attainment_level: int = 1           # 0/1/2/3 as per NBA
    direct_assessment: List[str] = []
    indirect_assessment: List[str] = []
    unit_test_marks: int = 20
    assignment_marks: int = 5
    end_sem_marks: int = 70

# ── Unit Object ──────────────────────────────────────────────────
class UnitObject(BaseModel):
    unit_id: str
    unit_title: str
    topics_paragraph: str
    topics: List[str]
    unit_objectives: List[str]
    unit_outcomes: List[str]
    satisfied_cos: List[str] = []
    assessments: List[str] = []
    readings: List[str] = []
    hours: Optional[int] = 8
    lecture_plan: Optional[str] = None

# ── Syllabus Request ─────────────────────────────────────────────
class SyllabusRequest(BaseModel):
    course_name: str = Field(..., min_length=3, max_length=100)
    course_description: str = Field(..., min_length=10, max_length=1000)
    num_units: int = Field(default=5, ge=1, le=10)
    education_level: Optional[str] = "undergraduate"
    programme: Optional[str] = "btech"
    year_of_study: Optional[int] = Field(default=None, ge=1, le=6)
    semester: Optional[int] = Field(default=None, ge=1, le=12)
    branch: Optional[str] = None
    course_code: Optional[str] = None
    credits: Optional[int] = Field(default=4, ge=1, le=10)
    ltp: Optional[str] = "3:1:0"
    university_name: Optional[str] = "G.B. Pant Institute of Engineering & Technology, Pauri Garhwal"
    custom_prompt: Optional[str] = None
    regenerate: Optional[bool] = False
    rejection_reason: Optional[str] = None

    @validator("course_name")
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("course_name cannot be empty")
        return v.strip()

# ── Syllabus Response — Full Indian NBA format ───────────────────
class SyllabusResponse(BaseModel):
    course_name: str
    course_code: Optional[str] = None
    education_level: str
    programme: str
    year_of_study: Optional[int] = None
    semester: Optional[int] = None
    branch: Optional[str] = None
    credits: Optional[int] = 4
    ltp: Optional[str] = "3:1:0"
    university_name: Optional[str] = None
    standards: Optional[str] = "NBA GAPC v4.0, AICTE, UGC-LOCF, NAAC, IQAC, Bloom's Taxonomy"
    total_hours: Optional[int] = None
    total_lectures: Optional[int] = None
    units: List[UnitObject]
    course_objectives: List[str] = []
    course_outcomes: List[COObject] = []
    course_outcomes_text: List[str] = []
    co_po_matrix: Optional[Dict] = {}
    co_pso_matrix: Optional[Dict] = {}
    # Indian university specific
    exam_pattern: Optional[Dict] = {
        "internal_assessment": 30,
        "end_semester_exam": 70,
        "total": 100,
        "internal_breakdown": {
            "unit_tests": 20,
            "assignments": 5,
            "attendance": 5
        }
    }
    attainment_formula: Optional[str] = "CO Attainment = (Direct × 0.8) + (Indirect × 0.2)"
    attainment_levels: Optional[Dict] = {
        "Level 3": "≥80% students score above threshold",
        "Level 2": "70-79% students score above threshold",
        "Level 1": "60-69% students score above threshold",
        "Level 0": "<60% students score above threshold"
    }
    po_attainment_formula: Optional[str] = "PO Attainment = Σ(CO_Attainment × CO-PO_Strength) / Σ(CO-PO_Strength)"
    cqi_plan: Optional[str] = None
    lesson_plan_note: Optional[str] = None
    naac_iqac_note: Optional[str] = None
    textbooks: List[str] = []
    youtube_resources: List[str] = []
    open_source_resources: List[str] = []