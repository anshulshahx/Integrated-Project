import json
import re
from pathlib import Path

BLOOM_VERBS_PATH = Path(__file__).parent.parent.parent / "data" / "bloom_verbs.json"

def load_bloom_verbs():
    with open(BLOOM_VERBS_PATH, "r") as f:
        return json.load(f)

def get_all_verbs(bloom_verbs: dict) -> list:
    all_verbs = []
    for level, verbs in bloom_verbs.items():
        all_verbs.extend(verbs)
    return all_verbs

# Rule 1
def check_bloom_verb(text: str, bloom_verbs: dict) -> tuple:
    first_word = text.strip().split()[0].lower().rstrip(".,;:")
    all_verbs  = get_all_verbs(bloom_verbs)
    if first_word not in all_verbs:
        return False, f"First word '{first_word}' is not a valid Bloom verb"
    return True, None

# Rule 2
def check_measurability(text: str) -> tuple:
    words     = text.lower().split()
    first_six = " ".join(words[:6])
    match     = re.search(r'\b(\w+)\s+and\s+(\w+)\b', first_six)
    if match:
        all_verbs = get_all_verbs(load_bloom_verbs())
        w1 = match.group(1).lower()
        w2 = match.group(2).lower()
        if w1 in all_verbs and w2 in all_verbs:
            return False, f"Compound verb detected: '{w1} and {w2}' — use single verb only"
    return True, None

# Rule 3
def similarity_score(text1: str, text2: str) -> float:
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    return len(words1 & words2) / len(words1 | words2)

def deduplicate(outcomes: list) -> tuple:
    unique  = []
    removed = []
    for outcome in outcomes:
        is_duplicate = any(
            similarity_score(outcome.text, u.text) > 0.8
            for u in unique
        )
        if is_duplicate:
            removed.append(outcome.text)
        else:
            unique.append(outcome)
    return unique, removed

# Rule 4
DOMAIN_TERMS = [
    "algorithm", "array", "linked list", "tree", "graph", "sorting", "searching",
    "recursion", "stack", "queue", "hash", "binary", "complexity", "database",
    "network", "operating system", "compiler", "machine learning", "neural network",
    "regression", "classification", "clustering", "api", "http", "protocol",
    "calculus", "matrix", "vector", "probability", "statistics", "differential",
    "integral", "linear algebra", "circuit", "transistor", "amplifier", "signal",
    "frequency", "voltage", "current", "microcontroller", "pid", "sensor",
    "analysis", "design", "implementation", "evaluation", "optimization",
    "simulation", "modeling", "testing", "debugging", "documentation"
]

def extract_domain_tags(text: str) -> list:
    text_lower = text.lower()
    return [term for term in DOMAIN_TERMS if term in text_lower]

# Rule 5
def check_length(text: str) -> tuple:
    word_count = len(text.strip().split())
    if word_count < 8:
        return False, f"Too short ({word_count} words) — minimum 8 required"
    if word_count > 30:
        return False, f"Too long ({word_count} words) — maximum 30 allowed"
    return True, None

# Rule 6
PROFANITY_LIST = [
    "damn","hell","crap","stupid","idiot","dumb","moron",
    "bloody","ass","jerk","loser","fool","hate","sucks",
    "terrible","awful","horrible","useless","pathetic","garbage"
]

def check_profanity(text: str) -> tuple:
    text_lower = text.lower()
    words      = re.findall(r'\b\w+\b', text_lower)
    for word in words:
        if word in PROFANITY_LIST:
            return False, f"Inappropriate word '{word}' detected"
    return True, None

# Rule 7
BIASED_TERMS = [
    "he", "she", "his", "her", "him", "himself", "herself",
    "mankind", "manpower", "manmade", "chairman", "policeman",
    "obviously", "just", "merely",
    "trivial", "anyone can", "everybody knows"
]

def check_bias(text: str) -> tuple:
    text_lower = text.lower()
    found      = []
    for term in BIASED_TERMS:
        pattern = r'\b' + re.escape(term) + r'\b'
        if re.search(pattern, text_lower):
            found.append(term)
    if found:
        return False, f"Biased term(s) {found} detected — consider neutral language"
    return True, None

# Rule 8
INFORMAL_TERMS = [
    "stuff", "things", "cool", "awesome", "basically", "kinda",
    "sorta", "lots of", "a lot of", "really", "very", "pretty much",
    "kind of", "sort of", "you know", "like", "okay", "ok",
    "great", "nice", "good enough", "etc"
]

def check_academic_tone(text: str) -> tuple:
    text_lower = text.lower()
    found      = []
    for term in INFORMAL_TERMS:
        if term in text_lower:
            found.append(term)
    if found:
        return False, f"Informal term(s) {found} detected — use academic language"
    return True, None

# Main engine
def run_rules_engine(outcomes: list) -> list:
    bloom_verbs = load_bloom_verbs()
    processed   = []

    for outcome in outcomes:
        flags = []

        valid, msg = check_bloom_verb(outcome.text, bloom_verbs)
        if not valid:
            flags.append(f"VERB_ERROR: {msg}")

        valid, msg = check_measurability(outcome.text)
        if not valid:
            flags.append(f"MEASURABILITY_ERROR: {msg}")

        tags = extract_domain_tags(outcome.text)

        valid, msg = check_length(outcome.text)
        if not valid:
            flags.append(f"LENGTH_ERROR: {msg}")

        valid, msg = check_profanity(outcome.text)
        if not valid:
            flags.append(f"PROFANITY_ERROR: {msg}")

        valid, msg = check_bias(outcome.text)
        if not valid:
            flags.append(f"BIAS_WARNING: {msg}")

        valid, msg = check_academic_tone(outcome.text)
        if not valid:
            flags.append(f"TONE_WARNING: {msg}")

        outcome.flags       = flags
        outcome.domain_tags = tags
        processed.append(outcome)

    final, removed = deduplicate(processed)

    print(f"\n── Rules Engine ──")
    print(f"Input:  {len(outcomes)} | Output: {len(final)} | Removed: {len(removed)}")
    for o in final:
        status = "✓ CLEAN" if not o.flags else "⚠ FLAGGED"
        print(f"  {status} | '{o.text[:55]}'")
        if o.flags:
            for f in o.flags:
                print(f"    → {f}")

    return final