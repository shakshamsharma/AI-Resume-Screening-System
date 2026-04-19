from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database import get_db
import models
from utils.auth import get_current_active_user

router = APIRouter()


class JobCreate(BaseModel):
    title: str
    department: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = []
    priority_skills: Optional[List[str]] = []
    experience_min: Optional[int] = 0
    experience_max: Optional[int] = 10
    education: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None


class JobUpdate(JobCreate):
    status: Optional[str] = None


@router.post("/")
def create_job(data: JobCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    job = models.Job(**data.dict(), created_by=current_user.id)
    db.add(job)
    db.commit()
    db.refresh(job)
    return _job_out(job)


@router.get("/")
def list_jobs(status: Optional[str] = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    q = db.query(models.Job)
    if status:
        q = q.filter(models.Job.status == status)
    jobs = q.order_by(models.Job.created_at.desc()).all()
    result = []
    for job in jobs:
        j = _job_out(job)
        j["candidate_count"] = db.query(models.Candidate).filter(models.Candidate.job_id == job.id).count()
        result.append(j)
    return result


@router.get("/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_out(job)


@router.put("/{job_id}")
def update_job(job_id: str, data: JobUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    for k, v in data.dict(exclude_none=True).items():
        setattr(job, k, v)
    db.commit()
    db.refresh(job)
    return _job_out(job)


@router.delete("/{job_id}")
def delete_job(job_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"message": "Deleted"}


def _job_out(job: models.Job) -> dict:
    return {
        "id": str(job.id),
        "title": job.title,
        "department": job.department,
        "description": job.description,
        "required_skills": job.required_skills or [],
        "priority_skills": job.priority_skills or [],
        "experience_min": job.experience_min,
        "experience_max": job.experience_max,
        "education": job.education,
        "location": job.location,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "status": job.status,
        "created_at": job.created_at.isoformat() if job.created_at else None,
    }
