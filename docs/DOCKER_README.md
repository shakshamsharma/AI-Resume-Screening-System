# 🐳 Docker Setup - Complete Guide

## Yes! You Can Run This Project with Docker

**The easiest way to run the entire HireIQ platform with all production fixes.**

---

## 🎯 What Docker Gives You

### One Command Setup ✅
```bash
docker-compose up --build
```

### Everything Included ✅
- ✅ PostgreSQL database (automatic setup)
- ✅ Backend API with all production fixes
- ✅ Frontend React app
- ✅ All dependencies installed
- ✅ Database migrations run automatically
- ✅ Sample data loaded
- ✅ Hot reload for development

### No Manual Setup Required ✅
- ❌ No Python virtual environment
- ❌ No PostgreSQL installation
- ❌ No dependency management
- ❌ No database configuration
- ❌ No migration scripts to run

---

## 📋 Prerequisites

### Required
- **Docker Desktop** (or Docker Engine + Docker Compose)
  - Download: https://www.docker.com/products/docker-desktop/
  - Windows: Docker Desktop for Windows
  - Mac: Docker Desktop for Mac
  - Linux: Docker Engine + Docker Compose

### Check Installation
```bash
docker --version
# Should show: Docker version 20.10+ or higher

docker-compose --version
# Should show: Docker Compose version 2.0+ or higher
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Navigate to Project
```bash
cd AI-Resume-Screening
```

### Step 2: (Optional) Add AI API Keys
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API key (optional)
# OPENAI_API_KEY=sk-your-key-here
# OR
# ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Note:** AI keys are optional. System works perfectly without them using rule-based evaluation.

### Step 3: Start Everything
```bash
docker-compose up --build
```

**First build takes 3-5 minutes.** Subsequent starts are much faster (< 30 seconds).

---

## 🌐 Access the Application

Once started, access:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Demo Login Credentials
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@hireiq.com | admin123 |
| Recruiter | recruiter@hireiq.com | recruiter123 |

---

## 🔧 Docker Services

### Three Services Running

#### 1. Database (PostgreSQL 15)
- **Port:** 5432
- **Database:** hireiq
- **User:** hireiq
- **Password:** hireiq_secret
- **Volume:** postgres_data (persistent)

#### 2. Backend (FastAPI + Python)
- **Port:** 8000
- **Features:**
  - Resume parsing (pdfplumber + PyMuPDF)
  - AI evaluation (optional)
  - Scoring engine
  - All production fixes
- **Volume:** resume_uploads (persistent)

#### 3. Frontend (React + Vite)
- **Port:** 3000
- **Features:**
  - Modern React UI
  - Real-time updates
  - Responsive design

---

## 📊 What Happens on Startup

```
1. Database Container Starts
   ↓
2. Runs init.sql (creates schema)
   ↓
3. Backend Container Starts
   ↓
4. Waits for database to be ready
   ↓
5. Runs production fixes migration
   ↓
6. Starts FastAPI server
   ↓
7. Frontend Container Starts
   ↓
8. Starts Vite dev server
   ↓
9. ✅ Application Ready!
```

---

## 🎮 Common Docker Commands

### Start Services
```bash
# Start in foreground (see logs)
docker-compose up

# Start in background (detached)
docker-compose up -d

# Rebuild and start
docker-compose up --build
```

### Stop Services
```bash
# Stop services (keeps data)
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# Last 100 lines
docker-compose logs --tail=100
```

### Check Status
```bash
# List running services
docker-compose ps

# Check resource usage
docker stats
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Access Containers
```bash
# Backend shell
docker-compose exec backend bash

# Database shell
docker-compose exec db psql -U hireiq -d hireiq

# Frontend shell
docker-compose exec frontend sh
```

---

## 🧪 Testing in Docker

### Test Backend Health
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### Test API Docs
```bash
open http://localhost:8000/docs
# Opens interactive API documentation
```

### Test Resume Upload
1. Go to http://localhost:3000
2. Login with demo credentials
3. Click "Upload Resumes"
4. Select a job
5. Upload a PDF resume
6. Check "Candidates" page

### Test Debug Endpoint
```bash
# After uploading a resume
curl http://localhost:8000/api/resumes/debug/{resume_id}
```

### Test Database
```bash
# Connect to database
docker-compose exec db psql -U hireiq -d hireiq

# Check tables
\dt

# Check candidates
SELECT full_name, years_experience, overall_score 
FROM candidates 
LIMIT 5;

# Exit
\q
```

---

## 🔄 Development Workflow

### Hot Reload Enabled ✅

Both backend and frontend support hot reload:

**Backend:**
1. Edit Python files in `backend/`
2. Save
3. Server auto-reloads
4. Changes reflected immediately

**Frontend:**
1. Edit React files in `frontend/src/`
2. Save
3. Browser auto-refreshes
4. Changes reflected immediately

### Adding Dependencies

**Backend (Python):**
```bash
# 1. Add to backend/requirements.txt
# 2. Rebuild backend
docker-compose up --build backend
```

**Frontend (Node):**
```bash
# 1. Add to frontend/package.json
# 2. Rebuild frontend
docker-compose up --build frontend
```

---

## 💾 Data Persistence

### Persistent Volumes

Docker creates two persistent volumes:

1. **postgres_data** - Database files
2. **resume_uploads** - Uploaded resume files

**Data survives container restarts!**

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

### Fresh Start (Delete All Data)
```bash
docker-compose down -v
docker-compose up --build
```

---

## 🐛 Troubleshooting

### Issue 1: Port Already in Use
**Error:** `Bind for 0.0.0.0:8000 failed`

**Solution:**
```bash
# Option 1: Stop conflicting service
lsof -i :8000  # Find process
kill -9 <PID>  # Kill it

# Option 2: Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Issue 2: Build Failed
**Error:** `failed to solve: process "/bin/sh -c pip install..."`

**Solution:**
```bash
# Clean build
docker-compose down -v
docker system prune -a
docker-compose build --no-cache
docker-compose up
```

### Issue 3: Database Connection Failed
**Error:** `could not connect to server`

**Solution:**
```bash
# Wait for database (takes 10-15 seconds)
docker-compose logs db

# Or restart
docker-compose restart
```

### Issue 4: Migration Error
**Error:** `relation "candidates" already exists`

**Solution:**
This is OK! Migration was already applied. System handles this gracefully.

### Issue 5: Out of Memory
**Error:** `Killed` or container crashes

**Solution:**
```bash
# Increase Docker memory
# Docker Desktop → Settings → Resources → Memory
# Set to at least 4GB
```

### Issue 6: Slow Performance
**Solution:**
```bash
# Check resource usage
docker stats

# Increase resources in Docker Desktop
# Settings → Resources → CPUs (2+), Memory (4GB+)
```

---

## 🔐 Security Notes

### Development (Current Setup)
- ✅ Suitable for local development
- ⚠️ Default passwords (change for production)
- ⚠️ Debug mode enabled
- ⚠️ CORS allows all origins

### Production Deployment
Update `docker-compose.yml`:
```yaml
environment:
  SECRET_KEY: ${SECRET_KEY}  # Strong random key
  DATABASE_URL: ${DATABASE_URL}  # Managed database
  CORS_ORIGINS: https://yourdomain.com
  DEBUG: false
```

Create `.env` file:
```bash
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:pass@prod-db:5432/hireiq
OPENAI_API_KEY=sk-...
```

---

## 📦 Docker Compose Configuration

### Current Setup
```yaml
services:
  db:        # PostgreSQL 15
  backend:   # FastAPI + Python 3.11
  frontend:  # React + Vite

volumes:
  postgres_data:    # Database persistence
  resume_uploads:   # Resume file persistence
```

### Customization
Edit `docker-compose.yml` to:
- Change ports
- Add environment variables
- Mount additional volumes
- Add new services

---

## 🚀 Production Deployment Options

### Option 1: Docker Compose (Simple)
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Option 2: Docker Swarm (Scalable)
```bash
docker stack deploy -c docker-compose.yml hireiq
```

### Option 3: Kubernetes (Enterprise)
```bash
# Convert to K8s manifests
kompose convert -f docker-compose.yml

# Deploy
kubectl apply -f .
```

### Option 4: Cloud Platforms
- **AWS:** ECS, Fargate, or EKS
- **Google Cloud:** Cloud Run or GKE
- **Azure:** Container Instances or AKS
- **DigitalOcean:** App Platform or Kubernetes

---

## ✅ Verification Checklist

After starting with Docker:

- [ ] All services running: `docker-compose ps`
- [ ] Frontend accessible: http://localhost:3000
- [ ] Backend accessible: http://localhost:8000
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Can login with demo credentials
- [ ] Can create a job
- [ ] Can upload a resume
- [ ] Resume parsing works correctly
- [ ] Candidate created with accurate data
- [ ] Debug endpoint works
- [ ] No errors in logs: `docker-compose logs`

---

## 📚 Additional Resources

### Documentation
- **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)** - 2-minute quick start
- **[DOCKER_GUIDE.md](DOCKER_GUIDE.md)** - Complete Docker guide
- **[PRODUCTION_FIXES.md](PRODUCTION_FIXES.md)** - All production fixes
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Testing approach

### External Resources
- **Docker Docs:** https://docs.docker.com/
- **Docker Compose:** https://docs.docker.com/compose/
- **PostgreSQL:** https://hub.docker.com/_/postgres

---

## 🎉 Success!

If you can:
- ✅ Access http://localhost:3000
- ✅ Login successfully
- ✅ Upload a resume
- ✅ See accurate candidate data
- ✅ No hallucinations (freshers show 0 years)

**Congratulations! The production-grade ATS is running!** 🎊

---

## 📞 Need Help?

1. **Check logs:** `docker-compose logs -f`
2. **Review guides:** See documentation links above
3. **Test endpoints:** Use debug endpoints
4. **Restart services:** `docker-compose restart`

---

**Docker makes running the entire platform incredibly easy!** 🐳

**One command. Everything works. Production-ready.** ✨
