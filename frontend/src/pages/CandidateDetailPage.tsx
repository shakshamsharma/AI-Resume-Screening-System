import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { candidatesApi, interviewsApi } from '../utils/api'
import { Card, CardTitle, AISummary, StatusPill, Avatar } from '../components/ui'
import { ArrowLeft, Mail, Phone, MapPin, GraduationCap, Building, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import type { Candidate } from '../types'

const SCORE_DIMS = [
  { key: 'skill_score', label: 'Skills Match', weight: '40%' },
  { key: 'experience_score', label: 'Experience', weight: '25%' },
  { key: 'education_score', label: 'Education', weight: '10%' },
  { key: 'industry_score', label: 'Industry Fit', weight: '10%' },
  { key: 'certification_score', label: 'Certifications', weight: '10%' },
  { key: 'location_score', label: 'Location', weight: '5%' },
]

export default function CandidateDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data: candidate, isLoading } = useQuery<Candidate>({
    queryKey: ['candidate', id],
    queryFn: () => candidatesApi.get(id!).then((r) => r.data),
    enabled: !!id,
  })

  const statusMutation = useMutation({
    mutationFn: (status: string) => candidatesApi.updateStatus(id!, status),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['candidate', id] })
      toast.success('Status updated')
    },
  })

  const interviewMutation = useMutation({
    mutationFn: (stage: string) =>
      interviewsApi.create({ candidate_id: id, job_id: candidate?.job_id, stage }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['candidate', id] })
      toast.success('Interview scheduled!')
    },
  })

  if (isLoading) return (
    <div className="p-6 space-y-4">
      <div className="skeleton h-8 w-48" />
      <div className="grid grid-cols-3 gap-4">
        <div className="skeleton h-80" />
        <div className="col-span-2 skeleton h-80" />
      </div>
    </div>
  )

  if (!candidate) return (
    <div className="p-6 text-center text-muted">Candidate not found</div>
  )

  const scoreColor = (s: number) => s >= 80 ? '#2D7D52' : s >= 65 ? '#C47F17' : '#C23B3B'

  return (
    <div className="p-6">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate(-1)} className="btn-ghost text-xs">
          <ArrowLeft size={13} /> Back
        </button>
        <div className="flex-1">
          <h1 className="font-display font-medium text-xl">{candidate.full_name || 'Unknown Candidate'}</h1>
          <p className="text-sm text-muted">{candidate.current_role || candidate.education_level} · {candidate.current_company}</p>
        </div>
        <div className="flex gap-2">
          <select
            className="input text-xs w-44"
            value={candidate.status}
            onChange={(e) => statusMutation.mutate(e.target.value)}
          >
            {['applied','screening','shortlisted','interview_1','technical','hr_round','offer','hired','rejected'].map((s) => (
              <option key={s} value={s}>{s.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}</option>
            ))}
          </select>
          <button
            className="btn-primary text-xs"
            onClick={() => interviewMutation.mutate('interview_1')}
            disabled={interviewMutation.isPending}
          >
            Schedule Interview
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-5">
        {/* Left column — profile */}
        <div className="space-y-4">
          <Card className="text-center">
            <Avatar name={candidate.full_name} size="lg" />
            <div className="mt-3 font-display font-medium text-base">{candidate.full_name}</div>
            <div className="text-xs text-muted mb-3">{candidate.current_role || 'Professional'}</div>
            <div className="flex justify-center gap-2 mb-4 flex-wrap">
              <StatusPill status={candidate.status} />
              {candidate.years_experience > 0 && (
                <span className="tag tag-blue text-[10px]">{candidate.years_experience.toFixed(0)} yrs exp</span>
              )}
            </div>

            {/* Big score */}
            <div className="bg-accent-light rounded-xl p-4">
              <div className="text-[10px] font-display font-medium text-accent uppercase tracking-widest mb-1">JD Match Score</div>
              <div className="text-4xl font-display font-medium text-accent leading-none">
                {candidate.overall_score.toFixed(0)}<span className="text-base text-muted">/100</span>
              </div>
            </div>

            <div className="mt-4 space-y-1.5 text-left">
              {candidate.email && (
                <div className="flex items-center gap-2 text-xs text-muted">
                  <Mail size={12} /> <span className="truncate">{candidate.email}</span>
                </div>
              )}
              {candidate.phone && (
                <div className="flex items-center gap-2 text-xs text-muted">
                  <Phone size={12} /> {candidate.phone}
                </div>
              )}
              {candidate.location && (
                <div className="flex items-center gap-2 text-xs text-muted">
                  <MapPin size={12} /> {candidate.location}
                </div>
              )}
              {candidate.education_level && (
                <div className="flex items-center gap-2 text-xs text-muted">
                  <GraduationCap size={12} /> {candidate.education_level}
                  {candidate.education_institution && ` · ${candidate.education_institution}`}
                </div>
              )}
            </div>
          </Card>

          {/* Trainability */}
          <Card>
            <CardTitle>Trainability Score</CardTitle>
            <div className="text-center">
              <div className="text-3xl font-display font-medium text-accent">{candidate.trainability_score.toFixed(0)}%</div>
              <div className="text-xs text-muted mt-1">Readiness for missing skills</div>
            </div>
          </Card>
        </div>

        {/* Right two columns */}
        <div className="col-span-2 space-y-4">
          <AISummary text={candidate.ai_summary} />
          <AISummary text={candidate.ai_fit_explanation} label="AI Fit Explanation" />

          {/* Score breakdown */}
          <Card>
            <CardTitle>Score Breakdown</CardTitle>
            <div className="grid grid-cols-3 gap-3 mb-4">
              {SCORE_DIMS.map(({ key, label, weight }) => {
                const val = candidate[key as keyof Candidate] as number ?? 0
                return (
                  <div key={key} className="bg-surface-secondary rounded-lg p-3 text-center">
                    <div className="text-[10px] text-muted font-display font-medium mb-1">{label}</div>
                    <div className="text-xl font-display font-medium" style={{ color: scoreColor(val) }}>
                      {val.toFixed(0)}
                    </div>
                    <div className="text-[10px] text-muted">{weight} weight</div>
                  </div>
                )
              })}
            </div>
          </Card>

          {/* Skills */}
          <Card>
            <CardTitle>Skills</CardTitle>
            <div className="flex flex-wrap gap-1.5">
              {(candidate.skills || []).map((s) => (
                <span key={s} className="tag tag-blue text-[11px]">{s}</span>
              ))}
              {candidate.skills?.length === 0 && <span className="text-xs text-muted">No skills extracted</span>}
            </div>
          </Card>

          {/* Work experience */}
          {(candidate.work_experience || []).length > 0 && (
            <Card>
              <CardTitle>Work Experience</CardTitle>
              <div className="relative pl-5">
                <div className="absolute left-1.5 top-1 bottom-1 w-px bg-border" />
                {(candidate.work_experience || []).map((exp, i) => (
                  <div key={i} className="relative mb-4 last:mb-0">
                    <div className="absolute -left-3.5 top-1 w-2.5 h-2.5 rounded-full bg-white border-2 border-accent" />
                    <div className="font-display font-medium text-sm">{exp.company}</div>
                    <div className="text-xs text-muted">{exp.role}</div>
                    <div className="text-[11px] text-muted mt-0.5">
                      {exp.start_date} – {exp.is_current ? 'Present' : exp.end_date}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Interviews */}
          {(candidate.interviews || []).length > 0 && (
            <Card>
              <CardTitle>Interview History</CardTitle>
              <div className="space-y-2">
                {(candidate.interviews || []).map((iv) => (
                  <div key={iv.id} className="flex items-center gap-3 py-2 border-b border-border last:border-0">
                    <span className="tag tag-blue text-[10px]">{iv.stage.replace('_', ' ')}</span>
                    {iv.scheduled_at && (
                      <span className="text-xs text-muted">
                        {new Date(iv.scheduled_at).toLocaleDateString()}
                      </span>
                    )}
                    {iv.feedback_score && (
                      <span className="text-xs font-display font-medium text-emerald-600 ml-auto">
                        Score: {iv.feedback_score}/10
                      </span>
                    )}
                    <span className={`tag text-[10px] ${
                      iv.drop_off_risk === 'high' ? 'tag-red' :
                      iv.drop_off_risk === 'medium' ? 'tag-warn' : 'tag-green'
                    }`}>
                      {iv.drop_off_risk} drop-off risk
                    </span>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
