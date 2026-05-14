import { useNavigate } from 'react-router-dom'
import { Zap, ArrowRight } from 'lucide-react'
import { CardSkeleton } from './Skeleton'

const DIFFICULTY_STYLES = {
  easy:   { label: 'Ușor',   className: 'text-success'        },
  medium: { label: 'Mediu',  className: 'text-warning'        },
  hard:   { label: 'Greu',   className: 'text-error'          },
  expert: { label: 'Expert', className: 'text-accent-purple'  },
}

export default function RecommendedTasks({ tasks = [], loading = false }) {
  const navigate = useNavigate()

  return (
    <div className="bg-surface border border-surface-hover rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <p className="text-text-secondary text-sm font-medium">Recomandate pentru tine</p>
        <button
          onClick={() => navigate('/arena')}
          className="text-accent-purple text-sm hover:text-accent-purple/80
                     transition-colors flex items-center gap-1"
        >
          Toate <ArrowRight size={13} />
        </button>
      </div>

      {loading ? (
        <div className="flex flex-col gap-3">
          {[1, 2, 3].map(i => <CardSkeleton key={i} />)}
        </div>
      ) : tasks.length === 0 ? (
        <p className="text-text-muted text-sm text-center py-4">
          Nicio sarcină recomandată momentan
        </p>
      ) : (
        <div className="flex flex-col gap-3">
          {tasks.map(task => {
            const diff = DIFFICULTY_STYLES[task.difficulty]
            return (
              <div
                key={task.id}
                onClick={() => navigate(`/arena/${task.id}`)}
                className="flex items-center justify-between p-3 rounded-xl
                           border border-surface-hover hover:border-accent-purple/50
                           hover:bg-surface-hover transition-all cursor-pointer group"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-text-primary text-sm font-medium
                                group-hover:text-accent-purple transition-colors truncate">
                    {task.title}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-xs ${diff.className}`}>{diff.label}</span>
                    <span className="text-text-muted text-xs flex items-center gap-1">
                      <Zap size={10} />
                      {Math.round(task.elo_rating)}
                    </span>
                  </div>
                </div>
                <ArrowRight
                  size={15}
                  className="text-text-muted group-hover:text-accent-purple
                             transition-colors shrink-0 ml-3"
                />
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}