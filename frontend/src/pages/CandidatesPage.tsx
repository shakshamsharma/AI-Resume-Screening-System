import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import { candidatesApi, jobsApi } from '../utils/api'
import { ScoreBar, RankBadge, StatusPill, EmptyState, Card } from '../components/ui'
import { Search, Filter, Download, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'
import type { Candidate, Job } from '../types'

const STATUS_TABS = [
  { label: 'All', value: '' },
  { label: 'Shortlisted', value: 'shortlisted' },
  { label: 'Interview 1', value: 'interview_1' },
  { label: 'Screening', value: 'screening' },
  { label: 'Applied', value: 'applied' },
  { label: 'Rejected', value: 'rejected' },
]

export default function CandidatesPage() {
  const [params] = useSearchParams()
  const [selectedJob, setSelectedJob] = useState(params.get('job') || '')
  const [statusFilter, setStatusFilter] = useState('')
  const [search, setSearch] = useState('')
  const [minScore, setMinScore] = useState(0)
  const qc = useQueryClient()

  const { data: jobs } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: () => jobsApi.list().then((r) => r.data),
  })

  const { data: candidates, isLoading } = useQuery<Candidate[]>({
    queryKey: ['candidates', selectedJob, statusFilter, search, minScore],
    queryFn: () =>
      selectedJob
        ? candidatesApi.listForJob(selectedJob, {
            status: statusFilter || undefined,
            search: search || undefined,
            min_score: minScore > 0 ? minScore : undefined,
          }).then((r) => r.data)
        : Promise.resolve([]),
    enabled: !!selectedJob,
  })

  const rankMutation = useMutation({
    mutationFn: () => candidatesApi.rank(selectedJob),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['candidates'] })
      toast.success('Candidates re-ranked!')
    },
  })

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => candidatesApi.updateStatus(id, status),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['candidates'] }),
  })

  const scoreColor = (s: number) => s >= 80 ? 'text-emerald-700' : s >= 65 ? 'text-amber-600' : 'text-red-600'

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display font-medium text-xl">Candidates</h1>
          <p className="text-sm text-muted mt-0.5">
            {candidates ? `${candidates.length} candidates` : 'Select a job to view candidates'}
          </p>
        </div>
        <div className="flex gap-2">
          {selectedJob && (
            <button className="btn-ghost text-xs" onClick={() => rankMutation.mutate()} disabled={rankMutation.isPending}>
              <RefreshCw size={13} className={rankMutation.isPending ? 'animate-spin' : ''} />
              Re-rank
            </button>
          )}
          <button className="btn-ghost text-xs"><Download size={13} />Export CSV</button>
        </div>
      </div>

      {/* Filters row */}
      <div className="flex items-center gap-3 mb-4 flex-wrap">
        <select
          className="input w-56 text-sm"
          value={selectedJob}
          onChange={(e) => setSelectedJob(e.target.value)}
        >
          <option value="">Select job…</option>
          {(jobs || []).map((j) => (
            <option key={j.id} value={j.id}>{j.title}</option>
          ))}
        </select>

        <div className="flex items-center gap-2 bg-white border border-border rounded-lg px-3 h-9">
          <Search size={13} className="text-muted" />
          <input
            className="outline-none text-sm bg-transparent w-44 placeholder-muted"
            placeholder="Search name, skill…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-2 bg-white border border-border rounded-lg px-3 h-9">
          <Filter size={13} className="text-muted" />
          <span className="text-xs text-muted">Min score</span>
          <input
            type="number"
            min={0} max={100}
            className="outline-none text-sm bg-transparent w-12 text-center"
            value={minScore || ''}
            placeholder="0"
            onChange={(e) => setMinScore(Number(e.target.value))}
          />
        </div>
      </div>

      {/* Status tabs */}
      <div className="flex gap-1 bg-surface-secondary p-1 rounded-lg w-fit mb-4">
        {STATUS_TABS.map((tab) => (
          <button
            key={tab.value}
            onClick={() => setStatusFilter(tab.value)}
            className={`px-3 py-1.5 rounded-md text-xs font-display font-medium transition-all ${
              statusFilter === tab.value
                ? 'bg-white text-[#1A1A18] shadow-sm'
                : 'text-muted hover:text-[#1A1A18]'
            }`}
          >
            {tab.label}
            {tab.value === '' && candidates && ` (${candidates.length})`}
          </button>
        ))}
      </div>

      {!selectedJob ? (
        <EmptyState icon="👥" title="Select a job" subtitle="Choose a hiring campaign to view ranked candidates" />
      ) : isLoading ? (
        <Card>
          <div className="space-y-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="skeleton w-6 h-6 rounded-full" />
                <div className="skeleton flex-1 h-4" />
                <div className="skeleton w-24 h-4" />
                <div className="skeleton w-20 h-4" />
              </div>
            ))}
          </div>
        </Card>
      ) : !candidates?.length ? (
        <EmptyState icon="📄" title="No candidates yet" subtitle="Upload resumes for this job to see ranked candidates" />
      ) : (
        <Card className="overflow-hidden p-0">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-surface-secondary">
                {['#', 'Candidate', 'Experience', 'Skills', 'JD Match', 'Status', 'Action'].map((h) => (
                  <th key={h} className="text-left text-[11px] font-display font-medium text-muted px-4 py-3 uppercase tracking-wider">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {candidates.map((c, idx) => (
                <tr key={c.id} className="border-b border-border last:border-0 hover:bg-surface-secondary/50 transition-colors">
                  <td className="px-4 py-3">
                    <RankBadge rank={c.rank_position ?? idx + 1} />
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-display font-medium text-sm">{c.full_name || 'Unknown'}</div>
                    <div className="text-[11px] text-muted">{c.current_company || c.email || '—'}</div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs text-muted">{c.years_experience?.toFixed(0) ?? 0} yrs</span>
                  </td>
                  <td className="px-4 py-3 max-w-[160px]">
                    <div className="flex flex-wrap gap-1">
                      {(c.skills || []).slice(0, 3).map((s) => (
                        <span key={s} className="tag tag-gray text-[10px]">{s}</span>
                      ))}
                      {(c.skills || []).length > 3 && (
                        <span className="tag tag-gray text-[10px]">+{c.skills.length - 3}</span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 w-40">
                    <ScoreBar score={c.overall_score} />
                  </td>
                  <td className="px-4 py-3">
                    <StatusPill status={c.status} />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1.5">
                      <Link
                        to={`/candidates/${c.id}`}
                        className="text-xs text-accent hover:underline font-sans"
                      >
                        View
                      </Link>
                      <span className="text-border">·</span>
                      <select
                        className="text-[11px] border border-border rounded-md px-1.5 py-1 bg-white font-sans outline-none"
                        value={c.status}
                        onChange={(e) => statusMutation.mutate({ id: c.id, status: e.target.value })}
                      >
                        {['applied','screening','shortlisted','interview_1','technical','hr_round','offer','hired','rejected'].map((s) => (
                          <option key={s} value={s}>{s.replace('_', ' ')}</option>
                        ))}
                      </select>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  )
}
