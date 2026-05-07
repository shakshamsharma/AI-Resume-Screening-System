# 🐳 Docker Quick Start - 2 Minutes to Running

## The Fastest Way to Run HireIQ

---

## ⚡ Super Quick Start

```bash
# 1. Navigate to project
cd AI-Resume-Screening

# 2. Start everything
docker-compose up --build

# 3. Wait 3-5 minutes for first build

# 4. Open browser
http://localhost:3000

# 5. Login
Email: admin@hireiq.com
Password: admin123
```

**Done!** 🎉

---

## 🎯 What You Get

- ✅ **Frontend** at http://localhost:3000
- ✅ **Backend API** at http://localhost:8000
- ✅ **API Docs** at http://localhost:8000/docs
- ✅ **PostgreSQL Database** (automatic)
- ✅ **All Production Fixes** (automatic)
- ✅ **Sample Data** (automatic)

---

## 🧪 Quick Test

### Test 1: Upload a Resume
1. Click "Upload Resumes"
2. Select a job
3. Drop a PDF resume
4. Click "Upload"
5. Wait 5-10 seconds
6. Go to "Candidates"
7. See parsed candidate ✅

### Test 2: Check Parsing Quality
```bash
# Get resume ID from upload response
# Then check debug endpoint
curl http://localhost:8000/api/resumes/debug/{resume_id}
```

### Test 3: Verify Zero Hallucinations
- Upload a **fresher resume** (no work experience)
- Expected: `years_experience: 0` ✅
- NOT: `years_experience: 2` ❌

---

## 🔍 Useful Commands

```bash
# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart

# Fresh start (deletes data)
docker-compose down -v && docker-compose up --build
```

---

## 🐛 Quick Troubleshooting

### Port Already in Use?
```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

### Build Failed?
```bash
# Clean build
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Can't Connect?
```bash
# Check services are running
docker-compose ps

# Check logs
docker-compose logs backend
```

---

## 🎓 Next Steps

1. **Test the fixes:** Upload resumes and verify accuracy
2. **Read docs:** See [PRODUCTION_FIXES.md](PRODUCTION_FIXES.md)
3. **Run tests:** See [TESTING_GUIDE.md](TESTING_GUIDE.md)
4. **Deploy:** See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

## 🆘 Need Help?

- **Full Docker Guide:** [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
- **Testing Guide:** [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **Quick Reference:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## ✅ Success Checklist

- [ ] Docker Desktop installed
- [ ] Ran `docker-compose up --build`
- [ ] Can access http://localhost:3000
- [ ] Can login with demo credentials
- [ ] Can upload a resume
- [ ] Resume parsed correctly
- [ ] Candidate shows accurate data

**If all checked, you're ready to go!** 🚀

---

**Docker makes it ridiculously easy!** 🐳
