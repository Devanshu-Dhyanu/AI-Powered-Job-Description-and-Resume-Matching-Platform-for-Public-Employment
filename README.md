# AI-Powered Job Recommendation System

This project is a working MVP for an AI/NLP-based job recommendation and skill gap analysis system inspired by the brief in the project statement.

## Project structure

- backend: FastAPI API with sample job data and candidate matching logic
- frontend: React + Vite UI for profile input and job recommendations

## Run locally

### Backend

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Then open:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## Main files

- [backend/app/main.py](backend/app/main.py)
- [backend/app/matching.py](backend/app/matching.py)
- [frontend/src/App.jsx](frontend/src/App.jsx)
- [frontend/src/styles.css](frontend/src/styles.css)

## Demo behavior

The app accepts a candidate profile text and returns ranked jobs with:

- match score
- skill match percentage
- semantic similarity estimate
- matched skills
- missing skills

This is a strong MVP foundation for expanding into resume PDF/DOCX parsing, real embeddings, and PostgreSQL + pgvector integration.
