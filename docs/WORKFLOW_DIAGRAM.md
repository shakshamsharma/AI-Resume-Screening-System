# System Workflow Diagram

## 📊 Complete Resume Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RESUME UPLOAD                                    │
│  User uploads PDF/DOCX/TXT files (single or bulk)                      │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 1: TEXT EXTRACTION                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐            │
│  │  pdfplumber  │───▶│   PyMuPDF    │───▶│  python-docx │            │
│  │  (primary)   │    │  (fallback)  │    │   (DOCX)     │            │
│  └──────────────┘    └──────────────┘    └──────────────┘            │
│                                                                          │
│  Output: (raw_text, extraction_confidence)                              │
│  Confidence: 0.0 - 1.0                                                  │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Confidence OK? │
                    │   (> 0.3)      │
                    └────┬───────┬───┘
                         │       │
                    YES  │       │ NO
                         │       │
                         │       ▼
                         │  ┌─────────────────────┐
                         │  │ Mark as FAILED      │
                         │  │ Flag: "Extraction   │
                         │  │ failed - corrupted" │
                         │  └─────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 2: DUPLICATE CHECK                              │
│  Compare with existing resumes:                                         │
│  • Email matching (primary)                                             │
│  • Text similarity (secondary, 85% threshold)                           │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  Duplicate?    │
                    └────┬───────┬───┘
                         │       │
                    NO   │       │ YES
                         │       │
                         │       ▼
                         │  ┌─────────────────────┐
                         │  │ Mark as DUPLICATE   │
                         │  │ Stop processing     │
                         │  │ No candidate created│
                         │  └─────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              STEP 3: DETERMINISTIC PARSING (NO AI)                      │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Name Extraction                                                   │  │
│  │ • First non-header line heuristic                                │  │
│  │ • Confidence scoring                                             │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Contact Info Extraction                                          │  │
│  │ • Email: regex pattern matching                                  │  │
│  │ • Phone: international format support                            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Skills Extraction                                                │  │
│  │ • 500+ tech skills database                                      │  │
│  │ • Word boundary matching (no false positives)                    │  │
│  │ • Categories: languages, frameworks, databases, cloud, etc.      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Work Experience Extraction ⭐ CRITICAL                           │  │
│  │ • Date range parsing: "Jan 2020 - Present"                       │  │
│  │ • Company name extraction                                        │  │
│  │ • Role/title extraction                                          │  │
│  │ • Duration calculation (months)                                  │  │
│  │ • Current job detection                                          │  │
│  │                                                                  │  │
│  │ Example Output:                                                  │  │
│  │ {                                                                │  │
│  │   "company": "Google Inc",                                       │  │
│  │   "role": "Senior Software Engineer",                            │  │
│  │   "start_date": "Jan 2020",                                      │  │
│  │   "end_date": "Present",                                         │  │
│  │   "duration_months": 64,                                         │  │
│  │   "is_current": true                                             │  │
│  │ }                                                                │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Experience Calculation ⭐ NO HALLUCINATIONS                      │  │
│  │                                                                  │  │
│  │ if work_experience is empty:                                     │  │
│  │     years_experience = 0.0  # FRESHER                            │  │
│  │ else:                                                            │  │
│  │     total_months = sum(exp.duration_months)                      │  │
│  │     years_experience = round(total_months / 12, 1)               │  │
│  │                                                                  │  │
│  │ ❌ NEVER estimate or guess                                       │  │
│  │ ✅ ONLY calculate from dates                                     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Education Extraction                                             │  │
│  │ • Level: PhD, Masters, Bachelors, Diploma                        │  │
│  │ • Institution: Premium institutes detection                      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Certifications Extraction                                        │  │
│  │ • AWS, GCP, Azure, Kubernetes, etc.                              │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  Output: Structured JSON (no AI involved)                               │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 4: QUALITY VALIDATION                           │
│                                                                          │
│  Calculate Parsing Confidence:                                          │
│  • Text extraction quality (30%)                                        │
│  • Name extraction (15%)                                                │
│  • Contact info (20%)                                                   │
│  • Skills count (15%)                                                   │
│  • Work experience (10%)                                                │
│  • Education (10%)                                                      │
│                                                                          │
│  Detect Issues:                                                         │
│  • Keyword stuffing (skill density > 15)                                │
│  • Suspicious patterns                                                  │
│                                                                          │
│  Output: parsing_confidence (0.0 - 1.0)                                 │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │ Confidence < 0.6?  │
                    └────┬───────────┬───┘
                         │           │
                    YES  │           │ NO
                         │           │
                         ▼           ▼
              ┌──────────────┐  ┌──────────────┐
              │ Flag for     │  │ Auto-process │
              │ Manual Review│  │              │
              └──────────────┘  └──────────────┘
                         │           │
                         └─────┬─────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              STEP 5: DETERMINISTIC SCORING                              │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Skills Match (40% weight)                                        │  │
│  │ • Matched skills: candidate ∩ required                           │  │
│  │ • Missing skills: required - candidate                           │  │
│  │ • Priority skills: 1.5x weight                                   │  │
│  │ • Bonus skills: candidate - required                             │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Experience Match (25% weight)                                    │  │
│  │ • In range (min-max): 90-100 score                               │  │
│  │ • Under-experienced: scaled penalty                              │  │
│  │ • Over-experienced: slight penalty                               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Education Match (10% weight)                                     │  │
│  │ • Level comparison                                               │  │
│  │ • Premium institution bonus                                      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Other Factors (25% weight)                                       │  │
│  │ • Industry fit (10%)                                             │  │
│  │ • Certifications (10%)                                           │  │
│  │ • Location (5%)                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  Output: Weighted overall score (0-100)                                 │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              STEP 6: AI EVALUATION (OPTIONAL)                           │
│                                                                          │
│  AI receives STRUCTURED DATA (not raw text):                            │
│  {                                                                       │
│    "name": "John Doe",                                                  │
│    "years_experience": 5.2,                                             │
│    "skills": ["python", "aws", "docker"],                               │
│    "scores": {                                                          │
│      "overall": 85,                                                     │
│      "skills": 90,                                                      │
│      "experience": 95                                                   │
│    },                                                                   │
│    "matched_skills": ["python", "aws"],                                 │
│    "missing_skills": ["kubernetes"]                                     │
│  }                                                                       │
│                                                                          │
│  AI Tasks (Evaluator, NOT Extractor):                                   │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 1. Generate Summary                                              │  │
│  │    "5-year senior engineer with Python, AWS background"          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 2. Explain Fit                                                   │  │
│  │    "Scored 85/100 due to strong skill match (Python, AWS)        │  │
│  │     and 5 years in target range. Missing Kubernetes."            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 3. Generate Recommendation                                       │  │
│  │    {                                                             │  │
│  │      "recommendation": "yes",                                    │  │
│  │      "reasoning": "Good match with trainable gaps",              │  │
│  │      "key_strengths": ["Strong Python", "AWS certified"],        │  │
│  │      "key_concerns": ["Missing Kubernetes"],                     │  │
│  │      "interview_focus": ["Assess K8s learning ability"]          │  │
│  │    }                                                             │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  Fallback: If AI unavailable, use rule-based generation                 │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 7: SAVE TO DATABASE                             │
│                                                                          │
│  Create Candidate Record:                                               │
│  • All extracted fields                                                 │
│  • All scores                                                           │
│  • Parsing confidence                                                   │
│  • AI evaluation results                                                │
│                                                                          │
│  Create Work Experience Records:                                        │
│  • Company, role, dates, duration                                       │
│                                                                          │
│  Update Resume Status:                                                  │
│  • parse_status = "done"                                                │
│  • is_flagged, flag_reason                                              │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         COMPLETE                                        │
│  Candidate ready for recruiter review                                   │
│  • Ranked by overall score                                              │
│  • Skill gaps identified                                                │
│  • AI insights available                                                │
│  • Quality validated                                                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Debug Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TROUBLESHOOTING WORKFLOW                             │
└─────────────────────────────────────────────────────────────────────────┘

Resume uploaded but no candidate?
    │
    ▼
GET /api/resumes/status/{resume_id}
    │
    ├─ parse_status = "failed"
    │   └─ Check flag_reason
    │       ├─ "Text extraction failed" → Corrupted/image PDF
    │       └─ "Processing error" → Check logs
    │
    ├─ is_duplicate = true
    │   └─ Duplicate detected, no candidate created
    │
    └─ parse_status = "done"
        └─ GET /api/resumes/debug/{resume_id}
            │
            ├─ parsing_confidence < 0.6
            │   └─ Low quality extraction, needs manual review
            │
            ├─ is_flagged = true
            │   └─ Check flag_reason (keyword stuffing, etc.)
            │
            └─ Check extraction_quality breakdown
                ├─ name_confidence
                ├─ has_email, has_phone
                ├─ skills_count
                └─ work_confidence
```

---

## 🎯 Key Decision Points

### 1. Extraction Confidence Check
```
if extraction_confidence < 0.3:
    ❌ FAIL: Mark as failed, stop processing
else:
    ✅ CONTINUE: Proceed to duplicate check
```

### 2. Duplicate Detection
```
if is_duplicate:
    ❌ STOP: Don't create candidate
else:
    ✅ CONTINUE: Proceed to parsing
```

### 3. Parsing Confidence Check
```
if parsing_confidence < 0.6:
    ⚠️ FLAG: Mark for manual review
    ✅ CONTINUE: Still create candidate
```

### 4. Experience Calculation
```
if work_experience is empty:
    years_experience = 0.0  # FRESHER
else:
    years_experience = calculate_from_dates()  # ACCURATE
```

### 5. AI Evaluation
```
if AI_API_KEY exists:
    ✅ USE AI: Generate insights
else:
    ✅ FALLBACK: Use rule-based generation
```

---

## 📊 Data Flow

```
Raw Resume (PDF/DOCX)
    ↓
Raw Text (string)
    ↓
Structured Data (JSON)
    {
      "name": "...",
      "email": "...",
      "skills": [...],
      "work_experience": [...]
    }
    ↓
Scores (JSON)
    {
      "overall_score": 85,
      "skill_score": 90,
      "matched_skills": [...],
      "missing_skills": [...]
    }
    ↓
AI Insights (JSON)
    {
      "ai_summary": "...",
      "ai_fit_explanation": "...",
      "ai_recommendation": "yes"
    }
    ↓
Database Record (PostgreSQL)
    candidates table
    work_experience table
```

---

## ⚡ Performance Characteristics

- **Upload**: Instant (file saved to disk)
- **Text Extraction**: 1-3 seconds per resume
- **Parsing**: < 1 second per resume
- **Scoring**: < 0.1 seconds per resume
- **AI Evaluation**: 2-5 seconds per resume (if enabled)
- **Total**: 3-10 seconds per resume

**Batch Processing**: Parallel background tasks for bulk uploads

---

## 🛡️ Error Handling

```
Try: pdfplumber extraction
    ↓ FAIL
Try: PyMuPDF extraction
    ↓ FAIL
Mark as failed, log error, notify user
```

```
Try: AI evaluation
    ↓ FAIL
Fallback: Rule-based generation
    ↓ ALWAYS SUCCEEDS
```

---

## ✅ Quality Gates

1. **Extraction Quality** → confidence > 0.3
2. **Duplicate Check** → not duplicate
3. **Parsing Quality** → confidence > 0.6 (or flag)
4. **Data Validation** → all required fields present
5. **Score Calculation** → deterministic, repeatable

---

**This workflow ensures ZERO HALLUCINATIONS and MAXIMUM ACCURACY.**
