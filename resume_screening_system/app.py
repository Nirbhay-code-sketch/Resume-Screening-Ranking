#!/usr/bin/env python3
"""
app.py
------
A simple Flask web interface for the Resume Screening & Ranking System.

Run with:
    python app.py

Then open http://127.0.0.1:5000 in your browser.

Features:
- Paste a job description or pick one of the bundled sample JDs
- Upload your own resume .txt files, or use the bundled sample resumes
- See a ranked, explainable results table + a comparison chart in the browser
- Download the results as CSV
"""

import os
import io
import base64
import uuid

from flask import Flask, render_template, request, send_file, session

from src.preprocessing import load_text_file
from src.scorer import compute_final_scores
from src.report import export_csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_JD_DIR = os.path.join(BASE_DIR, "data", "job_descriptions")
SAMPLE_RESUME_DIR = os.path.join(BASE_DIR, "data", "resumes")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = "resume-screening-demo-key"

# In-memory store for the last generated report so /download works
# without needing a database for this small demo app.
LAST_REPORT = {"report": None, "csv_path": None}


def get_sample_jds():
    files = sorted(f for f in os.listdir(SAMPLE_JD_DIR) if f.endswith(".txt"))
    return [(f, f.replace(".txt", "").replace("_", " ").title()) for f in files]


def make_chart_base64(report):
    """Render the ranking chart to a base64 PNG string (no disk file needed)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = [row["name"] for row in report]
    scores = [row["final_score"] for row in report]

    fig, ax = plt.subplots(figsize=(8, max(3, 0.55 * len(names))))
    bars = ax.barh(names[::-1], scores[::-1], color="#4C72B0")
    ax.set_xlabel("Overall Fit Score (%)")
    ax.set_title("Candidate Ranking")
    ax.set_xlim(0, 100)
    for bar, score in zip(bars, scores[::-1]):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                 f"{score}%", va="center", fontsize=9)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", sample_jds=get_sample_jds())


@app.route("/screen", methods=["POST"])
def screen():
    # ---- 1. Get the job description text ----
    jd_text = ""
    jd_source_name = "Custom Job Description"

    jd_choice = request.form.get("jd_choice")
    if jd_choice == "sample":
        sample_file = request.form.get("sample_jd")
        jd_path = os.path.join(SAMPLE_JD_DIR, sample_file)
        jd_text = load_text_file(jd_path)
        jd_source_name = sample_file.replace(".txt", "").replace("_", " ").title()
    elif jd_choice == "paste":
        jd_text = request.form.get("jd_text", "").strip()
    elif jd_choice == "upload":
        jd_file = request.files.get("jd_file")
        if jd_file and jd_file.filename:
            jd_text = jd_file.read().decode("utf-8", errors="ignore")
            jd_source_name = jd_file.filename

    if not jd_text.strip():
        return render_template("index.html", sample_jds=get_sample_jds(),
                                error="Please provide a job description (paste, upload, or pick a sample).")

    # ---- 2. Get the resumes ----
    resumes = {}
    resume_choice = request.form.get("resume_choice")

    if resume_choice == "sample":
        for fname in sorted(os.listdir(SAMPLE_RESUME_DIR)):
            if fname.endswith(".txt"):
                name = fname.replace(".txt", "").replace("_", " ").title()
                resumes[name] = load_text_file(os.path.join(SAMPLE_RESUME_DIR, fname))
    elif resume_choice == "upload":
        files = request.files.getlist("resume_files")
        for f in files:
            if f and f.filename:
                name = os.path.splitext(f.filename)[0].replace("_", " ").title()
                resumes[name] = f.read().decode("utf-8", errors="ignore")

    if not resumes:
        return render_template("index.html", sample_jds=get_sample_jds(),
                                error="Please upload at least one resume (.txt) or use the sample resumes.")

    # ---- 3. Score & rank ----
    report = compute_final_scores(jd_text, resumes)
    chart_b64 = make_chart_base64(report)

    # ---- 4. Save CSV for download ----
    run_id = uuid.uuid4().hex[:8]
    csv_path = os.path.join(OUTPUT_DIR, f"results_{run_id}.csv")
    export_csv(report, csv_path)
    LAST_REPORT["report"] = report
    LAST_REPORT["csv_path"] = csv_path

    return render_template(
        "results.html",
        report=report,
        chart_b64=chart_b64,
        jd_source_name=jd_source_name,
        num_resumes=len(resumes),
        run_id=run_id,
    )


@app.route("/download/<run_id>")
def download(run_id):
    csv_path = os.path.join(OUTPUT_DIR, f"results_{run_id}.csv")
    if os.path.exists(csv_path):
        return send_file(csv_path, as_attachment=True, download_name="resume_screening_results.csv")
    return "File not found. Please re-run the screening.", 404


if __name__ == "__main__":
    print("\nResume Screening System is running!")
    print("Open this link in your browser: http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)
