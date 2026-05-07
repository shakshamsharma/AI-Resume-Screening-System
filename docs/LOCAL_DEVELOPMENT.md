# 🏠 Local Development Guide

**Date:** May 7, 2026  
**Status:** ✅ Ready for Local Development

---

## 🚀 Quick Start (Docker)

The easiest way to run this project locally is with Docker:

```bash
# 1. Navigate to project folder
cd hireiq

# 2. Start everything with one command
docker-compose up --build

# 3. Open in browser
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**That's it!** Everything runs automatically:
- ✅ PostgreSQL database
- ✅ Backend API (FastAPI)
- ✅ Frontend (React)
- ✅ Database migrations
- ✅ All dependencies installed

---

## 📋 Prerequisites

### Required
- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
- **Git** - For cloning the repository

### Optional (for non-Docker development)
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 15**

---

## 🐳 Docker Development (Recommended)

### First Time Setup

```bash
# 1. Clone repository (if not already)
git clone <your-repo-url>
cd hireiq

# 2. Copy environment file (optional)
cp .env.example .env

# 3. Start all services
docker-compose up --build
```

**Wait 2-3 minutes** for first build (downloads images, installs dependencies)

### What Docker Does Automatically

1. ✅ Creates PostgreSQL database
2. ✅ Runs database migrations (`init.sql`)
3. ✅ Installs Python dependencies
4. ✅ Downloads spaCy NLP model
5. ✅ Installs Node.js dependencies
6. ✅ Starts backend API server
7. ✅ Starts frontend dev server
8. ✅ Connects everything together

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | React application |
| Backend API | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Database | localhost:5432 | PostgreSQL (internal) |

### Demo Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@hireiq.com | admin123 |
| Recruiter | recruiter@hireiq.com | recruiter123 |

---

## 🛠️ Daily Development Commands

### Start Services
```bash
# Start all services
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# Start with rebuild (after code changes)
docker-compose up --build
```

### Stop Services
```bash
# Stop services (Ctrl+C in terminal)
# Or:
docker-compose down

# Stop and remove volumes (clean slate)
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
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

### Execute Commands in Containers
```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh

# Database shell
docker-compose exec db psql -U hireiq -d hireiq
```

---

## 💻 Non-Docker Development (Manual Setup)

If you prefer not to use Docker:

### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Download spaCy model
python -m spacy download en_core_web_sm

# 6. Start PostgreSQL (separate terminal)
# Option A: Docker
docker run -d \
  --name hireiq-db \
  -e POSTGRES_DB=hireiq \
  -e POSTGRES_USER=hireiq \
  -e POSTGRES_PASSWORD=hireiq_secret \
  -p 5432:5432 \
  postgres:15-alpine

# Option B: Local PostgreSQL installation
# (Configure connection in .env)

# 7. Run database initialization
psql postgresql://hireiq:hireiq_secret@localhost:5432/hireiq < init.sql

# 8. Start backend server
DATABASE_URL=postgresql://hireiq:hireiq_secret@localhost:5432/hireiq \
uvicorn main:app --reload --port 8000
```

Backend will run on: http://localhost:8000

### Frontend Setup

```bash
# 1. Navigate to frontend (new terminal)
cd frontend

# 2. Install dependencies
npm install

# 3. Start dev server
VITE_API_URL=http://localhost:8000 npm run dev
```

Frontend will run on: http://localhost:5173 or http://localhost:3000

---

## 🔧 Configuration

### Environment Variables

#### Backend (`.env` or `backend/.env`)
```env
# Database
DATABASE_URL=postgresql://hireiq:hireiq_secret@localhost:5432/hireiq

# Security
SECRET_KEY=your-secret-key-here

# AI APIs (Optional)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# File Upload
UPLOAD_DIR=./uploads
```

#### Frontend (`.env` or `frontend/.env`)
```env
# Backend API URL
VITE_API_URL=http://localhost:8000
```

---

## 🧪 Testing

### Test Resume Upload
1. Go to http://localhost:3000
2. Login with demo credentials
3. Create a new job
4. Upload a sample resume (PDF/DOCX)
5. View parsed candidate data

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hireiq.com","password":"admin123"}'

# View API docs
open http://localhost:8000/docs
```

---

## 🐛 Troubleshooting

### Issue 1: Port Already in Use

**Error:** `Port 3000 is already allocated`

**Solution:**
```bash
# Find process using port
# Windows:
netstat -ano | findstr :3000
taskkill /PID <process-id> /F

# Mac/Linux:
lsof -ti:3000 | xargs kill -9

# Or change port in docker-compose.yml
```

### Issue 2: Database Connection Failed

**Error:** `could not connect to server`

**Solution:**
```bash
# Check if database container is running
docker-compose ps

# Restart database
docker-compose restart db

# Check logs
docker-compose logs db
```

### Issue 3: Frontend Can't Reach Backend

**Error:** `Network Error` or `Failed to fetch`

**Solution:**
1. Check backend is running: http://localhost:8000/health
2. Check CORS settings in `backend/main.py`
3. Verify `VITE_API_URL` in frontend `.env`

### Issue 4: Module Not Found

**Error:** `ModuleNotFoundError: No module named 'X'`

**Solution:**
```bash
# Rebuild containers
docker-compose down
docker-compose up --build

# Or for non-Docker:
pip install -r requirements.txt
```

### Issue 5: Database Migration Failed

**Error:** `relation "users" does not exist`

**Solution:**
```bash
# Re-run database initialization
docker-compose exec db psql -U hireiq -d hireiq < /docker-entrypoint-initdb.d/init.sql

# Or restart with clean database
docker-compose down -v
docker-compose up --build
```

---

## 📁 Project Structure

```
hireiq/
├── backend/                    # FastAPI backend
│   ├── routers/               # API endpoints
│   ├── services/              # Business logic
│   ├── utils/                 # Helper functions
│   ├── main.py                # FastAPI app
│   ├── models.py              # Database models
│   ├── database.py            # DB connection
│   ├── init.sql               # Database schema
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Backend container
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── pages/            # Page components
│   │   ├── components/       # Reusable components
│   │   ├── utils/            # API client
│   │   └── types/            # TypeScript types
│   ├── package.json          # Node dependencies
│   └── Dockerfile            # Frontend container
│
├── docs/                       # Documentation
├── docker-compose.yml         # Docker orchestration
├── .env.example               # Environment template
└── README.md                  # Main readme
```

---

## 🔄 Development Workflow

### Making Changes

1. **Edit code** in your IDE
2. **Changes auto-reload:**
   - Backend: FastAPI auto-reloads on save
   - Frontend: Vite HMR (Hot Module Replacement)
3. **Test changes** in browser
4. **Commit to Git**

### Adding Dependencies

**Backend:**
```bash
# Add to requirements.txt
echo "new-package==1.0.0" >> backend/requirements.txt

# Rebuild container
docker-compose up --build backend
```

**Frontend:**
```bash
# Install package
docker-compose exec frontend npm install new-package

# Or rebuild
docker-compose up --build frontend
```

### Database Changes

```bash
# Create migration file in backend/migrations/
# Then run:
docker-compose exec db psql -U hireiq -d hireiq < /path/to/migration.sql
```

---

## 🎯 Common Tasks

### Reset Database
```bash
docker-compose down -v
docker-compose up --build
```

### View Database
```bash
# Connect to database
docker-compose exec db psql -U hireiq -d hireiq

# List tables
\dt

# Query users
SELECT * FROM users;

# Exit
\q
```

### Check Logs for Errors
```bash
# Backend logs
docker-compose logs -f backend | grep ERROR

# Frontend logs
docker-compose logs -f frontend
```

### Clean Up Docker
```bash
# Remove all containers and volumes
docker-compose down -v

# Remove unused images
docker system prune -a
```

---

## 📊 Performance Tips

### Speed Up Builds
```bash
# Use Docker layer caching
# Don't change requirements.txt/package.json frequently

# Build specific service
docker-compose build backend
```

### Reduce Memory Usage
```bash
# Stop unused services
docker-compose stop frontend  # If only working on backend

# Limit container resources in docker-compose.yml
```

---

## ✅ Development Checklist

### Before Starting Development
- [ ] Docker Desktop is running
- [ ] Ports 3000, 8000, 5432 are free
- [ ] Git repository is up to date
- [ ] `.env` file is configured (optional)

### Daily Workflow
- [ ] Start services: `docker-compose up`
- [ ] Check all services are running
- [ ] Test login works
- [ ] Make code changes
- [ ] Test changes in browser
- [ ] Commit changes to Git
- [ ] Stop services: `docker-compose down`

### Before Committing
- [ ] Code works locally
- [ ] No console errors
- [ ] All features tested
- [ ] Database migrations included (if any)
- [ ] Documentation updated (if needed)

---

## 🆘 Getting Help

### Check These First
1. **Logs:** `docker-compose logs -f`
2. **Health check:** http://localhost:8000/health
3. **API docs:** http://localhost:8000/docs
4. **Browser console:** F12 → Console tab

### Common Solutions
- **Restart services:** `docker-compose restart`
- **Rebuild containers:** `docker-compose up --build`
- **Clean slate:** `docker-compose down -v && docker-compose up --build`

---

## 🎉 You're Ready!

With Docker, local development is simple:

```bash
docker-compose up --build
```

Open http://localhost:3000 and start developing! 🚀

---

**Last Updated:** May 7, 2026  
**Status:** ✅ Ready for Local Development  
**Recommended:** Use Docker for easiest setup

