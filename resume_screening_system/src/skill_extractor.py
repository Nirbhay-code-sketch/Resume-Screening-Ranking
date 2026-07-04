"""
skill_extractor.py
-------------------
Extracts canonical skills from raw resume / job-description text using
the taxonomy defined in skills_taxonomy.py.

Matching strategy:
  1. Lowercase + pad the raw text with spaces so alias matching at
     string boundaries is reliable (avoids "r" matching inside "your").
  2. For every canonical skill, check whether any of its aliases occur
     as a substring with word boundaries.
  3. Return the set of canonical skills found (order-independent).

This is intentionally simple and 100% explainable: for any match we can
say exactly which alias triggered it, which recruiters trust far more
than a black-box NER model.
"""

import re
from src.skills_taxonomy import SKILLS_TAXONOMY


def _boundary_pattern(alias: str) -> re.Pattern:
    """Build a regex that matches `alias` on word-ish boundaries.

    Handles aliases containing symbols like '++', '#', '.' correctly by
    using explicit lookaround instead of \\b (which misbehaves around
    punctuation).
    """
    escaped = re.escape(alias.strip())
    pattern = r"(?<![a-z0-9])" + escaped + r"(?![a-z0-9])"
    return re.compile(pattern, re.IGNORECASE)


def extract_skills(raw_text: str):
    """Return a dict: {canonical_skill: [matched_aliases]} found in text."""
    text = f" {raw_text.lower()} "
    found = {}
    for skill, aliases in SKILLS_TAXONOMY.items():
        matched_aliases = []
        for alias in aliases:
            if _boundary_pattern(alias).search(text):
                matched_aliases.append(alias.strip())
        if matched_aliases:
            found[skill] = matched_aliases
    return found


def extract_skill_set(raw_text: str):
    """Convenience wrapper returning just the set of canonical skill names."""
    return set(extract_skills(raw_text).keys())
