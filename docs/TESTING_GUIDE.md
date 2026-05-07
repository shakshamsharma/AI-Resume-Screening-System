# Testing Guide - Production Fixes Validation

## 🎯 Purpose

This guide helps you verify that all production fixes are working correctly and that the system no longer hallucinates data.

---

## 🧪 Test Cases

### Test 1: Fresher Resume (Zero Experience)

**Objective:** Verify system correctly identifies freshers without inventing experience.

**Test Resume Content:**
```
John Doe
john.doe@email.com | +1-234-567-8900

EDUCATION
Bachelor of Technology in Computer Science
XYZ University (2020-2024)

SKILLS
Python, JavaScript, React, Node.js, MongoDB

PROJECTS
- Built a todo app using MERN stack
- Created a weather app with React
```

**Expected Results:**
- ✅ `years_experience: 0` or `0.0`
- ✅ `education_level: "bachelors"`
- ✅ `skills: ["python", "javascript", "react", "node.js", "mongodb"]`
- ✅ `work_experience: []` (empty array)
- ✅ AI summary mentions "fresher" or "entry-level"

**How to Test:**
```bash
# 1. Upload resume
POST /api/resumes/upload
{
  "job_id": "...",
  "files": [fresher_resume.pdf]
}

# 2. Check debug endpoint
GET /api/resumes/debug/{resume_id}

# 3. Verify candidate
GET /api/candidates/{candidate_id}
```

**Red Flags (FAILURES):**
- ❌ `years_experience: 2` or any non-zero value
- ❌ AI summary says "2-year professional"
- ❌ Invented company names in work_experience

---

### Test 2: Senior Professional (10+ Years)

**Test Resume Content:**
```
Jane Smith
jane.smith@email.com | +1-987-654-3210

EXPERIENCE
Senior Software Engineer | Google Inc
Jan 2018 - Present
- Led team of 5 engineers
- Built microservices architecture

Software Engineer | Microsoft Corporation
Jun 2014 - Dec 2017
- Developed cloud solutions
- Worked on Azure platform

EDUCATION
M.S. Computer Science | Stanford University (2012-2014)

SKILLS
Python, Java, AWS, Kubernetes, Docker, Microservices
```

**Expected Results:**
- ✅ `years_experience: 9.5` (calculated from dates)
- ✅ `work_experience: [2 entries]`
- ✅ First entry: `company: "Google Inc"`, `is_current: true`
- ✅ Second entry: `company: "Microsoft Corporation"`, `duration_months: 42`
- ✅ `current_company: "Google Inc"`
- ✅ `education_level: "masters"`

**Calculation Verification:**
```
Jan 2018 - Present (May 2026) = 100 months = 8.3 years
Jun 2014 - Dec 2017 = 42 months = 3.5 years
Total = 11.8 years
```

**Red Flags (FAILURES):**
- ❌ Experience doesn't match date calculation
- ❌ Missing work experience entries
- ❌ Incorrect company names
- ❌ `is_current: false` for current job

---

### Test 3: Corrupted/Image-Based PDF

**Objective:** Verify system handles unreadable files gracefully.

**Test File:** Upload a scanned image PDF or corrupted file

**Expected Results:**
- ✅ `parse_status: "failed"`
- ✅ `flag_reason: "Text extraction failed - file may be corrupted or image-based PDF"`
- ✅ `parsing_confidence: < 0.3`
- ✅ No candidate created

**How to Test:**
```bash
# Upload corrupted file
POST /api/resumes/upload

# Check status
GET /api/resumes/status/{resume_id}
```

**Red Flags (FAILURES):**
- ❌ System creates candidate with random data
- ❌ No error message
- ❌ Invented experience or skills

---

### Test 4: Duplicate Detection

**Objective:** Verify duplicate resumes are detected and not processed twice.

**Test Steps:**
1. Upload resume A (john@email.com)
2. Upload same resume again
3. Upload different resume with same email

**Expected Results:**
- ✅ First upload: `is_duplicate: false`, candidate created
- ✅ Second upload: `is_duplicate: true`, no candidate created
- ✅ Third upload: `is_duplicate: true`, no candidate created

**How to Test:**
```bash
# Upload first time
POST /api/resumes/upload
# Check: is_duplicate = false

# Upload again
POST /api/resumes/upload
# Check: is_duplicate = true
```

---

### Test 5: Keyword Stuffing Detection

**Test Resume Content:**
```
John Doe
john@email.com

SKILLS
Python Python Python Python Python Python Python Python
Java Java Java Java Java Java Java Java Java Java
JavaScript JavaScript JavaScript JavaScript JavaScript
React React React React React React React React
AWS AWS AWS AWS AWS AWS AWS AWS AWS AWS AWS AWS
Docker Docker Docker Docker Docker Docker Docker
Kubernetes Kubernetes Kubernetes Kubernetes Kubernetes
[... 100+ repeated skills ...]
```

**Expected Results:**
- ✅ `is_flagged: true`
- ✅ `flag_reason: "Suspected keyword stuffing or manipulation"`
- ✅ Candidate still created but flagged for review

---

### Test 6: Parsing Confidence Scores

**Objective:** Verify confidence scoring works correctly.

**Test Cases:**

| Resume Quality | Expected Confidence | Expected Flag |
|---------------|---------------------|---------------|
| Perfect (all fields) | 0.8 - 1.0 | None |
| Good (missing phone) | 0.6 - 0.8 | None |
| Fair (missing contact) | 0.4 - 0.6 | Manual review |
| Poor (minimal text) | 0.0 - 0.4 | Manual review |

**How to Test:**
```bash
GET /api/resumes/debug/{resume_id}

# Check response:
{
  "parsing_confidence": 0.85,
  "needs_manual_review": false,
  "extraction_quality": {
    "name_confidence": 0.85,
    "has_email": true,
    "has_phone": true,
    "skills_count": 12,
    "work_confidence": 0.8
  }
}
```

---

### Test 7: Date Parsing Variations

**Objective:** Verify system handles various date formats.

**Test Date Formats:**
```
Jan 2020 - Present
January 2020 - Dec 2022
01/2020 - 12/2022
2020 - 2022
Jun 2019 - Current
2018 - Now
```

**Expected Results:**
- ✅ All formats parsed correctly
- ✅ "Present", "Current", "Now" treated as current date
- ✅ Duration calculated accurately

---

### Test 8: Skill Matching Accuracy

**Objective:** Verify skill extraction doesn't have false positives.

**Test Resume:**
```
SKILLS
Python, JavaScript, React, Node.js, PostgreSQL

EXPERIENCE
Worked on Python projects
Used JavaScript for frontend
```

**Expected Results:**
- ✅ Skills: `["python", "javascript", "react", "node.js", "postgresql"]`
- ✅ No false positives like "worked", "used", "projects"
- ✅ Word boundary matching prevents "JavaScript" from matching "Java"

---

### Test 9: AI Evaluation (If Enabled)

**Objective:** Verify AI provides insights without inventing data.

**Test:**
```bash
# Upload resume and check candidate
GET /api/candidates/{candidate_id}

# Verify AI fields:
{
  "ai_summary": "5-year senior engineer at Google with Python, AWS background.",
  "ai_fit_explanation": "Scored 85/100 due to strong skill match...",
  "ai_recommendation": "strong_yes",
  "ai_recommendation_reasoning": "Excellent match with all priority skills..."
}
```

**Expected:**
- ✅ AI summary matches extracted data
- ✅ No invented companies or skills
- ✅ Recommendation aligns with score

**Red Flags:**
- ❌ AI mentions skills not in resume
- ❌ AI invents experience not in work history
- ❌ AI creates fake company names

---

### Test 10: Score Calculation Accuracy

**Objective:** Verify deterministic scoring.

**Test Scenario:**
```
Job Requirements:
- Skills: Python, AWS, Docker, Kubernetes
- Priority: Python, AWS
- Experience: 3-5 years

Candidate:
- Skills: Python, AWS, Docker
- Experience: 4 years
```

**Expected Calculation:**
```
Skills Match:
- Matched: Python, AWS, Docker (3/4 = 75%)
- Priority matched: Python, AWS (2/2 = 100%)
- Score: (0.75 * 0.6 + 1.0 * 0.4) * 100 = 85

Experience Match:
- 4 years in range 3-5 = 90-100 score

Overall Score:
- Skills (40%): 85 * 0.4 = 34
- Experience (25%): 95 * 0.25 = 23.75
- ... other factors
- Total: ~75-85
```

**How to Test:**
```bash
# Create job with specific requirements
POST /api/jobs

# Upload matching resume
POST /api/resumes/upload

# Verify scores
GET /api/candidates/{candidate_id}
```

---

## 🔍 Debug Endpoints

### 1. Resume Debug Endpoint
```bash
GET /api/resumes/debug/{resume_id}
```

**Returns:**
- Extraction quality metrics
- Parsing confidence
- Extracted data breakdown
- Flags and warnings

### 2. Resume Status Endpoint
```bash
GET /api/resumes/status/{resume_id}
```

**Returns:**
- Processing status
- Duplicate flag
- Candidate ID
- Overall score

---

## ✅ Acceptance Criteria

### System is PRODUCTION-READY if:

1. ✅ **Zero Hallucinations**
   - No invented experience
   - No fake companies
   - No random skills

2. ✅ **Accurate Experience Calculation**
   - Freshers show 0 years
   - Seniors show correct calculation
   - Dates parsed correctly

3. ✅ **Robust Error Handling**
   - Corrupted files detected
   - Duplicates prevented
   - Keyword stuffing flagged

4. ✅ **Quality Validation**
   - Confidence scores accurate
   - Manual review triggered appropriately
   - Debug info available

5. ✅ **Deterministic Scoring**
   - Same resume = same score
   - Scores explainable
   - No randomness

---

## 🚨 Critical Failures

### STOP and FIX if you see:

1. ❌ **Fresher with 2+ years experience**
   - Check: `calculate_total_experience_years()`
   - Verify: Work history parsing

2. ❌ **Invented company names**
   - Check: Work experience extraction
   - Verify: No AI in extraction phase

3. ❌ **Random skills not in resume**
   - Check: Skill extraction logic
   - Verify: Word boundary matching

4. ❌ **Scores change on re-upload**
   - Check: Scoring logic
   - Verify: No randomness

5. ❌ **No error on corrupted file**
   - Check: Extraction confidence
   - Verify: Error handling

---

## 📊 Test Results Template

```
Test Date: ___________
Tester: ___________

| Test Case | Status | Notes |
|-----------|--------|-------|
| Fresher Resume | ✅/❌ | |
| Senior Professional | ✅/❌ | |
| Corrupted PDF | ✅/❌ | |
| Duplicate Detection | ✅/❌ | |
| Keyword Stuffing | ✅/❌ | |
| Confidence Scoring | ✅/❌ | |
| Date Parsing | ✅/❌ | |
| Skill Matching | ✅/❌ | |
| AI Evaluation | ✅/❌ | |
| Score Calculation | ✅/❌ | |

Overall: PASS / FAIL
```

---

## 🎓 Best Practices

1. **Test with Real Resumes**: Use actual resumes from various sources
2. **Test Edge Cases**: Unusual formats, missing sections, etc.
3. **Verify Calculations**: Manually check experience calculations
4. **Check Logs**: Review console output for errors
5. **Use Debug Endpoints**: Leverage debugging tools

---

## 📞 Troubleshooting

### Issue: Experience still wrong
**Solution:** Check `backend/services/parser.py` line 250-280

### Issue: Skills not extracted
**Solution:** Check word boundary matching in skill extraction

### Issue: Low confidence scores
**Solution:** Review extraction quality factors

### Issue: AI hallucinating
**Solution:** Verify AI receives structured data, not raw text

---

## ✨ Success Indicators

You'll know the system is working when:
- ✅ Freshers consistently show 0 years
- ✅ Experience matches manual calculation
- ✅ No invented data in any field
- ✅ Confidence scores make sense
- ✅ Errors are caught and logged
- ✅ Scores are repeatable

---

**Remember:** The goal is ZERO HALLUCINATIONS. All data must come from the resume.
