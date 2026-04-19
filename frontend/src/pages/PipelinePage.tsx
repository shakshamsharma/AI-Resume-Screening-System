import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { interviewsApi, jobsApi } from '../utils/api'
import { Card, CardTitle, EmptyState } from '../components/ui'
import { Link } from 'react-router-dom'
import type { Job } from '../types'
import clsx from 'clsx'

const STAGES = [
  { key: 'applied', label: 'Applied', color: '#B5D4F4' },
  { key: 'screening', label: 'Screening', color: '#AFA9EC' },
  { key: 'shortlisted', label: 'Shortlisted', color: '#378ADD' },
  { key: 'interview_1', label: 'Interview 1', color: '#7F77DD' },
  { key: 'technical', label: 'Technical', color: '#1D9E75' },
  { key: 'hr_round', label: 'HR Round', color: '#C47F17' },
  { key: 'offer', label: 'Offer', color: '#639922' },
  { key: 'hired', label: 'Hired', color: '#2D7D52' },
]

export default function PipelinePage() {
  const [selectedJob, setSelectedJob] = useState('')
  const qc = useQueryClient()

  const { data: jobs } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: () => jobsApi.list().then((r) => r.data),
  })

  const { data: pipeline } = useQuery({
    queryKey: ['pipeline', selectedJob],
    queryFn: () => interviewsApi.pipeline(selectedJob).then((r) => r.data),
    enabled: !!selectedJob,
    refetchInterval: 30000,
  })

  const totalInPipeline = pipeline
    ? Object.values(pipeline).reduce((sum: number, arr: any) => sum + arr.length, 0)
    : 0

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display font-medium text-xl">Interview Pipeline</h1>
          <p className="text-sm text-muted mt-0.5">
            {totalInPipeline > 0 ? `${totalInPipeline} candidates across all stages` : 'Kanban view of hiring stages'}
          </p>
        </div>
        <select
          className="input w-64 text-sm"
          value={selectedJob}
          onChange={(e) => setSelectedJob(e.target.value)}
        >
          <option value="">Select a job…</option>
          {(jobs || []).map((j) => (
            <option key={j.id} value={j.id}>{j.title}</option>
          ))}
        </select>
      </div>

      {!selectedJob ? (
        <EmptyState icon="🎯" title="Select a job" subtitle="Choose a campaign to view the interview pipeline" />
      ) : !pipeline ? (
        <div className="flex gap-3 overflow-x-auto pb-4">
          {STAGES.map((s) => (
            <div key={s.key} className="min-w-[180px] flex-shrink-0">
              <div className="skeleton h-6 rounded mb-3" />
              <div className="skeleton h-24 rounded-xl" />
            </div>
          ))}
        </div>
      ) : (
        <>
          {/* Stage counts summary */}
          <div className="flex gap-2 mb-5 flex-wrap">
            {STAGES.map((s) => {
              const count = (pipeline[s.key] || []).length
              return (
                <div key={s.key} className="flex items-center gap-1.5 bg-white border border-border rounded-lg px-3 py-1.5">
                  <div className="w-2 h-2 rounded-full" style={{ background: s.color }} />
                  <span className="text-xs text-muted">{s.label}</span>
                  <span className="text-xs font-display font-medium">{count}</span>
                </div>
              )
            })}
          </div>

          {/* Kanban board */}
          <div className="flex gap-3 overflow-x-auto pb-4">
            {STAGES.map((stage) => {
              const cards = pipeline[stage.key] || []
              return (
                <div key={stage.key} className="min-w-[180px] flex-shrink-0">
                  {/* Column header */}
                  <div className="flex items-center justify-between mb-2 px-1">
                    <div className="flex items-center gap-1.5">
                      <div className="w-2 h-2 rounded-full" style={{ background: stage.color }} />
                      <span className="text-[11px] font-display font-medium text-muted uppercase tracking-wider">
                        {stage.label}
                      </span>
                    </div>
                    <span className="bg-surface-secondary text-muted text-[10px] font-display px-2 py-0.5 rounded-full">
                      {cards.length}
                    </span>
                  </div>

                  {/* Cards */}
                  <div className="space-y-2 min-h-[60px]">
                    {cards.map((c: any) => (
                      <Link
                        key={c.id}
                        to={`/candidates/${c.id}`}
                        className="block bg-white border border-border rounded-xl p-3 hover:border-accent/40 hover:shadow-sm transition-all cursor-pointer"
                      >
                        <div className="font-display font-medium text-xs mb-0.5 leading-tight">
                          {c.full_name || 'Unknown'}
                        </div>
                        <div className="text-[11px] text-muted mb-2">
                          {c.years_experience?.toFixed(0) ?? 0} yrs
                          {c.ai_summary && ` · ${c.ai_summary.slice(0, 40)}…`}
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex-1 h-1 bg-surface-secondary rounded-full overflow-hidden mr-2">
                            <div
                              className="h-full rounded-full"
                              style={{
                                width: `${c.overall_score}%`,
                                background: c.overall_score >= 80 ? '#2D7D52' : c.overall_score >= 65 ? '#C47F17' : '#C23B3B',
                              }}
                            />
                          </div>
                          <span className={`text-[10px] font-display font-medium ${c.overall_score >= 80 ? 'text-emerald-700' : c.overall_score >= 65 ? 'text-amber-600' : 'text-red-600'}`}>
                            {c.overall_score?.toFixed(0) ?? 0}
                          </span>
                        </div>
                      </Link>
                    ))}

                    {cards.length === 0 && (
                      <div className="h-16 border border-dashed border-border rounded-xl flex items-center justify-center">
                        <span className="text-[11px] text-muted">Empty</span>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </>
      )}
    </div>
  )
}
