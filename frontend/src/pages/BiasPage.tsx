import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { analyticsApi, biasApi, jobsApi } from '../utils/api'
import { Card, CardTitle, NotifBanner, MetricCard, EmptyState } from '../components/ui'
import { Shield, CheckCircle, EyeOff } from 'lucide-react'
import type { Job } from '../types'

const HIDDEN_FIELDS = [
  { field: 'Candidate Name', note: 'Shown only after shortlist', status: 'hidden' },
  { field: 'Gender Indicators', note: 'Pronouns & photos removed', status: 'hidden' },
  { field: 'Age / Date of Birth', note: 'Birth year stripped', status: 'hidden' },
  { field: 'Profile Photo', note: 'Not rendered in candidate cards', status: 'hidden' },
  { field: 'Home Address', note: 'City-level only for location filter', status: 'hidden' },
  { field: 'Religion / Caste', note: 'Flagged and excluded from extraction', status: 'blocked' },
]

export default function BiasPage() {
  const [selectedJob, setSelectedJob] = useState('')

  const { data: jobs } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: () => jobsApi.list().then((r) => r.data),
  })

  const { data: biasData } = useQuery({
    queryKey: ['bias-analytics', selectedJob],
    queryFn: () => analyticsApi.bias(selectedJob).then((r) => r.data),
    enabled: !!selectedJob,
  })

  const { data: biasReport } = useQuery({
    queryKey: ['bias-report', selectedJob],
    queryFn: () => biasApi.report(selectedJob).then((r) => r.data),
    enabled: !!selectedJob,
  })

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display font-medium text-xl">Fairness & Bias AI</h1>
          <p className="text-sm text-muted mt-0.5">Monitoring selection integrity and diversity metrics</p>
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

      {selectedJob && biasData && (
        <NotifBanner type={biasData.manual_overrides > 2 ? 'warn' : 'success'}>
          {biasData.manual_overrides > 2
            ? <><strong className="font-display font-medium">Warning:</strong> {biasData.manual_overrides} manual overrides detected. Please add justification reasons for audit compliance.</>
            : <><strong className="font-display font-medium">Fairness status: Healthy.</strong> Selection is {biasData.skill_based_selection_pct}% skill-based. No significant bias patterns detected.</>
          }
        </NotifBanner>
      )}

      <div className="grid grid-cols-2 gap-5">
        {/* Left */}
        <div>
          <Card className="mb-4">
            <CardTitle>Anonymization Controls</CardTitle>
            <p className="text-xs text-muted mb-4">Sensitive fields hidden from recruiter view during first-pass screening</p>
            <div className="space-y-0">
              {HIDDEN_FIELDS.map(({ field, note, status }) => (
                <div key={field} className="flex items-center gap-3 py-2.5 border-b border-border last:border-0">
                  <EyeOff size={13} className={status === 'blocked' ? 'text-red-500' : 'text-muted'} />
                  <div className="flex-1">
                    <div className="text-xs font-display font-medium">{field}</div>
                    <div className="text-[11px] text-muted">{note}</div>
                  </div>
                  <span className={`tag text-[10px] ${status === 'blocked' ? 'tag-red' : 'tag-green'}`}>
                    {status === 'blocked' ? 'Blocked' : 'Hidden'}
                  </span>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <CardTitle>Fairness Principles</CardTitle>
            <div className="space-y-3">
              {[
                { title: 'Skill-first ranking', desc: 'Candidates ranked purely on JD match score, not personal attributes' },
                { title: 'Blind screening', desc: 'Sensitive information hidden until after initial shortlisting' },
                { title: 'Override audit trail', desc: 'Every manual change logged with recruiter ID and timestamp' },
                { title: 'Diversity tracking', desc: 'Shortlist composition monitored for demographic balance' },
              ].map(({ title, desc }) => (
                <div key={title} className="flex items-start gap-2.5">
                  <CheckCircle size={13} className="text-emerald-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <div className="text-xs font-display font-medium">{title}</div>
                    <div className="text-[11px] text-muted">{desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Right */}
        <div>
          {selectedJob && biasData ? (
            <>
              <div className="grid grid-cols-2 gap-3 mb-4">
                <MetricCard
                  label="Skill-Based Selection"
                  value={`${biasData.skill_based_selection_pct ?? 0}%`}
                  change="of shortlisting decisions"
                  changeUp
                />
                <MetricCard
                  label="Manual Overrides"
                  value={biasData.manual_overrides ?? 0}
                  change={biasData.manual_overrides > 2 ? 'needs review' : 'within threshold'}
                  changeUp={biasData.manual_overrides <= 2}
                />
              </div>

              <Card className="mb-4">
                <CardTitle>Selection Metrics</CardTitle>
                {[
                  { label: 'Total Candidates', val: biasData.total_candidates ?? 0 },
                  { label: 'Shortlisted', val: biasData.shortlisted ?? 0 },
                  { label: 'Shortlist Rate', val: `${biasData.shortlist_rate ?? 0}%` },
                ].map(({ label, val }) => (
                  <div key={label} className="flex justify-between items-center py-2 border-b border-border last:border-0">
                    <span className="text-xs text-muted">{label}</span>
                    <span className="text-xs font-display font-medium">{val}</span>
                  </div>
                ))}
              </Card>

              {biasReport && biasReport.override_details?.length > 0 && (
                <Card>
                  <CardTitle>Override Audit Log</CardTitle>
                  <div className="space-y-2">
                    {biasReport.override_details.map((o: any, i: number) => (
                      <div key={i} className="p-2.5 bg-amber-50 border border-amber-100 rounded-lg">
                        <div className="text-xs font-display font-medium text-amber-800">{o.action}</div>
                        <div className="text-[11px] text-amber-700 mt-0.5">{o.reason || 'No reason provided'}</div>
                        <div className="text-[10px] text-muted mt-1">
                          {o.created_at ? new Date(o.created_at).toLocaleString() : ''}
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              )}
            </>
          ) : (
            <Card>
              <div className="text-center py-8">
                <Shield size={32} className="text-muted mx-auto mb-3 opacity-30" />
                <div className="text-sm font-display font-medium text-[#1A1A18]">Select a job to view fairness metrics</div>
                <div className="text-xs text-muted mt-1">Analytics will appear once candidates are processed</div>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
