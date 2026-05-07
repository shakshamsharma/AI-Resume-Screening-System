from sqlalchemy import Column, String, Boolean, Float, Integer, Text, ARRAY, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="recruiter")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Job(Base):
    __tablename__ = "jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    department = Column(String(255))
    description = Column(Text)
    required_skills = Column(ARRAY(String))
    priority_skills = Column(ARRAY(String))
    experience_min = Column(Integer, default=0)
    experience_max = Column(Integer, default=20)
    education = Column(String(255))
    location = Column(String(255))
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    status = Column(String(50), default="active")
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    candidates = relationship("Candidate", back_populates="job", cascade="all, delete")


class Resume(Base):
    __tablename__ = "resumes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"))
    filename = Column(String(500), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    raw_text = Column(Text)
    parse_status = Column(String(50), default="pending")
    is_duplicate = Column(Boolean, default=False)
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(String(255))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    candidate = relationship("Candidate", back_populates="resume", uselist=False)


class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"))
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"))
    full_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    location = Column(String(255))
    years_experience = Column(Float, default=0)
    education_level = Column(String(255))
    education_institution = Column(String(255))
    current_company = Column(String(255))
    current_title = Column(String(255))
    skills = Column(ARRAY(String))
    certifications = Column(ARRAY(String))
    languages = Column(ARRAY(String))
    summary = Column(Text)
    has_career_gap = Column(Boolean, default=False)
    career_gap_months = Column(Integer, default=0)
    overall_score = Column(Float, default=0)
    skill_score = Column(Float, default=0)
    experience_score = Column(Float, default=0)
    education_score = Column(Float, default=0)
    industry_score = Column(Float, default=0)
    certification_score = Column(Float, default=0)
    location_score = Column(Float, default=0)
    parsing_confidence = Column(Float, default=0)
    ai_summary = Column(Text)
    ai_fit_explanation = Column(Text)
    ai_recommendation = Column(String(50))
    ai_recommendation_reasoning = Column(Text)
    trainability_score = Column(Float, default=0)
    status = Column(String(50), default="applied")
    rank_position = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resume = relationship("Resume", back_populates="candidate")
    job = relationship("Job", back_populates="candidates")
    work_experience = relationship("WorkExperience", back_populates="candidate", cascade="all, delete")
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete")


class WorkExperience(Base):
    __tablename__ = "work_experience"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    company = Column(String(255))
    role = Column(String(255))
    start_date = Column(String(50))
    end_date = Column(String(50))
    duration_months = Column(Integer, default=0)
    description = Column(Text)
    is_current = Column(Boolean, default=False)
    candidate = relationship("Candidate", back_populates="work_experience")


class Interview(Base):
    __tablename__ = "interviews"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"))
    stage = Column(String(100), nullable=False)
    scheduled_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    interviewer_name = Column(String(255))
    feedback = Column(Text)
    feedback_score = Column(Float)
    drop_off_risk = Column(String(50), default="low")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    candidate = relationship("Candidate", back_populates="interviews")


class BiasMetric(Base):
    __tablename__ = "bias_metrics"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"))
    recruiter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100))
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"))
    reason = Column(Text)
    is_skill_based = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(255))
    resource_type = Column(String(100))
    resource_id = Column(UUID(as_uuid=True))
    details = Column(JSON)
    ip_address = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
