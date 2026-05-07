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

# 2. (Optional) Copy env file for AI API keys
cp .env.example .env
# Edit .env if you want AI-powered evaluation (optional)

# 3. Start everything with one command
docker-compose up --build

# 4. Open in browser
open http://localhost:3000
```

**That's it!** First build takes ~3–5 minutes (downloads images, installs deps).

### What Docker Does Automatically ✅
- ✅ Sets up PostgreSQL database
- ✅ Runs all migrations (including production fixes)
- ✅ Installs all dependencies (PyMuPDF, pdfplumber, dateparser, etc.)
- ✅ Starts backend API server
- ✅ Starts frontend dev server
- ✅ Connects everything together

### Demo Login
| Role | Email | Password |
|---|---|---|
| Admin | admin@hireiq.com | admin123 |
| Recruiter | recruiter@hireiq.com | recruiter123 |

### Useful Docker Commands
```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Clean start (removes data)
docker-compose down -v && docker-compose up --build
```

**See [docs/DOCKER_GUIDE.md](docs/DOCKER_GUIDE.md) for complete Docker documentation.**

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


---

## 🚀 Production-Grade Enhancements

### ✨ Recent Major Improvements

This system has been transformed from a demo into a **production-ready ATS platform** with the following critical fixes:

#### 1. **Zero Hallucinations** ✅
- **Problem Fixed:** AI was inventing experience (e.g., "8 years" for freshers)
- **Solution:** Deterministic experience calculation from work history dates only
- **Result:** Freshers correctly show 0 years, seniors show accurate calculations

#### 2. **Robust Resume Parsing** ✅
- **Dual PDF extraction:** pdfplumber (primary) + PyMuPDF (fallback)
- **Confidence scoring:** Every extraction gets quality score (0-1)
- **Error handling:** Gracefully handles corrupted files and image-based PDFs
- **Date parsing:** Supports multiple formats (Jan 2020, 01/2020, 2020, Present, etc.)

#### 3. **Accurate Work Experience Extraction** ✅
- **Company name extraction:** Pattern-based detection
- **Role/title extraction:** Identifies job titles
- **Duration calculation:** Accurate month-based calculation
- **Current job detection:** Handles "Present", "Current", "Now"

#### 4. **AI as Evaluator (Not Extractor)** ✅
- **Separation of concerns:** AI reviews structured data, doesn't extract
- **No hallucinations:** AI receives JSON, not raw text
- **Fallback support:** Works without AI API keys (rule-based)
- **Supports:** OpenAI GPT-4 or Anthropic Claude

#### 5. **Quality Validation** ✅
- **Parsing confidence:** 0-1 score for extraction quality
- **Manual review triggers:** Low confidence resumes flagged
- **Debug endpoints:** `/api/resumes/debug/{id}` for troubleshooting
- **Duplicate detection:** Before parsing (saves processing)

#### 6. **Enhanced Scoring** ✅
- **Deterministic:** Same resume = same score
- **Weighted system:** Skills 40%, Experience 25%, etc.
- **Priority skills:** 1.5x weight for must-have skills
- **Skill gap analysis:** Shows matched, missing, bonus skills

### 📖 Additional Documentation

- **[docs/PRODUCTION_FIXES.md](docs/PRODUCTION_FIXES.md)** - Comprehensive list of all fixes
- **[docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md)** - Complete testing guide with test cases
- **[setup_production_fixes.sh](setup_production_fixes.sh)** - Automated setup script

### 🧪 Testing the Fixes

```bash
# Run setup script
chmod +x setup_production_fixes.sh
./setup_production_fixes.sh

# Test with sample resumes
# 1. Upload a fresher resume → should show 0 years
# 2. Upload a senior resume → should calculate from dates
# 3. Upload corrupted PDF → should fail gracefully

# Debug parsing
GET /api/resumes/debug/{resume_id}
```

### 🔍 Debug Endpoints

#### Resume Debug
```bash
GET /api/resumes/debug/{resume_id}
```
Returns detailed parsing breakdown with confidence scores.

#### Resume Status
```bash
GET /api/resumes/status/{resume_id}
```
Returns processing status and candidate info.

### 📊 Quality Metrics

#### Parsing Confidence Thresholds
- **0.8-1.0:** Excellent - Auto-process
- **0.6-0.8:** Good - Auto-process with review
- **0.4-0.6:** Fair - Manual review recommended
- **0.0-0.4:** Poor - Manual review required

#### Match Score Interpretation
- **85-100:** Strong match - Priority interview
- **70-84:** Good match - Consider for interview
- **55-69:** Moderate match - Review carefully
- **0-54:** Weak match - Likely reject

### 🛠️ New Dependencies

```bash
# Added for production fixes
PyMuPDF==1.24.0          # Fallback PDF extraction
openai==1.12.0           # OpenAI API (optional)
anthropic==0.18.1        # Anthropic API (optional)
dateparser==1.2.0        # Robust date parsing
fuzzywuzzy==0.18.0       # Fuzzy string matching
python-Levenshtein==0.25.0  # String similarity
```

### 🎯 Key Achievements

1. ✅ **Zero Hallucinations** - All data from resume only
2. ✅ **Accurate Experience** - Calculated from dates, not estimated
3. ✅ **Deterministic Scoring** - Repeatable, explainable results
4. ✅ **Quality Validation** - Confidence scores for every extraction
5. ✅ **Robust Parsing** - Handles complex PDFs, multiple formats
6. ✅ **Production-Ready** - Error handling, logging, debugging tools

### 🚨 Critical Rules Enforced

```python
# NEVER estimate experience - calculate from dates only
if not work_experience:
    years_experience = 0.0  # Fresher

# NEVER invent data - extract from resume only
if not found_in_resume:
    value = None  # Don't guess

# ALWAYS validate extraction quality
if parsing_confidence < 0.6:
    needs_manual_review = True
```

### 📞 Support & Troubleshooting

For issues:
1. Check console logs for error messages
2. Use `/api/resumes/debug/{resume_id}` endpoint
3. Review parsing confidence scores
4. Check `flag_reason` for flagged resumes
5. See [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) for test cases

---

**Remember:** This system NEVER invents data. All information comes from the resume.
