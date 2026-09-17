import math
import re
from typing import Iterable, List, Set

from .data import JOBS
from .resume_parser import extract_structured_profile

SYNONYM_MAP = {
    "js": "javascript",
    "javascript": "javascript",
    "reactjs": "react",
    "react": "react",
    "nodejs": "node",
    "node.js": "node",
    "node": "node",
    "springboot": "spring boot",
    "spring boot": "spring boot",
    "mysql": "sql",
    "sql": "sql",
    "postgresql": "sql",
    "rest api": "rest api",
    "api": "api",
    "ml": "machine learning",
    "machine learning": "machine learning",
    "deep learning": "deep learning",
    "python": "python",
    "java": "java",
    "html": "html",
    "css": "css",
    "power bi": "power bi",
    "excel": "excel",
    "tensorflow": "tensorflow",
    "scikit-learn": "scikit-learn",
    "data analysis": "data analysis",
    "ui design": "ui design",
    "microservices": "microservices",
    "full stack": "full stack",
    "backend": "backend",
    "frontend": "frontend",
}


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_skill(skill: str) -> str:
    cleaned = normalize_text(skill)
    return SYNONYM_MAP.get(cleaned, cleaned)


def extract_skills(text: str) -> Set[str]:
    normalized = normalize_text(text)
    known_skills = {
        normalize_skill(job["title"]) for job in JOBS
    }
    known_skills |= {
        normalize_skill(skill)
        for job in JOBS
        for skill in job["skills"]
    }
    known_skills |= {
        "java",
        "python",
        "javascript",
        "react",
        "sql",
        "html",
        "css",
        "spring boot",
        "rest api",
        "machine learning",
        "power bi",
        "node",
        "microservices",
        "data analysis",
        "ui design",
        "tensorflow",
        "scikit-learn",
        "backend",
        "frontend",
    }

    tokens = set(normalized.split())
    matched = {skill for skill in known_skills if skill in normalized}
    phrase_matches = set()
    for skill in known_skills:
        if " " in skill and skill in normalized:
            phrase_matches.add(skill)
    return matched | phrase_matches


def cosine_similarity(left: Iterable[str], right: Iterable[str]) -> float:
    left_set = set(left)
    right_set = set(right)
    if not left_set and not right_set:
        return 0.0
    if not left_set or not right_set:
        return 0.0
    intersection = left_set & right_set
    denominator = math.sqrt(len(left_set) * len(right_set))
    if denominator == 0:
        return 0.0
    return len(intersection) / denominator


def compute_job_score(candidate_text: str, job: dict) -> dict:
    parsed_profile = extract_structured_profile(candidate_text)
    candidate_skills = set(parsed_profile["skills"]) | extract_skills(candidate_text)
    job_skills = {normalize_skill(skill) for skill in job["skills"]}

    skill_overlap = candidate_skills & job_skills
    skill_match = len(skill_overlap) / max(len(job_skills), 1)

    candidate_tokens = set(normalize_text(candidate_text).split())
    job_tokens = set(normalize_text(job["description"]).split())
    semantic_similarity = cosine_similarity(candidate_tokens, job_tokens)

    resume_terms = {normalize_skill(term) for term in candidate_skills}
    job_terms = {normalize_skill(term) for term in job_skills}
    semantic_weight = len(resume_terms & job_terms) / max(len(job_terms), 1)

    experience_score = 0.8 if parsed_profile["experience"] else 0.3
    role_match = 1.0 if parsed_profile["role"] else 0.5

    final_score = (
        0.45 * semantic_similarity +
        0.30 * skill_match +
        0.15 * semantic_weight +
        0.10 * experience_score +
        0.10 * role_match
    )
    final_score = min(max(final_score, 0), 1) * 100

    missing_skills = sorted(job_skills - candidate_skills)
    matched_skills = sorted(skill_overlap)

    return {
        "job_id": job["id"],
        "title": job["title"],
        "company": job["company"],
        "location": job["location"],
        "salary": job["salary"],
        "sector": job["sector"],
        "match_score": round(final_score, 2),
        "skill_match": round(skill_match * 100, 2),
        "semantic_similarity": round((semantic_similarity + semantic_weight) / 2 * 100, 2),
        "experience_score": round(experience_score * 100, 2),
        "role_match_score": round(role_match * 100, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "parsed_profile": {
            "skills": sorted(parsed_profile["skills"]),
            "experience": sorted(parsed_profile["experience"]),
            "role": sorted(parsed_profile["role"]),
            "education": sorted(parsed_profile["education"]),
            "location": sorted(parsed_profile["location"]),
        },
    }


def get_all_job_matches(candidate_text: str) -> List[dict]:
    scores = [compute_job_score(candidate_text, job) for job in JOBS]
    return sorted(scores, key=lambda item: item["match_score"], reverse=True)
