# Resume Screening & Ranking System

An NLP-based system that automatically **screens, scores, and ranks resumes**
against a job description — the same core idea used by HR-tech platforms and
enterprise applicant tracking systems (ATS), built here in a small,
transparent, and fully explainable way.

Built for **Future Interns – Machine Learning Task 3 (2026)**.

---

## What it does

1. **Reads** resumes (`.txt`) and a job description (`.txt`)
2. **Cleans** the text (lowercasing, removing noise/stopwords)
3. **Extracts skills** from both the resume and the job description using a
   curated skills taxonomy (100+ tech & soft skills with aliases)
4. **Scores similarity** between each resume and the job description using
   TF-IDF + cosine similarity
5. **Ranks candidates** using a combined fit score:
   `final_score = 0.4 × text-similarity + 0.6 × skill-overlap`
6. **Explains results** in plain English — which skills matched, which are
   missing, and why a candidate ranked where they did
7. **Exports** a ranked `results.csv` and a `ranking_chart.png` bar chart

---

## Why this design?

| Design choice | Reason |
|---|---|
| Curated skill taxonomy instead of a generic NER model | Fully transparent and explainable — every match can be traced to an exact rule. No internet download of language models required. |
| TF-IDF + cosine similarity | Simple, fast, and battle-tested for document similarity; doesn't need GPU or heavy dependencies. |
| Weighted combination (skills weighted higher) | Recruiters care most about concrete required skills, but overall contextual relevance still matters — this balances both. |
| Plain-English report | The output must be usable by a non-technical recruiter or HR manager, not just a data scientist. |

---

## Project Structure

```
resume_screening_system/
├── data/
│   ├── job_descriptions/
│   │   ├── data_scientist.txt
│   │   └── backend_developer.txt
│   └── resumes/
│       ├── resume_priya_sharma.txt
│       ├── resume_arjun_mehta.txt
│       ├── resume_sara_khan.txt
│       ├── resume_daniel_lee.txt
│       ├── resume_emily_wong.txt
│       ├── resume_rahul_verma.txt
│       ├── resume_wei_zhang.txt
│       └── resume_ananya_iyer.txt
├── src/
│   ├── preprocessing.py      # text cleaning (no external downloads needed)
│   ├── skills_taxonomy.py    # editable dictionary of skills + aliases
│   ├── skill_extractor.py    # rule-based skill extraction
│   ├── scorer.py             # TF-IDF similarity + skill-overlap scoring
│   └── report.py             # plain-English report, CSV & chart export
├── templates/                # HTML templates for the web app
│   ├── index.html
│   └── results.html
├── static/
│   └── style.css             # web app styling
├── outputs/                  # generated results.csv + ranking_chart.png
├── app.py                    # Flask web app entry point
├── main.py                   # CLI entry point
├── requirements.txt
└── README.md
```

---

## How to run

```bash
pip install -r requirements.txt
```

### Option A — Web app (recommended)

```bash
python app.py
```

Then open **http://127.0.0.1:5000** in your browser. From there you can:
- Pick a sample job description, paste your own text, or upload a `.txt` JD
- Use the 8 bundled sample resumes, or upload your own `.txt` resumes
- View a ranked, color-coded results page with a chart, matched/missing
  skill tags per candidate, and a "Download results.csv" button

### Option B — Command line

```bash
# Screen resumes against the Data Scientist job description
python main.py --jd data/job_descriptions/data_scientist.txt --resumes data/resumes

# Try a different role
python main.py --jd data/job_descriptions/backend_developer.txt --resumes data/resumes
```

Both `--jd` and `--resumes` default to the Data Scientist example, so you can
also just run:

```bash
python main.py
```

Results are printed to the console and saved to `outputs/results.csv` and
`outputs/ranking_chart.png`.

---

## Using your own data

- **Job description**: put any `.txt` file describing the role and required
  skills anywhere, and pass its path with `--jd`.
- **Resumes**: drop any number of `.txt` resume files into a folder and pass
  it with `--resumes`. (PDFs can be converted to `.txt` first with a tool
  like `pdfplumber` or `PyPDF2` if you're working with real PDF resumes.)
- **Skills taxonomy**: open `src/skills_taxonomy.py` and add any
  skill/alias your industry needs — no retraining required.

You can also plug in real datasets such as the
[Kaggle Resume Dataset](https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset)
or the [Job Description Dataset](https://www.kaggle.com/datasets/ravindrasinghrana/job-description-dataset) —
just export each resume/JD as its own `.txt` file into the folders above.

---

## Example output

```
Candidate: Resume Priya Sharma  |  Rank #1  |  Overall Fit: 55.75%
  - Overall text/context match with job description: 53.65%
  - Required-skill coverage: 57.14% (12/21 required skills found)
  - Matched skills: communication, data analysis, data visualization, git,
    machine learning, numpy, pandas, python, scikit-learn, sql, statistics,
    tableau
  - Missing / gap skills: aws, azure, deep learning, nlp, power bi,
    problem solving, project management, pytorch, tensorflow
```

This is the kind of explanation a recruiter can read directly — no
data-science background needed.

---

## How scoring works (in plain terms)

1. **Text similarity (40% weight)** — treats the resume and job description
   as "bags of words" and measures how much their vocabulary overlaps,
   weighted by how distinctive each word is (TF-IDF). This captures general
   relevance even beyond exact skill keywords.
2. **Skill overlap (60% weight)** — directly checks how many of the
   *specific skills* mentioned in the job description also appear in the
   resume. This is weighted higher because it's the most concrete,
   defensible signal for a hiring decision.
3. The two scores are combined into one **0–100% "Overall Fit"** score per
   candidate, and candidates are ranked highest to lowest.

---

## Limitations & possible extensions

- Skill extraction is dictionary-based; it won't catch skills phrased in
  totally novel ways that aren't in `skills_taxonomy.py` (easy to fix by
  adding aliases).
- Currently reads `.txt` files only — a PDF-to-text step could be added
  using `pdfplumber` for real-world PDF resumes.
- Skill weighting is currently uniform; a future version could let
  recruiters mark certain skills (e.g. "must-have Python") as more
  important than others.
- Could be extended with a simple web UI (Flask/Streamlit) so recruiters
  can upload resumes directly instead of using the CLI.

---

*Built as part of the Future Interns Machine Learning internship track.*
