# autograder_functions.py
# All helper functions and grading logic for the autograder (static analysis only).

# autograder_functions.py
# Fixed version: NO early returns & better while True detection


import ast
import csv
import subprocess
import sys
import difflib
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List

# -------------------------
# Criteria weights
# -------------------------
M2_CRITERIA = {"input": 15, "decision_structure": 25, "output": 45, "pseudocode": 10, "variables": 5}
M3_CRITERIA = {"input": 15, "structure": 25, "output": 45, "pseudocode": 10, "variables": 5}
M4_CRITERIA = {"structure": 20, "output": 50, "functions": 10, "pseudocode": 5, "variables": 5}
M5_CRITERIA = {"structure": 20, "output": 40, "functions": 10, "csv": 15, "pseudocode": 5, "variables": 10}

@dataclass
class GradeResult:
    components: Dict[str, float]
    total: float
    notes: Dict[str, str]

# ======================================================
# EXE-SAFE PROGRAM EXECUTION
# ======================================================
def get_python_interpreter():
    """Find a valid Python interpreter, even inside an EXE."""
    if getattr(sys, "frozen", False):
        # Running as EXE
        for cmd in ["python", "python3", "py"]:
            try:
                subprocess.run([cmd, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return cmd
            except Exception:
                pass
        return None
    else:
        return sys.executable

def run_student_program(path_to_file: str, program_input: str = "", timeout: int = 5):
    python_exec = get_python_interpreter()
    if python_exec is None:
        return "", "ERROR: No valid Python interpreter available.", -2
    try:
        proc = subprocess.Popen(
            [python_exec, path_to_file],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate(program_input, timeout=timeout)
        return stdout.strip(), stderr.strip(), proc.returncode
    except subprocess.TimeoutExpired:
        return "", f"TIMEOUT after {timeout}s", -1
    except Exception as e:
        return "", f"ERROR: {e}", -2

# -----------------------------
# Static analysis helpers
# -----------------------------
def similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a.strip(), b.strip()).ratio() * 100

def contains_illegal_loop(src: str) -> bool:
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.While) and isinstance(node.test, ast.Constant) and node.test.value is True:
            return True
    return False

def has_disallowed_constructs_or_syntax_error(src: str, filename: str = "") -> bool:
    try:
        ast.parse(src)
        return False
    except SyntaxError:
        return True

def safe_parse(src: str):
    try:
        return ast.parse(src)
    except:
        return None

def count_comment_lines(src: str) -> int:
    return sum(1 for line in src.splitlines() if line.strip().startswith("#"))

# -----------------------------
# Behavior-based grading helper
# -----------------------------
def grade_behavior(student_file: str, solution_file: str, test_cases: List[Dict[str, str]], criteria: Dict[str, float]) -> GradeResult:
    src = Path(student_file).read_text()

    # STRICT RULES
    if contains_illegal_loop(src):
        return GradeResult({k: 1 for k in criteria}, 1, {"reason": "Illegal 'while True' loop"})
    if has_disallowed_constructs_or_syntax_error(src):
        return GradeResult({k: 1 for k in criteria}, 1, {"reason": "Syntax error"})

    components = {}
    input_scores = []
    output_scores = []

    for case in test_cases:
        stu_out, stu_err, _ = run_student_program(student_file, case["input"])
        sol_out, _, _ = run_student_program(solution_file, case["input"])

        # Input handled correctly if no runtime error
        input_scores.append(0 if stu_err else 100)

        # Compare outputs
        output_scores.append(similarity(stu_out, sol_out))

    if "input" in criteria:
        components["input"] = sum(input_scores) / len(input_scores) if input_scores else 0
    if "output" in criteria:
        components["output"] = sum(output_scores) / len(output_scores) if output_scores else 0

    # AST-based components
    tree = safe_parse(src)
    if "structure" in criteria:
        if tree:
            loops = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While)))
            ifs = sum(1 for n in ast.walk(tree) if isinstance(n, ast.If))
            components["structure"] = min((loops + ifs) * 40, 100)
        else:
            components["structure"] = 0

    if "decision_structure" in criteria:
        components["decision_structure"] = 100 if tree and any(isinstance(n, ast.If) for n in ast.walk(tree)) else 0

    if "functions" in criteria:
        if tree:
            functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            components["functions"] = 100 if functions else 0
        else:
            components["functions"] = 0

    if "pseudocode" in criteria:
        components["pseudocode"] = min(count_comment_lines(src) * 15, 100)

    if "variables" in criteria:
        components["variables"] = 100 if "=" in src else 0

    if "csv" in criteria:
        components["csv"] = 100 if ".csv" in src else 0

    total = sum(components[k] * (criteria[k] / 100.0) for k in criteria)
    return GradeResult(components, round(total, 2), {})

# -----------------------------
# Module-specific grading
# -----------------------------
def grade_module2(student_file: str, solution_file: str) -> GradeResult:
    test_cases = [{"input": "5\n", "expected_output": ""}, {"input": "10\n", "expected_output": ""}]
    return grade_behavior(student_file, solution_file, test_cases, M2_CRITERIA)

def grade_module_generic(student_file: str, solution_file: str,
                         expected_output: str, sample_input: str,
                         criteria: Dict[str, float], module: str) -> GradeResult:
    test_cases = [{"input": sample_input, "expected_output": expected_output}]
    return grade_behavior(student_file, solution_file, test_cases, criteria)

# -----------------------------
# CSV Writer
# -----------------------------
def write_csv_for_module(filename: str, fieldnames: list, row: dict):
    file_exists = Path(filename).exists()
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)