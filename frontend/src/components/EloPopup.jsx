import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function EloPopup({ delta, trigger }) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (trigger > 0) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setVisible(true)
      const timer = setTimeout(() => setVisible(false), 1500)
      return () => clearTimeout(timer)
    }
  }, [trigger])

  if (delta === 0) return null

  const isPositive = delta > 0
  const colorClass = isPositive ? 'text-success' : 'text-error'
  const sign = isPositive ? '+' : ''

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: 0, scale: 0.8 }}
          animate={{ opacity: 1, y: -40, scale: 1 }}
          exit={{ opacity: 0, y: -80, scale: 0.6 }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
          className={`pointer-events-none fixed text-2xl font-bold z-50 ${colorClass}`}
          style={{ right: '20px', bottom: '80px' }}
        >
          {sign}{Math.round(delta)} ELO
        </motion.div>
      )}
    </AnimatePresence>
  )
}