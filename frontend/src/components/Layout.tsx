import { Outlet, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { Search, Bell, Plus } from 'lucide-react'
import Sidebar from './Sidebar'
import { useAuth } from '../hooks/useAuth'

export default function Layout() {
  const [search, setSearch] = useState('')
  const navigate = useNavigate()
  const { user } = useAuth()

  return (
    <div className="flex h-screen overflow-hidden bg-surface-tertiary">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Topbar */}
        <header className="h-13 bg-white border-b border-border flex items-center px-6 gap-3 flex-shrink-0" style={{ height: 52 }}>
          <div className="flex-1" />
          {/* Search */}
          <div className="flex items-center bg-surface-secondary border border-border rounded-lg px-3 gap-2 w-64">
            <Search size={13} className="text-muted flex-shrink-0" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search candidates, roles..."
              className="bg-transparent border-none outline-none text-sm font-sans py-2 w-full placeholder-muted"
            />
          </div>
          <button className="btn-primary text-xs" onClick={() => navigate('/jobs/new')}>
            <Plus size={13} />
            New Job
          </button>
          <button className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-surface-secondary text-muted relative">
            <Bell size={15} />
            <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-red-500 rounded-full" />
          </button>
          <div className="w-8 h-8 rounded-full bg-accent-light flex items-center justify-center text-[11px] font-display font-medium text-accent">
            {user?.full_name?.slice(0, 2).toUpperCase() || 'U'}
          </div>
        </header>
        {/* Page */}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
