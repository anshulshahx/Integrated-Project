"""
adapter/g2_integration.py
Calls Group 2 endpoints with confirmed specs.

Group 2 endpoints (port 8001):
  POST /map/matrix     - CO x PO/PSO/PEO matrices, levels 0-3
  POST /sequencer/plan - semester plan from prerequisite graph

Group 2 scoring: 0.55*BERT + 0.35*SVM + 0.10*keywords
Group 2 levels:  <0.2=L0, <0.4=L1, <0.6=L2, >=0.6=L3

Group 1 field names (confirmed from zip):
  pos:  {"po_id","title","text"}
  psos: {"pso_id","text","domain"}
  peos: {"peo_id","text","focus_area"}
"""

import requests
from group3_integration.definitions import (
    PO_DEFINITIONS, PSO_DEFINITIONS, PEO_DEFINITIONS,
    OVERRIDE_POS, OVERRIDE_PSOS, OVERRIDE_PEOS
)


def _g1_pos_to_g2(pos: list) -> list:
    return [{"id": p["po_id"], "text": p.get("text", "")} for p in pos if p.get("po_id")]

def _g1_psos_to_g2(psos: list) -> list:
    return [{"id": p["pso_id"], "text": p.get("text", "")} for p in psos if p.get("pso_id")]

def _g1_peos_to_g2(peos: list) -> list:
    return [{"id": p["peo_id"], "text": p.get("text", "")} for p in peos if p.get("peo_id")]


def fetch_programme_from_g1(programme_name: str, programme_description: str,
                             g1_api_url: str, course_list: list = None) -> dict:
    try:
        r = requests.post(
            f"{g1_api_url}/programme/generate-all",
            json={
                "programme_name":        programme_name,
                "programme_description": programme_description,
                "course_list":           course_list or [],
                "n_peos": 5,
                "n_psos": 3,
            },
            timeout=300
        )
        r.raise_for_status()
        data = r.json()
        print(f"  ✅ Group 1: {len(data.get('peos',[]))} PEOs, "
              f"{len(data.get('pos',[]))} POs, {len(data.get('psos',[]))} PSOs")
        return data
    except requests.exceptions.ConnectionError:
        print("  ⚠️  Group 1 unreachable — using fallback definitions")
        return {}
    except Exception as e:
        print(f"  ⚠️  Group 1 programme call failed: {e} — using fallback")
        return {}


def resolve_definitions(programme_data: dict) -> tuple:
    if OVERRIDE_POS:
        pos = PO_DEFINITIONS
        print(f"  🔁 POs: Group 3 override ({len(pos)})")
    else:
        g1 = _g1_pos_to_g2(programme_data.get("pos", []))
        pos = g1 if g1 else PO_DEFINITIONS
        print(f"  {'✅' if g1 else '🔄'} POs: {'Group 1' if g1 else 'fallback'} ({len(pos)})")

    if OVERRIDE_PSOS:
        psos = PSO_DEFINITIONS
        print(f"  🔁 PSOs: Group 3 override ({len(psos)})")
    else:
        g1 = _g1_psos_to_g2(programme_data.get("psos", []))
        psos = g1 if g1 else PSO_DEFINITIONS
        print(f"  {'✅' if g1 else '🔄'} PSOs: {'Group 1' if g1 else 'fallback'} ({len(psos)})")

    if OVERRIDE_PEOS:
        peos = PEO_DEFINITIONS
        print(f"  🔁 PEOs: Group 3 override ({len(peos)})")
    else:
        g1 = _g1_peos_to_g2(programme_data.get("peos", []))
        peos = g1 if g1 else PEO_DEFINITIONS
        print(f"  {'✅' if g1 else '🔄'} PEOs: {'Group 1' if g1 else 'fallback'} ({len(peos)})")

    return pos, psos, peos


def run_integration(course_meta: dict, g1_cos: list,
                    g1_api_url: str = "http://localhost:8000",
                    g2_api_url: str = "http://localhost:8001",
                    shared_store_url: str = "http://localhost:9000") -> dict:

    course = course_meta.get("course_name", "?")
    print(f"\n[G3] Course: {course}")

    print("[G3] Step 1: Fetching POs/PSOs/PEOs from Group 1 ...")
    prog = fetch_programme_from_g1(
        programme_name=f"{course_meta.get('programme','btech').upper()} "
                       f"{course_meta.get('branch','Computer Science')}",
        programme_description=(
            f"A {course_meta.get('programme','btech').upper()} programme in "
            f"{course_meta.get('branch','Computer Science')} covering {course}."
        ),
        g1_api_url=g1_api_url,
        course_list=[course],
    )
    pos, psos, peos = resolve_definitions(prog)

    print("[G3] Step 2: CO x PO mapping via Group 2 /map/matrix ...")
    try:
        r = requests.post(f"{g2_api_url}/map/matrix",
                          json={"cos": g1_cos, "pos": pos, "top_k": len(pos)},
                          timeout=120)
        r.raise_for_status()
        po_matrix = r.json().get("matrix", {})
        print(f"  ✅ {len(g1_cos)} COs x {len(pos)} POs done")
    except Exception as e:
        return {"success": False, "step": "co_po_mapping", "error": str(e)}

    print("[G3] Step 3: CO x PSO mapping via Group 2 /map/matrix ...")
    try:
        r = requests.post(f"{g2_api_url}/map/matrix",
                          json={"cos": g1_cos, "pos": psos, "top_k": len(psos)},
                          timeout=120)
        r.raise_for_status()
        pso_matrix = r.json().get("matrix", {})
        print(f"  ✅ {len(g1_cos)} COs x {len(psos)} PSOs done")
    except Exception as e:
        return {"success": False, "step": "co_pso_mapping", "error": str(e)}

    print("[G3] Step 4: PO x PEO mapping via Group 2 /map/matrix ...")
    peo_matrix = {}
    try:
        r = requests.post(f"{g2_api_url}/map/matrix",
                          json={"cos": pos, "pos": peos, "top_k": len(peos)},
                          timeout=120)
        r.raise_for_status()
        peo_matrix = r.json().get("matrix", {})
        print(f"  ✅ {len(pos)} POs x {len(peos)} PEOs done")
    except Exception as e:
        print(f"  ⚠️  PO x PEO failed (non-critical): {e}")

    print("[G3] Step 5: Saving to unified store ...")
    try:
        r = requests.post(f"{shared_store_url}/store/g2",
                          json={"data": {
                              "course_meta": course_meta,
                              "cos": g1_cos, "pos": pos, "psos": psos, "peos": peos,
                              "po_matrix": po_matrix, "pso_matrix": pso_matrix,
                              "peo_matrix": peo_matrix,
                          }}, timeout=30)
        r.raise_for_status()
        print(f"  ✅ Stored: {r.json()}")
        return {"success": True, "po_matrix": po_matrix,
                "pso_matrix": pso_matrix, "peo_matrix": peo_matrix}
    except Exception as e:
        return {"success": False, "step": "store_write", "error": str(e)}