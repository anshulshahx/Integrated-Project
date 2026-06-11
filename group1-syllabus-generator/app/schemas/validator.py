"""
JSON Schema Validator
Validates all Group 1 outputs against official data contracts
"""
import json
from datetime import datetime

def validate_outcome_object(outcome: dict) -> dict:
    errors   = []
    warnings = []

    # Required fields
    required = ["text", "bloom_level", "assessment_suggestion",
                "confidence_est", "flags", "domain_tags"]
    for field in required:
        if field not in outcome:
            errors.append(f"Missing required field: '{field}'")

    # Text validation
    if "text" in outcome:
        words = len(outcome["text"].split())
        if words < 8:
            errors.append(f"text too short: {words} words (min 8)")
        if words > 30:
            warnings.append(f"text quite long: {words} words (max 30)")

    # Bloom level validation
    valid_levels = ["remember","understand","apply","analyze","evaluate","create"]
    if "bloom_level" in outcome:
        if outcome["bloom_level"].lower() not in valid_levels:
            errors.append(f"Invalid bloom_level: '{outcome['bloom_level']}'")

    # Confidence validation
    if "confidence_est" in outcome:
        c = outcome["confidence_est"]
        if not (0.0 <= c <= 1.0):
            errors.append(f"confidence_est must be 0.0-1.0, got {c}")

    # Flags check
    if "flags" in outcome and outcome["flags"]:
        warnings.append(f"Outcome has {len(outcome['flags'])} flag(s): {outcome['flags']}")

    return {
        "valid":    len(errors) == 0,
        "errors":   errors,
        "warnings": warnings
    }

def validate_unit_object(unit: dict) -> dict:
    errors   = []
    warnings = []

    required = ["unit_id","unit_title","unit_objectives",
                "unit_outcomes","assessments","readings"]
    for field in required:
        if field not in unit:
            errors.append(f"Missing required field: '{field}'")

    if "unit_objectives" in unit:
        if len(unit["unit_objectives"]) < 2:
            warnings.append("unit_objectives should have at least 2 items")

    if "unit_outcomes" in unit:
        if len(unit["unit_outcomes"]) < 1:
            errors.append("unit_outcomes must have at least 1 item")

    if "assessments" in unit:
        if len(unit["assessments"]) < 1:
            warnings.append("unit should have at least 1 assessment")

    return {
        "valid":    len(errors) == 0,
        "errors":   errors,
        "warnings": warnings
    }

def validate_programme_object(programme: dict) -> dict:
    errors   = []
    warnings = []

    # Check PEOs
    peos = programme.get("peos", [])
    if len(peos) < 3:
        errors.append(f"Need at least 3 PEOs, got {len(peos)}")
    for peo in peos:
        if not peo.get("text", "").strip():
            errors.append(f"PEO {peo.get('peo_id')} has empty text")

    # Check POs
    pos = programme.get("pos", [])
    if len(pos) < 12:
        warnings.append(f"Expected 12 POs, got {len(pos)}")
    for po in pos:
        if not po.get("title", "").strip():
            warnings.append(f"PO {po.get('po_id')} missing title")

    # Check PSOs
    psos = programme.get("psos", [])
    if len(psos) < 2:
        errors.append(f"Need at least 2 PSOs, got {len(psos)}")

    return {
        "valid":    len(errors) == 0,
        "errors":   errors,
        "warnings": warnings
    }

def validate_review_entry(review: dict) -> dict:
    errors   = []
    warnings = []

    required = ["outcome_id","course_name","original_text",
                "action","reviewed_at","training_label"]
    for field in required:
        if field not in review:
            errors.append(f"Missing field: '{field}'")

    valid_actions = ["accept","reject","edit"]
    if "action" in review:
        if review["action"] not in valid_actions:
            errors.append(f"Invalid action: '{review['action']}'")

    if "training_label" in review:
        label = review["training_label"]
        label_required = ["is_valid","was_edited","original_text",
                          "approved_text","bloom_level"]
        for field in label_required:
            if field not in label:
                errors.append(f"training_label missing: '{field}'")

    return {
        "valid":    len(errors) == 0,
        "errors":   errors,
        "warnings": warnings
    }

def run_full_validation(data: dict, data_type: str) -> dict:
    validators = {
        "outcome":   validate_outcome_object,
        "unit":      validate_unit_object,
        "programme": validate_programme_object,
        "review":    validate_review_entry,
    }

    if data_type not in validators:
        return {"error": f"Unknown data_type: {data_type}"}

    result = validators[data_type](data)
    result["data_type"]   = data_type
    result["validated_at"] = datetime.now().isoformat()
    return result