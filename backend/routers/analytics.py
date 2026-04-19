from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from database import get_db
import models
from utils.auth import get_current_active_user

router = APIRouter()


@router.get("/dashboard")
def dashboard_analytics(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    total_candidates = db.query(models.Candidate).count()
    total_jobs = db.query(models.Job).filter(models.Job.status == "active").count()
    
    avg_score = db.query(func.avg(models.Candidate.overall_score)).scalar() or 0
    
    # Funnel counts
    funnel = {}
    stages = ["applied", "screening", "shortlisted", "interview_1", "technical", "hr_round", "offer", "hired", "rejected"]
    for stage in stages:
        funnel[stage] = db.query(models.Candidate).filter(models.Candidate.status == stage).count()

    # Total applications = all candidates
    funnel["applied"] = total_candidates

    return {
        "total_applications": total_candidates,
        "active_jobs": total_jobs,
        "avg_match_score": round(float(avg_score), 1),
        "total_hired": funnel.get("hired", 0),
        "funnel": funnel,
        "shortlist_rate": round(funnel.get("shortlisted", 0) / max(total_candidates, 1) * 100, 1),
        "offer_acceptance_rate": round(funnel.get("hired", 0) / max(funnel.get("offer", 1), 1) * 100, 1),
    }


@router.get("/job/{job_id}")
def job_analytics(job_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    candidates = db.query(models.Candidate).filter(models.Candidate.job_id == job_id).all()
    
    if not candidates:
        return {"total": 0, "avg_score": 0, "funnel": {}, "skill_coverage": {}}

    scores = [c.overall_score for c in candidates]
    
    # Score distribution
    distribution = {"90-100": 0, "80-89": 0, "70-79": 0, "60-69": 0, "below-60": 0}
    for s in scores:
        if s >= 90: distribution["90-100"] += 1
        elif s >= 80: distribution["80-89"] += 1
        elif s >= 70: distribution["70-79"] += 1
        elif s >= 60: distribution["60-69"] += 1
        else: distribution["below-60"] += 1

    # Status funnel
    funnel = {}
    for c in candidates:
        funnel[c.status] = funnel.get(c.status, 0) + 1

    # Skill coverage across all candidates
    skill_freq = {}
    for c in candidates:
        for skill in (c.skills or []):
            skill_freq[skill] = skill_freq.get(skill, 0) + 1
    
    top_skills = sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)[:15]

    return {
        "total": len(candidates),
        "avg_score": round(sum(scores) / len(scores), 1),
        "max_score": round(max(scores), 1),
        "min_score": round(min(scores), 1),
        "score_distribution": distribution,
        "funnel": funnel,
        "top_skills_in_pool": dict(top_skills),
    }


@router.get("/bias/{job_id}")
def bias_analytics(job_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    all_cands = db.query(models.Candidate).filter(models.Candidate.job_id == job_id).count()
    shortlisted = db.query(models.Candidate).filter(
        models.Candidate.job_id == job_id,
        models.Candidate.status == "shortlisted"
    ).count()

    overrides = db.query(models.BiasMetric).filter(
        models.BiasMetric.job_id == job_id,
        models.BiasMetric.is_skill_based == False
    ).count()

    return {
        "total_candidates": all_cands,
        "shortlisted": shortlisted,
        "shortlist_rate": round(shortlisted / max(all_cands, 1) * 100, 1),
        "manual_overrides": overrides,
        "skill_based_selection_pct": round((shortlisted - overrides) / max(shortlisted, 1) * 100, 1),
    }
