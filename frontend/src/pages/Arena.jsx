import { useState, useEffect, useCallback } from 'react'
import { Search, Filter } from 'lucide-react'
import Layout from '../components/Layout'
import TaskCard from '../components/TaskCard'
import { CardSkeleton } from '../components/Skeleton'
import api from '../api/axios'

export default function Arena() {
  const [tasks, setTasks] = useState([])
  const [categories, setCategories] = useState([])
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(1)
  const [loading, setLoading] = useState(true)

  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [selectedDifficulty, setSelectedDifficulty] = useState('')
  const [page, setPage] = useState(1)

  const DIFFICULTIES = [
    { value: '',       label: 'Toate' },
    { value: 'easy',   label: 'Ușor'  },
    { value: 'medium', label: 'Mediu' },
    { value: 'hard',   label: 'Greu'  },
    { value: 'expert', label: 'Expert'},
  ]

  useEffect(() => {
    api.get('/categories').then(({ data }) => setCategories(data))
  }, [])

  const loadTasks = useCallback(async () => {
    setLoading(true)
    try {
      const params = { page, per_page: 12 }
      if (search.trim())      params.search      = search.trim()
      if (selectedCategory)   params.category_id = selectedCategory
      if (selectedDifficulty) params.difficulty  = selectedDifficulty

      const { data } = await api.get('/tasks', { params })
      setTasks(data.items)
      setTotal(data.total)
      setTotalPages(data.total_pages)
    } catch (err) {
      console.error('Eroare la încărcarea sarcinilor', err)
    } finally {
      setLoading(false)
    }
  }, [search, selectedCategory, selectedDifficulty, page])

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadTasks()
  }, [loadTasks])

  function handleSearchChange(e) {
    setSearch(e.target.value)
    setPage(1)
  }

  function handleCategoryChange(e) {
    setSelectedCategory(e.target.value)
    setPage(1)
  }

  function handleDifficultyChange(value) {
    setSelectedDifficulty(value)
    setPage(1)
  }

  return (
    <Layout>

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-text-primary">Arena</h1>
        <p className="text-text-secondary mt-1">
          {total} sarcini disponibile
        </p>
      </div>

      {/* Filtre */}
      <div className="bg-surface border border-surface-hover rounded-xl p-4 mb-6">

        {/* Search */}
        <div className="relative mb-4">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted"
          />
          <input
            type="text"
            placeholder="Caută o sarcină..."
            value={search}
            onChange={handleSearchChange}
            className="w-full bg-base border border-surface-hover rounded-lg
                       pl-9 pr-4 py-2.5 text-text-primary placeholder-text-muted
                       focus:outline-none focus:border-accent-purple text-sm
                       transition-colors"
          />
        </div>

        <div className="flex flex-wrap gap-3">

          {/* Filtru categorie */}
          <div className="flex items-center gap-2">
            <Filter size={14} className="text-text-muted" />
            <select
              value={selectedCategory}
              onChange={handleCategoryChange}
              className="bg-base border border-surface-hover rounded-lg
                         px-3 py-2 text-text-primary text-sm
                         focus:outline-none focus:border-accent-purple
                         transition-colors"
            >
              <option value="">Toate categoriile</option>
              {categories.map(cat => (
                <option key={cat.id} value={String(cat.id)}>{cat.name}</option>
              ))}
            </select>
          </div>

          {/* Filtre dificultate — chipuri */}
          <div className="flex items-center gap-2 flex-wrap">
            {DIFFICULTIES.map(diff => (
              <button
                key={diff.value}
                onClick={() => handleDifficultyChange(diff.value)}
                className={`px-3 py-1.5 rounded-lg text-sm transition-colors border
                  ${selectedDifficulty === diff.value
                    ? 'bg-accent-purple border-accent-purple text-text-primary'
                    : 'bg-base border-surface-hover text-text-secondary hover:border-accent-purple/50'
                  }`}
              >
                {diff.label}
              </button>
            ))}
          </div>

        </div>
      </div>

      {/* Lista sarcini */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {Array.from({ length: 12 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : tasks.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-text-muted text-lg">Nicio sarcină găsită</p>
          <p className="text-text-muted text-sm mt-1">
            Încearcă să schimbi filtrele
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {tasks.map(task => (
            <TaskCard key={task.id} task={task} />
          ))}
        </div>
      )}

      {/* Paginare */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 rounded-lg bg-surface border border-surface-hover
                       text-text-secondary hover:text-text-primary hover:border-accent-purple/50
                       disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-sm"
          >
            ← Anterior
          </button>

          <div className="flex items-center gap-1">
            {Array.from({ length: totalPages }, (_, i) => i + 1)
              .filter(p => p === 1 || p === totalPages || Math.abs(p - page) <= 1)
              .map((p, idx, arr) => (
                <span key={p}>
                  {idx > 0 && arr[idx - 1] !== p - 1 && (
                    <span className="text-text-muted px-1">...</span>
                  )}
                  <button
                    onClick={() => setPage(p)}
                    className={`w-9 h-9 rounded-lg text-sm transition-colors
                      ${p === page
                        ? 'bg-accent-purple text-text-primary'
                        : 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'
                      }`}
                  >
                    {p}
                  </button>
                </span>
              ))}
          </div>

          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 rounded-lg bg-surface border border-surface-hover
                       text-text-secondary hover:text-text-primary hover:border-accent-purple/50
                       disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-sm"
          >
            Următor →
          </button>
        </div>
      )}

    </Layout>
  )
}