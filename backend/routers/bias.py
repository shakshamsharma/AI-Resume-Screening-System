from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
import models
from utils.auth import get_current_active_user

router = APIRouter()


class BiasLog(BaseModel):
    job_id: str
    candidate_id: str
    action: str
    reason: Optional[str] = None
    is_skill_based: bool = True


@router.post("/log")
def log_action(data: BiasLog, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    metric = models.BiasMetric(
        job_id=data.job_id,
        candidate_id=data.candidate_id,
        recruiter_id=current_user.id,
        action=data.action,
        reason=data.reason,
        is_skill_based=data.is_skill_based,
    )
    db.add(metric)
    db.commit()
    return {"logged": True}


@router.get("/report/{job_id}")
def bias_report(job_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    metrics = db.query(models.BiasMetric).filter(models.BiasMetric.job_id == job_id).all()
    
    total = len(metrics)
    skill_based = sum(1 for m in metrics if m.is_skill_based)
    overrides = total - skill_based
    
    return {
        "total_actions": total,
        "skill_based": skill_based,
        "manual_overrides": overrides,
        "skill_based_pct": round(skill_based / max(total, 1) * 100, 1),
        "override_details": [
            {
                "candidate_id": str(m.candidate_id),
                "action": m.action,
                "reason": m.reason,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in metrics if not m.is_skill_based
        ],
    }
