"""
scorer.py
---------
Combines two complementary signals into one explainable "fit score"
per resume:

1. Semantic similarity (TF-IDF + cosine similarity)
   Captures overall textual/contextual overlap between a resume and
   the job description -- catches relevant experience even when exact
   skill keywords differ slightly.

2. Skill overlap score
   Captures how many of the *specific required skills* (from the
   taxonomy) appear in the resume. This is the part recruiters care
   about most: "does this person have the skills we listed?"

Final score = weighted sum of both, so a resume can't rank #1 purely
by being wordy -- it must also cover the required skills.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.preprocessing import preprocess
from src.skill_extractor import extract_skill_set

# Relative importance of each signal. Must sum to 1.0.
SIMILARITY_WEIGHT = 0.4
SKILL_OVERLAP_WEIGHT = 0.6


def compute_similarity_scores(job_description: str, resumes: dict):
    """Compute TF-IDF cosine similarity of each resume against the JD.

    Args:
        job_description: raw JD text
        resumes: dict {candidate_name: raw_resume_text}

    Returns:
        dict {candidate_name: similarity_score in [0, 1]}
    """
    names = list(resumes.keys())
    corpus = [preprocess(job_description)] + [preprocess(resumes[n]) for n in names]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)

    jd_vector = tfidf_matrix[0:1]
    resume_vectors = tfidf_matrix[1:]

    sims = cosine_similarity(jd_vector, resume_vectors)[0]
    return {name: float(score) for name, score in zip(names, sims)}


def compute_skill_scores(job_description: str, resumes: dict):
    """Compute skill overlap ratio and skill gap for each resume.

    Returns:
        dict {candidate_name: {
            'required_skills': set,
            'matched_skills': set,
            'missing_skills': set,
            'skill_score': float in [0, 1]
        }}
    """
    required_skills = extract_skill_set(job_description)
    results = {}

    for name, text in resumes.items():
        candidate_skills = extract_skill_set(text)
        matched = required_skills & candidate_skills
        missing = required_skills - candidate_skills
        skill_score = (len(matched) / len(required_skills)) if required_skills else 0.0

        results[name] = {
            "required_skills": required_skills,
            "matched_skills": matched,
            "missing_skills": missing,
            "skill_score": skill_score,
        }

    return results


def compute_final_scores(job_description: str, resumes: dict):
    """Combine similarity + skill overlap into one final ranked report.

    Returns:
        list of dicts sorted by final_score descending, each containing:
            name, final_score, similarity_score, skill_score,
            matched_skills, missing_skills, required_skills
    """
    similarity_scores = compute_similarity_scores(job_description, resumes)
    skill_data = compute_skill_scores(job_description, resumes)

    report = []
    for name in resumes:
        sim = similarity_scores[name]
        skl = skill_data[name]["skill_score"]
        final = (SIMILARITY_WEIGHT * sim) + (SKILL_OVERLAP_WEIGHT * skl)

        report.append({
            "name": name,
            "final_score": round(final * 100, 2),          # as a percentage
            "similarity_score": round(sim * 100, 2),
            "skill_score": round(skl * 100, 2),
            "matched_skills": sorted(skill_data[name]["matched_skills"]),
            "missing_skills": sorted(skill_data[name]["missing_skills"]),
            "required_skills": sorted(skill_data[name]["required_skills"]),
        })

    report.sort(key=lambda r: r["final_score"], reverse=True)
    for idx, row in enumerate(report, start=1):
        row["rank"] = idx

    return report
