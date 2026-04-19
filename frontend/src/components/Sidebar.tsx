import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Briefcase, Upload, Users, User,
  GitBranch, BarChart3, Shield, LogOut, Sparkles
} from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import clsx from 'clsx'

const NAV = [
  { section: 'Overview', items: [{ to: '/', icon: LayoutDashboard, label: 'Dashboard' }] },
  {
    section: 'Hiring',
    items: [
      { to: '/jobs', icon: Briefcase, label: 'Open Jobs', badge: null },
      { to: '/upload', icon: Upload, label: 'Upload Resumes' },
      { to: '/candidates', icon: Users, label: 'Candidates' },
    ],
  },
  {
    section: 'Intelligence',
    items: [
      { to: '/skills', icon: BarChart3, label: 'Skill Gaps' },
      { to: '/bias', icon: Shield, label: 'Fairness AI' },
      { to: '/pipeline', icon: GitBranch, label: 'Pipeline' },
    ],
  },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <aside className="w-[220px] min-w-[220px] bg-white border-r border-border flex flex-col">
      {/* Logo */}
      <div className="px-4 py-5 border-b border-border">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 bg-accent rounded-lg flex items-center justify-center flex-shrink-0">
            <Sparkles size={14} className="text-white" />
          </div>
          <div>
            <div className="font-display font-semibold text-sm text-[#1A1A18] leading-tight">HireIQ</div>
            <div className="text-[10px] text-muted font-sans">Hiring Intelligence</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-3 overflow-y-auto">
        {NAV.map((group) => (
          <div key={group.section}>
            <div className="section-label">{group.section}</div>
            {group.items.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) => clsx('nav-item', isActive && 'active')}
              >
                <Icon size={15} className="flex-shrink-0" />
                <span className="text-sm">{label}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      {/* User */}
      <div className="px-3 py-3 border-t border-border">
        <div className="flex items-center gap-2.5 px-2 py-2 rounded-lg hover:bg-surface-secondary cursor-pointer group">
          <div className="w-7 h-7 rounded-full bg-accent-light flex items-center justify-center text-[11px] font-display font-medium text-accent flex-shrink-0">
            {user?.full_name?.slice(0, 2).toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-display font-medium truncate">{user?.full_name}</div>
            <div className="text-[10px] text-muted capitalize">{user?.role}</div>
          </div>
          <button
            onClick={() => { logout(); navigate('/login') }}
            className="opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <LogOut size={13} className="text-muted hover:text-red-500 transition-colors" />
          </button>
        </div>
      </div>
    </aside>
  )
}
