import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/axios'
import { useAuth } from '../context/useAuth'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()

  const [formData, setFormData] = useState({ email: '', password: '' })
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  function handleChange(e) {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const { data } = await api.post('/auth/login', formData)
      login(data)
      navigate('/dashboard')
    } catch (err) {
      const message = err.response?.data?.detail || 'Eroare la autentificare'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-base flex items-center justify-center px-4">
      <div className="w-full max-w-md">

        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Elo<span className="text-accent-purple">Learning</span>
          </h1>
          <p className="text-text-secondary">Intră în cont pentru a continua</p>
        </div>

        {/* Card */}
        <div className="bg-surface rounded-2xl p-8 border burder-surface-cover">
          <h2 className="text-xl font-semibold text-white mb-6">Autentificare</h2>

          {/* Eroare server */}
          {error && (
            <div className="bg-error/10 border border-error/30 rounded-lg px-4 py-3 mb-4">
              <p className="text-error text-sm">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">

            {/* Email */}
            <div className="flex flex-col gap-1">
              <label className="text-text-secondary text-sm">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="email@exemplu.com"
                required
                className="bg-base border burder-surface-cover rounded-lg px-4 py-3
                           text-white placeholder-text-muted
                           focus:outline-none focus:border-accent-purple
                           transition-colors"
              />
            </div>

            {/* Parolă */}
            <div className="flex flex-col gap-1">
              <label className="text-text-secondary text-sm">Parolă</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                required
                className="bg-base border burder-surface-cover rounded-lg px-4 py-3
                           text-white placeholder-text-muted
                           focus:outline-none focus:border-accent-purple
                           transition-colors"
              />
            </div>

            {/* Buton submit */}
            <button
              type="submit"
              disabled={loading}
              className="bg-accent-purple hover:bg-[#7C3AED] disabled:opacity-50
                         disabled:cursor-not-allowed text-white font-semibold
                         py-3 rounded-lg transition-colors mt-2"
            >
              {loading ? 'Se încarcă...' : 'Intră în cont'}
            </button>

          </form>

          {/* Link register */}
          <p className="text-text-secondary text-sm text-center mt-6">
            Nu ai cont?{' '}
            <Link to="/register" className="text-accent-purple hover:text-[#7C3AED] transition-colors">
              Înregistrează-te
            </Link>
          </p>
        </div>

      </div>
    </div>
  )
}