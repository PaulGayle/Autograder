# Autograder

A Streamlit-powered grading system that automatically evaluates Python assignments across multiple modules. It compares student programs to an instructor solution using behavior-based output matching and static code analysis.

🚀 Features

Automatic execution & comparison of student code against instructor solutions

Strict detection of syntax errors and infinite while True loops

AST-based analysis of structure, functions, variables, pseudocode, and CSV usage

Weighted grading rubrics for Modules 2–5

CSV grade sheet generation (e.g., M2_grades.csv)

Interactive visualizations for class performance

🧠 How It Works

Upload the solution file for a module.

Upload one or more student .py files.

The autograder:

Saves and parses each file

Checks for syntax errors / infinite loops

Compares student output to the solution using difflib

Analyzes program structure with the ast module

Calculates component scores based on module-specific criteria

Writes results to a CSV and displays them in Streamlit

Modules include:

M2 – Decision Structures

M3 – Loops

M4 – Functions

M5 – CSV / File Processing
