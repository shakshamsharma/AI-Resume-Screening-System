-- HireIQ Database Schema

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users (recruiters, admins, managers)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'recruiter',  -- admin | recruiter | manager
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Jobs / hiring campaigns
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    department VARCHAR(255),
    description TEXT,
    required_skills TEXT[],
    priority_skills TEXT[],
    experience_min INTEGER DEFAULT 0,
    experience_max INTEGER DEFAULT 20,
    education VARCHAR(255),
    location VARCHAR(255),
    salary_min INTEGER,
    salary_max INTEGER,
    status VARCHAR(50) DEFAULT 'active',  -- active | paused | closed
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Resumes (raw uploads)
CREATE TABLE IF NOT EXISTS resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    raw_text TEXT,
    parse_status VARCHAR(50) DEFAULT 'pending',  -- pending | parsing | done | failed
    is_duplicate BOOLEAN DEFAULT false,
    is_flagged BOOLEAN DEFAULT false,
    flag_reason VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- Candidates (parsed from resumes)
CREATE TABLE IF NOT EXISTS candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID REFERENCES resumes(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    -- parsed fields
    full_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    location VARCHAR(255),
    years_experience FLOAT DEFAULT 0,
    education_level VARCHAR(255),
    education_institution VARCHAR(255),
    current_company VARCHAR(255),
    current_title VARCHAR(255),
    skills TEXT[],
    certifications TEXT[],
    languages TEXT[],
    summary TEXT,
    has_career_gap BOOLEAN DEFAULT false,
    career_gap_months INTEGER DEFAULT 0,
    -- ai scores
    overall_score FLOAT DEFAULT 0,
    skill_score FLOAT DEFAULT 0,
    experience_score FLOAT DEFAULT 0,
    education_score FLOAT DEFAULT 0,
    industry_score FLOAT DEFAULT 0,
    certification_score FLOAT DEFAULT 0,
    location_score FLOAT DEFAULT 0,
    ai_summary TEXT,
    ai_fit_explanation TEXT,
    trainability_score FLOAT DEFAULT 0,
    -- status
    status VARCHAR(50) DEFAULT 'applied',  -- applied | screening | shortlisted | rejected
    rank_position INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Work experience (linked to candidate)
CREATE TABLE IF NOT EXISTS work_experience (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    company VARCHAR(255),
    role VARCHAR(255),
    start_date VARCHAR(50),
    end_date VARCHAR(50),
    duration_months INTEGER,
    description TEXT,
    is_current BOOLEAN DEFAULT false
);

-- Interview pipeline
CREATE TABLE IF NOT EXISTS interviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    stage VARCHAR(100) NOT NULL,  -- shortlisted|interview_1|technical|hr_round|offer|hired|rejected
    scheduled_at TIMESTAMP,
    completed_at TIMESTAMP,
    interviewer_name VARCHAR(255),
    feedback TEXT,
    feedback_score FLOAT,
    drop_off_risk VARCHAR(50) DEFAULT 'low',  -- low | medium | high
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Bias metrics
CREATE TABLE IF NOT EXISTS bias_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    recruiter_id UUID REFERENCES users(id),
    action VARCHAR(100),  -- shortlist | reject | override
    candidate_id UUID REFERENCES candidates(id),
    reason TEXT,
    is_skill_based BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Audit logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(255),
    resource_type VARCHAR(100),
    resource_id UUID,
    details JSONB,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Seed default admin user (password: admin123)
INSERT INTO users (email, hashed_password, full_name, role)
VALUES (
    'admin@hireiq.com',
    '$2b$12$PyzWBChlKTErFHtkJjv9/.wsfPeI/XHrD/Lh//s9vpsoo.1Xuhg6W',
    'Admin User',
    'admin'
) ON CONFLICT (email) DO NOTHING;

-- Seed demo recruiter (password: recruiter123)
INSERT INTO users (email, hashed_password, full_name, role)
VALUES (
    'recruiter@hireiq.com',
    '$2b$12$HS3PjnWSNIY.ubOf0nH7qOaprvBQV0.rmyN65tCTwIsvKfoROfWki',
    'Sarah Recruiter',
    'recruiter'
) ON CONFLICT (email) DO NOTHING;
