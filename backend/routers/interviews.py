from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import get_db
import models
from utils.auth import get_current_active_user

router = APIRouter()

STAGES = ["shortlisted", "interview_1", "technical", "hr_round", "offer", "hired", "rejected"]


class InterviewCreate(BaseModel):
    candidate_id: str
    job_id: str
    stage: str
    scheduled_at: Optional[str] = None
    interviewer_name: Optional[str] = None


class InterviewUpdate(BaseModel):
    stage: Optional[str] = None
    feedback: Optional[str] = None
    feedback_score: Optional[float] = None
    drop_off_risk: Optional[str] = None
    completed_at: Optional[str] = None


@router.post("/")
def create_interview(data: InterviewCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    if data.stage not in STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage. Must be one of {STAGES}")
    
    scheduled = None
    if data.scheduled_at:
        try:
            scheduled = datetime.fromisoformat(data.scheduled_at)
        except:
            pass

    interview = models.Interview(
        candidate_id=data.candidate_id,
        job_id=data.job_id,
        stage=data.stage,
        scheduled_at=scheduled,
        interviewer_name=data.interviewer_name,
    )
    db.add(interview)

    # Also update candidate status
    candidate = db.query(models.Candidate).filter(models.Candidate.id == data.candidate_id).first()
    if candidate:
        candidate.status = data.stage

    db.commit()
    db.refresh(interview)
    return _interview_out(interview)


@router.get("/job/{job_id}")
def get_pipeline(job_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    """Return kanban-style pipeline data."""
    pipeline = {}
    for stage in STAGES:
        candidates = db.query(models.Candidate).filter(
            models.Candidate.job_id == job_id,
            models.Candidate.status == stage,
        ).order_by(models.Candidate.overall_score.desc()).all()
        pipeline[stage] = [
            {
                "id": str(c.id),
                "full_name": c.full_name,
                "overall_score": c.overall_score,
                "years_experience": c.years_experience,
                "ai_summary": c.ai_summary,
            }
            for c in candidates
        ]
    return pipeline


@router.patch("/{interview_id}")
def update_interview(interview_id: str, data: InterviewUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.dict(exclude_none=True).items():
        setattr(interview, k, v)
    db.commit()
    db.refresh(interview)
    return _interview_out(interview)


def _interview_out(i: models.Interview) -> dict:
    return {
        "id": str(i.id),
        "candidate_id": str(i.candidate_id),
        "job_id": str(i.job_id),
        "stage": i.stage,
        "scheduled_at": i.scheduled_at.isoformat() if i.scheduled_at else None,
        "interviewer_name": i.interviewer_name,
        "feedback": i.feedback,
        "feedback_score": i.feedback_score,
        "drop_off_risk": i.drop_off_risk,
    }
