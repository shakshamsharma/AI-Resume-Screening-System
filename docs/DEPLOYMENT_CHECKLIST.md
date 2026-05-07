# Production Deployment Checklist

## 📋 Pre-Deployment Checklist

### 1. Code Review ✓
- [x] All production fixes implemented
- [x] Code reviewed and tested
- [x] No hardcoded credentials
- [x] Error handling comprehensive
- [x] Logging configured properly

### 2. Dependencies ✓
- [x] `requirements.txt` updated
- [x] All dependencies installed
- [x] Version pinning verified
- [x] Security vulnerabilities checked

### 3. Database ✓
- [x] Migration scripts created
- [x] Schema changes documented
- [x] Backup strategy defined
- [x] Rollback plan prepared

### 4. Configuration ✓
- [x] `.env.example` created
- [x] Environment variables documented
- [x] Secrets management configured
- [x] CORS origins configured

### 5. Testing ✓
- [x] Unit tests passing
- [x] Integration tests passing
- [x] Manual testing completed
- [x] Edge cases tested

---

## 🚀 Deployment Steps

### Step 1: Backup Current System
```bash
# Backup database
pg_dump -U username -d hireiq_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup uploaded files
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz uploads/

# Backup environment config
cp .env .env.backup
```

### Step 2: Update Code
```bash
# Pull latest code
git pull origin main

# Or upload files if not using git
# scp -r backend/ user@server:/path/to/app/
```

### Step 3: Install Dependencies
```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install/update dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "pdfplumber|PyMuPDF|dateparser|openai|anthropic"
```

### Step 4: Run Database Migration
```bash
# Connect to database
psql $DATABASE_URL

# Run migration
\i migrations/add_parsing_confidence_and_recommendation.sql

# Verify changes
\d candidates
\d work_experience

# Exit
\q
```

### Step 5: Update Environment Variables
```bash
# Edit .env file
nano .env

# Required variables:
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Optional (for AI evaluation):
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-ant-...

# Other settings:
UPLOAD_DIR=./uploads
JWT_SECRET=your-secret-key
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Step 6: Test Backend
```bash
# Start backend in test mode
uvicorn main:app --host 0.0.0.0 --port 8000

# In another terminal, test endpoints
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

curl http://localhost:8000/
# Expected: {"message":"HireIQ API running","docs":"/docs"}

# Test resume upload (with auth token)
# See TESTING_GUIDE.md for detailed tests
```

### Step 7: Update Frontend (if needed)
```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Test build
npm run preview
```

### Step 8: Restart Services
```bash
# If using systemd
sudo systemctl restart hireiq-backend
sudo systemctl restart hireiq-frontend

# If using Docker
docker-compose down
docker-compose up -d --build

# If using PM2
pm2 restart hireiq-backend
pm2 restart hireiq-frontend

# Verify services are running
ps aux | grep uvicorn
# OR
docker ps
# OR
pm2 status
```

### Step 9: Smoke Tests
```bash
# Test critical flows:

# 1. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hireiq.com","password":"admin123"}'

# 2. Upload resume (use token from login)
# See TESTING_GUIDE.md

# 3. Check parsing
curl http://localhost:8000/api/resumes/status/{resume_id} \
  -H "Authorization: Bearer {token}"

# 4. Verify candidate created
curl http://localhost:8000/api/candidates/{candidate_id} \
  -H "Authorization: Bearer {token}"
```

### Step 10: Monitor Logs
```bash
# Backend logs
tail -f logs/hireiq.log

# Or if using Docker
docker logs -f hireiq-backend

# Or if using systemd
journalctl -u hireiq-backend -f

# Watch for errors:
# - Text extraction failures
# - Database connection issues
# - AI API errors (if enabled)
```

---

## ✅ Post-Deployment Verification

### 1. Functional Tests
- [ ] User can login
- [ ] User can create job
- [ ] User can upload resumes
- [ ] Resumes are parsed correctly
- [ ] Candidates are created
- [ ] Scores are calculated
- [ ] AI evaluation works (if enabled)
- [ ] Debug endpoints accessible

### 2. Data Integrity
- [ ] Existing candidates still accessible
- [ ] New fields populated correctly
- [ ] Work experience has duration
- [ ] Parsing confidence calculated
- [ ] AI recommendations generated

### 3. Performance
- [ ] Resume upload < 5 seconds
- [ ] Parsing completes < 10 seconds
- [ ] API response times < 500ms
- [ ] Database queries optimized
- [ ] No memory leaks

### 4. Error Handling
- [ ] Corrupted PDFs handled gracefully
- [ ] Duplicate detection works
- [ ] Keyword stuffing flagged
- [ ] Low confidence resumes flagged
- [ ] Error messages clear

### 5. Security
- [ ] Authentication required
- [ ] JWT tokens working
- [ ] CORS configured correctly
- [ ] File upload restrictions enforced
- [ ] No sensitive data in logs

---

## 🔍 Monitoring Setup

### Application Metrics
```bash
# Monitor API response times
# Monitor parsing success rate
# Monitor AI API usage (if enabled)
# Monitor database connections
# Monitor disk space (uploads folder)
```

### Alerts to Configure
1. **High Error Rate** (> 5% of requests)
2. **Slow Parsing** (> 30 seconds per resume)
3. **Database Connection Failures**
4. **Disk Space Low** (< 10% free)
5. **AI API Failures** (if enabled)

### Log Monitoring
```bash
# Watch for critical errors
grep -i "error\|exception\|failed" logs/hireiq.log

# Monitor parsing failures
grep "parse_status.*failed" logs/hireiq.log

# Check AI evaluation
grep "AI.*failed" logs/hireiq.log
```

---

## 🔄 Rollback Plan

### If Deployment Fails

#### Step 1: Stop New Services
```bash
sudo systemctl stop hireiq-backend
# OR
docker-compose down
# OR
pm2 stop hireiq-backend
```

#### Step 2: Restore Database
```bash
# Restore from backup
psql $DATABASE_URL < backup_YYYYMMDD_HHMMSS.sql
```

#### Step 3: Restore Code
```bash
# Revert to previous version
git checkout previous-tag
# OR restore from backup
```

#### Step 4: Restore Environment
```bash
cp .env.backup .env
```

#### Step 5: Restart Old Services
```bash
sudo systemctl start hireiq-backend
# OR
docker-compose up -d
# OR
pm2 start hireiq-backend
```

#### Step 6: Verify Rollback
```bash
# Test critical endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/jobs
```

---

## 📊 Success Criteria

Deployment is successful if:

1. ✅ **All services running** without errors
2. ✅ **Database migration** completed successfully
3. ✅ **Smoke tests passing** (login, upload, parse)
4. ✅ **No critical errors** in logs
5. ✅ **Performance acceptable** (< 10s per resume)
6. ✅ **Existing data intact** (no data loss)
7. ✅ **New features working** (confidence, AI recommendations)
8. ✅ **Error handling working** (corrupted files, duplicates)

---

## 🐛 Common Issues & Solutions

### Issue 1: Migration Fails
**Symptom:** SQL error when running migration
**Solution:**
```bash
# Check if columns already exist
psql $DATABASE_URL -c "\d candidates"

# If columns exist, skip migration
# If not, check for syntax errors in SQL
```

### Issue 2: Import Errors
**Symptom:** `ModuleNotFoundError: No module named 'fitz'`
**Solution:**
```bash
pip install PyMuPDF
# Note: Package name is PyMuPDF, import name is fitz
```

### Issue 3: AI Evaluation Fails
**Symptom:** Candidates created but no AI summary
**Solution:**
```bash
# Check if API key is set
echo $OPENAI_API_KEY

# Check logs for AI errors
grep "AI.*failed" logs/hireiq.log

# System will fallback to rule-based - this is OK
```

### Issue 4: Parsing Confidence Always 0
**Symptom:** All candidates have parsing_confidence = 0
**Solution:**
```bash
# Check if migration ran
psql $DATABASE_URL -c "SELECT parsing_confidence FROM candidates LIMIT 5"

# If NULL, run migration again
# If 0, check parser.py is updated
```

### Issue 5: Experience Still Wrong
**Symptom:** Freshers showing 2+ years
**Solution:**
```bash
# Verify parser.py is updated
grep "calculate_total_experience_years" backend/services/parser.py

# Check work experience extraction
curl http://localhost:8000/api/resumes/debug/{resume_id}

# Verify work_experience array is populated
```

---

## 📞 Support Contacts

### Technical Issues
- Check logs first
- Use debug endpoints
- Review TESTING_GUIDE.md
- Check PRODUCTION_FIXES.md

### Emergency Rollback
- Follow rollback plan above
- Restore from backups
- Contact system administrator

---

## 📝 Deployment Log Template

```
Deployment Date: ___________
Deployed By: ___________
Version: ___________

Pre-Deployment:
[ ] Code reviewed
[ ] Tests passing
[ ] Backups created
[ ] Team notified

Deployment:
[ ] Code updated
[ ] Dependencies installed
[ ] Migration ran
[ ] Services restarted
[ ] Smoke tests passed

Post-Deployment:
[ ] Monitoring configured
[ ] Logs checked
[ ] Performance verified
[ ] Team notified

Issues Encountered:
___________________________________________
___________________________________________

Resolution:
___________________________________________
___________________________________________

Status: SUCCESS / ROLLBACK
```

---

## 🎯 Next Steps After Deployment

1. **Monitor for 24 hours**
   - Watch error rates
   - Check parsing success
   - Verify AI evaluation

2. **Gather Feedback**
   - User experience
   - Performance issues
   - Feature requests

3. **Optimize**
   - Database queries
   - Parsing speed
   - AI prompts

4. **Document**
   - Update runbooks
   - Record issues
   - Share learnings

---

**Remember:** Always test in staging before production!
