import { Target, Gift } from 'lucide-react'
import api from '../api/axios'
import { useToast } from './Toast'
import { useState } from 'react'

export default function DailyGoalWidget({ goal, onClaimed }) {
  const { addToast } = useToast()
  const [claiming, setClaiming] = useState(false)

  if (!goal) return null

  const percent = Math.min(100, (goal.correct / goal.target) * 100)

  async function handleClaim() {
    setClaiming(true)
    try {
      await api.post('/daily-goal/claim')
      addToast(`+50 ELO bonus zilnic! 🎯`, 'achievement', 5000)
      onClaimed?.()
    } catch (err) {
      addToast(err.response?.data?.detail || 'Eroare', 'error')
    } finally {
      setClaiming(false)
    }
  }

  return (
    <div className="bg-surface border border-surface-hover rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <p className="text-text-secondary text-sm font-medium">Obiectiv zilnic</p>
        <Target size={16} className="text-accent-purple" />
      </div>

      {/* Numere */}
      <div className="flex items-end gap-1 mb-3">
        <span className="text-3xl font-bold text-text-primary">{goal.correct}</span>
        <span className="text-text-muted text-lg mb-1">/ {goal.target}</span>
      </div>

      {/* Progress bar */}
      <div className="h-2 bg-base rounded-full overflow-hidden mb-4">
        <div
          className="h-full bg-accent-purple rounded-full transition-all duration-500"
          style={{ width: `${percent}%` }}
        />
      </div>

      {/* Stare */}
      {goal.is_claimed ? (
        <div className="flex items-center gap-2 text-success text-sm font-medium">
          <Gift size={15} />
          Bonus ridicat azi!
        </div>
      ) : goal.is_reached ? (
        <button
          onClick={handleClaim}
          disabled={claiming}
          className="w-full bg-warning hover:bg-warning/80 disabled:opacity-50
                     text-black font-semibold py-2.5 rounded-xl
                     transition-colors text-sm"
        >
          {claiming ? 'Se procesează...' : '🎁 Ridică +50 ELO'}
        </button>
      ) : (
        <p className="text-text-muted text-sm">
          Mai ai {goal.target - goal.correct} sarcini corecte
        </p>
      )}
    </div>
  )
}