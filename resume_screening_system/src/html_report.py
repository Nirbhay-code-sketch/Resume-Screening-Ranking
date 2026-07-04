"""
html_report.py
---------------
Generates a polished, self-contained HTML dashboard from the ranking
report so results can be viewed in a web browser instead of the
terminal.

The file is fully self-contained (inline CSS, no internet required) so
it can be opened by simply double-clicking it -- no server needed.
"""

import os
import webbrowser


CARD_TEMPLATE = """
<div class="card">
  <div class="card-header">
    <div class="rank-badge rank-{rank_class}">#{rank}</div>
    <div class="name-block">
      <h2>{name}</h2>
      <div class="score-big">{final_score}% Overall Fit</div>
    </div>
  </div>

  <div class="bars">
    <div class="bar-row">
      <span class="bar-label">Text / Context Match</span>
      <div class="bar-track"><div class="bar-fill sim" style="width:{similarity_score}%"></div></div>
      <span class="bar-value">{similarity_score}%</span>
    </div>
    <div class="bar-row">
      <span class="bar-label">Required-Skill Coverage</span>
      <div class="bar-track"><div class="bar-fill skl" style="width:{skill_score}%"></div></div>
      <span class="bar-value">{skill_score}%</span>
    </div>
  </div>

  <div class="skills">
    <div class="skill-group">
      <h4>Matched Skills ({matched_count})</h4>
      <div class="tags">{matched_tags}</div>
    </div>
    <div class="skill-group">
      <h4>Missing Skills ({missing_count})</h4>
      <div class="tags">{missing_tags}</div>
    </div>
  </div>
</div>
"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Resume Screening Report</title>
<style>
  :root {{
    --bg: #f4f6fb;
    --card-bg: #ffffff;
    --text: #1f2430;
    --muted: #6b7280;
    --accent: #4C72B0;
    --good: #2e7d32;
    --bad: #c62828;
    --border: #e5e7eb;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    margin: 0;
    padding: 32px;
  }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  header {{ margin-bottom: 28px; }}
  header h1 {{ margin: 0 0 4px 0; font-size: 26px; }}
  header p {{ margin: 0; color: var(--muted); font-size: 14px; }}

  .chart-wrap {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 28px;
    text-align: center;
  }}
  .chart-wrap img {{ max-width: 100%; border-radius: 8px; }}

  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }}
  .card-header {{ display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }}
  .rank-badge {{
    flex: 0 0 auto;
    width: 46px; height: 46px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; color: white; font-size: 14px;
    background: var(--accent);
  }}
  .rank-1 {{ background: #d4af37; }}
  .rank-2 {{ background: #9ea7b3; }}
  .rank-3 {{ background: #b08d57; }}
  .name-block h2 {{ margin: 0; font-size: 18px; }}
  .score-big {{ color: var(--accent); font-weight: 600; font-size: 14px; margin-top: 2px; }}

  .bars {{ margin-bottom: 16px; }}
  .bar-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }}
  .bar-label {{ flex: 0 0 190px; font-size: 13px; color: var(--muted); }}
  .bar-track {{ flex: 1; background: #eef0f4; border-radius: 6px; height: 10px; overflow: hidden; }}
  .bar-fill {{ height: 100%; border-radius: 6px; }}
  .bar-fill.sim {{ background: #4C72B0; }}
  .bar-fill.skl {{ background: #55a868; }}
  .bar-value {{ flex: 0 0 42px; text-align: right; font-size: 13px; color: var(--muted); }}

  .skills {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .skill-group h4 {{ margin: 0 0 8px 0; font-size: 13px; color: var(--muted); text-transform: uppercase; letter-spacing: .03em; }}
  .tags {{ display: flex; flex-wrap: wrap; gap: 6px; }}
  .tag {{ padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 500; }}
  .tag.good {{ background: #e8f5e9; color: var(--good); }}
  .tag.bad {{ background: #fdecea; color: var(--bad); }}
  .none {{ color: var(--muted); font-size: 13px; font-style: italic; }}

  @media (max-width: 600px) {{
    .skills {{ grid-template-columns: 1fr; }}
    .bar-label {{ flex-basis: 130px; }}
  }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>Resume Screening &amp; Ranking Report</h1>
    <p>Job Description: {jd_name}  |  Candidates screened: {candidate_count}</p>
  </header>

  {chart_block}

  {cards}
</div>
</body>
</html>
"""


def _tags(skills, css_class):
    if not skills:
        return '<span class="none">None</span>'
    return "".join(f'<span class="tag {css_class}">{s}</span>' for s in skills)


def generate_html_report(report: list, jd_name: str, out_path: str, chart_relpath: str = None):
    """Build a self-contained HTML dashboard and write it to out_path.

    Args:
        report: output of scorer.compute_final_scores()
        jd_name: display name of the job description (e.g. filename)
        out_path: where to save the .html file
        chart_relpath: relative path (from out_path's folder) to the
            ranking chart PNG, if you want it embedded at the top.
    """
    cards_html = []
    for row in report:
        rank = row["rank"]
        rank_class = str(rank) if rank <= 3 else "other"
        cards_html.append(CARD_TEMPLATE.format(
            rank=rank,
            rank_class=rank_class,
            name=row["name"],
            final_score=row["final_score"],
            similarity_score=row["similarity_score"],
            skill_score=row["skill_score"],
            matched_count=len(row["matched_skills"]),
            missing_count=len(row["missing_skills"]),
            matched_tags=_tags(row["matched_skills"], "good"),
            missing_tags=_tags(row["missing_skills"], "bad"),
        ))

    chart_block = ""
    if chart_relpath:
        chart_block = f'<div class="chart-wrap"><img src="{chart_relpath}" alt="Ranking chart"></div>'

    html = PAGE_TEMPLATE.format(
        jd_name=jd_name,
        candidate_count=len(report),
        chart_block=chart_block,
        cards="".join(cards_html),
    )

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    return out_path


def open_in_browser(path: str):
    """Open the generated HTML file in the user's default web browser."""
    abs_path = os.path.abspath(path)
    webbrowser.open(f"file://{abs_path}")
