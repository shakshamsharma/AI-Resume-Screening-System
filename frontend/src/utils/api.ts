import axios from 'axios'

const API_URL = ''  // Vite proxy routes /api → backend service

export const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('hireiq_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('hireiq_token')
      localStorage.removeItem('hireiq_user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', new URLSearchParams({ username: email, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  register: (data: { email: string; password: string; full_name: string; role?: string }) =>
    api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
}

// ── Jobs ──────────────────────────────────────────────────────────────────────
export const jobsApi = {
  list: (status?: string) => api.get('/jobs/', { params: { status } }),
  get: (id: string) => api.get(`/jobs/${id}`),
  create: (data: any) => api.post('/jobs/', data),
  update: (id: string, data: any) => api.put(`/jobs/${id}`, data),
  delete: (id: string) => api.delete(`/jobs/${id}`),
}

// ── Resumes ───────────────────────────────────────────────────────────────────
export const resumesApi = {
  upload: (jobId: string, files: File[]) => {
    const form = new FormData()
    form.append('job_id', jobId)
    files.forEach((f) => form.append('files', f))
    return api.post('/resumes/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  listForJob: (jobId: string) => api.get(`/resumes/job/${jobId}`),
  status: (resumeId: string) => api.get(`/resumes/status/${resumeId}`),
}

// ── Candidates ────────────────────────────────────────────────────────────────
export const candidatesApi = {
  listForJob: (jobId: string, params?: { status?: string; min_score?: number; search?: string }) =>
    api.get(`/candidates/job/${jobId}`, { params }),
  get: (id: string) => api.get(`/candidates/${id}`),
  updateStatus: (id: string, status: string) =>
    api.patch(`/candidates/${id}/status`, null, { params: { status } }),
  rank: (jobId: string) => api.post(`/candidates/job/${jobId}/rank`),
}

// ── Analytics ─────────────────────────────────────────────────────────────────
export const analyticsApi = {
  dashboard: () => api.get('/analytics/dashboard'),
  job: (jobId: string) => api.get(`/analytics/job/${jobId}`),
  bias: (jobId: string) => api.get(`/analytics/bias/${jobId}`),
}

// ── Interviews ────────────────────────────────────────────────────────────────
export const interviewsApi = {
  create: (data: any) => api.post('/interviews/', data),
  pipeline: (jobId: string) => api.get(`/interviews/job/${jobId}`),
  update: (id: string, data: any) => api.patch(`/interviews/${id}`, data),
}

// ── Bias ──────────────────────────────────────────────────────────────────────
export const biasApi = {
  log: (data: any) => api.post('/bias/log', data),
  report: (jobId: string) => api.get(`/bias/report/${jobId}`),
}
