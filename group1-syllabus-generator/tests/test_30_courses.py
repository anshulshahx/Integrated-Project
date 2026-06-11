import sys
import os
import json
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.rules.engine import run_rules_engine, load_bloom_verbs
from app.schemas.models import OutcomeObject

bloom_verbs = load_bloom_verbs()

COURSES = [
    {"name":"Data Structures","bloom":["apply","analyze"],"domain":"cs"},
    {"name":"Algorithms","bloom":["analyze","evaluate"],"domain":"cs"},
    {"name":"Operating Systems","bloom":["understand","analyze"],"domain":"cs"},
    {"name":"Database Management","bloom":["apply","create"],"domain":"cs"},
    {"name":"Computer Networks","bloom":["analyze","evaluate"],"domain":"cs"},
    {"name":"Software Engineering","bloom":["apply","create"],"domain":"cs"},
    {"name":"Machine Learning","bloom":["apply","evaluate"],"domain":"cs"},
    {"name":"Artificial Intelligence","bloom":["analyze","create"],"domain":"cs"},
    {"name":"Web Development","bloom":["apply","create"],"domain":"cs"},
    {"name":"Cybersecurity","bloom":["analyze","evaluate"],"domain":"cs"},
    {"name":"Digital Electronics","bloom":["apply","analyze"],"domain":"electronics"},
    {"name":"Analog Circuits","bloom":["analyze","evaluate"],"domain":"electronics"},
    {"name":"Microprocessors","bloom":["apply","analyze"],"domain":"electronics"},
    {"name":"Embedded Systems","bloom":["apply","create"],"domain":"electronics"},
    {"name":"VLSI Design","bloom":["analyze","create"],"domain":"electronics"},
    {"name":"Signal Processing","bloom":["apply","analyze"],"domain":"electronics"},
    {"name":"Control Systems","bloom":["analyze","evaluate"],"domain":"electronics"},
    {"name":"Power Electronics","bloom":["apply","analyze"],"domain":"electronics"},
    {"name":"Communication Systems","bloom":["understand","analyze"],"domain":"electronics"},
    {"name":"IoT Systems","bloom":["apply","create"],"domain":"electronics"},
    {"name":"Engineering Mathematics","bloom":["apply","analyze"],"domain":"math"},
    {"name":"Probability and Statistics","bloom":["apply","evaluate"],"domain":"math"},
    {"name":"Linear Algebra","bloom":["apply","analyze"],"domain":"math"},
    {"name":"Numerical Methods","bloom":["apply","evaluate"],"domain":"math"},
    {"name":"Discrete Mathematics","bloom":["analyze","evaluate"],"domain":"math"},
    {"name":"Project Management","bloom":["apply","evaluate"],"domain":"management"},
    {"name":"Engineering Economics","bloom":["analyze","evaluate"],"domain":"management"},
    {"name":"Technical Communication","bloom":["apply","create"],"domain":"management"},
    {"name":"Professional Ethics","bloom":["evaluate","create"],"domain":"management"},
    {"name":"Innovation and Entrepreneurship","bloom":["evaluate","create"],"domain":"management"},
]

SAMPLE_OUTCOMES = {
    "Data Structures":[OutcomeObject(text="Apply binary search to find elements in sorted arrays efficiently",bloom_level="apply",assessment_suggestion="Coding",confidence_est=0.9),OutcomeObject(text="Analyze time and space complexity of sorting algorithms including quicksort",bloom_level="analyze",assessment_suggestion="Report",confidence_est=0.9),OutcomeObject(text="Design a hash table to store and retrieve student records efficiently",bloom_level="create",assessment_suggestion="Project",confidence_est=0.9)],
    "Algorithms":[OutcomeObject(text="Analyze the time complexity of divide and conquer algorithms systematically",bloom_level="analyze",assessment_suggestion="Problem set",confidence_est=0.9),OutcomeObject(text="Evaluate the efficiency of dynamic programming solutions for optimization problems",bloom_level="evaluate",assessment_suggestion="Exam",confidence_est=0.9),OutcomeObject(text="Apply greedy algorithms to solve graph traversal and shortest path problems",bloom_level="apply",assessment_suggestion="Assignment",confidence_est=0.9)],
    "Operating Systems":[OutcomeObject(text="Explain the process scheduling algorithms used in modern operating systems",bloom_level="understand",assessment_suggestion="Quiz",confidence_est=0.9),OutcomeObject(text="Analyze deadlock detection and prevention strategies in concurrent systems",bloom_level="analyze",assessment_suggestion="Case study",confidence_est=0.9),OutcomeObject(text="Compare different memory management techniques including paging and segmentation",bloom_level="analyze",assessment_suggestion="Report",confidence_est=0.9)],
    "Database Management":[OutcomeObject(text="Apply SQL queries to extract and manipulate data from relational databases",bloom_level="apply",assessment_suggestion="Lab",confidence_est=0.9),OutcomeObject(text="Design a normalized database schema for an enterprise management system",bloom_level="create",assessment_suggestion="Project",confidence_est=0.9),OutcomeObject(text="Evaluate transaction management and concurrency control mechanisms in databases",bloom_level="evaluate",assessment_suggestion="Exam",confidence_est=0.9)],
    "Computer Networks":[OutcomeObject(text="Analyze network packet transmission using TCP IP protocol stack layers",bloom_level="analyze",assessment_suggestion="Lab",confidence_est=0.9),OutcomeObject(text="Evaluate routing algorithms for optimal path selection in computer networks",bloom_level="evaluate",assessment_suggestion="Simulation",confidence_est=0.9),OutcomeObject(text="Design a subnet addressing scheme for an enterprise network infrastructure",bloom_level="create",assessment_suggestion="Project",confidence_est=0.9)],
    "Software Engineering":[OutcomeObject(text="Apply agile methodology to plan and execute a software development project",bloom_level="apply",assessment_suggestion="Sprint",confidence_est=0.9),OutcomeObject(text="Evaluate software quality using systematic testing and debugging strategies",bloom_level="evaluate",assessment_suggestion="Review",confidence_est=0.9),OutcomeObject(text="Design a system architecture document for a scalable web application",bloom_level="create",assessment_suggestion="Document",confidence_est=0.9)],
    "Machine Learning":[OutcomeObject(text="Implement a linear regression model to predict continuous output variables",bloom_level="apply",assessment_suggestion="Coding",confidence_est=0.9),OutcomeObject(text="Evaluate the accuracy of classification models using precision recall and F1 score",bloom_level="evaluate",assessment_suggestion="Report",confidence_est=0.9),OutcomeObject(text="Design a neural network architecture for image recognition tasks",bloom_level="create",assessment_suggestion="Project",confidence_est=0.9)],
    "Artificial Intelligence":[OutcomeObject(text="Analyze the performance of search algorithms in state space problem solving",bloom_level="analyze",assessment_suggestion="Assignment",confidence_est=0.9),OutcomeObject(text="Evaluate the effectiveness of various knowledge representation techniques",bloom_level="evaluate",assessment_suggestion="Exam",confidence_est=0.9),OutcomeObject(text="Design an expert system for medical diagnosis using rule based reasoning",bloom_level="create",assessment_suggestion="Project",confidence_est=0.9)],
    "Web Development":[OutcomeObject(text="Apply HTML CSS and JavaScript to build responsive and accessible web pages",bloom_level="apply",assessment_suggestion="Lab",confidence_est=0.9),OutcomeObject(text="Implement RESTful API endpoints using Node.js and Express framework",bloom_level="apply",assessment_suggestion="Coding",confidence_est=0.9),OutcomeObject(text="Design a full stack web application with authentication and database integration",bloom_level="create",assessment_suggestion="Project",confidence_est=0.9)],
    "Cybersecurity":[OutcomeObject(text="Analyze common network vulnerabilities and attack vectors in enterprise systems",bloom_level="analyze",assessment_suggestion="Case study",confidence_est=0.9),OutcomeObject(text="Evaluate cryptographic algorithms for securing data transmission and storage",bloom_level="evaluate",assessment_suggestion="Report",confidence_est=0.9),OutcomeObject(text="Design a security policy framework for protecting organizational information assets",bloom_level="create",assessment_suggestion="Project",confidence_est=0.9)],
    "Digital Electronics":[OutcomeObject(text="Analyze the behavior of logic gates in combinational circuit design problems",bloom_level="analyze",assessment_suggestion="Lab",confidence_est=0.9),OutcomeObject(text="Design a sequential circuit using flip flops and state diagram analysis",bloom_level="create",assessment_suggestion="Project",confidence_est=0.9),OutcomeObject(text="Calculate voltage and current in basic transistor amplifier circuit configurations",bloom_level="apply",assessment_suggestion="Test",confidence_est=0.9)],
    "Analog Circuits":[OutcomeObject(text="Analyze the frequency response of operational amplifier based filter circuits",bloom_level="analyze",assessment_suggestion="Lab",confidence_est=0.9),OutcomeObject(text="Evaluate the performance characteristics of BJT and MOSFET amplifier circuits",bloom_level="evaluate",assessment_suggestion="Report",confidence_est=0.9),OutcomeObject(text="Design a voltage regulator circuit for a given load specification requirement",bloom_level="create",assessment_suggestion="Project",confidence_est=0.9)],
    "Microprocessors":[OutcomeObject(text="Apply assembly language programming to control hardware peripherals efficiently",bloom_level="apply",assessment_suggestion="Lab",confidence_est=0.9),OutcomeObject(text="Analyze the instruction execution cycle of 8085 and 8086 microprocessors",bloom_level="analyze",assessment_suggestion="Exam",confidence_est=0.9),OutcomeObject(text="Design an interrupt driven system for real time data acquisition applications",bloom_level="create",assessment_suggestion="Project",confidence_est=0.9)],
    "Embedded Systems":[OutcomeObject(text="Implement firmware for microcontroller based sensor data acquisition systems",bloom_level="apply",assessment_suggestion="Lab",confidence_est=0.9),OutcomeObject(text="Analyze real time operating system scheduling for embedded application requirements",bloom_level="analyze",assessment_suggestion="Case study",confidence_est=0.9),OutcomeObject(text="Design a low power embedded system for IoT environmental monitoring applications",bloom_level="create",assessment_suggestion="Project",confidence_est=0.9)],
    "VLSI Design":[OutcomeObject(text="Analyze CMOS logic gate design for minimizing power consumption in circuits",bloom_level="analyze",assessment_suggestion="Simulation",confidence_est=0.9),OutcomeObject(text="Design a digital circuit layout using standard cell library design methodology",bloom_level="create",assessment_suggestion="Project",confidence_est=0.9),OutcomeObject(text="Evaluate timing constraints and setup hold violations in synchronous digital designs",bloom_level="evaluate",assessment_suggestion="Report",confidence_est=0.9)],
    "Signal Processing":[OutcomeObject(text="Apply Fourier transform to analyze frequency components of digital signals",bloom_level="apply",assessment_suggestion="Lab",confidence_est=0.9),OutcomeObject(text="Design FIR and IIR digital filters for audio signal processing applications",bloom_level="create",assessment_suggestion="Project",confidence_est=0.9),OutcomeObject(text="Analyze sampling and quantization effects on digital signal reconstruction quality",bloom_level="analyze",assessment_suggestion="Report",confidence_est=0.9)],
    "Control Systems":[OutcomeObject(text="Analyze stability of closed loop control systems using Bode plot techniques",bloom_level="analyze",assessment_suggestion="Assignment",confidence_est=0.9),OutcomeObject(text="Design a PID controller for a temperature regulation industrial control system",bloom_level="create",assessment_suggestion="Simulation",confidence_est=0.9),OutcomeObject(text="Evaluate the transient and steady state response of second order control systems",bloom_level="evaluate",assessment_suggestion="Lab",confidence_est=0.9)],
    "Power Electronics":[OutcomeObject(text="Analyze the operation of DC to DC converter circuits for voltage regulation",bloom_level="analyze",assessment_suggestion="Lab",confidence_est=0.9),OutcomeObject(text="Design a three phase inverter circuit for variable frequency drive applications",bloom_level="create",assessment_suggestion="Project",confidence_est=0.9),OutcomeObject(text="Calculate efficiency and power loss in switching power supply converter circuits",bloom_level="apply",assessment_suggestion="Assignment",confidence_est=0.9)],
    "Communication Systems":[OutcomeObject(text="Explain the principles of amplitude frequency and phase modulation techniques",bloom_level="understand",assessment_suggestion="Quiz",confidence_est=0.9),OutcomeObject(text="Analyze bit error rate performance of digital modulation schemes in AWGN channels",bloom_level="analyze",assessment_suggestion="Report",confidence_est=0.9),OutcomeObject(text="Compare FDMA TDMA and CDMA multiple access techniques for wireless communications",bloom_level="analyze",assessment_suggestion="Assignment",confidence_est=0.9)],
    "IoT Systems":[OutcomeObject(text="Implement an IoT sensor network using MQTT protocol for data communication",bloom_level="apply",assessment_suggestion="Lab",confidence_est=0.9),OutcomeObject(text="Design a cloud connected IoT system for smart home automation applications",bloom_level="create",assessment_suggestion="Project",confidence_est=0.9),OutcomeObject(text="Evaluate security vulnerabilities in IoT devices and propose mitigation strategies",bloom_level="evaluate",assessment_suggestion="Report",confidence_est=0.9)],
    "Engineering Mathematics":[OutcomeObject(text="Solve differential equations using Laplace transform techniques and methods",bloom_level="apply",assessment_suggestion="Exam",confidence_est=0.9),OutcomeObject(text="Compute eigenvalues and eigenvectors of matrices for engineering applications",bloom_level="apply",assessment_suggestion="Problem set",confidence_est=0.9),OutcomeObject(text="Analyze Fourier series representations of periodic functions in signal processing",bloom_level="analyze",assessment_suggestion="Assignment",confidence_est=0.9)],
    "Probability and Statistics":[OutcomeObject(text="Apply probability distributions to model and analyze engineering system failures",bloom_level="apply",assessment_suggestion="Problem set",confidence_est=0.9),OutcomeObject(text="Evaluate hypothesis testing results for quality control in manufacturing processes",bloom_level="evaluate",assessment_suggestion="Case study",confidence_est=0.9),OutcomeObject(text="Analyze regression models for predicting engineering system performance metrics",bloom_level="analyze",assessment_suggestion="Project",confidence_est=0.9)],
    "Linear Algebra":[OutcomeObject(text="Apply matrix operations to solve systems of linear equations in engineering problems",bloom_level="apply",assessment_suggestion="Assignment",confidence_est=0.9),OutcomeObject(text="Analyze vector spaces and linear transformations in multi dimensional data analysis",bloom_level="analyze",assessment_suggestion="Exam",confidence_est=0.9),OutcomeObject(text="Compute singular value decomposition for data compression and dimensionality reduction",bloom_level="apply",assessment_suggestion="Project",confidence_est=0.9)],
    "Numerical Methods":[OutcomeObject(text="Apply numerical integration methods to approximate definite integrals accurately",bloom_level="apply",assessment_suggestion="Lab",confidence_est=0.9),OutcomeObject(text="Evaluate the accuracy and convergence of iterative numerical solution methods",bloom_level="evaluate",assessment_suggestion="Report",confidence_est=0.9),OutcomeObject(text="Implement numerical algorithms for solving ordinary differential equations computationally",bloom_level="apply",assessment_suggestion="Coding",confidence_est=0.9)],
    "Discrete Mathematics":[OutcomeObject(text="Analyze graph theory concepts including trees paths and connectivity in networks",bloom_level="analyze",assessment_suggestion="Problem set",confidence_est=0.9),OutcomeObject(text="Evaluate logical propositions and construct formal proofs using predicate calculus",bloom_level="evaluate",assessment_suggestion="Exam",confidence_est=0.9),OutcomeObject(text="Apply combinatorial counting techniques to solve probability and arrangement problems",bloom_level="apply",assessment_suggestion="Assignment",confidence_est=0.9)],
    "Project Management":[OutcomeObject(text="Apply project scheduling techniques using Gantt charts and critical path method",bloom_level="apply",assessment_suggestion="Assignment",confidence_est=0.9),OutcomeObject(text="Evaluate risk assessment strategies for managing engineering project uncertainties",bloom_level="evaluate",assessment_suggestion="Case study",confidence_est=0.9),OutcomeObject(text="Design a project management plan including scope time cost and quality baselines",bloom_level="create",assessment_suggestion="Project",confidence_est=0.9)],
    "Engineering Economics":[OutcomeObject(text="Apply net present value analysis to evaluate engineering investment decisions",bloom_level="apply",assessment_suggestion="Problem set",confidence_est=0.9),OutcomeObject(text="Analyze cost benefit ratios for comparing alternative engineering project options",bloom_level="analyze",assessment_suggestion="Case study",confidence_est=0.9),OutcomeObject(text="Evaluate depreciation methods for engineering asset management and tax calculations",bloom_level="evaluate",assessment_suggestion="Assignment",confidence_est=0.9)],
    "Technical Communication":[OutcomeObject(text="Apply technical writing principles to produce clear engineering reports and documents",bloom_level="apply",assessment_suggestion="Report",confidence_est=0.9),OutcomeObject(text="Design a professional presentation structure for communicating complex engineering findings",bloom_level="create",assessment_suggestion="Presentation",confidence_est=0.9),OutcomeObject(text="Compose technical proposals and specifications following industry standard documentation",bloom_level="create",assessment_suggestion="Proposal",confidence_est=0.9)],
    "Professional Ethics":[OutcomeObject(text="Evaluate ethical dilemmas faced by engineers using established ethical frameworks",bloom_level="evaluate",assessment_suggestion="Case study",confidence_est=0.9),OutcomeObject(text="Analyze the social and environmental impact of engineering decisions on communities",bloom_level="analyze",assessment_suggestion="Report",confidence_est=0.9),OutcomeObject(text="Justify professional responsibility decisions using engineering code of ethics principles",bloom_level="evaluate",assessment_suggestion="Essay",confidence_est=0.9)],
    "Innovation and Entrepreneurship":[OutcomeObject(text="Evaluate startup business models for technical feasibility and market potential",bloom_level="evaluate",assessment_suggestion="Pitch",confidence_est=0.9),OutcomeObject(text="Design an innovative product concept addressing a real world engineering problem",bloom_level="create",assessment_suggestion="Prototype",confidence_est=0.9),OutcomeObject(text="Analyze successful technology entrepreneurship cases for key success factors",bloom_level="analyze",assessment_suggestion="Case study",confidence_est=0.9)],
}

def print_result(test_name, passed):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status} — {test_name}")
    return passed

if __name__ == "__main__":
    print("═"*60)
    print("  GROUP 1 — 30 COURSE QA BENCHMARK")
    print("═"*60)
    all_results  = []
    course_report= []
    start        = time.time()

    for i, course in enumerate(COURSES, 1):
        name     = course["name"]
        outcomes = SAMPLE_OUTCOMES.get(name, [])
        if not outcomes:
            continue
        print(f"\n[{i:02d}/30] {name}")
        processed     = run_rules_engine(outcomes)
        all_valid_verbs= True
        no_length_err  = True
        clean_count    = 0
        for o in processed:
            if any("VERB_ERROR" in f for f in o.flags):
                all_valid_verbs = False
            if any("LENGTH_ERROR" in f for f in o.flags):
                no_length_err = False
            if not o.flags:
                clean_count += 1
        has_tags = any(len(o.domain_tags) > 0 for o in processed)
        passed   = all_valid_verbs and no_length_err
        all_results.append(passed)
        status = "✅" if passed else "❌"
        print(f"  {status} Clean:{clean_count}/{len(processed)} Tags:{has_tags} VerbOK:{all_valid_verbs}")
        course_report.append({"course":name,"domain":course["domain"],"passed":passed})

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/benchmark_30_courses.json","w") as f:
        json.dump({"benchmark":"30 Course QA","total":len(course_report),"passed":sum(r["passed"] for r in course_report),"results":course_report},f,indent=2)

    elapsed = time.time() - start
    passed  = sum(all_results)
    total   = len(all_results)
    print(f"\n{'═'*60}")
    print(f"  BENCHMARK: {passed}/{total} courses passed")
    print(f"  Time: {elapsed:.1f}s")
    if passed == total:
        print("  🎉 ALL 30 COURSES PASSED!")
    else:
        print(f"  ⚠ {total-passed} failed")
    print("═"*60)