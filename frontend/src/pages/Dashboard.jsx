import Layout from '../components/Layout'
import { useToast } from '../components/Toast'

export default function Dashboard() {
  const { addToast } = useToast()

  return (
    <Layout>
      <h1 className="text-3xl font-bold text-text-primary mb-6">Dashboard</h1>

      <div className="flex flex-col gap-3 max-w-xs">
        <button
          onClick={() => addToast('Răspuns corect! +27 ELO', 'success')}
          className="bg-success/20 border border-success/30 text-success
                     py-2 px-4 rounded-lg hover:bg-success/30 transition-colors"
        >
          Test success toast
        </button>

        <button
          onClick={() => addToast('Răspuns greșit -5 ELO', 'error')}
          className="bg-error/20 border border-error/30 text-error
                     py-2 px-4 rounded-lg hover:bg-error/30 transition-colors"
        >
          Test error toast
        </button>

        <button
          onClick={() => addToast('Achievement deblocat! 🏆', 'achievement')}
          className="bg-warning/20 border border-warning/30 text-warning
                     py-2 px-4 rounded-lg hover:bg-warning/30 transition-colors"
        >
          Test achievement toast
        </button>

        <button
          onClick={() => addToast('Informație importantă', 'info')}
          className="bg-accent-blue/20 border border-accent-blue/30 text-accent-blue
                     py-2 px-4 rounded-lg hover:bg-accent-blue/30 transition-colors"
        >
          Test info toast
        </button>
      </div>
    </Layout>
  )
}