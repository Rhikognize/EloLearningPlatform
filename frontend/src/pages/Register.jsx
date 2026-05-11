import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/axios'
import { useAuth } from '../context/useAuth'

export default function Register() {
  const navigate = useNavigate()
  const { login } = useAuth()

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [errors, setErrors] = useState({})
  const [serverError, setServerError] = useState(null)
  const [loading, setLoading] = useState(false)

  function handleChange(e) {
    setFormData({ ...formData, [e.target.name]: e.target.value })
    // Ștergem eroarea câmpului când utilizatorul scrie
    if (errors[e.target.name]) {
      setErrors({ ...errors, [e.target.name]: null })
    }
  }

  function validate() {
    const newErrors = {}

    if (formData.username.length < 3) {
      newErrors.username = 'Username-ul trebuie să aibă minim 3 caractere'
    }
    if (!/^[a-zA-Z0-9_-]+$/.test(formData.username)) {
      newErrors.username = 'Doar litere, cifre, _ și -'
    }
    if (!formData.email.includes('@')) {
      newErrors.email = 'Email invalid'
    }
    if (formData.password.length < 8) {
      newErrors.password = 'Parola trebuie să aibă minim 8 caractere'
    }
    if (!/\d/.test(formData.password)) {
      newErrors.password = 'Parola trebuie să conțină cel puțin o cifră'
    }
    if (!/[a-zA-Z]/.test(formData.password)) {
      newErrors.password = 'Parola trebuie să conțină cel puțin o literă'
    }
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Parolele nu coincid'
    }

    return newErrors
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setServerError(null)

    // Validare client
    const validationErrors = validate()
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors)
      return
    }

    setLoading(true)
    try {
      const { data } = await api.post('/auth/register', {
        username: formData.username,
        email: formData.email,
        password: formData.password,
      })
      login(data)
      navigate('/dashboard')
    } catch (err) {
      const message = err.response?.data?.detail || 'Eroare la înregistrare'
      setServerError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-base flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">

        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Elo<span className="text-accent-muted">Learning</span>
          </h1>
          <p className="text-text-secondary">Creează un cont nou</p>
        </div>

        {/* Card */}
        <div className="bg-surface rounded-2xl p-8 border border-surface-cover">
          <h2 className="text-xl font-semibold text-white mb-6">Înregistrare</h2>

          {/* Eroare server */}
          {serverError && (
            <div className="bg-error/10 border border-error/30 rounded-lg px-4 py-3 mb-4">
              <p className="text-error text-sm">{serverError}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">

            {/* Username */}
            <div className="flex flex-col gap-1">
              <label className="text-text-secondary text-sm">Username</label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="username123"
                className="bg-base border border-surface-cover rounded-lg px-4 py-3
                           text-white placeholder-text-muted
                           focus:outline-none focus:border-accent-muted
                           transition-colors"
              />
              {errors.username && (
                <p className="text-error text-xs mt-1">{errors.username}</p>
              )}
            </div>

            {/* Email */}
            <div className="flex flex-col gap-1">
              <label className="text-text-secondary text-sm">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="email@exemplu.com"
                className="bg-base border border-surface-cover rounded-lg px-4 py-3
                           text-white placeholder-text-muted
                           focus:outline-none focus:border-accent-muted
                           transition-colors"
              />
              {errors.email && (
                <p className="text-error text-xs mt-1">{errors.email}</p>
              )}
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
                className="bg-base border border-surface-cover rounded-lg px-4 py-3
                           text-white placeholder-text-muted
                           focus:outline-none focus:border-accent-muted
                           transition-colors"
              />
              {errors.password && (
                <p className="text-error text-xs mt-1">{errors.password}</p>
              )}
            </div>

            {/* Confirmă parola */}
            <div className="flex flex-col gap-1">
              <label className="text-text-secondary text-sm">Confirmă parola</label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="••••••••"
                className="bg-base border border-surface-cover rounded-lg px-4 py-3
                           text-white placeholder-text-muted
                           focus:outline-none focus:border-accent-muted
                           transition-colors"
              />
              {errors.confirmPassword && (
                <p className="text-error text-xs mt-1">{errors.confirmPassword}</p>
              )}
            </div>

            {/* Buton submit */}
            <button
              type="submit"
              disabled={loading}
              className="bg-accent-muted hover:bg-[#7C3AED] disabled:opacity-50
                         disabled:cursor-not-allowed text-white font-semibold
                         py-3 rounded-lg transition-colors mt-2"
            >
              {loading ? 'Se încarcă...' : 'Creează cont'}
            </button>

          </form>

          {/* Link login */}
          <p className="text-text-secondary text-sm text-center mt-6">
            Ai deja cont?{' '}
            <Link to="/login" className="text-accent-muted hover:text-[#7C3AED] transition-colors">
              Intră în cont
            </Link>
          </p>
        </div>

      </div>
    </div>
  )
}