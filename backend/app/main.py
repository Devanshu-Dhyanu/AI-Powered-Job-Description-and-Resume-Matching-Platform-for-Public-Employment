from io import BytesIO
from typing import Dict

import fitz
from docx import Document
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .data import JOBS
from .matching import get_all_job_matches
from .resume_parser import extract_structured_profile

app = FastAPI(title="AI Job Recommendation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MatchRequest(BaseModel):
    candidate_text: str


def extract_text_from_bytes(filename: str, content: bytes) -> str:
    lowered = filename.lower()

    if lowered.endswith(".pdf"):
        pdf_doc = fitz.open(stream=content, filetype="pdf")
        return "\n".join(page.get_text() for page in pdf_doc)

    if lowered.endswith(".docx"):
        doc = Document(BytesIO(content))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)

    return content.decode("utf-8", errors="ignore")


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "AI job recommendation backend is running"}


@app.get("/api/jobs")
def list_jobs():
    return {"jobs": JOBS}


@app.post("/api/match")
def match_candidate(payload: MatchRequest):
    matches = get_all_job_matches(payload.candidate_text)
    return {"matches": matches}


@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")

    content = await file.read()
    text = extract_text_from_bytes(file.filename, content)
    if not text.strip():
        raise HTTPException(status_code=400, detail="Uploaded file contains no readable text")

    matches = get_all_job_matches(text)
    return {
        "filename": file.filename,
        "extracted_text": text,
        "parsed_profile": {
            "skills": sorted(extract_structured_profile(text)["skills"]),
            "experience": sorted(extract_structured_profile(text)["experience"]),
            "role": sorted(extract_structured_profile(text)["role"]),
            "education": sorted(extract_structured_profile(text)["education"]),
            "location": sorted(extract_structured_profile(text)["location"]),
        },
        "matches": matches[:5],
    }


@app.get("/api/dashboard")
def dashboard_stats():
    return {
        "total_job_seekers": 12540,
        "active_jobs": 1284,
        "applications": 8430,
        "average_match_score": 72,
        "top_skills": {
            "Java": 92,
            "Python": 81,
            "React": 74,
            "SQL": 68,
        },
        "demand_by_sector": {
            "IT": 38,
            "Manufacturing": 24,
            "Healthcare": 16,
            "Education": 12,
            "Other": 10,
        },
    }
