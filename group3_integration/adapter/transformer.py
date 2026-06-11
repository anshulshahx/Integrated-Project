"""
adapter/transformer.py
Converts Group 1 SyllabusResponse to Group 2 SequencerRequest.
Group 2 confirmed input: {"courses": [{"id","credits","prerequisites"}], "max_credits_per_sem"}
"""

def transform_syllabus_to_sequencer_input(syllabus: dict, max_credits_per_sem: int = 20) -> dict:
    units   = syllabus.get("units", [])
    credits = syllabus.get("credits", 4)

    if not units:
        return {"courses": [], "max_credits_per_sem": max_credits_per_sem}

    unit_co_map = {}
    for unit in units:
        uid = _safe_id(unit.get("unit_id", f"UNIT{len(unit_co_map)+1}"))
        unit_co_map[uid] = set(unit.get("satisfied_cos", []))

    unit_ids = list(unit_co_map.keys())
    courses  = []

    for i, unit in enumerate(units):
        uid     = unit_ids[i]
        prereqs = []
        if i > 0:
            my_cos = unit_co_map[uid]
            for j in range(i):
                if my_cos & unit_co_map[unit_ids[j]]:
                    prereqs.append(unit_ids[j])
            if not prereqs:
                prereqs = [unit_ids[i - 1]]
        courses.append({
            "id":            uid,
            "credits":       max(1, credits // len(units)),
            "prerequisites": prereqs,
        })

    return {
        "courses":             courses,
        "max_credits_per_sem": max_credits_per_sem,
        "_meta": {
            "course_name": syllabus.get("course_name", ""),
            "course_code": syllabus.get("course_code", ""),
            "total_units": len(units),
            "total_cos":   len(syllabus.get("course_outcomes", [])),
        }
    }


def build_mapping_request(syllabus: dict, pos: list, psos: list = None,
                           peos: list = None, top_k: int = 12) -> dict:
    cos = [
        {"id": co.get("co_id"), "text": co.get("text", "").replace("[VERB_WARNING]", "").strip()}
        for co in syllabus.get("course_outcomes", [])
        if co.get("co_id") and co.get("text")
    ]
    payload = {"cos": cos, "pos": pos, "top_k": top_k}
    if psos:
        payload["psos"] = psos
    if peos:
        payload["peos"] = peos
    return payload


def _safe_id(raw: str) -> str:
    return raw.strip().replace(" ", "_").replace("-", "_").upper()