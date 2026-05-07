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
from services.scorer import calculate_overall_score, calculate_trainability_score
from services.ai_evaluator import generate_ai_summary, generate_fit_explanation, generate_hiring_recommendation

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}


async def process_resume(resume_id: str, job_id: str, db: Session):
    """
    Background task: parse + score a resume.
    
    WORKFLOW:
    1. Extract text from file
    2. Parse structured data (NO AI)
    3. Check for duplicates
    4. Calculate deterministic scores
    5. Generate AI evaluation (optional)
    6. Save to database
    """
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not resume or not job:
        return

    try:
        resume.parse_status = "parsing"
        db.commit()

        # Step 1: Extract text with confidence scoring
        raw_text, extraction_confidence = extract_text(resume.file_path, resume.file_type)
        resume.raw_text = raw_text
        
        # Check if extraction failed
        if extraction_confidence < 0.3:
            resume.parse_status = "failed"
            resume.flag_reason = "Text extraction failed - file may be corrupted or image-based PDF"
            db.commit()
            return

        # Step 2: Check duplicate BEFORE parsing
        existing_texts = [
            r.raw_text for r in db.query(models.Resume)
            .filter(models.Resume.job_id == job_id, models.Resume.id != resume_id, models.Resume.raw_text != None)
            .all()
        ]
        is_dup = detect_duplicate(raw_text, existing_texts)
        resume.is_duplicate = is_dup
        
        if is_dup:
            resume.parse_status = "duplicate"
            resume.flag_reason = "Duplicate resume detected"
            db.commit()
            return  # Don't create candidate for duplicate

        # Step 3: Parse resume (deterministic, no AI)
        parsed = parse_resume(raw_text, extraction_confidence)
        
        resume.is_flagged = parsed.get("is_flagged", False)
        resume.flag_reason = parsed.get("flag_reason")
        resume.parse_status = "done"
        db.commit()

        # Step 4: Calculate deterministic scores
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

        # Step 5: Generate AI evaluation (acts as evaluator, not extractor)
        candidate_data = {**parsed, **scores}
        job_data = {
            "title": job.title,
            "experience_min": job.experience_min,
            "experience_max": job.experience_max,
            "required_skills": job.required_skills,
            "priority_skills": job.priority_skills,
        }
        
        ai_summary = generate_ai_summary(candidate_data, job_data)
        ai_explanation = generate_fit_explanation(scores, candidate_data, job_data)
        trainability = calculate_trainability_score(scores, parsed.get("years_experience", 0))
        
        # Generate hiring recommendation
        recommendation = generate_hiring_recommendation(scores, candidate_data, job_data)

        # Step 6: Create candidate record
        candidate = models.Candidate(
            resume_id=resume_id,
            job_id=job_id,
            full_name=parsed.get("full_name"),
            email=parsed.get("email"),
            phone=parsed.get("phone"),
            skills=parsed.get("skills", []),
            certifications=parsed.get("certifications", []),
            years_experience=parsed.get("years_experience", 0),
            education_level=parsed.get("education_level"),
            education_institution=parsed.get("education_institution"),
            current_company=parsed.get("current_company"),
            current_title=parsed.get("current_role"),
            overall_score=scores["overall_score"],
            skill_score=scores["skill_score"],
            experience_score=scores["experience_score"],
            education_score=scores["education_score"],
            industry_score=scores["industry_score"],
            certification_score=scores["certification_score"],
            location_score=scores["location_score"],
            parsing_confidence=parsed.get("parsing_confidence", 0),
            ai_summary=ai_summary,
            ai_fit_explanation=ai_explanation,
            ai_recommendation=recommendation.get("recommendation", "maybe"),
            ai_recommendation_reasoning=recommendation.get("reasoning", ""),
            trainability_score=trainability,
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        # Step 7: Save work experience with proper duration
        for exp in parsed.get("work_experience", []):
            we = models.WorkExperience(
                candidate_id=candidate.id,
                company=exp.get("company"),
                role=exp.get("role"),
                start_date=exp.get("start_date"),
                end_date=exp.get("end_date"),
                duration_months=exp.get("duration_months", 0),
                is_current=exp.get("is_current", False),
            )
            db.add(we)
        db.commit()
        
        print(f"✓ Successfully processed resume: {parsed.get('full_name')} - Score: {scores['overall_score']:.1f}")

    except Exception as e:
        print(f"✗ Resume processing error: {e}")
        import traceback
        traceback.print_exc()
        resume.parse_status = "failed"
        resume.flag_reason = f"Processing error: {str(e)[:200]}"
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
    
    # Get candidate if exists
    candidate = db.query(models.Candidate).filter(models.Candidate.resume_id == resume_id).first()
    
    return {
        "id": str(resume.id),
        "status": resume.parse_status,
        "is_duplicate": resume.is_duplicate,
        "is_flagged": resume.is_flagged,
        "flag_reason": resume.flag_reason,
        "candidate_id": str(candidate.id) if candidate else None,
        "candidate_name": candidate.full_name if candidate else None,
        "overall_score": candidate.overall_score if candidate else None,
    }


@router.delete("/{resume_id}")
def delete_resume(resume_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    """
    Delete a resume and its associated candidate.
    Also deletes the physical file from disk.
    """
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Delete physical file
    if resume.file_path and os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except Exception as e:
            print(f"Failed to delete file {resume.file_path}: {e}")
    
    # Delete from database (cascade will delete candidate and work_experience)
    db.delete(resume)
    db.commit()
    
    return {"message": "Resume deleted successfully", "id": resume_id}


@router.get("/debug/{resume_id}")
def debug_resume_parsing(resume_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    """
    Debug endpoint to see detailed parsing results.
    Useful for troubleshooting extraction issues.
    """
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    candidate = db.query(models.Candidate).filter(models.Candidate.resume_id == resume_id).first()
    
    # Re-parse to get detailed extraction info
    if resume.raw_text:
        parsed = parse_resume(resume.raw_text, 1.0)
        
        return {
            "resume_id": str(resume.id),
            "filename": resume.filename,
            "parse_status": resume.parse_status,
            "extraction_quality": parsed.get("extraction_quality", {}),
            "parsing_confidence": parsed.get("parsing_confidence", 0),
            "needs_manual_review": parsed.get("needs_manual_review", False),
            "extracted_data": {
                "name": parsed.get("full_name"),
                "email": parsed.get("email"),
                "phone": parsed.get("phone"),
                "skills_count": len(parsed.get("skills", [])),
                "skills": parsed.get("skills", [])[:10],
                "years_experience": parsed.get("years_experience", 0),
                "work_experience_count": len(parsed.get("work_experience", [])),
                "education": {
                    "level": parsed.get("education_level"),
                    "institution": parsed.get("education_institution"),
                },
                "certifications": parsed.get("certifications", []),
            },
            "flags": {
                "is_flagged": parsed.get("is_flagged", False),
                "flag_reason": parsed.get("flag_reason"),
            },
            "candidate_created": candidate is not None,
            "candidate_score": candidate.overall_score if candidate else None,
        }
    
    return {"error": "No text extracted from resume"}
