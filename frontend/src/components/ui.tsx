import { ReactNode } from 'react'
import clsx from 'clsx'

// ── Score Badge ───────────────────────────────────────────────────────────────
export function ScoreBadge({ score }: { score: number }) {
  const color = score >= 80 ? 'text-emerald-700' : score >= 65 ? 'text-amber-600' : 'text-red-600'
  return (
    <span className={clsx('font-display font-medium text-sm tabular-nums', color)}>
      {score.toFixed(0)}
    </span>
  )
}

// ── Score Bar ─────────────────────────────────────────────────────────────────
export function ScoreBar({ score, showNum = true }: { score: number; showNum?: boolean }) {
  const fillColor = score >= 80 ? 'bg-emerald-600' : score >= 65 ? 'bg-amber-500' : 'bg-red-500'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-surface-secondary rounded-full overflow-hidden">
        <div className={clsx('h-full rounded-full score-fill', fillColor)} style={{ width: `${score}%` }} />
      </div>
      {showNum && <ScoreBadge score={score} />}
    </div>
  )
}

// ── Status Pill ───────────────────────────────────────────────────────────────
const STATUS_STYLES: Record<string, string> = {
  applied: 'bg-surface-secondary text-muted',
  screening: 'bg-amber-50 text-amber-700',
  shortlisted: 'bg-emerald-50 text-emerald-700',
  interview_1: 'bg-accent-light text-accent',
  technical: 'bg-blue-50 text-blue-700',
  hr_round: 'bg-purple-50 text-purple-700',
  offer: 'bg-orange-50 text-orange-700',
  hired: 'bg-emerald-100 text-emerald-800',
  rejected: 'bg-red-50 text-red-600',
}

export function StatusPill({ status }: { status: string }) {
  const label = status.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase())
  return (
    <span className={clsx('tag font-display', STATUS_STYLES[status] || 'bg-surface-secondary text-muted')}>
      {label}
    </span>
  )
}

// ── Rank Badge ────────────────────────────────────────────────────────────────
export function RankBadge({ rank }: { rank: number }) {
  const styles =
    rank === 1 ? 'bg-amber-100 text-amber-800' :
    rank === 2 ? 'bg-accent-light text-accent' :
    rank === 3 ? 'bg-emerald-50 text-emerald-700' :
    'bg-surface-secondary text-muted'
  return (
    <div className={clsx('w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-display font-medium flex-shrink-0', styles)}>
      {rank}
    </div>
  )
}

// ── Card ──────────────────────────────────────────────────────────────────────
export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={clsx('card', className)}>{children}</div>
}

export function CardTitle({ children, action }: { children: ReactNode; action?: ReactNode }) {
  return (
    <div className="flex items-center justify-between mb-4">
      <h3 className="font-display font-medium text-sm text-[#1A1A18]">{children}</h3>
      {action && <div className="text-xs text-accent cursor-pointer font-sans">{action}</div>}
    </div>
  )
}

// ── Metric Card ───────────────────────────────────────────────────────────────
export function MetricCard({ label, value, change, changeUp }: { label: string; value: string | number; change?: string; changeUp?: boolean }) {
  return (
    <div className="bg-white border border-border rounded-xl p-4">
      <div className="text-[11px] font-display font-medium text-muted uppercase tracking-wider mb-2">{label}</div>
      <div className="text-2xl font-display font-medium text-[#1A1A18] leading-none">{value}</div>
      {change && (
        <div className={clsx('text-[11px] mt-1.5', changeUp ? 'text-emerald-600' : 'text-red-500')}>
          {changeUp ? '↑' : '↓'} {change}
        </div>
      )}
    </div>
  )
}

// ── Avatar ────────────────────────────────────────────────────────────────────
export function Avatar({ name, size = 'md' }: { name?: string; size?: 'sm' | 'md' | 'lg' }) {
  const initials = name?.split(' ').map((w) => w[0]).join('').toUpperCase().slice(0, 2) || '?'
  const sizes = { sm: 'w-7 h-7 text-[10px]', md: 'w-9 h-9 text-xs', lg: 'w-16 h-16 text-lg' }
  return (
    <div className={clsx('rounded-full bg-accent-light flex items-center justify-center font-display font-medium text-accent flex-shrink-0', sizes[size])}>
      {initials}
    </div>
  )
}

// ── AI Summary Box ────────────────────────────────────────────────────────────
export function AISummary({ text, label = 'AI Summary' }: { text?: string; label?: string }) {
  if (!text) return null
  return (
    <div className="bg-gradient-to-br from-accent-light to-blue-50 border border-blue-100 rounded-lg p-3 mb-3">
      <div className="text-[10px] font-display font-medium text-accent uppercase tracking-widest mb-1">{label}</div>
      <p className="text-xs text-[#1A1A18] leading-relaxed">{text}</p>
    </div>
  )
}

// ── Skeleton ──────────────────────────────────────────────────────────────────
export function Skeleton({ className }: { className?: string }) {
  return <div className={clsx('skeleton', className)} />
}

// ── Empty State ───────────────────────────────────────────────────────────────
export function EmptyState({ icon, title, subtitle }: { icon?: string; title: string; subtitle?: string }) {
  return (
    <div className="text-center py-16 text-muted">
      {icon && <div className="text-4xl mb-3 opacity-30">{icon}</div>}
      <div className="font-display font-medium text-sm text-[#1A1A18]">{title}</div>
      {subtitle && <div className="text-xs mt-1">{subtitle}</div>}
    </div>
  )
}

// ── Notification Banner ───────────────────────────────────────────────────────
export function NotifBanner({ children, type = 'info' }: { children: ReactNode; type?: 'info' | 'warn' | 'success' }) {
  const styles = {
    info: 'bg-accent-light border-blue-200',
    warn: 'bg-amber-50 border-amber-200',
    success: 'bg-emerald-50 border-emerald-200',
  }
  const dotColors = { info: 'bg-accent', warn: 'bg-amber-500', success: 'bg-emerald-600' }
  return (
    <div className={clsx('border rounded-lg p-3 flex items-start gap-2.5 mb-4', styles[type])}>
      <div className={clsx('w-2 h-2 rounded-full mt-1 flex-shrink-0', dotColors[type])} />
      <div className="text-xs text-[#1A1A18] leading-relaxed">{children}</div>
    </div>
  )
}
