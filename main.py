import sys, json, requests, os, glob, time

GROUP1_URL = "http://localhost:8000"
GROUP2_URL = "http://localhost:8001"


def get_latest_saved_syllabus(course_name):
    safe = course_name.replace(" ", "_")
    pattern = f"group1-syllabus-generator/outputs/syllabus_{safe}_*.json"
    files = glob.glob(pattern)
    if not files:
        return None
    latest = max(files, key=os.path.getmtime)
    print(f"  Using saved syllabus: {latest}")
    with open(latest) as f:
        return json.load(f)


def call_group1(course_name, course_description, course_code,
                num_units, programme, year_of_study, semester, branch, credits):
    return requests.post(f"{GROUP1_URL}/generate/syllabus", json={
        "course_name":        course_name,
        "course_description": course_description,
        "course_code":        course_code,
        "num_units":          num_units,
        "education_level":    "undergraduate",
        "programme":          programme,
        "year_of_study":      year_of_study,
        "semester":           semester,
        "branch":             branch,
        "credits":            credits,
        "ltp":                "3:1:0",
    }, timeout=900)


def run_pipeline(
    course_name,
    course_code        = "CS601",
    course_description = None,
    num_units          = 5,
    programme          = "btech",
    year_of_study      = 2,
    semester           = 3,
    branch             = "Computer Science and Engineering",
    credits            = 4,
):
    if not course_description:
        course_description = f"A comprehensive course on {course_name} for engineering students."

    print(f"\n{'='*60}")
    print(f"  INTEGRATED PIPELINE")
    print(f"  Course : {course_name} [{course_code}]")
    print(f"{'='*60}\n")

    # STEP 1: Call Group 1 for syllabus
    print("[1] Calling Group 1 - generating syllabus...")
    syllabus = None

    try:
        r = call_group1(course_name, course_description, course_code,
                        num_units, programme, year_of_study, semester, branch, credits)
        r.raise_for_status()
        syllabus = r.json()
        print(f"  OK - {len(syllabus.get('units', []))} units, "
              f"{len(syllabus.get('course_outcomes', []))} COs received")

    except requests.exceptions.ConnectionError:
        print("  ERROR - Group 1 unreachable at port 8000")
        print("  Run: python -m uvicorn app.main:app --port 8000 --reload")
        sys.exit(1)

    except requests.exceptions.ReadTimeout:
        print("  Group 1 timed out - Ollama is busy")
        print("  Waiting 60 seconds and retrying...")
        time.sleep(60)
        try:
            r = call_group1(course_name, course_description, course_code,
                            num_units, programme, year_of_study, semester, branch, credits)
            r.raise_for_status()
            syllabus = r.json()
            print(f"  OK - retry succeeded - "
                  f"{len(syllabus.get('units', []))} units, "
                  f"{len(syllabus.get('course_outcomes', []))} COs received")
        except requests.exceptions.ReadTimeout:
            print("  Retry timed out - checking for saved syllabus...")
            syllabus = get_latest_saved_syllabus(course_name)
            if not syllabus:
                print("  ERROR - No saved syllabus found for this course.")
                print("  Wait for Ollama to finish and try again.")
                sys.exit(1)
        except Exception as e:
            print(f"  Retry failed: {e}")
            print("  Checking for saved syllabus...")
            syllabus = get_latest_saved_syllabus(course_name)
            if not syllabus:
                print("  ERROR - No saved syllabus found for this course.")
                sys.exit(1)

    except Exception as e:
        print(f"  ERROR - {e}")
        print("  Checking for saved syllabus...")
        syllabus = get_latest_saved_syllabus(course_name)
        if not syllabus:
            print("  ERROR - No saved syllabus found for this course.")
            sys.exit(1)

    cos = syllabus.get("course_outcomes", [])
    print(f"  Units: {len(syllabus.get('units', []))} | COs: {len(cos)}")

    # STEP 2: Validate
    print("[2] Validating syllabus...")
    from group3_integration.adapter.validator import validate_syllabus_response
    issues = validate_syllabus_response(syllabus)
    if issues:
        for issue in issues:
            print(f"  WARNING: {issue}")
    else:
        print("  OK - syllabus is valid")

    # STEP 3: Prepare COs
    print("[3] Preparing COs for Group 2...")
    g2_cos = [
        {"id": co["co_id"], "text": co["text"].replace("[VERB_WARNING]", "").strip()}
        for co in cos if co.get("co_id") and co.get("text")
    ]
    print(f"  OK - {len(g2_cos)} COs ready")

    # STEP 4: Get POs/PSOs/PEOs from Group 1
    print("[4] Fetching POs/PSOs/PEOs from Group 1...")
    from group3_integration.adapter.g2_integration import (
        fetch_programme_from_g1, resolve_definitions
    )
    prog = fetch_programme_from_g1(
        programme_name=f"{programme.upper()} {branch}",
        programme_description=(
            f"A {programme.upper()} programme in {branch} covering {course_name}."
        ),
        g1_api_url=GROUP1_URL,
        course_list=[course_name],
    )
    pos, psos, peos = resolve_definitions(prog)

    # STEP 5: Group 2 CO-PO mapping
    print("[5] Running CO-PO mapping via Group 2...")
    po_matrix  = {}
    pso_matrix = {}
    peo_matrix = {}
    try:
        r = requests.post(
            f"{GROUP2_URL}/map/matrix",
            json={"cos": g2_cos, "pos": pos,
                  "psos": psos, "peos": peos, "top_k": len(pos)},
            timeout=120
        )
        r.raise_for_status()
        resp       = r.json()
        po_matrix  = resp.get("matrix",     {})
        pso_matrix = resp.get("pso_matrix", {})
        peo_matrix = resp.get("peo_matrix", {})
        print(f"  OK - {len(g2_cos)} COs x {len(pos)} POs mapped")
    except requests.exceptions.ConnectionError:
        print("  ERROR - Group 2 unreachable at port 8001")
        print("  Run: python -m uvicorn api.main:app --port 8001 --reload")
    except Exception as e:
        print(f"  ERROR - {e}")

    # STEP 6: Group 2 sequencer
    print("[6] Running semester sequencer via Group 2...")
    from group3_integration.adapter.transformer import transform_syllabus_to_sequencer_input
    plan = {}
    try:
        seq = transform_syllabus_to_sequencer_input(syllabus)
        r = requests.post(
            f"{GROUP2_URL}/sequencer/plan",
            json={"courses":             seq["courses"],
                  "max_credits_per_sem": seq["max_credits_per_sem"]},
            timeout=30
        )
        r.raise_for_status()
        plan = r.json()
        if plan.get("error"):
            print(f"  WARNING - {plan['error']}")
        else:
            print(f"  OK - {plan.get('total_semesters','?')} semesters, "
                  f"{plan.get('total_courses','?')} units placed")
    except Exception as e:
        print(f"  WARNING - sequencer failed: {e}")

    # STEP 7: Final output
    print(f"\n{'─'*60}")
    print("FINAL OUTPUT")
    print(f"{'─'*60}")
    print(f"  Course       : {course_name}")
    print(f"  Code         : {course_code}")
    print(f"  Programme    : {programme.upper()} | {branch}")
    print(f"  COs          : {len(g2_cos)} (from Group 1)")
    print(f"  POs          : {len(pos)} (from Group 1)")
    print(f"  CO-PO matrix : {len(po_matrix)} rows (mapped by Group 2)")

    if plan.get("plan"):
        print(f"  Semesters    : {plan.get('total_semesters','?')}")
        for sem in plan["plan"]:
            print(f"    Sem {sem['semester']}: "
                  f"{sem['courses']} ({sem['credits']} credits)")

    if po_matrix:
        print()
        print("  CO-PO Matrix:")
        for co_id, row in po_matrix.items():
            mapped = [p + "=" + str(v) for p, v in row.items() if v > 0]
            print("  " + co_id + ": " +
                  (", ".join(mapped) if mapped else "no mapping"))

    print(f"{'─'*60}")
    print("\nPipeline complete.\n")

    return {
        "syllabus":   syllabus,
        "po_matrix":  po_matrix,
        "pso_matrix": pso_matrix,
        "peo_matrix": peo_matrix,
        "plan":       plan,
    }


if __name__ == "__main__":
    course = sys.argv[1] if len(sys.argv) > 1 else "Computer Organization and Architecture"
    code   = sys.argv[2] if len(sys.argv) > 2 else "COA-401"
    run_pipeline(course, course_code=code)