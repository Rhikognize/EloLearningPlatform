import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'
import { Timer, Lightbulb, Send, ArrowRight, ChevronLeft } from 'lucide-react'
import Layout from '../components/Layout'
import { CardSkeleton } from '../components/Skeleton'
import { useToast } from '../components/Toast'
import EloPopup from '../components/EloPopup'
import api from '../api/axios'

export default function TaskSolve() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { addToast } = useToast()

  const [task, setTask] = useState(null)
  const [loading, setLoading] = useState(true)
  const [answer, setAnswer] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)
  const [showHint, setShowHint] = useState(false)

  const [seconds, setSeconds] = useState(0)
  const timerRef = useRef(null)
  const startTimeRef = useRef(null)

  // ELO popup
  const [eloDelta, setEloDelta] = useState(0)
  const [eloTrigger, setEloTrigger] = useState(0)

  // Încarcă sarcina
  useEffect(() => {
    let cancelled = false

    async function load() {
      setLoading(true)
      try {
        const { data } = await api.get(`/tasks/${id}`)
        if (!cancelled) {
          setTask(data)
        }
      } catch {
        if (!cancelled) {
          addToast('Sarcina nu a fost găsită', 'error')
          navigate('/arena')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    load()

    return () => {
      cancelled = true
    }
  }, [id, addToast, navigate])

  // Pornește timer-ul
  useEffect(() => {
    startTimeRef.current = Date.now()

    const interval = setInterval(() => {
      setSeconds(Math.floor((Date.now() - startTimeRef.current) / 1000))
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  async function handleSubmit() {
    if (!answer.trim() || submitting || result) return

    clearInterval(timerRef.current)
    setSubmitting(true)

    try {
      const { data } = await api.post(`/tasks/${id}/solve`, {
        answer: answer.trim(),
        time_taken: seconds,
      })

      setResult(data)

      // ELO popup
      if (data.elo_delta !== 0) {
        setEloDelta(data.elo_delta)
        setEloTrigger(prev => prev + 1)
      }

      // Toast
      if (data.is_correct) {
        const sign = data.elo_delta >= 0 ? '+' : ''
        addToast(
          `Corect! ${sign}${Math.round(data.elo_delta)} ELO`,
          'success'
        )
        // Achievement toast
        data.achievements_earned?.forEach(a => {
          addToast(`🏆 ${a.title}`, 'achievement', 5000)
        })
      } else {
        addToast(
          `Greșit! ${Math.round(data.elo_delta)} ELO`,
          'error'
        )
        setShowHint(true)
      }

    } catch (err) {
      const msg = err.response?.data?.detail || 'Eroare la trimiterea răspunsului'
      addToast(msg, 'error')
    } finally {
      setSubmitting(false)
    }
  }

  function handleNextTask() {
    navigate('/arena')
  }

  function formatTime(s) {
    const m = Math.floor(s / 60)
    const sec = s % 60
    return `${m}:${sec.toString().padStart(2, '0')}`
  }

  // ── Loading ────────────────────────────────────────
  if (loading) {
    return (
      <Layout>
        <div className="max-w-2xl mx-auto">
          <CardSkeleton />
        </div>
      </Layout>
    )
  }

  const DIFFICULTY_COLORS = {
    easy:   'text-success',
    medium: 'text-warning',
    hard:   'text-error',
    expert: 'text-accent-purple',
  }

  const DIFFICULTY_LABELS = {
    easy: 'Ușor', medium: 'Mediu', hard: 'Greu', expert: 'Expert'
  }

  return (
    <Layout>
      <div className="max-w-2xl mx-auto">

        {/* ELO Popup */}
        <EloPopup delta={eloDelta} trigger={eloTrigger} />

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => navigate('/arena')}
            className="flex items-center gap-2 text-text-secondary
                       hover:text-text-primary transition-colors text-sm"
          >
            <ChevronLeft size={16} />
            Înapoi la Arena
          </button>

          {/* Timer */}
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg
            bg-surface border border-surface-hover text-sm
            ${result ? 'text-text-muted' : 'text-text-primary'}`}
          >
            <Timer size={14} />
            {formatTime(seconds)}
          </div>
        </div>

        {/* Card sarcină */}
        <div className="bg-surface border border-surface-hover rounded-2xl p-6 mb-4">

          {/* Meta */}
          <div className="flex items-center gap-3 mb-4">
            <span className="text-text-muted text-sm">{task.category_name}</span>
            <span className="text-text-muted">·</span>
            <span className={`text-sm font-medium ${DIFFICULTY_COLORS[task.difficulty]}`}>
              {DIFFICULTY_LABELS[task.difficulty]}
            </span>
            <span className="text-text-muted">·</span>
            <span className="text-text-muted text-sm">{Math.round(task.elo_rating)} ELO</span>
          </div>

          {/* Titlu */}
          <h1 className="text-xl font-bold text-text-primary mb-4">
            {task.title}
          </h1>

          {/* Condiție cu Markdown + KaTeX */}
          <div className="prose prose-invert max-w-none text-text-secondary
                          prose-p:text-text-secondary prose-strong:text-text-primary">
            <ReactMarkdown
              remarkPlugins={[remarkMath]}
              rehypePlugins={[rehypeKatex]}
            >
              {task.description}
            </ReactMarkdown>
          </div>

        </div>

        {/* Hint */}
        {showHint && task.hint && !result?.show_explanation && (
          <div className="bg-warning/10 border border-warning/30 rounded-xl p-4 mb-4">
            <div className="flex items-start gap-2">
              <Lightbulb size={16} className="text-warning mt-0.5 shrink-0" />
              <p className="text-warning text-sm">{task.hint}</p>
            </div>
          </div>
        )}

        {/* Explanation — după 3 greșeli */}
        {result?.show_explanation && result?.explanation && (
          <div className="bg-accent-blue/10 border border-accent-blue/30 rounded-xl p-4 mb-4">
            <p className="text-accent-blue text-sm font-semibold mb-2">
              Explicație pas cu pas:
            </p>
            <div className="text-text-secondary text-sm prose prose-invert max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkMath]}
                rehypePlugins={[rehypeKatex]}
              >
                {result.explanation}
              </ReactMarkdown>
            </div>
          </div>
        )}

        {/* Rezultat */}
        {result && (
          <div className={`rounded-xl p-4 mb-4 border
            ${result.is_correct
              ? 'bg-success/10 border-success/30'
              : 'bg-error/10 border-error/30'
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className={`font-semibold ${result.is_correct ? 'text-success' : 'text-error'}`}>
                  {result.is_correct ? '✓ Corect!' : '✗ Greșit'}
                </p>
                {!result.is_correct && result.correct_answer && (
                  <p className="text-text-secondary text-sm mt-1">
                    Răspuns corect: <span className="text-text-primary font-mono">{result.correct_answer}</span>
                  </p>
                )}
              </div>
              <div className="text-right">
                <p className={`text-lg font-bold
                  ${result.elo_delta >= 0 ? 'text-success' : 'text-error'}`}
                >
                  {result.elo_delta >= 0 ? '+' : ''}{Math.round(result.elo_delta)} ELO
                </p>
                <p className="text-text-muted text-xs">
                  Streak: {result.streak} zile
                </p>
              </div>
            </div>

            {/* Daily goal progress */}
            <div className="mt-3 pt-3 border-t border-surface-hover">
              <div className="flex items-center justify-between text-xs text-text-muted mb-1">
                <span>Obiectiv zilnic</span>
                <span>{result.daily_goal_progress.correct}/{result.daily_goal_progress.target}</span>
              </div>
              <div className="h-1.5 bg-base rounded-full overflow-hidden">
                <div
                  className="h-full bg-accent-purple rounded-full transition-all"
                  style={{
                    width: `${Math.min(100, (result.daily_goal_progress.correct / result.daily_goal_progress.target) * 100)}%`
                  }}
                />
              </div>
              {result.daily_goal_progress.is_reached && (
                <p className="text-warning text-xs mt-1 font-medium">
                  🎯 Obiectiv zilnic atins! Mergi la Dashboard pentru recompensă.
                </p>
              )}
            </div>
          </div>
        )}

        {/* Input răspuns */}
        {!result && (
          <div className="bg-surface border border-surface-hover rounded-2xl p-6">

            {/* Multiple choice */}
            {task.answer_type === 'multiple_choice' && task.answer_options ? (
              <div className="flex flex-col gap-3 mb-4">
                {task.answer_options.map((option, idx) => {
                  const letter = ['A', 'B', 'C', 'D'][idx]
                  return (
                    <button
                      key={idx}
                      onClick={() => setAnswer(letter)}
                      className={`flex items-center gap-3 p-3 rounded-xl border
                        text-left transition-colors
                        ${answer === letter
                          ? 'border-accent-purple bg-accent-purple/20 text-text-primary'
                          : 'border-surface-hover text-text-secondary hover:border-accent-purple/50'
                        }`}
                    >
                      <span className={`w-7 h-7 rounded-lg flex items-center justify-center
                        text-sm font-bold shrink-0
                        ${answer === letter ? 'bg-accent-purple text-white' : 'bg-base text-text-muted'}`}
                      >
                        {letter}
                      </span>
                      {option}
                    </button>
                  )
                })}
              </div>
            ) : (
              /* Exact / Numeric */
              <div className="mb-4">
                <label className="text-text-secondary text-sm mb-2 block">
                  Răspunsul tău:
                </label>
                <input
                  type={task.answer_type === 'numeric' ? 'text' : 'text'}
                  value={answer}
                  onChange={e => setAnswer(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleSubmit()}
                  placeholder={task.answer_type === 'numeric' ? 'Introdu un număr...' : 'Introdu răspunsul...'}
                  className="w-full bg-base border border-surface-hover rounded-xl
                             px-4 py-3 text-text-primary placeholder-text-muted
                             focus:outline-none focus:border-accent-purple text-sm
                             transition-colors"
                />
              </div>
            )}

            {/* Butoane */}
            <div className="flex items-center gap-3">
              {task.hint && (
                <button
                  onClick={() => setShowHint(true)}
                  disabled={showHint}
                  className="flex items-center gap-2 px-4 py-2.5 rounded-xl
                             border border-warning/30 text-warning text-sm
                             hover:bg-warning/10 disabled:opacity-40
                             disabled:cursor-not-allowed transition-colors"
                >
                  <Lightbulb size={15} />
                  Indiciu
                </button>
              )}

              <button
                onClick={handleSubmit}
                disabled={!answer.trim() || submitting}
                className="flex-1 flex items-center justify-center gap-2
                           bg-accent-purple hover:bg-accent-purple/80
                           disabled:opacity-40 disabled:cursor-not-allowed
                           text-white font-semibold py-2.5 rounded-xl
                           transition-colors"
              >
                <Send size={15} />
                {submitting ? 'Se trimite...' : 'Trimite răspunsul'}
              </button>
            </div>

          </div>
        )}

        {/* Buton Sarcina următoare */}
        {result && (
          <button
            onClick={handleNextTask}
            className="w-full flex items-center justify-center gap-2
                       bg-accent-purple hover:bg-accent-purple/80
                       text-white font-semibold py-3 rounded-xl
                       transition-colors mt-2"
          >
            Înapoi la Arena
            <ArrowRight size={16} />
          </button>
        )}

      </div>
    </Layout>
  )
}