def build_peo_prompt(programme_name: str, programme_description: str, n_peos: int) -> str:
    return f"""You are an NBA/ABET accreditation expert.

Generate exactly {n_peos} Program Educational Objectives (PEOs) for:
Programme: {programme_name}
Description: {programme_description}

RULES:
- PEOs describe what graduates achieve 3-5 years after graduation
- Start each with "Graduates will" or "Alumni will"
- Must align with NBA accreditation standards
- Respond in STRICT JSON only

JSON:
{{
  "peos": [
    {{
      "peo_id": "PEO1",
      "text": "Graduates will ...",
      "focus_area": "Industry/Research/Entrepreneurship/Society"
    }}
  ]
}}

Generate {n_peos} PEOs now:"""


def build_po_prompt(programme_name: str, programme_description: str) -> str:
    return f"""You are an NBA/ABET accreditation expert.

Generate all 12 standard Program Outcomes (POs) for:
Programme: {programme_name}
Description: {programme_description}

RULES:
- Use the 12 standard NBA POs as reference
- Each PO must be specific and measurable
- Start with action verbs
- Respond in STRICT JSON only

JSON:
{{
  "pos": [
    {{
      "po_id": "PO1",
      "title": "Engineering Knowledge",
      "text": "Apply knowledge of mathematics, science and engineering fundamentals"
    }}
  ]
}}

Generate all 12 POs now:"""


def build_pso_prompt(programme_name: str, course_list: list, n_psos: int) -> str:
    courses = ", ".join(course_list) if course_list else "core programme courses"
    return f"""You are an NBA accreditation expert.

Generate exactly {n_psos} Program Specific Outcomes (PSOs) for:
Programme: {programme_name}
Core Courses: {courses}

RULES:
- PSOs are specific to this programme
- Must reflect domain-specific skills at graduation
- Start with action verbs
- Respond in STRICT JSON only

JSON:
{{
  "psos": [
    {{
      "pso_id": "PSO1",
      "text": "Apply ... to ...",
      "domain": "specific domain"
    }}
  ]
}}

Generate {n_psos} PSOs now:"""