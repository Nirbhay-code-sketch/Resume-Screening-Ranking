#!/usr/bin/env python3
"""
main.py
-------
Command-line entry point for the Resume Screening & Ranking System.

Usage:
    python main.py --jd data/job_descriptions/data_scientist.txt \
                    --resumes data/resumes \
                    --out outputs

If --jd / --resumes are omitted, defaults under data/ are used so you
can just run `python main.py` to see a full demo.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.preprocessing import load_text_file
from src.scorer import compute_final_scores
from src.report import print_report, export_csv, export_chart
from src.html_report import generate_html_report, open_in_browser


def load_resumes(resumes_dir: str) -> dict:
    resumes = {}
    for fname in sorted(os.listdir(resumes_dir)):
        if fname.lower().endswith(".txt"):
            path = os.path.join(resumes_dir, fname)
            name = os.path.splitext(fname)[0].replace("_", " ").title()
            resumes[name] = load_text_file(path)
    return resumes


def main():
    parser = argparse.ArgumentParser(description="Resume Screening & Ranking System")
    parser.add_argument(
        "--jd", default="data/job_descriptions/data_scientist.txt",
        help="Path to job description text file",
    )
    parser.add_argument(
        "--resumes", default="data/resumes",
        help="Path to a directory of resume .txt files",
    )
    parser.add_argument(
        "--out", default="outputs",
        help="Directory to write results.csv and ranking_chart.png",
    )
    args = parser.parse_args()

    if not os.path.exists(args.jd):
        print(f"Job description file not found: {args.jd}")
        sys.exit(1)
    if not os.path.isdir(args.resumes):
        print(f"Resumes directory not found: {args.resumes}")
        sys.exit(1)

    job_description = load_text_file(args.jd)
    resumes = load_resumes(args.resumes)

    if not resumes:
        print(f"No .txt resumes found in {args.resumes}")
        sys.exit(1)

    report = compute_final_scores(job_description, resumes)

    print_report(report)

    csv_path = export_csv(report, os.path.join(args.out, "results.csv"))
    chart_path = export_chart(report, os.path.join(args.out, "ranking_chart.png"))

    print(f"\nSaved ranked results to: {csv_path}")
    print(f"Saved comparison chart to: {chart_path}")


if __name__ == "__main__":
    main()
