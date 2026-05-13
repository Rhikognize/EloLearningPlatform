import { createContext, useContext, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle, XCircle, Trophy, Info, X } from 'lucide-react'

const ToastContext = createContext(null)

const ICONS = {
  success:     <CheckCircle size={18} className="text-success" />,
  error:       <XCircle     size={18} className="text-error"   />,
  achievement: <Trophy      size={18} className="text-warning" />,
  info:        <Info        size={18} className="text-accent-blue" />,
}

const COLORS = {
  success:     'border-success/30 bg-success/10',
  error:       'border-error/30 bg-error/10',
  achievement: 'border-warning/30 bg-warning/10',
  info:        'border-accent-blue/30 bg-accent-blue/10',
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = 'info', duration = 3000) => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, duration)
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}

      <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full">
        <AnimatePresence>
          {toasts.map(toast => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, x: 50, scale: 0.9 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 50, scale: 0.9 }}
              transition={{ duration: 0.2 }}
              className={`flex items-start gap-3 p-4 rounded-xl border
                ${COLORS[toast.type]}`}
            >
              <div className="mt-0.5 shrink-0">
                {ICONS[toast.type]}
              </div>
              <p className="text-text-primary text-sm flex-1">{toast.message}</p>
              <button
                onClick={() => removeToast(toast.id)}
                className="text-text-secondary hover:text-text-primary shrink-0"
              >
                <X size={14} />
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useToast() {
  const context = useContext(ToastContext)
  if (!context) throw new Error('useToast trebuie folosit în ToastProvider')
  return context
}