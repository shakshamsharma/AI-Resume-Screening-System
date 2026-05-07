from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
import models
from utils.auth import get_current_active_user

router = APIRouter()


@router.get("/job/{job_id}")
def get_candidates(
    job_id: str,
    status: Optional[str] = None,
    min_score: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: str = "overall_score",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    q = db.query(models.Candidate).filter(models.Candidate.job_id == job_id)

    if status:
        q = q.filter(models.Candidate.status == status)
    if min_score:
        q = q.filter(models.Candidate.overall_score >= min_score)
    if search:
        q = q.filter(
            models.Candidate.full_name.ilike(f"%{search}%") |
            models.Candidate.skills.any(search.lower())
        )

    sort_col = getattr(models.Candidate, sort_by, models.Candidate.overall_score)
    candidates = q.order_by(sort_col.desc()).all()

    return [_candidate_out(c) for c in candidates]


@router.get("/{candidate_id}")
def get_candidate(candidate_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    c = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    result = _candidate_out(c)
    result["work_experience"] = [
        {
            "company": we.company,
            "role": we.role,
            "start_date": we.start_date,
            "end_date": we.end_date,
            "duration_months": we.duration_months,
            "is_current": we.is_current,
        }
        for we in c.work_experience
    ]
    result["interviews"] = [
        {
            "id": str(i.id),
            "stage": i.stage,
            "scheduled_at": i.scheduled_at.isoformat() if i.scheduled_at else None,
            "feedback_score": i.feedback_score,
            "drop_off_risk": i.drop_off_risk,
        }
        for i in c.interviews
    ]
    return result


@router.patch("/{candidate_id}/status")
def update_status(candidate_id: str, status: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    c = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    valid = ["applied", "screening", "shortlisted", "interview_1", "technical", "hr_round", "offer", "hired", "rejected"]
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid}")
    c.status = status
    db.commit()
    return {"id": str(c.id), "status": c.status}


@router.post("/job/{job_id}/rank")
def rank_candidates(job_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    candidates = db.query(models.Candidate).filter(models.Candidate.job_id == job_id).all()
    sorted_cands = sorted(candidates, key=lambda c: (c.overall_score, c.skill_score), reverse=True)
    for i, c in enumerate(sorted_cands):
        c.rank_position = i + 1
    db.commit()
    return {"ranked": len(sorted_cands), "top_3": [{"name": c.full_name, "score": c.overall_score} for c in sorted_cands[:3]]}


@router.delete("/{candidate_id}")
def delete_candidate(candidate_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    """
    Delete a candidate and optionally their resume.
    """
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Get resume
    resume = db.query(models.Resume).filter(models.Resume.id == candidate.resume_id).first()
    
    # Delete candidate (cascade will delete work_experience and interviews)
    db.delete(candidate)
    db.commit()
    
    return {
        "message": "Candidate deleted successfully",
        "id": candidate_id,
        "resume_id": str(resume.id) if resume else None
    }


def _candidate_out(c: models.Candidate) -> dict:
    return {
        "id": str(c.id),
        "resume_id": str(c.resume_id) if c.resume_id else None,
        "job_id": str(c.job_id) if c.job_id else None,
        "full_name": c.full_name,
        "email": c.email,
        "phone": c.phone,
        "location": c.location,
        "years_experience": c.years_experience,
        "education_level": c.education_level,
        "education_institution": c.education_institution,
        "current_company": c.current_company,
        "current_title": c.current_title,
        "skills": c.skills or [],
        "certifications": c.certifications or [],
        "overall_score": c.overall_score,
        "skill_score": c.skill_score,
        "experience_score": c.experience_score,
        "education_score": c.education_score,
        "industry_score": c.industry_score,
        "certification_score": c.certification_score,
        "location_score": c.location_score,
        "parsing_confidence": c.parsing_confidence,
        "ai_summary": c.ai_summary,
        "ai_fit_explanation": c.ai_fit_explanation,
        "ai_recommendation": c.ai_recommendation,
        "ai_recommendation_reasoning": c.ai_recommendation_reasoning,
        "trainability_score": c.trainability_score,
        "status": c.status,
        "rank_position": c.rank_position,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }
