import requests
import json
import os
from datetime import datetime
from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from app.prompts.outcome_prompt import build_outcome_prompt
from app.schemas.models import OutcomeRequest, OutcomeObject
from app.rules.engine import run_rules_engine

OUTPUTS_DIR = "outputs"

def save_to_file(data: dict, prefix: str):
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"{OUTPUTS_DIR}/{prefix}_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {filename}")

def generate_outcomes(request: OutcomeRequest) -> list[OutcomeObject]:
    prompt = build_outcome_prompt(
        course_name         = request.course_name,
        course_description  = request.course_description,
        target_bloom_levels = request.target_bloom_levels,
        n_candidates        = request.n_candidates,
        education_level     = request.education_level or "undergraduate",
        programme           = request.programme       or "btech",
        year_of_study       = request.year_of_study,
        custom_prompt       = request.custom_prompt
    )
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json"},
            timeout=300
        )
        print(f"Ollama status: {response.status_code}")
        if response.status_code != 200:
            return []
        raw  = response.json()
        text = raw.get("response", "").strip()
        if not text:
            return []
        if "```" in text:
            for part in text.split("```"):
                if "{" in part:
                    text = part.lstrip("json").strip()
                    break
        parsed   = json.loads(text.strip())
        outcomes = []
        for item in parsed.get("outcomes", []):
            outcomes.append(OutcomeObject(
                text                  = item.get("text", ""),
                bloom_level           = item.get("bloom_level", ""),
                assessment_suggestion = item.get("assessment_suggestion", ""),
                confidence_est        = float(item.get("confidence_est", 0.8))
            ))
        outcomes = run_rules_engine(outcomes)
        save_to_file({
            "course_name":    request.course_name,
            "education_level":request.education_level,
            "programme":      request.programme,
            "year_of_study":  request.year_of_study,
            "generated_at":   datetime.now().isoformat(),
            "outcomes":       [o.dict() for o in outcomes]
        }, f"outcomes_{request.course_name.replace(' ', '_')}")
        return outcomes
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []