import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import { getRank } from '../utils/ranks'
import api from '../api/axios'
import {
  LayoutDashboard, Swords, Trophy,
  User, LogOut, Zap
} from 'lucide-react'

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  async function handleLogout() {
    try {
      await api.post('/auth/logout')
    } catch {
      // logout local chiar dacă request-ul eșuează
    }
    logout()
    navigate('/login')
  }

  const links = [
    { to: '/dashboard',   label: 'Dashboard',  icon: LayoutDashboard },
    { to: '/arena',       label: 'Arena',       icon: Swords          },
    { to: '/leaderboard', label: 'Leaderboard', icon: Trophy          },
    { to: '/profile',     label: 'Profil',      icon: User            },
  ]

  if (!isAuthenticated) return null
  
  const rank = getRank(user?.elo_rating || 1200)

  return (
    <nav className="bg-surface border-b border-surface-hover px-4 py-3">
      <div className="max-w-6xl mx-auto flex items-center justify-between">

        {/* Logo */}
        <Link to="/dashboard" className="text-xl font-bold text-text-primary">
          Elo<span className="text-accent-purple">Learning</span>
        </Link>

        {/* Links desktop */}
        <div className="hidden md:flex items-center gap-1">
          {links.map(({ to, label, icon: Icon }) => {
            const isActive = location.pathname === to
            return (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm
                  transition-colors
                  ${isActive
                    ? 'bg-accent-purple text-text-primary'
                    : 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'
                  }`}
              >
                <Icon size={16} />
                {label}
              </Link>
            )
          })}
        </div>

        {/* ELO badge + logout */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-base px-3 py-2 rounded-lg">
            <Zap size={14} style={{ color: rank.color }} />
            <span className="text-text-primary text-sm font-semibold">
              {Math.round(user?.elo_rating || 1200)}
            </span>
            <span className="text-xs hidden sm:block" style={{ color: rank.color }}>
              {rank.name}
            </span>
          </div>

          <button
            onClick={handleLogout}
            className="text-text-secondary hover:text-error transition-colors p-2 rounded-lg hover:bg-surface-hover"
            title="Deconectare"
          >
            <LogOut size={18} />
          </button>
        </div>

      </div>

      {/* Links mobile */}
      <div className="flex md:hidden items-center gap-1 mt-2 overflow-x-auto">
        {links.map(({ to, label, icon: Icon }) => {
          const isActive = location.pathname === to
          return (
            <Link
              key={to}
              to={to}
              className={`flex items-center gap-1 px-3 py-2 rounded-lg text-xs
                whitespace-nowrap transition-colors
                ${isActive
                  ? 'bg-accent-purple text-text-primary'
                  : 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'
                }`}
            >
              <Icon size={14} />
              {label}
            </Link>
          )
        })}
      </div>
    </nav>
  )
}