# ── NBA 12 POs — Indian Universities ────────────────────────────
NBA_12_POS_TEXT = """PO1:  Engineering Knowledge — Apply mathematics, science, engineering fundamentals and specialization to solve complex engineering problems
PO2:  Problem Analysis — Identify, formulate, research literature and analyze complex engineering problems using principles of mathematics, natural sciences and engineering
PO3:  Design/Development of Solutions — Design solutions for complex engineering problems considering public health, safety, cultural, societal and environmental considerations
PO4:  Conduct Investigations of Complex Problems — Use research-based knowledge and methods including design of experiments, analysis, interpretation of data for complex problems
PO5:  Modern Tool Usage — Create, select and apply appropriate techniques, resources and modern engineering tools including IT tools for complex engineering activities
PO6:  The Engineer and Society — Apply contextual knowledge to assess societal, health, safety, legal and cultural issues and professional engineering responsibilities
PO7:  Environment and Sustainability — Understand the impact of professional engineering solutions in societal and environmental contexts and demonstrate knowledge for sustainable development
PO8:  Ethics — Apply ethical principles and commit to professional ethics, responsibilities and norms of engineering practice
PO9:  Individual and Team Work — Function effectively as an individual and as a member or leader in diverse teams in multidisciplinary settings
PO10: Communication — Communicate effectively on complex engineering activities — reports, effective presentations, give and receive clear instructions
PO11: Project Management and Finance — Demonstrate knowledge and understanding of engineering management and financial principles and apply these to ones own work
PO12: Life Long Learning — Recognize the need for and have the preparation and ability to engage in independent and lifelong learning"""


def get_programme_context(programme: str) -> str:
    contexts = {
        "btech":   "B.Tech Engineering — AICTE approved, NBA accredited, 4-year UG programme",
        "bsc":     "B.Sc Science — UGC-LOCF compliant, 3-year UG programme",
        "bcom":    "B.Com Commerce — UGC-LOCF compliant, 3-year UG programme",
        "ba":      "B.A Arts — UGC-LOCF compliant, 3-year UG programme",
        "mtech":   "M.Tech Post-graduate Engineering — AICTE approved, NBA accredited",
        "msc":     "M.Sc Post-graduate Science — UGC compliant",
        "mca":     "MCA — AICTE approved, NBA accredited, 3-year PG programme",
        "bca":     "BCA — UGC compliant, 3-year UG programme",
        "mcom":    "M.Com Post-graduate Commerce — UGC compliant",
        "phd":     "PhD — UGC compliant doctoral programme",
        "diploma": "Diploma — AICTE approved, State Board of Technical Education affiliated",
        "mbbs":    "MBBS — NMC/MCI approved medical programme",
        "mba":     "MBA — AICTE approved business programme",
        "llb":     "LLB — BCI approved law programme",
        "bed":     "B.Ed — NCTE approved teacher education programme",
        "barch":   "B.Arch — CoA approved architecture programme",
    }
    return contexts.get(programme.lower(), "UGC/AICTE approved university programme")


# ═══════════════════════════════════════════════════════════════
# CALL 1 — Course Objectives + Course Outcomes (COs)
# ═══════════════════════════════════════════════════════════════
def build_call1_prompt(
    course_name: str,
    course_description: str,
    num_units: int,
    education_level: str = "undergraduate",
    programme: str = "btech",
    year_of_study: int = None,
    semester: int = None,
    branch: str = None,
    credits: int = 4,
    ltp: str = "3:1:0",
    custom_prompt: str = None
) -> str:
    year_text   = f"Year {year_of_study}" if year_of_study else "Not specified"
    sem_text    = f"Semester {semester}"  if semester      else "Not specified"
    branch_text = branch                  if branch        else "General"
    custom_text = f"\nADDITIONAL INSTRUCTIONS: {custom_prompt}" if custom_prompt else ""
    prog_ctx    = get_programme_context(programme)

    return f"""You are an expert Indian university curriculum designer following NBA GAPC v4.0, AICTE, UGC-LOCF OBE framework.

COURSE DETAILS:
Course: {course_name}
Description: {course_description}
Programme: {programme.upper()} — {prog_ctx}
Education Level: {education_level} | Year: {year_text} | Semester: {sem_text}
Branch: {branch_text} | Credits: {credits} | L:T:P: {ltp}
{custom_text}

NBA 12 PROGRAMME OUTCOMES:
{NBA_12_POS_TEXT}

YOUR TASK — Generate ONLY:
1. Exactly 5 Course Objectives (broad teaching intentions)
2. Exactly 5 Course Outcomes CO1 to CO5 with COMPLETE NBA fields
3. A realistic Indian university course code

RULES FOR COURSE OUTCOMES:
- Each CO must start with a Bloom action verb
- Bloom levels must progress: CO1=Remember/L1, CO2=Understand/L2, CO3=Apply/L3, CO4=Analyze/L4, CO5=Evaluate/L5
- Each CO must map to minimum 2 POs from PO1-PO12
- po_correlation must have ALL 12 POs (0 if not mapped)
- Each CO must map to minimum 1 PSO
- pso_correlation must have PSO1, PSO2, PSO3
- attainment_level is always 1 for new course
- STRICT JSON ONLY — no markdown no explanation

JSON FORMAT:
{{
  "course_code": "CS-301",
  "course_objectives": [
    "To understand the fundamental principles of {course_name}",
    "To apply the theoretical knowledge of {course_name} to solve practical problems",
    "To analyze problems in {course_name} using standard methods",
    "To evaluate solutions for practical applications",
    "To develop problem solving skills in {course_name}"
  ],
  "course_outcomes": [
    {{
      "co_id": "CO1",
      "text": "Define and list the fundamental concepts of {course_name} and their significance",
      "bloom_level": "Remember",
      "bloom_verb": "Define",
      "bloom_level_number": "L1",
      "mapped_pos": ["PO1", "PO2"],
      "po_correlation": {{"PO1": 3, "PO2": 2, "PO3": 0, "PO4": 0, "PO5": 0, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 0, "PO12": 1}},
      "mapped_psos": ["PSO1"],
      "pso_correlation": {{"PSO1": 3, "PSO2": 1, "PSO3": 0}},
      "attainment_target": "60% of students score above 60% marks",
      "attainment_level": 1,
      "direct_assessment": ["Unit Test I (20 marks)", "Assignment I (5 marks)"],
      "indirect_assessment": ["Course End Survey"],
      "unit_test_marks": 20,
      "assignment_marks": 5,
      "end_sem_marks": 70
    }},
    {{
      "co_id": "CO2",
      "text": "Explain the working principles and mechanisms of {course_name}",
      "bloom_level": "Understand",
      "bloom_verb": "Explain",
      "bloom_level_number": "L2",
      "mapped_pos": ["PO1", "PO3"],
      "po_correlation": {{"PO1": 2, "PO2": 0, "PO3": 3, "PO4": 0, "PO5": 0, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 0, "PO12": 1}},
      "mapped_psos": ["PSO1", "PSO2"],
      "pso_correlation": {{"PSO1": 2, "PSO2": 3, "PSO3": 0}},
      "attainment_target": "60% of students score above 60% marks",
      "attainment_level": 1,
      "direct_assessment": ["Unit Test I (20 marks)", "End Semester Exam (70 marks)"],
      "indirect_assessment": ["Course End Survey"],
      "unit_test_marks": 20,
      "assignment_marks": 5,
      "end_sem_marks": 70
    }},
    {{
      "co_id": "CO3",
      "text": "Solve practical problems in {course_name} using standard techniques",
      "bloom_level": "Apply",
      "bloom_verb": "Solve",
      "bloom_level_number": "L3",
      "mapped_pos": ["PO2", "PO3"],
      "po_correlation": {{"PO1": 0, "PO2": 3, "PO3": 2, "PO4": 0, "PO5": 1, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 0, "PO12": 0}},
      "mapped_psos": ["PSO2"],
      "pso_correlation": {{"PSO1": 1, "PSO2": 3, "PSO3": 2}},
      "attainment_target": "60% of students score above 60% marks",
      "attainment_level": 1,
      "direct_assessment": ["Unit Test II (20 marks)", "Assignment II (5 marks)", "End Semester Exam (70 marks)"],
      "indirect_assessment": ["Course End Survey"],
      "unit_test_marks": 20,
      "assignment_marks": 5,
      "end_sem_marks": 70
    }},
    {{
      "co_id": "CO4",
      "text": "Analyze the components and behavior of {course_name} systems",
      "bloom_level": "Analyze",
      "bloom_verb": "Analyze",
      "bloom_level_number": "L4",
      "mapped_pos": ["PO2", "PO4"],
      "po_correlation": {{"PO1": 0, "PO2": 2, "PO3": 0, "PO4": 3, "PO5": 0, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 0, "PO12": 0}},
      "mapped_psos": ["PSO2", "PSO3"],
      "pso_correlation": {{"PSO1": 0, "PSO2": 2, "PSO3": 3}},
      "attainment_target": "60% of students score above 60% marks",
      "attainment_level": 1,
      "direct_assessment": ["Unit Test II (20 marks)", "End Semester Exam (70 marks)"],
      "indirect_assessment": ["Exit Survey"],
      "unit_test_marks": 20,
      "assignment_marks": 5,
      "end_sem_marks": 70
    }},
    {{
      "co_id": "CO5",
      "text": "Evaluate and compare different approaches in {course_name} for real applications",
      "bloom_level": "Evaluate",
      "bloom_verb": "Evaluate",
      "bloom_level_number": "L5",
      "mapped_pos": ["PO3", "PO11", "PO12"],
      "po_correlation": {{"PO1": 0, "PO2": 0, "PO3": 2, "PO4": 0, "PO5": 0, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 2, "PO12": 3}},
      "mapped_psos": ["PSO3"],
      "pso_correlation": {{"PSO1": 0, "PSO2": 1, "PSO3": 3}},
      "attainment_target": "60% of students score above 60% marks",
      "attainment_level": 1,
      "direct_assessment": ["Assignment II (5 marks)", "End Semester Exam (70 marks)"],
      "indirect_assessment": ["Alumni Feedback Survey", "Course End Survey"],
      "unit_test_marks": 20,
      "assignment_marks": 5,
      "end_sem_marks": 70
    }}
  ]
}}

Generate course code, 5 objectives and 5 COs for {course_name} now:"""


# ═══════════════════════════════════════════════════════════════
# CALL 2 — Unit-wise Syllabus
# ═══════════════════════════════════════════════════════════════
def build_call2_prompt(
    course_name: str,
    course_description: str,
    num_units: int,
    education_level: str = "undergraduate",
    programme: str = "btech",
    year_of_study: int = None,
    branch: str = None,
    cos_summary: str = "",
    custom_prompt: str = None
) -> str:
    year_text   = f"Year {year_of_study}" if year_of_study else "Not specified"
    branch_text = branch if branch else "General"
    custom_text = f"\nADDITIONAL INSTRUCTIONS: {custom_prompt}" if custom_prompt else ""
    total_hours = num_units * 8

    return f"""You are an expert Indian university curriculum designer following NBA GAPC v4.0 OBE framework.

COURSE: {course_name}
Description: {course_description}
Programme: {programme.upper()} | Level: {education_level} | Year: {year_text} | Branch: {branch_text}
Total Units: {num_units} | Total Hours: {total_hours} (8 hours per unit)
{custom_text}

COURSE OUTCOMES ALREADY GENERATED:
{cos_summary}

YOUR TASK — Generate ONLY the {num_units} units syllabus.

STRICT RULES FOR EACH UNIT:
- Each unit must have exactly 8 hours
- Minimum 12-15 specific detailed subtopics per unit
- topics_paragraph: comma-separated flowing paragraph ending with (8 hours)
- unit_objectives: exactly 3 items with Bloom verb and level
- unit_outcomes: exactly 2 items mapped to COs
- satisfied_cos: which COs (CO1-CO5) this unit covers
- assessments: minimum 2 assessment items with marks
- readings: exactly 2 readings with chapter, author, book, edition
- lecture_plan: how 9 lectures are distributed
- STRICT JSON ONLY

JSON FORMAT:
{{
  "units": [
    {{
      "unit_id": "UNIT 1",
      "unit_title": "INTRODUCTION AND FUNDAMENTALS",
      "hours": 8,
      "satisfied_cos": ["CO1", "CO2"],
      "lecture_plan": "Lectures 1-2: Introduction and overview. Lectures 3-5: Core concepts and theory. Lectures 6-7: Applications and examples. Lectures 8-9: Problem solving and revision.",
      "topics_paragraph": "Introduction to {course_name}, Historical background and development, Basic terminology and definitions, Classification and types, Fundamental principles, Mathematical foundations, Standard notation and conventions, Key properties and characteristics, Comparison with related concepts, Real world applications overview, Laboratory and practical aspects, Recent advances and trends, Industry relevance and standards. (8 hours)",
      "topics": [
        "Introduction to {course_name}",
        "Historical background and development",
        "Basic terminology and definitions",
        "Classification and types",
        "Fundamental principles",
        "Mathematical foundations",
        "Standard notation and conventions",
        "Key properties and characteristics",
        "Comparison with related concepts",
        "Real world applications overview",
        "Laboratory and practical aspects",
        "Recent advances and trends",
        "Industry relevance and standards"
      ],
      "unit_objectives": [
        "Remember (Bloom L1): Define and list the fundamental concepts and terminology of {course_name}",
        "Understand (Bloom L2): Explain and describe the basic principles and working of {course_name}",
        "Apply (Bloom L3): Solve simple numerical and analytical problems related to {course_name}"
      ],
      "unit_outcomes": [
        "Students will be able to define and explain the fundamental concepts of {course_name} (maps to CO1)",
        "Students will be able to apply basic principles to solve introductory problems (maps to CO2)"
      ],
      "assessments": [
        "Unit Test I — Questions from Unit 1 — mapped to CO1 and CO2 (20 marks)",
        "Assignment I — Problems and theory from Unit 1 — mapped to CO1 (5 marks)"
      ],
      "readings": [
        "Chapter 1: Introduction — Author Name, Book Title, Publisher, 3rd Edition, 2019",
        "Chapter 2: Fundamentals — Author Name, Book Title, Publisher, 2nd Edition, 2020"
      ]
    }}
  ]
}}

Generate exactly {num_units} detailed units for {course_name} now:"""


# ═══════════════════════════════════════════════════════════════
# CALL 3 — CO-PO Matrix + CO-PSO Matrix + Exam Pattern + Attainment
# ═══════════════════════════════════════════════════════════════
def build_call3_prompt(
    course_name: str,
    cos_summary: str,
    num_units: int
) -> str:
    total_lectures = num_units * 9

    return f"""You are an NBA accreditation expert for Indian universities following NBA GAPC v4.0.

COURSE: {course_name}

COURSE OUTCOMES GENERATED:
{cos_summary}

YOUR TASK — Generate ONLY the mapping matrices, exam pattern and attainment data.

RULES:
- CO-PO matrix: 5 COs x 12 POs — values must be 0, 1, 2, or 3 only
- CO-PSO matrix: 5 COs x 3 PSOs — values must be 0, 1, 2, or 3 only
- Values must be CONSISTENT with CO-PO mappings from the course outcomes above
- 3 = High correlation, 2 = Medium, 1 = Low, 0 = No correlation
- exam_pattern follows Indian university standard (30 internal + 70 end sem)
- STRICT JSON ONLY

JSON FORMAT:
{{
  "co_po_matrix": {{
    "CO1": {{"PO1": 3, "PO2": 2, "PO3": 0, "PO4": 0, "PO5": 0, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 0, "PO12": 1}},
    "CO2": {{"PO1": 2, "PO2": 0, "PO3": 3, "PO4": 0, "PO5": 0, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 0, "PO12": 1}},
    "CO3": {{"PO1": 0, "PO2": 3, "PO3": 2, "PO4": 0, "PO5": 1, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 0, "PO12": 0}},
    "CO4": {{"PO1": 0, "PO2": 2, "PO3": 0, "PO4": 3, "PO5": 0, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 0, "PO12": 0}},
    "CO5": {{"PO1": 0, "PO2": 0, "PO3": 2, "PO4": 0, "PO5": 0, "PO6": 0, "PO7": 0, "PO8": 0, "PO9": 0, "PO10": 0, "PO11": 2, "PO12": 3}}
  }},
  "co_pso_matrix": {{
    "CO1": {{"PSO1": 3, "PSO2": 1, "PSO3": 0}},
    "CO2": {{"PSO1": 2, "PSO2": 3, "PSO3": 0}},
    "CO3": {{"PSO1": 1, "PSO2": 3, "PSO3": 2}},
    "CO4": {{"PSO1": 0, "PSO2": 2, "PSO3": 3}},
    "CO5": {{"PSO1": 0, "PSO2": 1, "PSO3": 3}}
  }},
  "exam_pattern": {{
    "internal_assessment": 30,
    "end_semester_exam": 70,
    "total": 100,
    "internal_breakdown": {{
      "unit_tests_2_tests": 20,
      "assignments": 5,
      "attendance": 5
    }}
  }},
  "attainment_formula": "CO Attainment = (Direct Assessment x 0.8) + (Indirect Assessment x 0.2)",
  "attainment_levels": {{
    "Level 3": "80% or more students score above 60% threshold",
    "Level 2": "70-79% students score above 60% threshold",
    "Level 1": "60-69% students score above 60% threshold",
    "Level 0": "Less than 60% students score above threshold"
  }},
  "po_attainment_formula": "PO Attainment = Sum(CO_Attainment x CO-PO_Strength) / Sum(CO-PO_Strength)",
  "lesson_plan_note": "Total {total_lectures} lectures planned: {num_units} units x 9 lectures per unit.",
  "naac_iqac_note": "This syllabus is prepared as per NBA GAPC v4.0, NAAC SSR criteria 1.1.2 and IQAC guidelines for Outcome Based Education."
}}

Generate CO-PO matrix, CO-PSO matrix, exam pattern and attainment data for {course_name} now:"""


# ═══════════════════════════════════════════════════════════════
# CALL 4 — Textbooks + Resources + CQI Plan
# ═══════════════════════════════════════════════════════════════
def build_call4_prompt(
    course_name: str,
    course_description: str,
    education_level: str = "undergraduate",
    programme: str = "btech"
) -> str:

    return f"""You are an expert Indian university curriculum designer.

COURSE: {course_name}
Description: {course_description}
Programme: {programme.upper()} | Level: {education_level}

YOUR TASK — Generate ONLY the following resources and CQI plan.

RULES:
- 5 real textbooks with real authors, real publishers, modern editions (2015 onwards)
- 3 YouTube/NPTEL/online video resources with real URLs
- 3 open source/SWAYAM/NPTEL resources with real URLs
- CQI plan: what action to take if CO attainment is below target
- All textbooks must be real books actually used in Indian universities
- STRICT JSON ONLY

JSON FORMAT:
{{
  "textbooks": [
    "1. Author Surname, First Name — Title of Book — Publisher — Edition — Year",
    "2. Author Surname, First Name — Title of Book — Publisher — Edition — Year",
    "3. Author Surname, First Name — Title of Book — Publisher — Edition — Year",
    "4. Author Surname, First Name — Title of Book — Publisher — Edition — Year",
    "5. Author Surname, First Name — Title of Book — Publisher — Edition — Year"
  ],
  "youtube_resources": [
    "NPTEL — Course Name — Prof. Name — IIT/IISc — https://nptel.ac.in/courses/",
    "MIT OpenCourseWare — Topic Name — https://ocw.mit.edu/",
    "Khan Academy — Topic Name — https://www.khanacademy.org/"
  ],
  "open_source_resources": [
    "NPTEL SWAYAM — Course Name — Free Certification — https://swayam.gov.in",
    "MIT OpenCourseWare — Free Course Materials — https://ocw.mit.edu",
    "PhET Interactive Simulations — University of Colorado — https://phet.colorado.edu"
  ],
  "cqi_plan": "1. Review CO attainment every semester end. 2. If any CO attainment below Level 1 (less than 60%): redesign assessment tools, add remedial classes, change teaching methodology. 3. Document Action Taken Report (ATR) for each low attainment CO. 4. Present ATR in IQAC meeting for approval. 5. Re-measure next semester to verify improvement. 6. Update course file with revised plan."
}}

Generate textbooks, resources and CQI plan for {course_name} now:"""


# ═══════════════════════════════════════════════════════════════
# REGENERATE PROMPTS
# ═══════════════════════════════════════════════════════════════
def build_regenerate_call1_prompt(
    course_name: str,
    course_description: str,
    num_units: int,
    education_level: str,
    programme: str,
    year_of_study: int = None,
    semester: int = None,
    branch: str = None,
    credits: int = 4,
    ltp: str = "3:1:0",
    rejection_reason: str = None,
    custom_prompt: str = None
) -> str:
    reason = f"REJECTION REASON: {rejection_reason}" if rejection_reason else "User not satisfied with previous version"
    base   = build_call1_prompt(
        course_name, course_description, num_units,
        education_level, programme, year_of_study,
        semester, branch, credits, ltp, custom_prompt
    )
    return f"""IMPORTANT: Previous syllabus for "{course_name}" was REJECTED.
{reason}
Generate COMPLETELY DIFFERENT Course Objectives and Course Outcomes.
Use different Bloom verbs, different PO mappings, stronger correlation values.

{base}"""


def build_regenerate_call2_prompt(
    course_name: str,
    course_description: str,
    num_units: int,
    education_level: str,
    programme: str,
    year_of_study: int = None,
    branch: str = None,
    cos_summary: str = "",
    rejection_reason: str = None,
    custom_prompt: str = None
) -> str:
    reason = f"REJECTION REASON: {rejection_reason}" if rejection_reason else "User not satisfied"
    base   = build_call2_prompt(
        course_name, course_description, num_units,
        education_level, programme, year_of_study,
        branch, cos_summary, custom_prompt
    )
    return f"""IMPORTANT: Previous syllabus was REJECTED.
{reason}
Generate COMPLETELY DIFFERENT unit titles, topics and subtopics.
More detailed content, different coverage approach.

{base}"""


# ═══════════════════════════════════════════════════════════════
# OUTCOME PROMPT — used by llm_client.py
# ═══════════════════════════════════════════════════════════════
def build_outcome_prompt(
    course_name: str,
    course_description: str,
    target_bloom_levels: list,
    n_candidates: int,
    education_level: str = "undergraduate",
    programme: str = "btech",
    year_of_study: int = None,
    custom_prompt: str = None
) -> str:
    levels      = ", ".join(target_bloom_levels)
    year_text   = f"Year {year_of_study}" if year_of_study else ""
    custom_text = f"\nADDITIONAL INSTRUCTIONS: {custom_prompt}" if custom_prompt else ""

    return f"""You are an Indian university curriculum designer following NBA GAPC v4.0 and AICTE OBE framework.

Generate exactly {n_candidates} Course Outcomes (COs) for:
Course: {course_name}
Description: {course_description}
Bloom Levels to use: {levels}
Programme: {programme.upper()} {education_level} {year_text}
{custom_text}

Rules:
- Each CO MUST start with a valid Bloom action verb from: {levels}
- One verb per CO only — no compound verbs
- Be specific and measurable
- VALID JSON ONLY — no explanation no markdown

Format:
{{"outcomes":[{{"text":"verb + outcome","bloom_level":"level","assessment_suggestion":"method","confidence_est":0.9}}]}}

Generate {n_candidates} outcomes now:"""