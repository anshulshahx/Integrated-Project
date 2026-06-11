"""
Day 11 — Helper utilities for error handling, logging and polish
"""
import os
import json
import logging
from datetime import datetime
from typing import Any

# ── Logging setup ─────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("curriculum_ai")

def log_request(endpoint: str, data: dict):
    logger.info(f"REQUEST → {endpoint} | data={json.dumps(data)[:100]}")

def log_response(endpoint: str, status: str, count: int = 0):
    logger.info(f"RESPONSE ← {endpoint} | status={status} | items={count}")

def log_error(endpoint: str, error: str):
    logger.error(f"ERROR @ {endpoint} | {error}")

# ── Output helpers ────────────────────────────────────────────────
def sanitize_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in " _-" else "_" for c in name).replace(" ", "_")

def save_json(data: Any, folder: str, prefix: str, name: str) -> str:
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = sanitize_filename(name)
    filepath  = f"{folder}/{prefix}_{safe_name}_{timestamp}.json"
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved → {filepath}")
    return filepath

def load_json(filepath: str) -> Any:
    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        return None
    with open(filepath, "r") as f:
        return json.load(f)

# ── Response wrappers ─────────────────────────────────────────────
def success_response(data: Any, message: str = "Success") -> dict:
    return {
        "status":     "success",
        "message":    message,
        "timestamp":  datetime.now().isoformat(),
        "data":       data
    }

def error_response(message: str, code: int = 500) -> dict:
    return {
        "status":    "error",
        "message":   message,
        "timestamp": datetime.now().isoformat(),
        "code":      code
    }

# ── Stats helper ──────────────────────────────────────────────────
def get_system_stats() -> dict:
    outputs    = os.listdir("outputs") if os.path.exists("outputs") else []
    reviews    = []
    if os.path.exists("feedback/reviews.json"):
        with open("feedback/reviews.json") as f:
            reviews = json.load(f)

    return {
        "generated_files":    len(outputs),
        "total_reviews":      len(reviews),
        "accepted_reviews":   len([r for r in reviews if r.get("action") == "accept"]),
        "rejected_reviews":   len([r for r in reviews if r.get("action") == "reject"]),
        "edited_reviews":     len([r for r in reviews if r.get("action") == "edit"]),
        "logs_directory":     "logs/",
        "outputs_directory":  "outputs/",
        "feedback_directory": "feedback/",
    }