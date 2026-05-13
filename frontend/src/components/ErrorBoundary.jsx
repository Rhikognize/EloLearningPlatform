import { Component } from 'react'
import { AlertTriangle } from 'lucide-react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    console.error('ErrorBoundary:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-base flex items-center justify-center p-4">
          <div className="bg-surface rounded-2xl p-8 border border-surface-hover max-w-md w-full text-center">
            <AlertTriangle size={48} className="text-error mx-auto mb-4" />
            <h2 className="text-xl font-bold text-text-primary mb-2">
              Ceva a mers greșit
            </h2>
            <p className="text-text-secondary mb-6 text-sm">
              {this.state.error?.message || 'Eroare necunoscută'}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="bg-accent-purple hover:bg-accent-purple/80 text-text-primary
                         font-semibold py-2 px-6 rounded-lg transition-colors"
            >
              Reîncarcă pagina
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}