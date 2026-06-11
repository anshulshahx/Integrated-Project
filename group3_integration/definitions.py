"""
definitions.py
Group 3 fallback/override definitions for POs, PSOs, PEOs.
Set OVERRIDE_* = True to force these instead of Group 1's generated values.
"""

OVERRIDE_POS  = False
OVERRIDE_PSOS = False
OVERRIDE_PEOS = False

PO_DEFINITIONS = [
    {"id": "PO1",  "text": "Apply knowledge of mathematics, science and engineering fundamentals."},
    {"id": "PO2",  "text": "Identify, formulate and solve complex engineering problems."},
    {"id": "PO3",  "text": "Design solutions for complex engineering problems."},
    {"id": "PO4",  "text": "Conduct investigations of complex problems using research-based knowledge."},
    {"id": "PO5",  "text": "Use modern engineering and IT tools for complex engineering activities."},
    {"id": "PO6",  "text": "Understand the impact of engineering solutions in society and environment."},
    {"id": "PO7",  "text": "Apply reasoning to assess societal, health, safety and legal issues."},
    {"id": "PO8",  "text": "Apply ethical principles and commit to professional ethics."},
    {"id": "PO9",  "text": "Function effectively as an individual and in multidisciplinary teams."},
    {"id": "PO10", "text": "Communicate effectively on complex engineering activities."},
    {"id": "PO11", "text": "Manage projects and finances in multidisciplinary environments."},
    {"id": "PO12", "text": "Recognize the need for lifelong learning and professional development."},
]

PSO_DEFINITIONS = [
    {"id": "PSO1", "text": "Design and implement efficient algorithms and data structures."},
    {"id": "PSO2", "text": "Analyze and evaluate computer systems, networks and databases."},
    {"id": "PSO3", "text": "Apply software engineering principles to develop large-scale systems."},
]

PEO_DEFINITIONS = [
    {"id": "PEO1", "text": "Graduates will apply technical knowledge to solve real-world engineering problems."},
    {"id": "PEO2", "text": "Graduates will pursue higher studies and engage in research and development."},
    {"id": "PEO3", "text": "Graduates will demonstrate professional ethics and leadership in engineering."},
    {"id": "PEO4", "text": "Graduates will communicate effectively and contribute to society."},
    {"id": "PEO5", "text": "Graduates will engage in lifelong learning and adapt to new technologies."},
]

PO_IDS  = [p["id"] for p in PO_DEFINITIONS]
PSO_IDS = [p["id"] for p in PSO_DEFINITIONS]
PEO_IDS = [p["id"] for p in PEO_DEFINITIONS]