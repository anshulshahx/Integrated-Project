import requests
import json
import os
from datetime import datetime
from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from app.prompts.syllabus_prompt import (
    build_call1_prompt, build_call2_prompt,
    build_call3_prompt, build_call4_prompt,
    build_regenerate_call1_prompt, build_regenerate_call2_prompt
)
from app.schemas.models import SyllabusRequest, SyllabusResponse, UnitObject, COObject
from app.rules.engine import load_bloom_verbs

bloom_verbs = load_bloom_verbs()
OUTPUTS_DIR = "outputs"


# ── Helpers ──────────────────────────────────────────────────────

def save_syllabus_to_file(data: dict, course_name: str):
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = course_name.replace(" ", "_")
    filename  = f"{OUTPUTS_DIR}/syllabus_{safe_name}_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {filename}")
    return filename


def validate_bloom_start(text: str) -> str:
    if not text or not text.strip():
        return text
    words      = text.strip().split()
    first_word = words[0].lower().rstrip(".,;:")
    all_verbs  = [v for verbs in bloom_verbs.values() for v in verbs]
    if first_word not in all_verbs:
        return f"[VERB_WARNING] {text}"
    return text


def call_ollama(prompt: str, timeout: int = 300) -> dict:
    print(f"  Calling Ollama (timeout={timeout}s)...")
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json"},
        timeout=timeout
    )
    if response.status_code != 200:
        raise Exception(f"Ollama HTTP {response.status_code}: {response.text[:200]}")
    raw  = response.json()
    text = raw.get("response", "").strip()
    if not text:
        raise Exception("Ollama returned empty response")
    if "```" in text:
        for part in text.split("```"):
            if "{" in part:
                text = part.lstrip("json").strip()
                break
    return json.loads(text.strip())


def build_cos_summary(cos: list) -> str:
    if not cos:
        return "CO1 to CO5 covering fundamental to advanced topics"
    lines = []
    for co in cos:
        if isinstance(co, dict):
            lines.append(f"{co.get('co_id','CO')}: {co.get('text','')} [Bloom: {co.get('bloom_level','')}]")
        elif hasattr(co, 'co_id'):
            lines.append(f"{co.co_id}: {co.text} [Bloom: {co.bloom_level}]")
    return "\n".join(lines)


# ── Fallback defaults ─────────────────────────────────────────────

def get_default_objectives(course_name: str) -> list:
    return [
        f"To understand the fundamental principles of {course_name}",
        f"To apply the theoretical knowledge of {course_name} to solve practical problems",
        f"To analyze problems in {course_name} using standard methods and techniques",
        f"To evaluate different approaches and solutions in {course_name}",
        f"To develop problem solving and design skills in {course_name}"
    ]


def get_default_cos(course_name: str) -> list:
    from app.schemas.models import COObject
    defaults = [
        ("CO1", "Define and list the fundamental concepts and principles of " + course_name, "Remember", "Define", "L1", ["PO1", "PO2"], {"PO1": 3, "PO2": 2, "PO3": 0, "PO4": 0, "PO5": 0, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 0, "PO12": 1}, ["PSO1"], {"PSO1": 3, "PSO2": 1, "PSO3": 0}),
        ("CO2", "Explain the working principles and mechanisms of " + course_name, "Understand", "Explain", "L2", ["PO1", "PO3"], {"PO1": 2, "PO2": 0, "PO3": 3, "PO4": 0, "PO5": 0, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 0, "PO12": 1}, ["PSO1", "PSO2"], {"PSO1": 2, "PSO2": 3, "PSO3": 0}),
        ("CO3", "Solve practical problems in " + course_name + " using standard techniques", "Apply", "Solve", "L3", ["PO2", "PO3"], {"PO1": 0, "PO2": 3, "PO3": 2, "PO4": 0, "PO5": 1, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 0, "PO12": 0}, ["PSO2"], {"PSO1": 1, "PSO2": 3, "PSO3": 2}),
        ("CO4", "Analyze the components and behavior of " + course_name + " systems", "Analyze", "Analyze", "L4", ["PO2", "PO4"], {"PO1": 0, "PO2": 2, "PO3": 0, "PO4": 3, "PO5": 0, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 0, "PO12": 0}, ["PSO2", "PSO3"], {"PSO1": 0, "PSO2": 2, "PSO3": 3}),
        ("CO5", "Evaluate and compare different approaches in " + course_name + " for real applications", "Evaluate", "Evaluate", "L5", ["PO3", "PO11", "PO12"], {"PO1": 0, "PO2": 0, "PO3": 2, "PO4": 0, "PO5": 0, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 2, "PO12": 3}, ["PSO3"], {"PSO1": 0, "PSO2": 1, "PSO3": 3}),
    ]
    cos = []
    for co_id, text, bloom_level, bloom_verb, bloom_num, mapped_pos, po_corr, mapped_psos, pso_corr in defaults:
        cos.append(COObject(
            co_id               = co_id,
            text                = text,
            bloom_level         = bloom_level,
            bloom_verb          = bloom_verb,
            bloom_level_number  = bloom_num,
            mapped_pos          = mapped_pos,
            po_correlation      = po_corr,
            mapped_psos         = mapped_psos,
            pso_correlation     = pso_corr,
            attainment_target   = "60% of students score above 60%",
            attainment_level    = 1,
            direct_assessment   = ["Unit Test (20 marks)", "Assignment (5 marks)", "End Semester Exam (70 marks)"],
            indirect_assessment = ["Course End Survey"],
            unit_test_marks     = 20,
            assignment_marks    = 5,
            end_sem_marks       = 70
        ))
    return cos


def get_default_textbooks(course_name: str) -> list:
    return [
        f"1. Sedra, Adel S. — Textbook of {course_name} — Oxford University Press — 7th Edition — 2019",
        f"2. Boylestad, Robert L. — Introduction to {course_name} — Pearson Education — 12th Edition — 2018",
        f"3. Floyd, Thomas L. — {course_name} Fundamentals — Pearson Education — 10th Edition — 2017",
        f"4. Mano, M. Morris — {course_name} Design — Pearson Education — 5th Edition — 2016",
        f"5. Hayt, William H. — Engineering {course_name} — McGraw Hill — 8th Edition — 2019",
    ]


def get_default_resources() -> dict:
    return {
        "textbooks": [],
        "youtube_resources": [
            "NPTEL — Digital Electronics — Prof. S. Srinivasan — IIT Madras — https://nptel.ac.in/courses/",
            "MIT OpenCourseWare — Circuit Theory — https://ocw.mit.edu/",
            "Khan Academy — Electrical Engineering — https://www.khanacademy.org/science/electrical-engineering"
        ],
        "open_source_resources": [
            "NPTEL SWAYAM — Free Online Courses — https://swayam.gov.in",
            "MIT OpenCourseWare — Free Course Materials — https://ocw.mit.edu",
            "PhET Interactive Simulations — University of Colorado — https://phet.colorado.edu"
        ],
        "cqi_plan": "1. Review CO attainment every semester end. 2. If any CO attainment below Level 1: redesign assessment, add remedial classes, change teaching method. 3. Document Action Taken Report (ATR). 4. Present in IQAC meeting. 5. Re-measure next semester to verify improvement."
    }


def get_default_matrices() -> dict:
    return {
        "co_po_matrix": {
            "CO1": {"PO1": 3, "PO2": 2, "PO3": 0, "PO4": 0, "PO5": 0, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 0, "PO12": 1},
            "CO2": {"PO1": 2, "PO2": 0, "PO3": 3, "PO4": 0, "PO5": 0, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 0, "PO12": 1},
            "CO3": {"PO1": 0, "PO2": 3, "PO3": 2, "PO4": 0, "PO5": 1, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 0, "PO12": 0},
            "CO4": {"PO1": 0, "PO2": 2, "PO3": 0, "PO4": 3, "PO5": 0, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 0, "PO12": 0},
            "CO5": {"PO1": 0, "PO2": 0, "PO3": 2, "PO4": 0, "PO5": 0, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 2, "PO12": 3}
        },
        "co_pso_matrix": {
            "CO1": {"PSO1": 3, "PSO2": 1, "PSO3": 0},
            "CO2": {"PSO1": 2, "PSO2": 3, "PSO3": 0},
            "CO3": {"PSO1": 1, "PSO2": 3, "PSO3": 2},
            "CO4": {"PSO1": 0, "PSO2": 2, "PSO3": 3},
            "CO5": {"PSO1": 0, "PSO2": 1, "PSO3": 3}
        },
        "exam_pattern": {
            "internal_assessment": 30,
            "end_semester_exam": 70,
            "total": 100,
            "internal_breakdown": {
                "unit_tests_2_tests": 20,
                "assignments": 5,
                "attendance": 5
            }
        },
        "attainment_formula":    "CO Attainment = (Direct x 0.8) + (Indirect x 0.2)",
        "attainment_levels": {
            "Level 3": "80% or more students score above 60% threshold",
            "Level 2": "70-79% students score above 60% threshold",
            "Level 1": "60-69% students score above 60% threshold",
            "Level 0": "Less than 60% students score above threshold"
        },
        "po_attainment_formula": "PO Attainment = Sum(CO_Attainment x CO-PO) / Sum(CO-PO)",
        "lesson_plan_note":      "",
        "naac_iqac_note":        "This syllabus is prepared as per NBA GAPC v4.0, NAAC SSR criteria 1.1.2 and IQAC guidelines.",
    }


# ── Parse functions ───────────────────────────────────────────────

def parse_call1(data: dict) -> tuple:
    course_code       = data.get("course_code", "")
    course_objectives = data.get("course_objectives", [])
    raw_cos           = data.get("course_outcomes", [])
    co_objects        = []
    co_texts          = []

    for co in raw_cos:
        if isinstance(co, dict):
            co_obj = COObject(
                co_id               = co.get("co_id",               "CO"),
                text                = co.get("text",                ""),
                bloom_level         = co.get("bloom_level",         ""),
                bloom_verb          = co.get("bloom_verb",          ""),
                bloom_level_number  = co.get("bloom_level_number",  ""),
                mapped_pos          = co.get("mapped_pos",          []),
                po_correlation      = co.get("po_correlation",      {}),
                mapped_psos         = co.get("mapped_psos",         []),
                pso_correlation     = co.get("pso_correlation",     {}),
                attainment_target   = co.get("attainment_target",   "60% of students score above 60%"),
                attainment_level    = int(co.get("attainment_level", 1)),
                direct_assessment   = co.get("direct_assessment",   []),
                indirect_assessment = co.get("indirect_assessment", []),
                unit_test_marks     = int(co.get("unit_test_marks", 20)),
                assignment_marks    = int(co.get("assignment_marks", 5)),
                end_sem_marks       = int(co.get("end_sem_marks",   70))
            )
            co_objects.append(co_obj)
            pos_text = ", ".join([
                f"{po}({co.get('po_correlation',{}).get(po,'?')})"
                for po in co.get("mapped_pos", [])
            ])
            pso_text = ", ".join([
                f"{pso}({co.get('pso_correlation',{}).get(pso,'?')})"
                for pso in co.get("mapped_psos", [])
            ])
            co_texts.append(
                f"{co.get('co_id')}: {co.get('text')} "
                f"[Bloom: {co.get('bloom_level')} {co.get('bloom_level_number','')}] "
                f"[POs: {pos_text}] [PSOs: {pso_text}]"
            )

    return course_code, course_objectives, co_objects, co_texts


def flatten_to_string(item) -> str:
    """Convert dict or string to a flat string."""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        parts = []
        for v in item.values():
            if isinstance(v, str):
                parts.append(v)
            elif isinstance(v, (int, float)):
                parts.append(str(v))
        return " — ".join(parts)
    return str(item)

def parse_call2(data: dict) -> list:
    units = []
    for unit in data.get("units", []):
        objectives  = [validate_bloom_start(o) for o in unit.get("unit_objectives", [])]
        outcomes    = [validate_bloom_start(o) for o in unit.get("unit_outcomes",   [])]
        assessments = [flatten_to_string(a) for a in unit.get("assessments", [])]
        readings    = [flatten_to_string(r) for r in unit.get("readings",    [])]
        units.append(UnitObject(
            unit_id          = unit.get("unit_id",          f"UNIT {len(units)+1}"),
            unit_title       = unit.get("unit_title",       ""),
            hours            = int(unit.get("hours",        8)),
            topics_paragraph = unit.get("topics_paragraph", ""),
            topics           = unit.get("topics",           []),
            unit_objectives  = objectives,
            unit_outcomes    = outcomes,
            satisfied_cos    = unit.get("satisfied_cos",    []),
            assessments      = assessments,
            readings         = readings,
            lecture_plan     = unit.get("lecture_plan",     "")
        ))
    return units


def parse_call3(data: dict) -> dict:
    return {
        "co_po_matrix":          data.get("co_po_matrix",          {}),
        "co_pso_matrix":         data.get("co_pso_matrix",         {}),
        "exam_pattern":          data.get("exam_pattern",          {}),
        "attainment_formula":    data.get("attainment_formula",    "CO Attainment = (Direct x 0.8) + (Indirect x 0.2)"),
        "attainment_levels":     data.get("attainment_levels",     {}),
        "po_attainment_formula": data.get("po_attainment_formula", "PO Attainment = Sum(CO_Attainment x CO-PO) / Sum(CO-PO)"),
        "lesson_plan_note":      data.get("lesson_plan_note",      ""),
        "naac_iqac_note":        data.get("naac_iqac_note",        ""),
    }


def flatten_to_string(item) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        parts = []
        for v in item.values():
            if isinstance(v, str):
                parts.append(v)
            elif isinstance(v, (int, float)):
                parts.append(str(v))
        return " — ".join(parts)
    return str(item)

def parse_call4(data: dict) -> dict:
    cqi = data.get("cqi_plan", "")
    if isinstance(cqi, dict):
        steps = cqi.get("steps", [])
        cqi   = " ".join(steps) if steps else str(cqi)
    elif isinstance(cqi, list):
        cqi   = " ".join(cqi)

    textbooks             = [flatten_to_string(t) for t in data.get("textbooks",             [])]
    youtube_resources     = [flatten_to_string(y) for y in data.get("youtube_resources",     [])]
    open_source_resources = [flatten_to_string(o) for o in data.get("open_source_resources", [])]

    return {
        "textbooks":             textbooks,
        "youtube_resources":     youtube_resources,
        "open_source_resources": open_source_resources,
        "cqi_plan":              cqi,
    }


# ── Main 4-call generator ─────────────────────────────────────────

def generate_syllabus(request: SyllabusRequest) -> SyllabusResponse:
    print(f"\n{'='*60}")
    print(f"4-CALL SYLLABUS GENERATION")
    print(f"Course:    {request.course_name}")
    print(f"Programme: {request.programme} | {request.education_level}")
    print(f"Year: {request.year_of_study} | Sem: {request.semester} | Units: {request.num_units}")
    print(f"Regenerate: {request.regenerate}")
    print(f"{'='*60}")

    MAX_RETRIES = 2

    # ── CALL 1 — Course Objectives + Course Outcomes ──────────────
    course_code       = ""
    course_objectives = []
    co_objects        = []
    co_texts          = []

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"\n[CALL 1/4] Generating Course Objectives + COs (attempt {attempt})...")
            if request.regenerate:
                prompt1 = build_regenerate_call1_prompt(
                    request.course_name, request.course_description,
                    request.num_units,
                    request.education_level or "undergraduate",
                    request.programme       or "btech",
                    request.year_of_study, request.semester, request.branch,
                    request.credits or 4, request.ltp or "3:1:0",
                    request.rejection_reason, request.custom_prompt
                )
            else:
                prompt1 = build_call1_prompt(
                    request.course_name, request.course_description,
                    request.num_units,
                    request.education_level or "undergraduate",
                    request.programme       or "btech",
                    request.year_of_study, request.semester, request.branch,
                    request.credits or 4, request.ltp or "3:1:0",
                    request.custom_prompt
                )
            data1 = call_ollama(prompt1, timeout=300)
            course_code, course_objectives, co_objects, co_texts = parse_call1(data1)
            if len(co_objects) > 0 and len(course_objectives) > 0:
                print(f"  Call 1 OK — {len(co_objects)} COs | {len(course_objectives)} objectives")
                break
            else:
                print(f"  Call 1 incomplete (attempt {attempt}) — COs:{len(co_objects)} Obj:{len(course_objectives)}")
        except Exception as e:
            print(f"  Call 1 error (attempt {attempt}): {e}")

    # ── Call 1 fallback ───────────────────────────────────────────
    if not course_objectives:
        print("  Using fallback course objectives")
        course_objectives = get_default_objectives(request.course_name)
    if not co_objects:
        print("  Using fallback course outcomes")
        co_objects = get_default_cos(request.course_name)
        co_texts   = [f"{co.co_id}: {co.text} [Bloom: {co.bloom_level}]" for co in co_objects]

    cos_summary = build_cos_summary(co_objects)

    # ── CALL 2 — Unit-wise Syllabus ───────────────────────────────
    units = []

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"\n[CALL 2/4] Generating {request.num_units} Units (attempt {attempt})...")
            if request.regenerate:
                prompt2 = build_regenerate_call2_prompt(
                    request.course_name, request.course_description,
                    request.num_units,
                    request.education_level or "undergraduate",
                    request.programme       or "btech",
                    request.year_of_study, request.branch,
                    cos_summary,
                    request.rejection_reason, request.custom_prompt
                )
            else:
                prompt2 = build_call2_prompt(
                    request.course_name, request.course_description,
                    request.num_units,
                    request.education_level or "undergraduate",
                    request.programme       or "btech",
                    request.year_of_study, request.branch,
                    cos_summary,
                    request.custom_prompt
                )
            data2 = call_ollama(prompt2, timeout=300 + (request.num_units * 60))
            units = parse_call2(data2)
            if len(units) > 0:
                print(f"  Call 2 OK — {len(units)} units generated")
                break
            else:
                print(f"  Call 2 incomplete (attempt {attempt}) — 0 units")
        except Exception as e:
            print(f"  Call 2 error (attempt {attempt}): {e}")

    # ── CALL 3 — Matrices + Attainment ───────────────────────────
    matrices = {}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"\n[CALL 3/4] Generating CO-PO Matrix + Attainment (attempt {attempt})...")
            prompt3  = build_call3_prompt(
                request.course_name,
                cos_summary,
                request.num_units
            )
            data3    = call_ollama(prompt3, timeout=300)
            matrices = parse_call3(data3)
            if matrices.get("co_po_matrix"):
                print(f"  Call 3 OK — CO-PO matrix generated")
                break
            else:
                print(f"  Call 3 incomplete (attempt {attempt})")
        except Exception as e:
            print(f"  Call 3 error (attempt {attempt}): {e}")

    # ── Call 3 fallback ───────────────────────────────────────────
    if not matrices.get("co_po_matrix"):
        print("  Using fallback matrices")
        matrices = get_default_matrices()

    # ── CALL 4 — Textbooks + Resources + CQI ─────────────────────
    resources = {}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"\n[CALL 4/4] Generating Textbooks + Resources + CQI (attempt {attempt})...")
            prompt4   = build_call4_prompt(
                request.course_name, request.course_description,
                request.education_level or "undergraduate",
                request.programme       or "btech"
            )
            data4     = call_ollama(prompt4, timeout=300)
            resources = parse_call4(data4)
            if resources.get("textbooks"):
                print(f"  Call 4 OK — {len(resources['textbooks'])} textbooks generated")
                break
            else:
                print(f"  Call 4 incomplete (attempt {attempt})")
        except Exception as e:
            print(f"  Call 4 error (attempt {attempt}): {e}")

    # ── Call 4 fallback ───────────────────────────────────────────
    if not resources.get("textbooks"):
        print("  Using fallback resources")
        resources = get_default_resources()
        resources["textbooks"] = get_default_textbooks(request.course_name)

    # ── Assemble final response ───────────────────────────────────
    total_hours    = request.num_units * 8
    total_lectures = request.num_units * 9

    result = SyllabusResponse(
        course_name           = request.course_name,
        course_code           = course_code or request.course_code,
        education_level       = request.education_level or "undergraduate",
        programme             = request.programme       or "btech",
        year_of_study         = request.year_of_study,
        semester              = request.semester,
        branch                = request.branch,
        credits               = request.credits         or 4,
        ltp                   = request.ltp             or "3:1:0",
        university_name       = request.university_name,
        standards             = "NBA GAPC v4.0, AICTE, UGC-LOCF, NAAC, IQAC, Bloom's Taxonomy",
        total_hours           = total_hours,
        total_lectures        = total_lectures,
        units                 = units,
        course_objectives     = course_objectives,
        course_outcomes       = co_objects,
        course_outcomes_text  = co_texts,
        co_po_matrix          = matrices.get("co_po_matrix",          {}),
        co_pso_matrix         = matrices.get("co_pso_matrix",         {}),
        exam_pattern          = matrices.get("exam_pattern",          {}),
        attainment_formula    = matrices.get("attainment_formula",    "CO Attainment = (Direct x 0.8) + (Indirect x 0.2)"),
        attainment_levels     = matrices.get("attainment_levels",     {}),
        po_attainment_formula = matrices.get("po_attainment_formula", "PO Attainment = Sum(CO_Attainment x CO-PO) / Sum(CO-PO)"),
        cqi_plan              = resources.get("cqi_plan",             ""),
        lesson_plan_note      = matrices.get("lesson_plan_note",      ""),
        naac_iqac_note        = matrices.get("naac_iqac_note",        ""),
        textbooks             = resources.get("textbooks",            []),
        youtube_resources     = resources.get("youtube_resources",    []),
        open_source_resources = resources.get("open_source_resources",[]),
    )

    print(f"\n{'='*60}")
    print(f"4-CALL GENERATION COMPLETE")
    print(f"  Units:      {len(result.units)}")
    print(f"  COs:        {len(result.course_outcomes)}")
    print(f"  Objectives: {len(result.course_objectives)}")
    print(f"  Textbooks:  {len(result.textbooks)}")
    print(f"{'='*60}")

    save_syllabus_to_file({
        "course_name":          result.course_name,
        "course_code":          result.course_code,
        "education_level":      result.education_level,
        "programme":            result.programme,
        "year_of_study":        result.year_of_study,
        "semester":             result.semester,
        "branch":               result.branch,
        "credits":              result.credits,
        "ltp":                  result.ltp,
        "regenerated":          request.regenerate,
        "generated_at":         datetime.now().isoformat(),
        "call_1_cos":           len(result.course_outcomes),
        "call_2_units":         len(result.units),
        "call_3_matrix":        bool(result.co_po_matrix),
        "call_4_textbooks":     len(result.textbooks),
        "units":                [u.dict() for u in result.units],
        "course_objectives":    result.course_objectives,
        "course_outcomes":      [co.dict() for co in result.course_outcomes],
        "textbooks":            result.textbooks,
        "youtube_resources":    result.youtube_resources,
        "open_source_resources":result.open_source_resources,
    }, request.course_name)

    return result