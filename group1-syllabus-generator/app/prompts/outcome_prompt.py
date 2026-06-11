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

    return f"""You are a curriculum designer for {programme.upper()} {education_level} {year_text}.

Generate exactly {n_candidates} Course Outcomes (COs) for:
Course: {course_name}
Description: {course_description}
Bloom Levels: {levels}
Programme: {programme.upper()} {education_level} {year_text}
{custom_text}

Rules:
- Each outcome MUST start with a valid Bloom action verb from: {levels}
- One verb per outcome only — no compound verbs
- Be specific and measurable
- Match difficulty to {programme.upper()} {education_level}
- Respond with VALID JSON ONLY. No explanation. No markdown.

Format:
{{"outcomes":[{{"text":"verb + outcome here","bloom_level":"level","assessment_suggestion":"how to assess","confidence_est":0.9}}]}}

Generate {n_candidates} outcomes now:"""