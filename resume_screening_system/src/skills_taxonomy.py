"""
skills_taxonomy.py
-------------------
A curated, extensible taxonomy of skills grouped by category.

Why a taxonomy instead of a generic NLP model?
Off-the-shelf NER models (like spaCy's) are NOT trained to recognise
"skills" as an entity type out of the box, and downloading extra
language models requires internet access that isn't always available
in a hiring team's secure environment. A curated taxonomy is:
  - Transparent  -> recruiters can see and edit exactly what counts as a skill
  - Explainable  -> every match can be traced back to a rule
  - Extensible   -> add a new skill/alias in seconds, no retraining

Each skill maps to a list of aliases/synonyms that may appear in resumes
or job descriptions (case-insensitive matching is handled by the extractor).
"""

SKILLS_TAXONOMY = {
    # ---- Programming languages ----
    "python": ["python", "py3"],
    "java": ["java"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "csharp"],
    "javascript": ["javascript", "js", "es6"],
    "typescript": ["typescript", "ts"],
    "sql": ["sql", "mysql", "postgresql", "postgres", "t-sql", "pl/sql"],
    "r": ["r programming", " r "],
    "go": ["golang", " go "],
    "scala": ["scala"],
    "bash": ["bash", "shell scripting", "shell script"],

    # ---- Data science / ML ----
    "machine learning": ["machine learning", "ml "],
    "deep learning": ["deep learning", "dl "],
    "nlp": ["nlp", "natural language processing"],
    "computer vision": ["computer vision", "cv "],
    "data analysis": ["data analysis", "data analytics"],
    "data visualization": ["data visualization", "data viz"],
    "statistics": ["statistics", "statistical modeling", "statistical analysis"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "tensorflow": ["tensorflow", "tf.keras"],
    "pytorch": ["pytorch", "torch"],
    "keras": ["keras"],
    "spacy": ["spacy"],
    "nltk": ["nltk"],
    "opencv": ["opencv"],
    "xgboost": ["xgboost"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "excel": ["excel", "ms excel", "advanced excel"],

    # ---- Web / backend ----
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "react": ["react", "react.js", "reactjs"],
    "angular": ["angular", "angular.js"],
    "vue": ["vue", "vue.js"],
    "node.js": ["node.js", "node js", "nodejs"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "spring boot": ["spring boot", "spring framework"],
    "rest api": ["rest api", "restful api", "rest apis"],
    "graphql": ["graphql"],

    # ---- Cloud / DevOps ----
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "docker": ["docker", "containerization"],
    "kubernetes": ["kubernetes", "k8s"],
    "ci/cd": ["ci/cd", "continuous integration", "continuous deployment", "jenkins"],
    "git": ["git", "github", "gitlab", "version control"],
    "linux": ["linux", "unix"],

    # ---- Databases ----
    "mongodb": ["mongodb", "mongo db"],
    "nosql": ["nosql"],
    "redis": ["redis"],

    # ---- Soft / management skills ----
    "communication": ["communication skills", "communication"],
    "leadership": ["leadership", "team leadership"],
    "project management": ["project management", "agile", "scrum", "kanban"],
    "problem solving": ["problem solving", "problem-solving"],
    "teamwork": ["teamwork", "collaboration", "team player"],
    "time management": ["time management"],
}


def get_all_skills():
    """Return the sorted list of canonical skill names."""
    return sorted(SKILLS_TAXONOMY.keys())


def get_aliases(skill):
    """Return alias list for a canonical skill name."""
    return SKILLS_TAXONOMY.get(skill, [skill])
