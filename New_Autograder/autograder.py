import streamlit as st
import os
from pathlib import Path
import ast
import pandas as pd
import altair as alt

from autograder_functions import (
    contains_illegal_loop,
    has_disallowed_constructs_or_syntax_error,
    grade_module2,
    grade_module_generic,
    M2_CRITERIA,
    M3_CRITERIA,
    M4_CRITERIA,
    M5_CRITERIA,
    write_csv_for_module
)

# ---------------------------------------------------------
# Save uploaded file to a temporary directory
# ---------------------------------------------------------
def save_uploaded_file(uploaded_file):
    temp_path = Path("temp_uploads")
    temp_path.mkdir(exist_ok=True)
    file_path = temp_path / uploaded_file.name
    file_path.write_bytes(uploaded_file.read())
    return str(file_path)


# ---------------------------------------------------------
# Unified grading workflow for all modules
# ---------------------------------------------------------
def grade_multiple_files(module_name, criteria, grade_function, solution_file, student_files):

    st.write(f"### Grading Results for {module_name}")

    # Save instructor solution
    solution_path = save_uploaded_file(solution_file)
    solution_file_path = Path(solution_path)

    if not solution_file_path.exists():
        st.error(f"❌ Internal Error: Solution file missing.\nPath tried: {solution_file_path}")
        st.stop()

    solution_src = solution_file_path.read_text()

    # Extract required functions from solution
    try:
        solution_funcs = [
            node.name for node in ast.walk(ast.parse(solution_src))
            if isinstance(node, ast.FunctionDef)
        ]
    except:
        solution_funcs = []

    results_table = []
    csv_filename = f"{module_name}_grades.csv"

    warnings = {
        "illegal_loops": [],
        "syntax_errors": [],
        "missing_functions": []
    }

    # ---------------------------------------------------------
    # PROCESS EACH STUDENT FILE
    # ---------------------------------------------------------
    for student_file in student_files:
        student_path = save_uploaded_file(student_file)
        src = Path(student_path).read_text()

        # Strict rule: illegal loop
        if contains_illegal_loop(src):
            warnings["illegal_loops"].append(
                f"⚠️ '{student_file.name}' contains illegal 'while True' — forced grade = 1"
            )

        # Strict rule: syntax error
        if has_disallowed_constructs_or_syntax_error(src, student_file.name):
            warnings["syntax_errors"].append(
                f"❌ Syntax error in '{student_file.name}' — forced grade = 1"
            )

        # Missing required functions
        try:
            student_funcs = [
                node.name for node in ast.walk(ast.parse(src))
                if isinstance(node, ast.FunctionDef)
            ]
            missing = [f for f in solution_funcs if f not in student_funcs]
            if missing:
                warnings["missing_functions"].append(
                    f"📌 '{student_file.name}' missing required functions: {missing}"
                )
        except:
            warnings["missing_functions"].append(
                f"📌 Unable to analyze functions in '{student_file.name}'"
            )

        # ---------------------------------------------------------
        # RUN GRADING
        # ---------------------------------------------------------
        if module_name == "M2":
            result = grade_function(student_path, solution_path)
        else:
            # sample_input & expected_output not needed with behavior grading
            result = grade_function(student_path, solution_path, "", "", criteria, module_name)

        # ---------------------------------------------------------
        # CSV row building
        # ---------------------------------------------------------
        row = {
            "file_name": student_file.name,
            "total": result.total,
            "reason": result.notes.get("reason", "")
        }

        for key in criteria.keys():
            row[key] = result.components.get(key, 0)

        write_csv_for_module(
            csv_filename,
            ["file_name"] + list(criteria.keys()) + ["total", "reason"],
            row
        )

        results_table.append(row)

    # ---------------------------------------------------------
    # SHOW WARNINGS
    # ---------------------------------------------------------
    if any(warnings.values()):
        st.error("### ⚠️ Issues Detected")

        if warnings["illegal_loops"]:
            st.subheader("🌀 Illegal Infinite Loops")
            for msg in warnings["illegal_loops"]:
                st.write(msg)

        if warnings["syntax_errors"]:
            st.subheader("❌ Syntax Errors")
            for msg in warnings["syntax_errors"]:
                st.write(msg)

        if warnings["missing_functions"]:
            st.subheader("📌 Missing Required Functions")
            for msg in warnings["missing_functions"]:
                st.write(msg)

    # ---------------------------------------------------------
    # SHOW RESULTS TABLE
    # ---------------------------------------------------------
    st.success("### Grading Complete!")
    st.dataframe(results_table)

    # ---------------------------------------------------------
    # CHART VISUALIZATIONS
    # ---------------------------------------------------------
    df = pd.DataFrame(results_table)

    if not df.empty:
        st.subheader("📊 Grade Visualizations")

        # -----------------------------
        # Total Score Bar Chart
        # -----------------------------
        total_chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("file_name:N", title="Student File", sort="-y"),
                y=alt.Y("total:Q", title="Total Score"),
                tooltip=["file_name", "total"]
            )
            .properties(height=350, title="Total Score per Student")
        )

        st.altair_chart(total_chart, use_container_width=True)

        # -----------------------------
        # Component Stacked Bar Chart
        # -----------------------------
        comp_cols = [col for col in df.columns if col not in ["file_name", "total", "reason"]]

        df_melted = df.melt(id_vars="file_name",
                            value_vars=comp_cols,
                            var_name="component",
                            value_name="score")

        stacked_chart = (
            alt.Chart(df_melted)
            .mark_bar()
            .encode(
                x=alt.X("file_name:N", title="Student File"),
                y=alt.Y("score:Q", title="Score"),
                color=alt.Color("component:N", title="Component"),
                tooltip=["file_name", "component", "score"]
            )
            .properties(height=350, title="Component Scores per Student")
        )

        st.altair_chart(stacked_chart, use_container_width=True)

        # -----------------------------
        # Pie Chart — Average Component Performance
        # -----------------------------
        avg_scores = df[comp_cols].mean().reset_index()
        avg_scores.columns = ["component", "average"]

        pie_chart = (
            alt.Chart(avg_scores)
            .mark_arc()
            .encode(
                theta="average:Q",
                color="component:N",
                tooltip=["component", "average"]
            )
            .properties(title="Average Score by Component")
        )

        st.altair_chart(pie_chart, use_container_width=True)


# ---------------------------------------------------------
# STREAMLIT UI
# ---------------------------------------------------------
st.set_page_config(page_title="Python Autograder", layout="centered")
st.title("📘 Python Autograder System")
st.write("Upload files for each module to automatically grade student assignments with behavior-based comparison and visual analytics.")

page = st.sidebar.radio(
    "Select Module",
    ["Home", "Module 2", "Module 3", "Module 4", "Module 5"]
)

# -------------------------------
# HOME PAGE
# -------------------------------
if page == "Home":
    st.header("Welcome to Your Autograder")
    st.write("""
    This system provides:
    - Behavior-based grading using difflib
    - Strict detection of infinite loops & syntax errors
    - Function signature checking
    - Fully weighted criteria scoring
    - CSV grade sheet generation
    - **Interactive charts & analytics**
    """)

# -------------------------------
# MODULE PAGES
# -------------------------------
elif page == "Module 2":
    st.header("Module 2 – Decision Structures")
    sol = st.file_uploader("Upload Solution File", type=["py"])
    stu = st.file_uploader("Upload Student Files", type=["py"], accept_multiple_files=True)
    if sol and stu and st.button("Grade Files"):
        grade_multiple_files("M2", M2_CRITERIA, grade_module2, sol, stu)

elif page == "Module 3":
    st.header("Module 3 – Loops")
    sol = st.file_uploader("Upload Solution File", type=["py"])
    stu = st.file_uploader("Upload Student Files", type=["py"], accept_multiple_files=True)
    if sol and stu and st.button("Grade Files"):
        grade_multiple_files("M3", M3_CRITERIA, grade_module_generic, sol, stu)

elif page == "Module 4":
    st.header("Module 4 – Functions")
    sol = st.file_uploader("Upload Solution File", type=["py"])
    stu = st.file_uploader("Upload Student Files", type=["py"], accept_multiple_files=True)
    if sol and stu and st.button("Grade Files"):
        grade_multiple_files("M4", M4_CRITERIA, grade_module_generic, sol, stu)

elif page == "Module 5":
    st.header("Module 5 – Reading Files / CSV Processing")
    sol = st.file_uploader("Upload Solution File", type=["py"])
    stu = st.file_uploader("Upload Student Files", type=["py"], accept_multiple_files=True)
    if sol and stu and st.button("Grade Files"):
        grade_multiple_files("M5", M5_CRITERIA, grade_module_generic, sol, stu)

def shutdown():
    print("Exiting the application..")
    os.exit(0)
