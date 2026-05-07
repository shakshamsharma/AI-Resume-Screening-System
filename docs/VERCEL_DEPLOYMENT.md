# 🚀 Vercel Deployment Guide

**Date:** May 7, 2026  
**Status:** Hybrid Deployment Strategy

---

## ⚠️ Important: Vercel Limitations

Vercel **cannot host the full application** because:

1. ❌ **FastAPI backend** requires persistent server (Vercel is serverless)
2. ❌ **PostgreSQL database** needs persistent storage (Vercel doesn't host databases)
3. ❌ **File uploads** need persistent storage (Vercel is stateless)
4. ❌ **Background processing** for resume parsing won't work well

**Solution:** Use a **hybrid approach** - Frontend on Vercel, Backend elsewhere.

---

## ✅ Recommended Deployment Strategy

### **Option 1: Frontend on Vercel + Backend on Railway** ⭐ RECOMMENDED

This is the easiest and most cost-effective approach:

```
┌─────────────────┐         ┌──────────────────┐
│  Vercel         │         │  Railway         │
│  (Frontend)     │────────▶│  (Backend + DB)  │
│                 │  API    │                  │
│  - React App    │ Calls   │  - FastAPI       │
│  - Static Files │         │  - PostgreSQL    │
│  - CDN          │         │  - File Storage  │
└─────────────────┘         └──────────────────┘
```

**Benefits:**
- ✅ Frontend on fast global CDN (Vercel)
- ✅ Backend on persistent server (Railway)
- ✅ Easy setup for both platforms
- ✅ Free tiers available
- ✅ Automatic HTTPS
- ✅ Git-based deployments

---

## 📋 Step-by-Step Deployment

### Part 1: Deploy Backend to Railway

#### 1. Create Railway Account
- Go to [railway.app](https://railway.app)
- Sign up with GitHub

#### 2. Create New Project
```bash
# Install Railway CLI (optional)
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init
```

#### 3. Add PostgreSQL Database
- In Railway dashboard, click "New" → "Database" → "PostgreSQL"
- Railway will automatically create database and provide connection URL

#### 4. Configure Backend Environment Variables
In Railway dashboard, add these variables:
```env
DATABASE_URL=${{Postgres.DATABASE_URL}}  # Auto-filled by Railway
SECRET_KEY=your-secret-key-here-generate-random-256-bit
OPENAI_API_KEY=your-openai-key-optional
ANTHROPIC_API_KEY=your-anthropic-key-optional
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

#### 5. Deploy Backend
```bash
# From project root
cd backend

# Railway will auto-detect Python and use Dockerfile
railway up
```

Or connect GitHub repo:
- In Railway dashboard: "New" → "GitHub Repo"
- Select your repository
- Set root directory to `backend`
- Railway will auto-deploy on every push

#### 6. Get Backend URL
- Railway will provide a URL like: `https://your-app.railway.app`
- Save this URL for frontend configuration

---

### Part 2: Deploy Frontend to Vercel

#### 1. Create Vercel Account
- Go to [vercel.com](https://vercel.com)
- Sign up with GitHub

#### 2. Install Vercel CLI (Optional)
```bash
npm install -g vercel
```

#### 3. Configure Frontend Environment
Create `frontend/.env.production`:
```env
VITE_API_URL=https://your-app.railway.app
```

#### 4. Deploy to Vercel

**Option A: Using Vercel Dashboard (Easiest)**
1. Go to Vercel dashboard
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
   - **Environment Variables:** Add `VITE_API_URL`
5. Click "Deploy"

**Option B: Using Vercel CLI**
```bash
# From project root
cd frontend

# Deploy
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name? hireiq-frontend
# - Directory? ./
# - Override settings? No

# Deploy to production
vercel --prod
```

#### 5. Configure Environment Variables in Vercel
- Go to Project Settings → Environment Variables
- Add: `VITE_API_URL` = `https://your-app.railway.app`
- Redeploy

---

## 🔧 Configuration Files

### `vercel.json` (Already Created)
```json
{
  "version": 2,
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

### Update `backend/main.py` CORS Settings
```python
from fastapi.middleware.cors import CORSMiddleware

# Add your Vercel URL to allowed origins
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://your-vercel-app.vercel.app",  # Add this
    "https://*.vercel.app",  # Allow all Vercel preview deployments
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🔒 Fixing 404 Errors

### Frontend 404 Errors (React Router)

The `vercel.json` file already handles this with rewrites:
```json
"rewrites": [
  {
    "source": "/(.*)",
    "destination": "/index.html"
  }
]
```

This ensures all routes (like `/candidates`, `/jobs`) are handled by React Router.

### API 404 Errors

Make sure:
1. ✅ `VITE_API_URL` points to correct Railway backend URL
2. ✅ Backend CORS allows your Vercel domain
3. ✅ API endpoints are correct (check `frontend/src/utils/api.ts`)

---

## 🧪 Testing Deployment

### 1. Test Backend (Railway)
```bash
# Health check
curl https://your-app.railway.app/health

# API docs
open https://your-app.railway.app/docs
```

### 2. Test Frontend (Vercel)
```bash
# Open app
open https://your-vercel-app.vercel.app

# Check console for API errors
# Open browser DevTools → Console
```

### 3. Test Full Flow
1. ✅ Login page loads
2. ✅ Can login with credentials
3. ✅ Can create job
4. ✅ Can upload resume
5. ✅ Can view candidates
6. ✅ No CORS errors in console

---

## 🐛 Common Issues & Solutions

### Issue 1: 404 on Page Refresh
**Problem:** Refreshing `/candidates` gives 404

**Solution:** Already fixed with `vercel.json` rewrites. If still happening:
```bash
# Redeploy with vercel.json
vercel --prod
```

### Issue 2: API Calls Failing
**Problem:** Frontend can't reach backend

**Solution:**
1. Check `VITE_API_URL` in Vercel environment variables
2. Check CORS settings in backend
3. Verify Railway backend is running

### Issue 3: CORS Errors
**Problem:** "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solution:** Update `backend/main.py`:
```python
origins = [
    "https://your-vercel-app.vercel.app",
    "https://*.vercel.app",  # For preview deployments
]
```

### Issue 4: Environment Variables Not Working
**Problem:** `VITE_API_URL` is undefined

**Solution:**
1. Vercel: Add in Project Settings → Environment Variables
2. Must start with `VITE_` prefix
3. Redeploy after adding

### Issue 5: Build Fails on Vercel
**Problem:** "Cannot find module" or build errors

**Solution:**
```bash
# Make sure package.json is in frontend folder
cd frontend
npm install
npm run build  # Test locally first
```

---

## 💰 Cost Breakdown

### Free Tier (Hobby Projects)
- **Vercel:** Free (100GB bandwidth/month)
- **Railway:** $5/month credit (enough for small apps)
- **Total:** ~$0-5/month

### Production (Paid)
- **Vercel Pro:** $20/month (team features, more bandwidth)
- **Railway:** ~$10-20/month (based on usage)
- **Total:** ~$30-40/month

---

## 🚀 Alternative Platforms

If you want everything on one platform:

### Railway (All-in-One) ⭐ EASIEST
- ✅ Frontend + Backend + Database
- ✅ Docker support
- ✅ Easy setup
- ✅ ~$10-15/month
- 📖 [Railway Docs](https://docs.railway.app)

### Render (All-in-One)
- ✅ Frontend + Backend + Database
- ✅ Free tier available
- ✅ Good for Python
- 📖 [Render Docs](https://render.com/docs)

### Fly.io (Docker-Based)
- ✅ Full Docker support
- ✅ Global edge deployment
- ✅ Free tier available
- 📖 [Fly.io Docs](https://fly.io/docs)

### AWS/GCP/Azure (Enterprise)
- ✅ Full control
- ✅ Scalable
- ❌ Complex setup
- ❌ More expensive

---

## 📝 Deployment Checklist

### Before Deploying
- [ ] Test locally with Docker
- [ ] Update CORS origins in backend
- [ ] Set strong SECRET_KEY
- [ ] Add .env.production files
- [ ] Test build locally: `npm run build`

### Backend (Railway)
- [ ] Create Railway account
- [ ] Add PostgreSQL database
- [ ] Set environment variables
- [ ] Deploy backend
- [ ] Run database migrations
- [ ] Test API endpoints
- [ ] Save backend URL

### Frontend (Vercel)
- [ ] Create Vercel account
- [ ] Set VITE_API_URL environment variable
- [ ] Deploy frontend
- [ ] Test all routes (no 404s)
- [ ] Test API calls work
- [ ] Check browser console for errors

### Post-Deployment
- [ ] Test login flow
- [ ] Test resume upload
- [ ] Test candidate viewing
- [ ] Test all CRUD operations
- [ ] Monitor logs for errors
- [ ] Set up error tracking (Sentry)

---

## 🔗 Useful Links

- **Vercel Docs:** https://vercel.com/docs
- **Railway Docs:** https://docs.railway.app
- **Vite Deployment:** https://vitejs.dev/guide/static-deploy.html
- **FastAPI Deployment:** https://fastapi.tiangolo.com/deployment/

---

## 📞 Need Help?

### Vercel Issues
- Check build logs in Vercel dashboard
- Review environment variables
- Test build locally first

### Railway Issues
- Check deployment logs
- Verify database connection
- Test API endpoints directly

### CORS Issues
- Update backend CORS origins
- Check browser console
- Verify API URL is correct

---

## ✅ Summary

**Can you deploy to Vercel without 404 errors?**

✅ **Yes, for the frontend** - with proper configuration (vercel.json)  
❌ **No, for the backend** - Vercel doesn't support FastAPI/PostgreSQL

**Best approach:**
1. Deploy **frontend** to **Vercel** (fast, free, no 404s)
2. Deploy **backend** to **Railway** (easy, affordable, persistent)
3. Connect them via environment variables

This gives you:
- ✅ No 404 errors (handled by vercel.json)
- ✅ Fast global CDN for frontend
- ✅ Persistent backend with database
- ✅ Easy deployment and updates
- ✅ Affordable hosting

---

**Status:** Ready to Deploy  
**Recommended:** Vercel (Frontend) + Railway (Backend)  
**Cost:** ~$5-10/month for small projects

