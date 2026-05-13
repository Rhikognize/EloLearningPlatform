import { useNavigate } from 'react-router-dom'
import { ChevronRight, Zap } from 'lucide-react'

const DIFFICULTY_STYLES = {
  easy:   { label: 'Ușor',   className: 'bg-success/20 text-success border-success/30'       },
  medium: { label: 'Mediu',  className: 'bg-warning/20 text-warning border-warning/30'       },
  hard:   { label: 'Greu',   className: 'bg-error/20 text-error border-error/30'             },
  expert: { label: 'Expert', className: 'bg-accent-purple/20 text-accent-purple border-accent-purple/30' },
}

export default function TaskCard({ task }) {
  const navigate = useNavigate()
  const diff = DIFFICULTY_STYLES[task.difficulty] || DIFFICULTY_STYLES.medium

  return (
    <div
      onClick={() => navigate(`/arena/${task.id}`)}
      className="bg-surface border border-surface-hover rounded-xl p-4
                 hover:border-accent-purple/50 hover:bg-surface-hover
                 transition-all cursor-pointer group"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">

          {/* Categorie */}
          <p className="text-text-muted text-xs mb-1">{task.category_name}</p>

          {/* Titlu */}
          <h3 className="text-text-primary font-semibold text-sm
                         group-hover:text-accent-purple transition-colors
                         truncate">
            {task.title}
          </h3>

          {/* Badges */}
          <div className="flex items-center gap-2 mt-2">
            <span className={`text-xs px-2 py-0.5 rounded-full border ${diff.className}`}>
              {diff.label}
            </span>
            <span className="flex items-center gap-1 text-xs text-text-muted">
              <Zap size={11} />
              {Math.round(task.elo_rating)} ELO
            </span>
          </div>

        </div>

        <ChevronRight
          size={18}
          className="text-text-muted group-hover:text-accent-purple
                     transition-colors shrink-0 mt-1"
        />
      </div>
    </div>
  )
}