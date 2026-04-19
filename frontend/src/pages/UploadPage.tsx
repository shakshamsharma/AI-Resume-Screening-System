import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { jobsApi, resumesApi } from '../utils/api'
import { Card, CardTitle, NotifBanner } from '../components/ui'
import { Upload, FileText, CheckCircle, AlertCircle, Loader, X } from 'lucide-react'
import toast from 'react-hot-toast'
import clsx from 'clsx'
import type { Job } from '../types'

interface QueuedFile { file: File; status: 'pending' | 'uploading' | 'done' | 'error'; resumeId?: string }

export default function UploadPage() {
  const [params] = useSearchParams()
  const [selectedJob, setSelectedJob] = useState(params.get('job') || '')
  const [queue, setQueue] = useState<QueuedFile[]>([])
  const [uploading, setUploading] = useState(false)

  const { data: jobs } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: () => jobsApi.list('active').then((r) => r.data),
  })

  const onDrop = useCallback((accepted: File[]) => {
    const newFiles = accepted.map((f) => ({ file: f, status: 'pending' as const }))
    setQueue((q) => [...q, ...newFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    multiple: true,
  })

  const handleUpload = async () => {
    if (!selectedJob) { toast.error('Select a job first'); return }
    const pending = queue.filter((q) => q.status === 'pending')
    if (!pending.length) { toast.error('No files to upload'); return }

    setUploading(true)
    try {
      // Upload in batches of 10
      const BATCH = 10
      for (let i = 0; i < pending.length; i += BATCH) {
        const batch = pending.slice(i, i + BATCH)
        setQueue((q) => q.map((item) =>
          batch.find((b) => b.file === item.file) ? { ...item, status: 'uploading' } : item
        ))
        try {
          await resumesApi.upload(selectedJob, batch.map((b) => b.file))
          setQueue((q) => q.map((item) =>
            batch.find((b) => b.file === item.file) ? { ...item, status: 'done' } : item
          ))
        } catch {
          setQueue((q) => q.map((item) =>
            batch.find((b) => b.file === item.file) ? { ...item, status: 'error' } : item
          ))
        }
      }
      toast.success('Resumes uploaded! AI parsing in background…')
    } finally {
      setUploading(false)
    }
  }

  const removeFile = (file: File) => setQueue((q) => q.filter((item) => item.file !== file))
  const doneCount = queue.filter((q) => q.status === 'done').length
  const pendingCount = queue.filter((q) => q.status === 'pending').length

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display font-medium text-xl">Upload Resumes</h1>
          <p className="text-sm text-muted mt-0.5">Bulk upload PDF, DOCX, or TXT files</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          {/* Job selector */}
          <Card className="mb-4">
            <CardTitle>Select Campaign</CardTitle>
            <select
              className="input"
              value={selectedJob}
              onChange={(e) => setSelectedJob(e.target.value)}
            >
              <option value="">Choose a job…</option>
              {(jobs || []).map((j) => (
                <option key={j.id} value={j.id}>{j.title} — {j.department}</option>
              ))}
            </select>
          </Card>

          {/* Drop zone */}
          <div
            {...getRootProps()}
            className={clsx(
              'border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all',
              isDragActive ? 'border-accent bg-accent-light' : 'border-border hover:border-accent hover:bg-accent-light/40'
            )}
          >
            <input {...getInputProps()} />
            <div className="w-12 h-12 bg-surface-secondary rounded-xl mx-auto mb-3 flex items-center justify-center">
              <Upload size={22} className={isDragActive ? 'text-accent' : 'text-muted'} />
            </div>
            <p className="text-sm font-display font-medium mb-1">
              {isDragActive ? 'Drop files here' : 'Drop resumes here'}
            </p>
            <p className="text-xs text-muted mb-4">PDF, DOCX, TXT — up to 500 files</p>
            <button type="button" className="btn-ghost text-xs">Browse files</button>
          </div>

          {queue.length > 0 && (
            <div className="mt-4 flex gap-2">
              <button
                className="btn-primary text-xs flex-1 justify-center"
                onClick={handleUpload}
                disabled={uploading || !pendingCount}
              >
                {uploading ? <><Loader size={13} className="animate-spin" /> Processing…</> : `Upload ${pendingCount} files`}
              </button>
              <button className="btn-ghost text-xs" onClick={() => setQueue([])}>Clear all</button>
            </div>
          )}
        </div>

        <div>
          {/* Stats */}
          {queue.length > 0 && (
            <Card className="mb-4">
              <div className="grid grid-cols-3 gap-3 text-center">
                <div>
                  <div className="text-lg font-display font-medium">{queue.length}</div>
                  <div className="text-[11px] text-muted">Total</div>
                </div>
                <div>
                  <div className="text-lg font-display font-medium text-emerald-600">{doneCount}</div>
                  <div className="text-[11px] text-muted">Uploaded</div>
                </div>
                <div>
                  <div className="text-lg font-display font-medium text-amber-600">{pendingCount}</div>
                  <div className="text-[11px] text-muted">Pending</div>
                </div>
              </div>
              {doneCount > 0 && (
                <div className="mt-3">
                  <div className="h-1.5 bg-surface-secondary rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                      style={{ width: `${(doneCount / queue.length) * 100}%` }}
                    />
                  </div>
                </div>
              )}
            </Card>
          )}

          {/* File list */}
          {queue.length > 0 && (
            <Card>
              <CardTitle>File Queue ({queue.length})</CardTitle>
              <div className="space-y-1 max-h-80 overflow-y-auto">
                {queue.map(({ file, status }, i) => (
                  <div key={i} className="flex items-center gap-2.5 py-1.5 px-1 rounded-lg hover:bg-surface-secondary group">
                    <FileText size={13} className="text-muted flex-shrink-0" />
                    <span className="flex-1 text-xs truncate font-sans">{file.name}</span>
                    <span className="text-[10px] text-muted">{(file.size / 1024).toFixed(0)}KB</span>
                    {status === 'pending' && <div className="w-2 h-2 rounded-full bg-border flex-shrink-0" />}
                    {status === 'uploading' && <Loader size={12} className="animate-spin text-accent flex-shrink-0" />}
                    {status === 'done' && <CheckCircle size={13} className="text-emerald-600 flex-shrink-0" />}
                    {status === 'error' && <AlertCircle size={13} className="text-red-500 flex-shrink-0" />}
                    {status === 'pending' && (
                      <button onClick={() => removeFile(file)} className="opacity-0 group-hover:opacity-100 transition-opacity">
                        <X size={12} className="text-muted hover:text-red-500" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          )}

          {queue.length === 0 && (
            <Card>
              <CardTitle>AI Processing Info</CardTitle>
              <div className="space-y-3">
                {[
                  { label: 'Resume Parsing', desc: 'Extracts name, email, skills, experience, education' },
                  { label: 'JD Match Scoring', desc: 'Scores each candidate 0–100 against job requirements' },
                  { label: 'Skill Gap Analysis', desc: 'Identifies missing required skills per candidate' },
                  { label: 'Duplicate Detection', desc: 'Merges duplicate submissions automatically' },
                  { label: 'Fraud Detection', desc: 'Flags keyword stuffing and suspicious patterns' },
                  { label: 'AI Summary', desc: 'Generates one-line candidate summary' },
                ].map(({ label, desc }) => (
                  <div key={label} className="flex items-start gap-2.5">
                    <CheckCircle size={13} className="text-emerald-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <div className="text-xs font-display font-medium">{label}</div>
                      <div className="text-[11px] text-muted">{desc}</div>
                    </div>
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
