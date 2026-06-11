import sys
import os
import json
import requests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

BASE_URL = "http://127.0.0.1:8000"

def print_result(test_name, passed):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status} — {test_name}")
    return passed

def divider(title=""):
    print(f"\n{'═'*60}")
    if title:
        print(f"  {title}")
        print(f"{'═'*60}")

def test_health():
    divider("Test 1 — Health Check")
    results = []
    try:
        r    = requests.get(f"{BASE_URL}/health", timeout=10)
        data = r.json()
        results.append(print_result("HTTP 200", r.status_code == 200))
        results.append(print_result("api is running", data.get("api") == "running"))
        results.append(print_result("ollama connected", data.get("ollama") == "connected"))
        results.append(print_result("model is curriculum-ai", data.get("model") == "curriculum-ai"))
        results.append(print_result("endpoints listed", len(data.get("endpoints", [])) >= 5))
    except Exception as e:
        print(f"  ❌ Health failed: {e}")
        results.append(False)
    return results

def test_validation():
    divider("Test 2 — Input Validation")
    results = []
    r = requests.post(f"{BASE_URL}/generate/outcomes", json={
        "course_name": "",
        "course_description": "A course about data structures",
        "n_candidates": 3
    }, timeout=10)
    results.append(print_result("Empty course name returns 422", r.status_code == 422))
    r = requests.post(f"{BASE_URL}/generate/outcomes", json={
        "course_name": "Data Structures",
        "course_description": "Arrays and linked lists",
        "target_bloom_levels": ["invalid_level"],
        "n_candidates": 3
    }, timeout=10)
    results.append(print_result("Invalid bloom level returns 422", r.status_code == 422))
    r = requests.post(f"{BASE_URL}/generate/outcomes", json={
        "course_name": "Data Structures",
        "course_description": "Arrays and linked lists",
        "n_candidates": 100
    }, timeout=10)
    results.append(print_result("n_candidates=100 returns 422", r.status_code == 422))
    r = requests.post(f"{BASE_URL}/generate/syllabus", json={
        "course_name": "Data Structures",
        "course_description": "Arrays and linked lists",
        "num_units": 99
    }, timeout=10)
    results.append(print_result("num_units=99 returns 422", r.status_code == 422))
    return results

def test_review_system():
    divider("Test 3 — Review System")
    results = []
    payload = {"reviews": [
        {"outcome_id":"T001","course_name":"Test","original_text":"Apply pipeline testing to validate endpoints","edited_text":None,"bloom_level":"apply","action":"accept","reviewer_comment":"Good"},
        {"outcome_id":"T002","course_name":"Test","original_text":"Know the basics of testing","edited_text":"Identify and apply basic software testing methodologies","bloom_level":"apply","action":"edit","reviewer_comment":"Fixed verb"},
        {"outcome_id":"T003","course_name":"Test","original_text":"Understand stuff about networks","edited_text":None,"bloom_level":"understand","action":"reject","reviewer_comment":"Too vague"},
    ]}
    try:
        r    = requests.post(f"{BASE_URL}/review/submit", json=payload, timeout=30)
        data = r.json()
        results.append(print_result("Review submit HTTP 200", r.status_code == 200))
        results.append(print_result("total_reviewed is 3", data.get("total_reviewed") == 3))
        results.append(print_result("accepted is 1", data.get("accepted") == 1))
        results.append(print_result("rejected is 1", data.get("rejected") == 1))
        results.append(print_result("edited is 1", data.get("edited") == 1))
        r2    = requests.get(f"{BASE_URL}/review/training-labels", timeout=10)
        data2 = r2.json()
        results.append(print_result("Training labels HTTP 200", r2.status_code == 200))
        results.append(print_result("Positive labels exist", data2.get("positive_labels", 0) > 0))
        results.append(print_result("Negative labels exist", data2.get("negative_labels", 0) > 0))
    except Exception as e:
        print(f"  ❌ Review failed: {e}")
        results.append(False)
    return results

def test_output_files():
    divider("Test 4 — Output Files")
    results = []
    results.append(print_result("outputs/ exists", os.path.exists("outputs")))
    results.append(print_result("feedback/ exists", os.path.exists("feedback")))
    results.append(print_result("feedback/reviews.json exists", os.path.exists("feedback/reviews.json")))
    try:
        with open("feedback/reviews.json", "r") as f:
            reviews = json.load(f)
        results.append(print_result("reviews.json has entries", len(reviews) > 0))
        results.append(print_result("Each review has training_label",
            all("training_label" in r for r in reviews)))
    except Exception as e:
        print(f"  ❌ reviews.json check failed: {e}")
        results.append(False)
    output_files = os.listdir("outputs") if os.path.exists("outputs") else []
    results.append(print_result("outputs/ has files", len(output_files) > 0))
    return results

def test_outcome_generation():
    divider("Test 5 — Outcome Generation")
    results = []
    courses = [
        {"course_name":"Data Structures","course_description":"Arrays, linked lists, trees, graphs and sorting algorithms","target_bloom_levels":["apply","analyze"],"n_candidates":3},
        {"course_name":"Machine Learning","course_description":"Supervised learning, neural networks, regression and classification","target_bloom_levels":["evaluate","create"],"n_candidates":3},
    ]
    for course in courses:
        try:
            r    = requests.post(f"{BASE_URL}/generate/outcomes", json=course, timeout=600)
            data = r.json()
            results.append(print_result(f"{course['course_name']} — outcomes generated", len(data.get("outcomes",[])) > 0))
            results.append(print_result(f"{course['course_name']} — flags present", all("flags" in o for o in data.get("outcomes",[]))))
            results.append(print_result(f"{course['course_name']} — domain_tags present", all("domain_tags" in o for o in data.get("outcomes",[]))))
        except Exception as e:
            print(f"  ❌ {course['course_name']} failed: {e}")
            results.append(False)
    return results

def test_syllabus_generation():
    divider("Test 6 — Syllabus Generation")
    results = []
    payload = {
        "course_name": "Digital Electronics",
        "course_description": "Logic gates, boolean algebra, combinational and sequential circuits",
        "num_units": 3,
        "education_level": "undergraduate",
        "programme": "btech",
        "year_of_study": 2
    }
    try:
        r     = requests.post(f"{BASE_URL}/generate/syllabus", json=payload, timeout=1200)
        data  = r.json()
        units = data.get("units", [])
        results.append(print_result("Syllabus HTTP 200", r.status_code == 200))
        results.append(print_result("3 units generated", len(units) >= 1))
        results.append(print_result("Each unit has unit_id",
            all("unit_id" in u for u in units)))
        results.append(print_result("Each unit has unit_title",
            all("unit_title" in u and u["unit_title"] for u in units)))
        results.append(print_result("Each unit has unit_objectives",
            all(len(u.get("unit_objectives",[])) > 0 for u in units)))
        results.append(print_result("Each unit has unit_outcomes",
            all(len(u.get("unit_outcomes",[])) > 0 for u in units)))
        results.append(print_result("course_objectives present",
            len(data.get("course_objectives",[])) > 0))
        results.append(print_result("course_outcomes present",
            len(data.get("course_outcomes",[])) > 0))
        results.append(print_result("textbooks present",
            len(data.get("textbooks",[])) > 0))
        # New fields
        results.append(print_result("co_po_matrix present",
            isinstance(data.get("co_po_matrix"), dict)))
        results.append(print_result("exam_pattern present",
            isinstance(data.get("exam_pattern"), dict)))
        results.append(print_result("standards present",
            data.get("standards") is not None))
    except Exception as e:
        print(f"  ❌ Syllabus failed: {e}")
        results.append(False)
    return results

def test_programme_generation():
    divider("Test 7 — Programme Generation")
    results = []
    try:
        r = requests.post(f"{BASE_URL}/programme/peos", json={
            "programme_name": "B.Tech CSE",
            "programme_description": "Four year undergraduate programme in computer science",
            "n_peos": 3
        }, timeout=600)
        data = r.json()
        results.append(print_result("PEO HTTP 200", r.status_code == 200))
        results.append(print_result("3 PEOs generated", len(data.get("peos",[])) == 3))
    except Exception as e:
        print(f"  ❌ PEO failed: {e}")
        results.append(False)
    try:
        r = requests.post(f"{BASE_URL}/programme/pos", json={
            "programme_name": "B.Tech CSE",
            "programme_description": "Four year undergraduate programme in computer science"
        }, timeout=300)
        data = r.json()
        results.append(print_result("PO HTTP 200", r.status_code == 200))
        results.append(print_result("12 POs generated", len(data.get("pos",[])) == 12))
    except Exception as e:
        print(f"  ❌ PO failed: {e}")
        results.append(False)
    try:
        r = requests.post(f"{BASE_URL}/programme/psos", json={
            "programme_name": "B.Tech CSE",
            "course_list": ["Data Structures", "Machine Learning"],
            "n_psos": 3
        }, timeout=300)
        data = r.json()
        results.append(print_result("PSO HTTP 200", r.status_code == 200))
        results.append(print_result("3 PSOs generated", len(data.get("psos",[])) == 3))
    except Exception as e:
        print(f"  ❌ PSO failed: {e}")
        results.append(False)
    return results

if __name__ == "__main__":
    print("═"*60)
    print("  GROUP 1 — FULL PIPELINE INTEGRATION TEST")
    print("  Make sure server is running first!")
    print("═"*60)
    all_results = []
    all_results += test_health()
    all_results += test_validation()
    all_results += test_review_system()
    all_results += test_output_files()
    print("\n⏳ Running LLM tests (takes 5-10 minutes)...")
    all_results += test_outcome_generation()
    all_results += test_syllabus_generation()
    all_results += test_programme_generation()
    passed = sum(all_results)
    total  = len(all_results)
    divider("FINAL RESULTS")
    print(f"  PASSED: {passed}/{total}")
    if passed == total:
        print("  🎉 ALL PIPELINE TESTS PASSED!")
    else:
        print(f"  ⚠ {total-passed} test(s) failed")
    print("═"*60)