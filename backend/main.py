from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from routers import auth, jobs, resumes, candidates, analytics, interviews, bias
from database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HireIQ - AI Resume Screening API",
    description="Production-grade hiring intelligence platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for resume uploads
upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(resumes.router, prefix="/api/resumes", tags=["Resumes"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(interviews.router, prefix="/api/interviews", tags=["Interviews"])
app.include_router(bias.router, prefix="/api/bias", tags=["Bias & Fairness"])


@app.get("/")
def root():
    return {"message": "HireIQ API running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}
