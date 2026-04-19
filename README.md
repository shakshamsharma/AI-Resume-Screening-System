# HireIQ — AI Resume Screening & Hiring Intelligence System

A production-grade full-stack hiring platform with AI-powered resume parsing, candidate scoring, skill gap analysis, fairness monitoring, and a full interview pipeline tracker.

---

## Features

- **Bulk Resume Upload** — PDF, DOCX, TXT. Up to 500 files at once.
- **AI Resume Parsing** — Extracts name, email, skills, experience, education, work history.
- **JD Match Scoring** — Weighted 0–100 score per candidate against job requirements.
- **Skill Gap Analysis** — Shows exactly which required skills each candidate is missing.
- **Candidate Ranking** — Auto-ranks all applicants. One-click re-rank.
- **Duplicate Detection** — Merges duplicate submissions by email/text similarity.
- **Fraud Detection** — Flags keyword-stuffed resumes.
- **Bias Reduction** — Hides name, age, photo, gender indicators during screening.
- **Interview Pipeline** — Kanban board across 8 hiring stages.
- **Analytics Dashboard** — Funnel charts, score distribution, source quality.
- **Role-Based Access** — Admin / Recruiter / Manager roles via JWT.
- **Audit Logs** — Every action logged for compliance.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Tailwind CSS, React Query, Recharts |
| Backend | FastAPI (Python 3.11), SQLAlchemy, Pydantic v2 |
| Database | PostgreSQL 15 |
| AI/NLP | spaCy, pdfplumber, python-docx, regex NLP pipeline |
| Auth | JWT (python-jose), bcrypt |
| Infrastructure | Docker, Docker Compose |

---

## Quick Start (Docker — Recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Ports 3000, 8000, 5432 free

### Steps

```bash
# 1. Clone / unzip the project
cd hireiq

# 2. Copy env file
cp .env.example .env

# 3. Start everything
docker-compose up --build

# 4. Open in browser
open http://localhost:3000
```

First build takes ~3–5 minutes (downloads Python + Node images, installs deps).

### Demo Login
| Role | Email | Password |
|---|---|---|
| Admin | admin@hireiq.com | admin123 |
| Recruiter | recruiter@hireiq.com | recruiter123 |

---

## Local Development (Without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate       # Mac/Linux
# OR: venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Start PostgreSQL (local or Docker)
docker run -d \
  --name hireiq-db \
  -e POSTGRES_DB=hireiq \
  -e POSTGRES_USER=hireiq \
  -e POSTGRES_PASSWORD=hireiq_secret \
  -p 5432:5432 \
  postgres:15-alpine

# Run init SQL
psql postgresql://hireiq:hireiq_secret@localhost:5432/hireiq < init.sql

# Start API server
DATABASE_URL=postgresql://hireiq:hireiq_secret@localhost:5432/hireiq \
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend

# Install
npm install

# Start dev server
VITE_API_URL=http://localhost:8000 npm run dev
```

App: http://localhost:3000

---

## Project Structure

```
hireiq/
├── docker-compose.yml
├── .env.example
│
├── backend/
│   ├── main.py              # FastAPI app entry
│   ├── database.py          # DB connection
│   ├── models.py            # SQLAlchemy ORM models
│   ├── init.sql             # DB schema + seed data
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── routers/
│   │   ├── auth.py          # Login / Register
│   │   ├── jobs.py          # CRUD job descriptions
│   │   ├── resumes.py       # Upload + background parsing
│   │   ├── candidates.py    # Ranked candidates
│   │   ├── interviews.py    # Pipeline / scheduling
│   │   ├── analytics.py     # Dashboard metrics
│   │   └── bias.py          # Fairness logging + reports
│   ├── services/
│   │   ├── parser.py        # PDF/DOCX extraction + NLP
│   │   └── scorer.py        # JD match scoring engine
│   └── utils/
│       └── auth.py          # JWT + password utils
│
└── frontend/
    ├── index.html
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── package.json
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── index.css
        ├── types/index.ts
        ├── utils/api.ts       # Axios API client
        ├── hooks/useAuth.tsx
        ├── components/
        │   ├── ui.tsx         # Shared UI components
        │   ├── Sidebar.tsx
        │   └── Layout.tsx
        └── pages/
            ├── LoginPage.tsx
            ├── DashboardPage.tsx
            ├── JobsPage.tsx
            ├── UploadPage.tsx
            ├── CandidatesPage.tsx
            ├── CandidateDetailPage.tsx
            ├── SkillsPage.tsx
            ├── BiasPage.tsx
            └── PipelinePage.tsx
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/auth/login | JWT login |
| POST | /api/auth/register | Create user |
| GET | /api/jobs/ | List all jobs |
| POST | /api/jobs/ | Create job |
| POST | /api/resumes/upload | Bulk upload resumes |
| GET | /api/candidates/job/{id} | Ranked candidates for job |
| GET | /api/candidates/{id} | Candidate detail |
| PATCH | /api/candidates/{id}/status | Update candidate status |
| POST | /api/candidates/job/{id}/rank | Re-rank candidates |
| GET | /api/analytics/dashboard | Dashboard metrics |
| GET | /api/analytics/job/{id} | Per-job analytics |
| GET | /api/interviews/job/{id} | Pipeline kanban data |
| POST | /api/interviews/ | Schedule interview |
| GET | /api/bias/report/{id} | Bias report for job |

Full interactive docs: **http://localhost:8000/docs**

---

## Scoring Algorithm

| Factor | Weight |
|---|---|
| Skill match (required + priority) | 40% |
| Experience relevance | 25% |
| Education level | 10% |
| Industry relevance | 10% |
| Certifications | 10% |
| Location compatibility | 5% |

Priority skills (set in JD) count 1.5× in the skill score calculation.

---

## Deployment (Production)

For production, update `.env`:
```
SECRET_KEY=<random-256-bit-string>
DATABASE_URL=<your-rds-or-supabase-url>
ANTHROPIC_API_KEY=<optional-for-ai-summaries>
```

Then deploy with:
```bash
docker-compose -f docker-compose.yml up -d --build
```

For AWS ECS / Kubernetes, each service (frontend, backend, db) maps to a separate container/pod. S3 can replace the local upload volume.

---

## License
MIT
