import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.helpers import (
    sanitize_filename, save_json, load_json,
    success_response, error_response, get_system_stats
)

def print_result(test_name, passed):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status} — {test_name}")
    return passed

def divider(title=""):
    print(f"\n{'═'*60}")
    if title:
        print(f"  {title}")
        print(f"{'═'*60}")

def test_helpers():
    divider("Test 1 — Helpers")
    results = []
    results.append(print_result("Spaces replaced in filename", sanitize_filename("Data Structures") == "Data_Structures"))
    results.append(print_result("Special chars removed", "_" in sanitize_filename("Data/Structures:Test")))
    test_data = {"test": "data", "value": 123}
    path = save_json(test_data, "outputs", "test", "HelperTest")
    results.append(print_result("JSON saved", os.path.exists(path)))
    loaded = load_json(path)
    results.append(print_result("JSON loaded correctly", loaded == test_data))
    missing = load_json("outputs/nonexistent_file.json")
    results.append(print_result("Missing file returns None", missing is None))
    return results

def test_response_wrappers():
    divider("Test 2 — Response Wrappers")
    results = []
    success = success_response({"key": "value"}, "Test passed")
    results.append(print_result("success_response status=success", success.get("status") == "success"))
    results.append(print_result("success_response has timestamp", "timestamp" in success))
    results.append(print_result("success_response has data", success.get("data") == {"key": "value"}))
    error = error_response("Something went wrong", 500)
    results.append(print_result("error_response status=error", error.get("status") == "error"))
    results.append(print_result("error_response has code", error.get("code") == 500))
    return results

def test_system_stats():
    divider("Test 3 — System Stats")
    results = []
    stats = get_system_stats()
    results.append(print_result("has generated_files", "generated_files" in stats))
    results.append(print_result("has total_reviews", "total_reviews" in stats))
    results.append(print_result("has accepted_reviews", "accepted_reviews" in stats))
    results.append(print_result("has rejected_reviews", "rejected_reviews" in stats))
    results.append(print_result("has edited_reviews", "edited_reviews" in stats))
    results.append(print_result("generated_files is int", isinstance(stats["generated_files"], int)))
    return results

def test_logging():
    divider("Test 4 — Logging")
    results = []
    results.append(print_result("logs/ exists", os.path.exists("logs")))
    results.append(print_result("logs/app.log exists", os.path.exists("logs/app.log")))
    if os.path.exists("logs/app.log"):
        with open("logs/app.log") as f:
            content = f.read()
        results.append(print_result("app.log has content", len(content) > 0))
    return results

def test_output_structure():
    divider("Test 5 — Output Structure")
    results = []
    for folder in ["outputs", "feedback", "logs"]:
        results.append(print_result(f"{folder}/ exists", os.path.exists(folder)))
    results.append(print_result("30-course benchmark exists", os.path.exists("outputs/benchmark_30_courses.json")))
    results.append(print_result("contracts file exists", os.path.exists("outputs/data_contracts_v1.json")))
    results.append(print_result("reviews.json exists", os.path.exists("feedback/reviews.json")))
    return results

def test_edge_cases():
    divider("Test 6 — Edge Cases")
    results = []
    results.append(print_result("Empty filename handled", isinstance(sanitize_filename(""), str)))
    long_name = "A" * 200
    results.append(print_result("Long filename handled", isinstance(sanitize_filename(long_name), str)))
    resp = success_response(None, "Empty data")
    results.append(print_result("None data in success_response", resp["data"] is None))
    with open("outputs/test_invalid.json", "w") as f:
        f.write("not valid json{{{")
    try:
        load_json("outputs/test_invalid.json")
        results.append(print_result("Invalid JSON raises exception", False))
    except Exception:
        results.append(print_result("Invalid JSON raises exception as expected", True))
    finally:
        if os.path.exists("outputs/test_invalid.json"):
            os.remove("outputs/test_invalid.json")
    return results

if __name__ == "__main__":
    print("═"*60)
    print("  GROUP 1 — POLISH & BUG FIX TESTS")
    print("═"*60)
    all_results = []
    all_results += test_helpers()
    all_results += test_response_wrappers()
    all_results += test_system_stats()
    all_results += test_logging()
    all_results += test_output_structure()
    all_results += test_edge_cases()
    passed = sum(all_results)
    total  = len(all_results)
    print(f"\n{'═'*60}")
    print(f"  FINAL RESULT: {passed}/{total} tests passed")
    if passed == total:
        print("  🎉 ALL POLISH TESTS PASSED!")
        print("  ✅ Platform is production ready!")
    else:
        print(f"  ⚠ {total-passed} failed")
    print("═"*60)