import re
from typing import Dict, Set

SECTION_KEYWORDS = {
    "skills": {"skill", "skills"},
    "experience": {"experience", "work experience", "projects", "project"},
    "education": {"education", "degree", "qualifications"},
    "certifications": {"certification", "certifications"},
    "role": {"preferred", "job role", "role", "interest"},
    "location": {"location", "city", "preferred location"},
}


def normalize_text(text: str) -> str:
    cleaned = text.lower()
    cleaned = re.sub(r"[^a-z0-9\s\-]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def extract_structured_profile(candidate_text: str) -> Dict[str, Set[str]]:
    text = candidate_text.strip()
    result: Dict[str, Set[str]] = {"skills": set(), "experience": set(), "education": set(), "certifications": set(), "role": set(), "location": set()}
    if not text:
        return result

    for line in text.splitlines():
        line_clean = line.strip()
        if not line_clean or ":" not in line_clean:
            continue
        key, value = line_clean.split(":", 1)
        key_norm = key.strip().lower()
        for section, keys in SECTION_KEYWORDS.items():
            if key_norm in keys or key_norm.startswith(tuple(keys)):
                items = [part.strip() for part in value.split(",")]
                result[section].update(item for item in items if item)

    normalized = normalize_text(text)
    skills_candidates = {
        "java",
        "python",
        "javascript",
        "react",
        "spring boot",
        "mysql",
        "sql",
        "html",
        "css",
        "rest api",
        "node",
        "machine learning",
        "power bi",
        "tensorflow",
        "scikit-learn",
        "data analysis",
        "ui design",
        "microservices",
        "backend",
        "frontend",
    }

    for skill in skills_candidates:
        if skill in normalized:
            result["skills"].add(skill)

    if "project" in normalized or "experience" in normalized:
        result["experience"].add("project experience")

    return result
