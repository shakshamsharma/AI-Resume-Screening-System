# 🐳 Docker Deployment Guide

## Quick Start with Docker

The easiest way to run the entire HireIQ platform with all production fixes.

---

## 🚀 One-Command Start

```bash
# Start everything (database, backend, frontend)
docker-compose up --build
```

That's it! The application will be available at:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Database:** localhost:5432

---

## 📋 Prerequisites

### Required
- **Docker Desktop** (or Docker Engine + Docker Compose)
  - Download: https://www.docker.com/products/docker-desktop/
  - Minimum version: Docker 20.10+, Docker Compose 2.0+

### Optional (for AI evaluation)
- OpenAI API key OR Anthropic API key
- System works without these (falls back to rule-based)

---

## 🔧 Setup Steps

### Step 1: Clone/Download Project
```bash
cd AI-Resume-Screening
```

### Step 2: (Optional) Configure AI API Keys

Create a `.env` file in the project root:
```bash
# Optional: For AI-powered evaluation
OPENAI_API_KEY=sk-your-openai-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

**Note:** If you don't set these, the system will use rule-based evaluation (works perfectly fine).

### Step 3: Start Services
```bash
# Build and start all services
docker-compose up --build

# Or run in background (detached mode)
docker-compose up -d --build
```

### Step 4: Wait for Services to Start
The first build takes 3-5 minutes. You'll see:
```
✓ Database ready
✓ Running migrations...
✓ Backend server started
✓ Frontend ready
```

### Step 5: Access Application
- Open browser: http://localhost:3000
- Login with demo credentials:
  - Email: `admin@hireiq.com`
  - Password: `admin123`

---

## 🎯 What Docker Does Automatically

### 1. Database Setup ✅
- Creates PostgreSQL database
- Runs initial schema (`init.sql`)
- Runs production fixes migration
- Seeds demo data

### 2. Backend Setup ✅
- Installs all Python dependencies
- Installs PyMuPDF, pdfplumber, dateparser
- Downloads spaCy model
- Runs database migrations
- Starts FastAPI server

### 3. Frontend Setup ✅
- Installs Node.js dependencies
- Starts Vite dev server
- Connects to backend automatically

---

## 📊 Service Architecture

```
┌─────────────────────────────────────────────────┐
│  Frontend (React + Vite)                        │
│  Port: 3000                                     │
│  http://localhost:3000                          │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Backend (FastAPI)                              │
│  Port: 8000                                     │
│  http://localhost:8000                          │
│  • Resume parsing (pdfplumber + PyMuPDF)        │
│  • AI evaluation (optional)                     │
│  • Scoring engine                               │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Database (PostgreSQL 15)                       │
│  Port: 5432                                     │
│  • Candidates, Jobs, Resumes                    │
│  • Work Experience, Interviews                  │
└─────────────────────────────────────────────────┘
```

---

## 🔍 Useful Docker Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Check Service Status
```bash
docker-compose ps
```

### Execute Commands in Container
```bash
# Access backend shell
docker-compose exec backend bash

# Access database
docker-compose exec db psql -U hireiq -d hireiq

# Run Python commands
docker-compose exec backend python -c "import pdfplumber; print('OK')"
```

### Rebuild After Code Changes
```bash
# Rebuild and restart
docker-compose up --build

# Rebuild specific service
docker-compose up --build backend
```

---

## 🧪 Testing in Docker

### Test Backend
```bash
# Check health
curl http://localhost:8000/health

# Check API docs
open http://localhost:8000/docs

# Test resume upload (with auth token)
# See TESTING_GUIDE.md for detailed tests
```

### Test Database
```bash
# Connect to database
docker-compose exec db psql -U hireiq -d hireiq

# Check tables
\dt

# Check candidates
SELECT full_name, years_experience, overall_score FROM candidates LIMIT 5;

# Check new fields
\d candidates

# Exit
\q
```

### Test Parsing
```bash
# Upload a resume via UI
# Then check debug endpoint
curl http://localhost:8000/api/resumes/debug/{resume_id}
```

---

## 🐛 Troubleshooting

### Issue 1: Port Already in Use
**Error:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution:**
```bash
# Check what's using the port
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Issue 2: Database Connection Failed
**Error:** `could not connect to server`

**Solution:**
```bash
# Wait for database to be ready (takes 10-15 seconds)
docker-compose logs db

# Or restart services
docker-compose restart
```

### Issue 3: Migration Failed
**Error:** `relation "candidates" already exists`

**Solution:**
This is OK! It means the migration was already applied. The system handles this gracefully.

### Issue 4: Build Failed
**Error:** `failed to solve: process "/bin/sh -c pip install..."`

**Solution:**
```bash
# Clean build
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Issue 5: Frontend Can't Connect to Backend
**Error:** `Network Error` in browser console

**Solution:**
```bash
# Check backend is running
docker-compose ps

# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Issue 6: Out of Disk Space
**Error:** `no space left on device`

**Solution:**
```bash
# Clean up Docker
docker system prune -a --volumes

# Remove old images
docker image prune -a
```

---

## 🔐 Security Notes

### For Development
The default configuration is suitable for development:
- Default passwords (change in production)
- Debug mode enabled
- CORS allows all origins

### For Production
Update `docker-compose.yml`:
```yaml
environment:
  SECRET_KEY: ${SECRET_KEY}  # Use strong random key
  DATABASE_URL: ${DATABASE_URL}  # Use managed database
  CORS_ORIGINS: https://yourdomain.com
  DEBUG: false
```

And use `.env` file:
```bash
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:pass@prod-db:5432/hireiq
OPENAI_API_KEY=sk-...
```

---

## 📦 Data Persistence

### Volumes
Docker creates persistent volumes for:
- **postgres_data:** Database files
- **resume_uploads:** Uploaded resume files

### Backup Data
```bash
# Backup database
docker-compose exec db pg_dump -U hireiq hireiq > backup.sql

# Backup uploads
docker cp $(docker-compose ps -q backend):/app/uploads ./uploads_backup
```

### Restore Data
```bash
# Restore database
cat backup.sql | docker-compose exec -T db psql -U hireiq hireiq

# Restore uploads
docker cp ./uploads_backup $(docker-compose ps -q backend):/app/uploads
```

---

## 🚀 Production Deployment

### Using Docker Compose (Simple)
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d
```

### Using Docker Swarm (Scalable)
```bash
docker stack deploy -c docker-compose.yml hireiq
```

### Using Kubernetes (Enterprise)
```bash
# Convert to Kubernetes manifests
kompose convert -f docker-compose.yml

# Deploy
kubectl apply -f .
```

---

## 🔄 Development Workflow

### Hot Reload Enabled
Both backend and frontend support hot reload:
- **Backend:** Edit Python files → auto-reload
- **Frontend:** Edit React files → auto-reload

### Making Changes
```bash
# 1. Edit code in your IDE
# 2. Changes auto-reload in Docker
# 3. Test in browser
# 4. Commit changes
```

### Adding Dependencies

**Backend:**
```bash
# 1. Add to requirements.txt
# 2. Rebuild
docker-compose up --build backend
```

**Frontend:**
```bash
# 1. Add to package.json
# 2. Rebuild
docker-compose up --build frontend
```

---

## 📊 Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Database health
docker-compose exec db pg_isready -U hireiq
```

### Resource Usage
```bash
# Check resource usage
docker stats

# Check disk usage
docker system df
```

### Logs
```bash
# Follow all logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f backend
```

---

## 🎯 Quick Commands Reference

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Logs
docker-compose logs -f

# Status
docker-compose ps

# Rebuild
docker-compose up --build

# Clean start
docker-compose down -v && docker-compose up --build

# Access backend shell
docker-compose exec backend bash

# Access database
docker-compose exec db psql -U hireiq -d hireiq

# Backup database
docker-compose exec db pg_dump -U hireiq hireiq > backup.sql
```

---

## ✅ Verification Checklist

After starting with Docker, verify:

- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend accessible at http://localhost:8000
- [ ] API docs at http://localhost:8000/docs
- [ ] Can login with demo credentials
- [ ] Can create a job
- [ ] Can upload a resume
- [ ] Resume parsing works
- [ ] Candidate created with correct data
- [ ] Debug endpoint works: `/api/resumes/debug/{id}`

---

## 🎓 Learning Resources

- **Docker Docs:** https://docs.docker.com/
- **Docker Compose:** https://docs.docker.com/compose/
- **PostgreSQL in Docker:** https://hub.docker.com/_/postgres

---

## 🆘 Getting Help

### Check Logs First
```bash
docker-compose logs -f
```

### Common Issues
1. Port conflicts → Change ports in docker-compose.yml
2. Build failures → Clean build with `--no-cache`
3. Connection issues → Check service health
4. Migration errors → Usually OK, already applied

### Still Stuck?
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review [TESTING_GUIDE.md](TESTING_GUIDE.md)
3. Check Docker logs
4. Restart services

---

## 🎉 Success!

If you can:
- ✅ Access http://localhost:3000
- ✅ Login successfully
- ✅ Upload a resume
- ✅ See parsed candidate data

**You're all set! The production-grade ATS is running in Docker!**

---

## 📝 Next Steps

1. **Test the fixes:** See [TESTING_GUIDE.md](TESTING_GUIDE.md)
2. **Understand changes:** See [PRODUCTION_FIXES.md](PRODUCTION_FIXES.md)
3. **Deploy to production:** See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

**Docker makes it easy to run the entire platform with one command!** 🐳
