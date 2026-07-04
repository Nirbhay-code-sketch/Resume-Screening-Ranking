"""
report.py
---------
Turns the raw scoring output into plain-English explanations that a
non-technical recruiter or hiring manager can read directly, plus
helpers to export results as CSV and a comparison chart.
"""

import csv
import os


def explain_candidate(row: dict) -> str:
    """Build a short natural-language explanation for one candidate."""
    name = row["name"]
    final = row["final_score"]
    sim = row["similarity_score"]
    skl = row["skill_score"]
    matched = row["matched_skills"]
    missing = row["missing_skills"]

    lines = [f"Candidate: {name}  |  Rank #{row['rank']}  |  Overall Fit: {final}%"]
    lines.append(
        f"  - Overall text/context match with job description: {sim}%"
    )
    lines.append(
        f"  - Required-skill coverage: {skl}% "
        f"({len(matched)}/{len(matched) + len(missing)} required skills found)"
    )

    if matched:
        lines.append(f"  - Matched skills: {', '.join(matched)}")
    else:
        lines.append("  - Matched skills: none found")

    if missing:
        lines.append(f"  - Missing / gap skills: {', '.join(missing)}")
    else:
        lines.append("  - Missing / gap skills: none -- full skill coverage!")

    return "\n".join(lines)


def print_report(report: list):
    print("=" * 70)
    print("RESUME SCREENING & RANKING REPORT")
    print("=" * 70)
    for row in report:
        print()
        print(explain_candidate(row))
    print()
    print("=" * 70)


def export_csv(report: list, out_path: str):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fieldnames = [
        "rank", "name", "final_score", "similarity_score", "skill_score",
        "matched_skills", "missing_skills",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in report:
            writer.writerow({
                "rank": row["rank"],
                "name": row["name"],
                "final_score": row["final_score"],
                "similarity_score": row["similarity_score"],
                "skill_score": row["skill_score"],
                "matched_skills": "; ".join(row["matched_skills"]),
                "missing_skills": "; ".join(row["missing_skills"]),
            })
    return out_path


def export_chart(report: list, out_path: str):
    """Bar chart comparing candidates' final scores. Requires matplotlib."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    names = [row["name"] for row in report]
    scores = [row["final_score"] for row in report]

    plt.figure(figsize=(9, 5))
    bars = plt.barh(names[::-1], scores[::-1], color="#4C72B0")
    plt.xlabel("Overall Fit Score (%)")
    plt.title("Candidate Ranking - Resume Screening System")
    plt.xlim(0, 100)

    for bar, score in zip(bars, scores[::-1]):
        plt.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                  f"{score}%", va="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path
