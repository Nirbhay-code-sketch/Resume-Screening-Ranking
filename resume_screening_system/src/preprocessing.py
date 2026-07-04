"""
preprocessing.py
-----------------
Lightweight, dependency-free text cleaning utilities for resumes and
job descriptions.

We deliberately avoid NLTK/spaCy downloads here (they require internet
access to fetch models/corpora on first run). Everything below uses
only Python's standard library, which keeps the pipeline fully
reproducible offline.
"""

import re

# A small, hand-picked stopword list is enough for this task -- we are
# not doing deep syntactic analysis, only cleaning text before keyword /
# similarity matching.
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "of", "at", "by", "for",
    "with", "about", "against", "between", "into", "through", "during",
    "before", "after", "above", "below", "to", "from", "up", "down", "in",
    "out", "on", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "s", "t", "can", "will", "just", "don", "should", "now", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "having",
    "do", "does", "did", "doing", "it", "its", "this", "that", "these",
    "those", "i", "we", "you", "he", "she", "they", "them", "their", "our",
    "your", "as", "also", "etc",
}


def clean_text(text: str) -> str:
    """Lowercase, strip special characters, and collapse whitespace.

    Keeps letters, digits, spaces, and a few symbols that matter for
    skills such as 'c++', 'c#', 'node.js'.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\+\#\./\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str):
    """Very simple whitespace tokenizer over already-cleaned text."""
    return [tok for tok in text.split(" ") if tok]


def remove_stopwords(tokens):
    return [tok for tok in tokens if tok not in STOPWORDS and len(tok) > 1]


def preprocess(text: str) -> str:
    """Full pipeline: clean -> tokenize -> remove stopwords -> rejoin.

    Returns a cleaned string (not a token list) because scikit-learn's
    vectorizers expect raw strings.
    """
    cleaned = clean_text(text)
    tokens = tokenize(cleaned)
    tokens = remove_stopwords(tokens)
    return " ".join(tokens)


def load_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
