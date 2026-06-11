"""
adapter/validator.py
Validates data at both integration boundaries.
Group 2 confirmed: cos/pos = [{"id","text"}], matrix levels = 0-3
"""

def validate_syllabus_response(syllabus: dict) -> list:
    errors = []
    if not isinstance(syllabus, dict):
        return [f"Expected dict, got {type(syllabus).__name__}"]
    if not syllabus.get("course_name", "").strip():
        errors.append("Missing: course_name")
    if not syllabus.get("units"):
        errors.append("Missing: units[]")
    else:
        for i, u in enumerate(syllabus["units"]):
            if not u.get("unit_id"):
                errors.append(f"units[{i}]: missing unit_id")
            if not u.get("unit_title"):
                errors.append(f"units[{i}]: missing unit_title")
    if not syllabus.get("course_outcomes"):
        errors.append("Missing: course_outcomes[]")
    else:
        for i, co in enumerate(syllabus["course_outcomes"]):
            if not co.get("co_id"):
                errors.append(f"course_outcomes[{i}]: missing co_id")
            if not co.get("text"):
                errors.append(f"course_outcomes[{i}]: missing text")
            if not co.get("bloom_level"):
                errors.append(f"course_outcomes[{i}]: missing bloom_level")
    return errors


def validate_mapping_request(payload: dict) -> list:
    errors = []
    for field in ["cos", "pos"]:
        if field not in payload:
            errors.append(f"Missing: '{field}'")
            continue
        if not isinstance(payload[field], list) or len(payload[field]) == 0:
            errors.append(f"'{field}' must be a non-empty list")
            continue
        for i, item in enumerate(payload[field]):
            if not item.get("id"):
                errors.append(f"{field}[{i}]: missing 'id'")
            if not item.get("text"):
                errors.append(f"{field}[{i}]: missing 'text'")
    return errors


def validate_sequencer_input(payload: dict) -> list:
    errors = []
    if "courses" not in payload:
        errors.append("Missing: 'courses'")
        return errors
    if not isinstance(payload["courses"], list) or len(payload["courses"]) == 0:
        errors.append("'courses' must be a non-empty list")
        return errors
    course_ids = set()
    for i, c in enumerate(payload["courses"]):
        if not c.get("id", "").strip():
            errors.append(f"courses[{i}]: missing 'id'")
        else:
            if c["id"] in course_ids:
                errors.append(f"courses[{i}]: duplicate id '{c['id']}'")
            course_ids.add(c["id"])
        if not isinstance(c.get("credits"), int) or c.get("credits", 0) < 1:
            errors.append(f"courses[{i}]: 'credits' must be a positive integer")
        if not isinstance(c.get("prerequisites", []), list):
            errors.append(f"courses[{i}]: 'prerequisites' must be a list")
    for i, c in enumerate(payload["courses"]):
        for prereq in c.get("prerequisites", []):
            if prereq not in course_ids:
                errors.append(f"courses[{i}]: prerequisite '{prereq}' not found")
    return errors


def validate_g2_matrix_response(response: dict, expected_co_ids: list) -> list:
    errors = []
    if "matrix" not in response:
        errors.append("Group 2 response missing 'matrix' key")
        return errors
    matrix = response["matrix"]
    for co_id in expected_co_ids:
        if co_id not in matrix:
            errors.append(f"matrix missing row for {co_id}")
        else:
            for po_id, level in matrix[co_id].items():
                if level not in [0, 1, 2, 3]:
                    errors.append(f"matrix[{co_id}][{po_id}]: invalid level {level}")
    return errors