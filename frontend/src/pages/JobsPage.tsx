import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { jobsApi } from '../utils/api'
import { Card, CardTitle, EmptyState } from '../components/ui'
import { Plus, Users, ChevronRight, Briefcase } from 'lucide-react'
import toast from 'react-hot-toast'
import type { Job } from '../types'

export default function JobsPage() {
  const [showForm, setShowForm] = useState(false)
  const qc = useQueryClient()
  const navigate = useNavigate()

  const { data: jobs, isLoading } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: () => jobsApi.list().then((r) => r.data),
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => jobsApi.create(data),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ['jobs'] })
      toast.success('Job created!')
      setShowForm(false)
      navigate(`/upload?job=${res.data.id}`)
    },
    onError: () => toast.error('Failed to create job'),
  })

  const [form, setForm] = useState({
    title: '', department: '', description: '',
    required_skills: '', priority_skills: '',
    experience_min: 2, experience_max: 7,
    education: '', location: '',
    salary_min: '', salary_max: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate({
      ...form,
      required_skills: form.required_skills.split(',').map((s) => s.trim()).filter(Boolean),
      priority_skills: form.priority_skills.split(',').map((s) => s.trim()).filter(Boolean),
      experience_min: Number(form.experience_min),
      experience_max: Number(form.experience_max),
      salary_min: form.salary_min ? Number(form.salary_min) : null,
      salary_max: form.salary_max ? Number(form.salary_max) : null,
    })
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display font-medium text-xl">Open Jobs</h1>
          <p className="text-sm text-muted mt-0.5">{jobs?.length ?? 0} hiring campaigns</p>
        </div>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          <Plus size={14} /> Create Job
        </button>
      </div>

      {/* Create form */}
      {showForm && (
        <Card className="mb-6 max-w-2xl">
          <CardTitle>New Job Description</CardTitle>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-display font-medium text-muted block mb-1">Job Title *</label>
                <input className="input" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="e.g. Senior Backend Engineer" />
              </div>
              <div>
                <label className="text-xs font-display font-medium text-muted block mb-1">Department</label>
                <input className="input" value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} placeholder="e.g. Engineering" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-display font-medium text-muted block mb-1">Min Experience (yrs)</label>
                <input type="number" className="input" value={form.experience_min} onChange={(e) => setForm({ ...form, experience_min: Number(e.target.value) })} />
              </div>
              <div>
                <label className="text-xs font-display font-medium text-muted block mb-1">Max Experience (yrs)</label>
                <input type="number" className="input" value={form.experience_max} onChange={(e) => setForm({ ...form, experience_max: Number(e.target.value) })} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-display font-medium text-muted block mb-1">Location</label>
                <input className="input" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} placeholder="e.g. Bangalore / Remote" />
              </div>
              <div>
                <label className="text-xs font-display font-medium text-muted block mb-1">Education</label>
                <input className="input" value={form.education} onChange={(e) => setForm({ ...form, education: e.target.value })} placeholder="e.g. B.Tech/B.E." />
              </div>
            </div>
            <div>
              <label className="text-xs font-display font-medium text-muted block mb-1">Required Skills (comma-separated)</label>
              <input className="input" value={form.required_skills} onChange={(e) => setForm({ ...form, required_skills: e.target.value })} placeholder="Python, Django, AWS, Docker, Kubernetes" />
            </div>
            <div>
              <label className="text-xs font-display font-medium text-muted block mb-1">Priority / Must-Have Skills</label>
              <input className="input" value={form.priority_skills} onChange={(e) => setForm({ ...form, priority_skills: e.target.value })} placeholder="Python, AWS" />
            </div>
            <div>
              <label className="text-xs font-display font-medium text-muted block mb-1">Job Description</label>
              <textarea className="input h-24 resize-y" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Describe the role and responsibilities…" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-display font-medium text-muted block mb-1">Salary Min (₹ LPA)</label>
                <input type="number" className="input" value={form.salary_min} onChange={(e) => setForm({ ...form, salary_min: e.target.value })} placeholder="18" />
              </div>
              <div>
                <label className="text-xs font-display font-medium text-muted block mb-1">Salary Max (₹ LPA)</label>
                <input type="number" className="input" value={form.salary_max} onChange={(e) => setForm({ ...form, salary_max: e.target.value })} placeholder="30" />
              </div>
            </div>
            <div className="flex gap-2 pt-2">
              <button type="submit" disabled={createMutation.isPending} className="btn-primary text-xs disabled:opacity-60">
                {createMutation.isPending ? 'Creating…' : 'Save & Activate'}
              </button>
              <button type="button" className="btn-ghost text-xs" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </Card>
      )}

      {/* Jobs grid */}
      {isLoading ? (
        <div className="grid grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <div key={i} className="card h-32 skeleton" />)}
        </div>
      ) : jobs && jobs.length > 0 ? (
        <div className="grid grid-cols-3 gap-4">
          {jobs.map((job) => (
            <Link
              key={job.id}
              to={`/candidates?job=${job.id}`}
              className="card hover:border-accent/40 hover:shadow-md transition-all group cursor-pointer block"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-9 h-9 bg-accent-light rounded-lg flex items-center justify-center flex-shrink-0">
                  <Briefcase size={15} className="text-accent" />
                </div>
                <span className={`tag text-[10px] ${job.status === 'active' ? 'tag-green' : job.status === 'paused' ? 'tag-warn' : 'tag-gray'}`}>
                  {job.status}
                </span>
              </div>
              <div className="font-display font-medium text-sm mb-0.5">{job.title}</div>
              <div className="text-xs text-muted mb-3">{job.department} · {job.experience_min}–{job.experience_max} yrs</div>
              <div className="flex flex-wrap gap-1 mb-3">
                {(job.required_skills || []).slice(0, 3).map((s) => (
                  <span key={s} className="tag tag-gray text-[10px]">{s}</span>
                ))}
                {(job.required_skills || []).length > 3 && (
                  <span className="tag tag-gray text-[10px]">+{job.required_skills.length - 3}</span>
                )}
              </div>
              <div className="flex items-center justify-between text-xs text-muted pt-2.5 border-t border-border">
                <span className="flex items-center gap-1"><Users size={12} />{job.candidate_count ?? 0} applicants</span>
                <ChevronRight size={13} className="group-hover:text-accent transition-colors" />
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState icon="💼" title="No jobs yet" subtitle="Create your first hiring campaign to get started" />
      )}
    </div>
  )
}
