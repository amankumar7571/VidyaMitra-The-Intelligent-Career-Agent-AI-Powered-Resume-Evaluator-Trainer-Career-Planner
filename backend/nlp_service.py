import os
from typing import List

# Try loading spacy; fallback gracefully so the server doesn't crash on import.
try:
    import spacy
    from spacy.matcher import PhraseMatcher
    try:
        _nlp = spacy.load("en_core_web_sm")
    except OSError:
        _nlp = spacy.blank("en")
    _SPACY_AVAILABLE = True
except ImportError:
    _nlp = None
    _SPACY_AVAILABLE = False

# Full list of skills recognizable by the system
MASTER_SKILLS: List[str] = [
    "Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "React",
    "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "FastAPI",
    "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL", "AWS", "Azure",
    "GCP", "Docker", "Kubernetes", "Machine Learning", "Deep Learning",
    "Data Science", "Artificial Intelligence", "NLP", "Computer Vision",
    "TensorFlow", "PyTorch", "Scikit-Learn", "Pandas", "NumPy", "Git",
    "Agile", "Scrum", "Jira", "Linux", "Bash", "REST API", "GraphQL",
    "HTML", "CSS", "TailwindCSS", "Sass", "Redux", "Data Structures",
    "Algorithms", "Problem Solving", "Tableau", "Power BI", "Excel",
    "Statistics", "CI/CD",
]

# Build a lowercase → original-casing lookup once
_SKILL_LOOKUP = {s.lower(): s for s in MASTER_SKILLS}


def _simple_keyword_extract(text: str) -> List[str]:
    """
    Fast fallback: split text on word boundaries and look up known skills.
    Works even when spaCy is not installed.
    """
    text_lower = text.lower()
    found = set()
    for skill_lower, skill_orig in _SKILL_LOOKUP.items():
        if skill_lower in text_lower:
            found.add(skill_orig)
    return list(found)


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract skills from resume text.
    Uses spaCy PhraseMatcher when available; falls back to simple keyword search.
    Returns a unique list with original skill casing.
    """
    if not _SPACY_AVAILABLE or _nlp is None:
        return _simple_keyword_extract(text)

    try:
        matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")
        # Build patterns using lowercase so matching works correctly
        patterns = [_nlp.make_doc(skill.lower()) for skill in MASTER_SKILLS]
        matcher.add("SKILLS", patterns)

        doc = _nlp(text.lower())
        matches = matcher(doc)

        found = set()
        for _, start, end in matches:
            span_text = doc[start:end].text.lower()
            original = _SKILL_LOOKUP.get(span_text)
            if original:
                found.add(original)
        return list(found)
    except Exception:
        # If anything goes wrong with spaCy, use the simple fallback
        return _simple_keyword_extract(text)
