import { Flame } from 'lucide-react'
import { motion } from 'framer-motion'

export default function StreakWidget({ streak = 0 }) {
  return (
    <div className="bg-surface border border-surface-hover rounded-2xl p-6">
      <p className="text-text-secondary text-sm font-medium mb-4">Streak curent</p>

      <div className="flex items-center gap-4">
        <motion.div
          animate={streak > 0 ? {
            scale: [1, 1.15, 1],
          } : {}}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
        >
          <Flame
            size={48}
            className={streak > 0 ? 'text-warning' : 'text-text-muted'}
            fill={streak > 0 ? 'currentColor' : 'none'}
          />
        </motion.div>

        <div>
          <p className="text-4xl font-bold text-text-primary">{streak}</p>
          <p className="text-text-secondary text-sm">
            {streak === 0
              ? 'Rezolvă o sarcină azi!'
              : streak === 1
              ? 'zi consecutivă'
              : 'zile consecutive'}
          </p>
        </div>
      </div>
    </div>
  )
}