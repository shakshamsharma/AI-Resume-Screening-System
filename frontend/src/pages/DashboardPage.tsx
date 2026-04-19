import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { analyticsApi, jobsApi } from '../utils/api'
import { MetricCard, Card, CardTitle, StatusPill, ScoreBar, NotifBanner } from '../components/ui'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import { Briefcase, Users, Clock, TrendingUp } from 'lucide-react'
import type { DashboardAnalytics, Job } from '../types'

const FUNNEL_COLORS: Record<string, string> = {
  applied: '#378ADD', screening: '#185FA5', shortlisted: '#1D9E75',
  interview_1: '#2D7D52', technical: '#639922', hr_round: '#C47F17',
  offer: '#FAC775', hired: '#BA7517',
}

export default function DashboardPage() {
  const { data: analytics } = useQuery<DashboardAnalytics>({
    queryKey: ['dashboard'],
    queryFn: () => analyticsApi.dashboard().then((r) => r.data),
  })
  const { data: jobs } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: () => jobsApi.list('active').then((r) => r.data),
  })

  const funnel = analytics?.funnel || {}
  const funnelData = Object.entries(funnel)
    .filter(([k]) => k !== 'rejected')
    .map(([stage, count]) => ({
      stage: stage.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
      count,
      fill: FUNNEL_COLORS[stage] || '#888',
    }))

  return (
    <div className="p-6">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="font-display font-medium text-xl text-[#1A1A18]">Dashboard</h1>
          <p className="text-sm text-muted mt-0.5">Q2 2025 · All active campaigns</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-ghost text-xs">Export PDF</button>
          <button className="btn-ghost text-xs">Share</button>
        </div>
      </div>

      {analytics && analytics.total_applications > 0 && (
        <NotifBanner type="info">
          <strong className="font-display font-medium">AI Alert:</strong> Platform is live with{' '}
          {analytics.total_applications} total applications.{' '}
          <Link to="/candidates" className="text-accent underline">Review candidates →</Link>
        </NotifBanner>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-4 gap-3 mb-6">
        <MetricCard
          label="Total Applications"
          value={(analytics?.total_applications ?? 0).toLocaleString()}
          change="Track all uploads"
          changeUp
        />
        <MetricCard
          label="Avg Match Score"
          value={`${analytics?.avg_match_score ?? 0}/100`}
          change="AI-ranked accuracy"
          changeUp
        />
        <MetricCard
          label="Active Jobs"
          value={analytics?.active_jobs ?? 0}
          change="Open campaigns"
          changeUp
        />
        <MetricCard
          label="Offer Acceptance"
          value={`${analytics?.offer_acceptance_rate ?? 0}%`}
          change="Conversion rate"
          changeUp
        />
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        {/* Funnel chart */}
        <div className="col-span-2">
          <Card>
            <CardTitle action={<Link to="/pipeline">View pipeline →</Link>}>Hiring Funnel</CardTitle>
            {funnelData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={funnelData} layout="vertical" margin={{ left: 12, right: 20, top: 0, bottom: 0 }}>
                  <XAxis type="number" tick={{ fontSize: 11, fill: '#7A7974' }} axisLine={false} tickLine={false} />
                  <YAxis type="category" dataKey="stage" tick={{ fontSize: 11, fill: '#7A7974' }} axisLine={false} tickLine={false} width={80} />
                  <Tooltip
                    contentStyle={{ fontSize: 12, border: '0.5px solid #E4E3DF', borderRadius: 8, boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }}
                    cursor={{ fill: '#F2F1EE' }}
                  />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]} maxBarSize={18}>
                    {funnelData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-48 flex items-center justify-center text-sm text-muted">
                No data yet — upload resumes to get started
              </div>
            )}
            <div className="flex justify-between text-xs text-muted pt-3 mt-2 border-t border-border">
              <span>Shortlist rate: <strong className="text-[#1A1A18]">{analytics?.shortlist_rate ?? 0}%</strong></span>
              <span>Total hired: <strong className="text-[#1A1A18]">{analytics?.total_hired ?? 0}</strong></span>
            </div>
          </Card>
        </div>

        {/* Active jobs list */}
        <Card>
          <CardTitle action={<Link to="/jobs">All jobs →</Link>}>Active Roles</CardTitle>
          <div className="space-y-2">
            {(jobs || []).slice(0, 6).map((job) => (
              <Link
                key={job.id}
                to={`/candidates?job=${job.id}`}
                className="flex items-center gap-2.5 p-2.5 rounded-lg bg-surface-secondary hover:bg-[#E8E7E3] transition-colors cursor-pointer"
              >
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-display font-medium truncate">{job.title}</div>
                  <div className="text-[11px] text-muted">{job.department} · {job.candidate_count ?? 0} applicants</div>
                </div>
                <span className={`tag text-[10px] ${job.status === 'active' ? 'tag-green' : 'tag-gray'}`}>
                  {job.status}
                </span>
              </Link>
            ))}
            {(!jobs || jobs.length === 0) && (
              <div className="text-xs text-muted text-center py-6">
                No active jobs yet.<br />
                <Link to="/jobs/new" className="text-accent underline">Create one →</Link>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Quick stats row */}
      <div className="grid grid-cols-4 gap-3">
        {[
          { icon: Briefcase, label: 'Jobs Created', val: jobs?.length ?? 0 },
          { icon: Users, label: 'Candidates', val: analytics?.total_applications ?? 0 },
          { icon: TrendingUp, label: 'Shortlisted', val: funnel['shortlisted'] ?? 0 },
          { icon: Clock, label: 'In Interviews', val: (funnel['interview_1'] ?? 0) + (funnel['technical'] ?? 0) },
        ].map(({ icon: Icon, label, val }) => (
          <div key={label} className="card flex items-center gap-3">
            <div className="w-9 h-9 bg-accent-light rounded-lg flex items-center justify-center flex-shrink-0">
              <Icon size={16} className="text-accent" />
            </div>
            <div>
              <div className="text-lg font-display font-medium leading-none">{val}</div>
              <div className="text-[11px] text-muted mt-0.5">{label}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
