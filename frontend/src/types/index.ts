export interface Job {
  id: string
  title: string
  department?: string
  description?: string
  required_skills: string[]
  priority_skills: string[]
  experience_min: number
  experience_max: number
  education?: string
  location?: string
  salary_min?: number
  salary_max?: number
  status: 'active' | 'paused' | 'closed'
  created_at?: string
  candidate_count?: number
}

export interface Candidate {
  id: string
  resume_id?: string
  job_id?: string
  full_name?: string
  email?: string
  phone?: string
  location?: string
  years_experience: number
  education_level?: string
  education_institution?: string
  current_company?: string
  current_role?: string
  skills: string[]
  certifications: string[]
  overall_score: number
  skill_score: number
  experience_score: number
  education_score: number
  industry_score: number
  certification_score: number
  location_score: number
  ai_summary?: string
  ai_fit_explanation?: string
  trainability_score: number
  status: string
  rank_position?: number
  created_at?: string
  work_experience?: WorkExperience[]
  interviews?: Interview[]
}

export interface WorkExperience {
  company?: string
  role?: string
  start_date?: string
  end_date?: string
  duration_months?: number
  is_current: boolean
}

export interface Interview {
  id: string
  stage: string
  scheduled_at?: string
  feedback_score?: number
  drop_off_risk: 'low' | 'medium' | 'high'
}

export interface Resume {
  id: string
  filename: string
  file_type: string
  parse_status: 'pending' | 'parsing' | 'done' | 'failed'
  is_duplicate: boolean
  is_flagged: boolean
  flag_reason?: string
  uploaded_at?: string
}

export interface DashboardAnalytics {
  total_applications: number
  active_jobs: number
  avg_match_score: number
  total_hired: number
  funnel: Record<string, number>
  shortlist_rate: number
  offer_acceptance_rate: number
}

export const PIPELINE_STAGES = [
  'applied', 'screening', 'shortlisted', 'interview_1',
  'technical', 'hr_round', 'offer', 'hired', 'rejected'
] as const

export const STAGE_LABELS: Record<string, string> = {
  applied: 'Applied',
  screening: 'Screening',
  shortlisted: 'Shortlisted',
  interview_1: 'Interview 1',
  technical: 'Technical',
  hr_round: 'HR Round',
  offer: 'Offer',
  hired: 'Hired',
  rejected: 'Rejected',
}
