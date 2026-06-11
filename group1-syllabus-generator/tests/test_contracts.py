import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.schemas.validator import (
    validate_outcome_object, validate_unit_object,
    validate_programme_object, validate_review_entry,
    run_full_validation
)
from app.schemas.contracts import ALL_CONTRACTS

def print_result(test_name, passed):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status} — {test_name}")
    return passed

def divider(title=""):
    print(f"\n{'═'*60}")
    if title:
        print(f"  {title}")
        print(f"{'═'*60}")

def test_contracts_loaded():
    divider("Test 1 — Contracts Loaded")
    results = []
    results.append(print_result("version field exists", "version" in ALL_CONTRACTS))
    results.append(print_result("OutcomeObject contract", "OutcomeObject" in ALL_CONTRACTS))
    results.append(print_result("CourseUnits contract", "CourseUnits" in ALL_CONTRACTS))
    results.append(print_result("MappingResponse contract", "MappingResponse" in ALL_CONTRACTS))
    results.append(print_result("TrainingLabel contract", "TrainingLabel" in ALL_CONTRACTS))
    results.append(print_result("Programme contract", "Programme" in ALL_CONTRACTS))
    return results

def test_valid_outcomes():
    divider("Test 2 — Valid Outcome Objects")
    results = []
    for outcome in [
        {"text":"Apply binary search to optimize array searches efficiently","bloom_level":"apply","assessment_suggestion":"Coding","confidence_est":0.9,"flags":[],"domain_tags":["algorithm"]},
        {"text":"Analyze time and space complexity of sorting algorithms","bloom_level":"analyze","assessment_suggestion":"Report","confidence_est":0.85,"flags":[],"domain_tags":["algorithm"]},
    ]:
        result = validate_outcome_object(outcome)
        results.append(print_result(f"Valid outcome passes — '{outcome['text'][:40]}'", result["valid"]))
    return results

def test_invalid_outcomes():
    divider("Test 3 — Invalid Outcome Objects")
    results = []
    result = validate_outcome_object({"text":"Apply sorting","bloom_level":"apply"})
    results.append(print_result("Missing fields detected", result["valid"] == False))
    result = validate_outcome_object({"text":"Apply sorting algorithms to solve problems efficiently","bloom_level":"memorize","assessment_suggestion":"Quiz","confidence_est":0.9,"flags":[],"domain_tags":[]})
    results.append(print_result("Invalid bloom level detected", result["valid"] == False))
    result = validate_outcome_object({"text":"Apply sorting algorithms to solve complex problems","bloom_level":"apply","assessment_suggestion":"Quiz","confidence_est":1.5,"flags":[],"domain_tags":[]})
    results.append(print_result("confidence_est > 1.0 detected", result["valid"] == False))
    result = validate_outcome_object({"text":"Apply sorting","bloom_level":"apply","assessment_suggestion":"Quiz","confidence_est":0.9,"flags":[],"domain_tags":[]})
    results.append(print_result("Text too short detected", result["valid"] == False))
    return results

def test_valid_units():
    divider("Test 4 — Valid Unit Objects")
    results = []
    valid_unit = {
        "unit_id":"U1","unit_title":"Arrays and Linked Lists",
        "unit_objectives":["Define arrays","Explain linked lists","Compare structures"],
        "unit_outcomes":["Analyze complexity","Design algorithms"],
        "assessments":["Mid-term","Coding assignment"],
        "readings":["Chapter 1","Chapter 2"]
    }
    result = validate_unit_object(valid_unit)
    results.append(print_result("Valid unit passes", result["valid"] == True))
    invalid_unit = {"unit_id":"U1","unit_title":"Arrays","unit_objectives":["Define arrays"],"unit_outcomes":[],"assessments":["Quiz"],"readings":["Chapter 1"]}
    result = validate_unit_object(invalid_unit)
    results.append(print_result("Empty unit_outcomes detected", result["valid"] == False))
    return results

def test_valid_programme():
    divider("Test 5 — Valid Programme Objects")
    results = []
    valid_prog = {
        "programme_name":"B.Tech CSE",
        "peos":[{"peo_id":"PEO1","text":"Graduates will design software systems","focus_area":"Industry"},{"peo_id":"PEO2","text":"Alumni will pursue research","focus_area":"Research"},{"peo_id":"PEO3","text":"Graduates will serve society","focus_area":"Society"}],
        "pos":[{"po_id":f"PO{i}","title":f"Title {i}","text":f"Text {i}"} for i in range(1,13)],
        "psos":[{"pso_id":"PSO1","text":"Apply ML algorithms","domain":"ML"},{"pso_id":"PSO2","text":"Design networks","domain":"Networks"}]
    }
    result = validate_programme_object(valid_prog)
    results.append(print_result("Valid programme passes", result["valid"] == True))
    invalid_prog = {"programme_name":"B.Tech","peos":[{"peo_id":"PEO1","text":"Graduates will...","focus_area":"Industry"}],"pos":[],"psos":[]}
    result = validate_programme_object(invalid_prog)
    results.append(print_result("Too few PEOs detected", result["valid"] == False))
    return results

def test_review_validation():
    divider("Test 6 — Review Validation")
    results = []
    valid_review = {
        "outcome_id":"OC001","course_name":"DS","original_text":"Apply binary search","final_text":"Apply binary search",
        "action":"accept","reviewed_at":"2026-05-01T10:00:00",
        "training_label":{"is_valid":True,"was_edited":False,"original_text":"Apply binary search","approved_text":"Apply binary search","bloom_level":"apply"}
    }
    result = validate_review_entry(valid_review)
    results.append(print_result("Valid review passes", result["valid"] == True))
    invalid_review = {**valid_review, "action":"approve"}
    result = validate_review_entry(invalid_review)
    results.append(print_result("Invalid action 'approve' detected", result["valid"] == False))
    return results

def test_real_reviews():
    divider("Test 7 — Real reviews.json Validation")
    results = []
    if not os.path.exists("feedback/reviews.json"):
        print("  ⚠ reviews.json not found — skipping")
        return results
    with open("feedback/reviews.json","r") as f:
        reviews = json.load(f)
    results.append(print_result(f"reviews.json has {len(reviews)} entries", len(reviews) > 0))
    valid_count = sum(1 for r in reviews if validate_review_entry(r)["valid"])
    results.append(print_result(f"All {len(reviews)} entries valid", valid_count == len(reviews)))
    return results

def test_contract_export():
    divider("Test 8 — Contract Export")
    results = []
    os.makedirs("outputs", exist_ok=True)
    export_path = "outputs/data_contracts_v1.json"
    with open(export_path, "w") as f:
        json.dump(ALL_CONTRACTS, f, indent=2)
    results.append(print_result("Contracts exported", os.path.exists(export_path)))
    with open(export_path,"r") as f:
        loaded = json.load(f)
    results.append(print_result("Exported file is valid JSON", "version" in loaded))
    return results

if __name__ == "__main__":
    print("═"*60)
    print("  GROUP 1 — JSON CONTRACT TESTS")
    print("═"*60)
    all_results = []
    all_results += test_contracts_loaded()
    all_results += test_valid_outcomes()
    all_results += test_invalid_outcomes()
    all_results += test_valid_units()
    all_results += test_valid_programme()
    all_results += test_review_validation()
    all_results += test_real_reviews()
    all_results += test_contract_export()
    passed = sum(all_results)
    total  = len(all_results)
    print(f"\n{'═'*60}")
    print(f"  FINAL RESULT: {passed}/{total} tests passed")
    if passed == total:
        print("  🎉 ALL CONTRACT TESTS PASSED!")
    else:
        print(f"  ⚠ {total-passed} failed")
    print("═"*60)