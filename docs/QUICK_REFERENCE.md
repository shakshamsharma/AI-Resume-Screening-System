# Quick Reference Card

## 🚀 Quick Start

```bash
# Setup
./setup_production_fixes.sh

# Start Backend
cd backend
uvicorn main:app --reload

# Start Frontend
cd frontend
npm run dev
```

---

## 🔑 Key Endpoints

### Debug & Troubleshooting
```bash
# Debug resume parsing
GET /api/resumes/debug/{resume_id}

# Check resume status
GET /api/resumes/status/{resume_id}

# Health check
GET /health
```

### Core Operations
```bash
# Upload resumes
POST /api/resumes/upload

# List candidates
GET /api/candidates/job/{job_id}

# Get candidate details
GET /api/candidates/{candidate_id}

# Rank candidates
POST /api/candidates/job/{job_id}/rank
```

---

## 📊 Key Metrics

### Parsing Confidence
- **0.8-1.0**: Excellent ✅
- **0.6-0.8**: Good ✅
- **0.4-0.6**: Fair ⚠️
- **0.0-0.4**: Poor ❌

### Match Scores
- **85-100**: Strong match 🟢
- **70-84**: Good match 🔵
- **55-69**: Moderate 🟡
- **0-54**: Weak match 🔴

### AI Recommendations
- **strong_yes**: Priority hire ✓✓
- **yes**: Recommend ✓
- **maybe**: Consider ?
- **no**: Pass ✗

---

## 🐛 Common Issues

### Fresher Shows Experience
```python
# Check: backend/services/parser.py
# Line: calculate_total_experience_years()
# Should return 0.0 if no work_experience
```

### Parsing Failed
```bash
# Check extraction confidence
GET /api/resumes/debug/{resume_id}

# Look for:
# - extraction_confidence < 0.3
# - Corrupted/image-based PDF
```

### No AI Summary
```bash
# Check API keys
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# System falls back to rule-based (OK)
```

### Duplicate Not Detected
```bash
# Check email extraction
GET /api/resumes/debug/{resume_id}

# Verify: has_email = true
```

---

## 🔧 Configuration

### Required
```bash
DATABASE_URL=postgresql://user:pass@host/db
```

### Optional (AI)
```bash
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-ant-...
```

### Other
```bash
UPLOAD_DIR=./uploads
JWT_SECRET=your-secret
CORS_ORIGINS=http://localhost:3000
```

---

## 📁 Key Files

### Backend
- `services/parser.py` - Resume parsing (600+ lines)
- `services/scorer.py` - Match scoring
- `services/ai_evaluator.py` - AI evaluation
- `routers/resumes.py` - Upload & processing
- `models.py` - Database schema

### Frontend
- `pages/CandidatesPage.tsx` - Candidate list
- `pages/CandidateDetailPage.tsx` - Details view
- `types/index.ts` - TypeScript types

### Documentation
- `PRODUCTION_FIXES.md` - All fixes
- `TESTING_GUIDE.md` - Test cases
- `DEPLOYMENT_CHECKLIST.md` - Deploy steps
- `WORKFLOW_DIAGRAM.md` - System flow

---

## 🧪 Quick Tests

### Test 1: Fresher
```bash
# Upload resume with no work experience
# Expected: years_experience = 0
```

### Test 2: Senior
```bash
# Upload resume with 10 years experience
# Expected: Accurate calculation from dates
```

### Test 3: Corrupted
```bash
# Upload corrupted PDF
# Expected: parse_status = "failed"
```

### Test 4: Duplicate
```bash
# Upload same resume twice
# Expected: is_duplicate = true
```

---

## 🔍 Debug Commands

```bash
# Check logs
tail -f logs/hireiq.log

# Check database
psql $DATABASE_URL -c "SELECT * FROM candidates LIMIT 5"

# Check parsing
curl http://localhost:8000/api/resumes/debug/{id}

# Check services
ps aux | grep uvicorn
```

---

## 📊 Database Schema

### New Fields (Candidates)
```sql
parsing_confidence FLOAT
ai_recommendation VARCHAR(50)
ai_recommendation_reasoning TEXT
```

### New Fields (Work Experience)
```sql
company VARCHAR(255)
role VARCHAR(255)
duration_months INT DEFAULT 0
```

---

## 🎯 Critical Rules

### 1. Experience Calculation
```python
# ONLY from work history dates
# NEVER estimate or guess
if not work_experience:
    return 0.0  # Fresher
```

### 2. Data Extraction
```python
# ONLY from resume text
# NEVER invent or hallucinate
if not found_in_text:
    return None
```

### 3. AI Usage
```python
# AI = Evaluator (not extractor)
# Input: Structured JSON
# Output: Insights & recommendations
```

---

## 🚨 Red Flags

### In Code
- ❌ Random experience estimation
- ❌ AI extracting data
- ❌ Hardcoded credentials
- ❌ No error handling

### In Data
- ❌ Fresher with 2+ years
- ❌ Invented company names
- ❌ Skills not in resume
- ❌ Parsing confidence = 0

### In Logs
- ❌ Frequent extraction failures
- ❌ Database connection errors
- ❌ Unhandled exceptions
- ❌ AI API errors (if enabled)

---

## 💡 Best Practices

### 1. Always Check Confidence
```python
if parsing_confidence < 0.6:
    flag_for_manual_review()
```

### 2. Use Debug Endpoints
```bash
# Before investigating issues
GET /api/resumes/debug/{resume_id}
```

### 3. Validate Extraction
```python
# After parsing
assert years_experience >= 0
assert all(skill in text for skill in skills)
```

### 4. Handle Errors Gracefully
```python
try:
    extract_text()
except Exception as e:
    log_error(e)
    mark_as_failed()
```

---

## 📞 Quick Help

### Issue: Import Error
```bash
pip install -r requirements.txt
```

### Issue: Migration Failed
```bash
psql $DATABASE_URL -f migrations/add_parsing_confidence_and_recommendation.sql
```

### Issue: Service Won't Start
```bash
# Check logs
tail -f logs/hireiq.log

# Check port
lsof -i :8000
```

### Issue: Tests Failing
```bash
# See TESTING_GUIDE.md
# Use debug endpoints
# Check extraction quality
```

---

## 🎓 Learning Resources

1. **PRODUCTION_FIXES.md** - Understand all fixes
2. **TESTING_GUIDE.md** - Learn testing approach
3. **WORKFLOW_DIAGRAM.md** - Understand system flow
4. **API Docs** - http://localhost:8000/docs

---

## ✅ Deployment Checklist

- [ ] Run setup script
- [ ] Configure .env
- [ ] Run migration
- [ ] Test endpoints
- [ ] Check logs
- [ ] Verify parsing
- [ ] Monitor performance

---

## 🔗 Useful Links

- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Health: http://localhost:8000/health

---

**Print this card and keep it handy!**
