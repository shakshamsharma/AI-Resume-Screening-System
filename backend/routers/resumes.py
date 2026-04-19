import os
import uuid
import asyncio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
from utils.auth import get_current_active_user
from services.parser import extract_text, parse_resume, detect_duplicate
from services.scorer import calculate_overall_score, generate_ai_summary, generate_fit_explanation, calculate_trainability_score

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}


async def process_resume(resume_id: str, job_id: str, db: Session):
    """Background task: parse + score a resume."""
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not resume or not job:
        return

    try:
        resume.parse_status = "parsing"
        db.commit()

        # Extract text
        raw_text = extract_text(resume.file_path, resume.file_type)
        resume.raw_text = raw_text

        # Check duplicate
        existing_texts = [
            r.raw_text for r in db.query(models.Resume)
            .filter(models.Resume.job_id == job_id, models.Resume.id != resume_id, models.Resume.raw_text != None)
            .all()
        ]
        is_dup = detect_duplicate(raw_text, existing_texts)
        resume.is_duplicate = is_dup

        # Parse
        parsed = parse_resume(raw_text, job.required_skills)
        resume.is_flagged = parsed.get("is_flagged", False)
        resume.flag_reason = parsed.get("flag_reason")
        resume.parse_status = "done"
        db.commit()

        if is_dup:
            return  # Don't create candidate for duplicate

        # Score
        scores = calculate_overall_score(
            candidate_skills=parsed.get("skills", []),
            required_skills=job.required_skills or [],
            priority_skills=job.priority_skills or [],
            years_experience=parsed.get("years_experience", 0),
            exp_min=job.experience_min or 0,
            exp_max=job.experience_max or 10,
            education_level=parsed.get("education_level", "unknown"),
            required_education=job.education,
            education_institution=parsed.get("education_institution", ""),
            candidate_location=parsed.get("location", ""),
            job_location=job.location or "",
            raw_text=raw_text,
        )

        candidate_data = {**parsed, **scores}
        ai_summary = generate_ai_summary(candidate_data)
        ai_explanation = generate_fit_explanation(scores, candidate_data, {
            "experience_min": job.experience_min,
            "experience_max": job.experience_max,
        })
        trainability = calculate_trainability_score(scores, parsed.get("years_experience", 0))

        candidate = models.Candidate(
            resume_id=resume_id,
            job_id=job_id,
            full_name=parsed.get("full_name"),
            email=parsed.get("email"),
            phone=parsed.get("phone"),
            skills=parsed.get("skills", []),
            years_experience=parsed.get("years_experience", 0),
            education_level=parsed.get("education_level"),
            education_institution=parsed.get("education_institution"),
            overall_score=scores["overall_score"],
            skill_score=scores["skill_score"],
            experience_score=scores["experience_score"],
            education_score=scores["education_score"],
            industry_score=scores["industry_score"],
            certification_score=scores["certification_score"],
            location_score=scores["location_score"],
            ai_summary=ai_summary,
            ai_fit_explanation=ai_explanation,
            trainability_score=trainability,
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        # Save work experience
        for exp in parsed.get("work_experience", []):
            we = models.WorkExperience(
                candidate_id=candidate.id,
                start_date=exp.get("start_date"),
                end_date=exp.get("end_date"),
                is_current=exp.get("is_current", False),
            )
            db.add(we)
        db.commit()

    except Exception as e:
        print(f"Resume processing error: {e}")
        resume.parse_status = "failed"
        db.commit()


@router.post("/upload")
async def upload_resumes(
    background_tasks: BackgroundTasks,
    job_id: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    results = []
    for file in files:
        content_type = file.content_type or ""
        file_type = ALLOWED_TYPES.get(content_type)
        
        # Try to infer from filename
        if not file_type:
            fn = file.filename.lower()
            if fn.endswith(".pdf"):
                file_type = "pdf"
            elif fn.endswith(".docx"):
                file_type = "docx"
            elif fn.endswith(".txt"):
                file_type = "txt"

        if not file_type:
            results.append({"filename": file.filename, "status": "rejected", "reason": "Unsupported file type"})
            continue

        # Save file
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Create resume record
        resume = models.Resume(
            job_id=job_id,
            filename=file.filename,
            file_path=file_path,
            file_type=file_type,
            parse_status="pending",
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        # Background processing
        background_tasks.add_task(process_resume, str(resume.id), job_id, db)

        results.append({
            "filename": file.filename,
            "resume_id": str(resume.id),
            "status": "queued",
        })

    return {"uploaded": len(results), "results": results}


@router.get("/job/{job_id}")
def get_resumes_for_job(job_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    resumes = db.query(models.Resume).filter(models.Resume.job_id == job_id).all()
    return [
        {
            "id": str(r.id),
            "filename": r.filename,
            "file_type": r.file_type,
            "parse_status": r.parse_status,
            "is_duplicate": r.is_duplicate,
            "is_flagged": r.is_flagged,
            "flag_reason": r.flag_reason,
            "uploaded_at": r.uploaded_at.isoformat() if r.uploaded_at else None,
        }
        for r in resumes
    ]


@router.get("/status/{resume_id}")
def get_resume_status(resume_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {"id": str(resume.id), "status": resume.parse_status, "is_duplicate": resume.is_duplicate, "is_flagged": resume.is_flagged}
