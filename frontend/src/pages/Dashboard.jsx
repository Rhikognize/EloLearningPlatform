import { useState, useEffect } from 'react'
import Layout from '../components/Layout'
import StreakWidget from '../components/StreakWidget'
import DailyGoalWidget from '../components/DailyGoalWidget'
import EloChart from '../components/EloChart'
import RecommendedTasks from '../components/RecommendedTasks'
import { ProfileSkeleton } from '../components/Skeleton'
import { getRank } from '../utils/ranks'
import api from '../api/axios'
import { Shield, Target, Zap } from 'lucide-react'

export default function Dashboard() {
  const [profile, setProfile] = useState(null)
  const [history, setHistory] = useState([])
  const [dailyGoal, setDailyGoal] = useState(null)
  const [recommended, setRecommended] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadingRec, setLoadingRec] = useState(true)

  useEffect(() => {
    loadDashboard()
  }, [])

  async function loadDashboard() {
    setLoading(true)
    try {
      const [profileRes, historyRes, goalRes] = await Promise.all([
        api.get('/users/me'),
        api.get('/users/me/history?limit=20'),
        api.get('/daily-goal/today'),
      ])
      setProfile(profileRes.data)
      setHistory(historyRes.data.items)
      setDailyGoal(goalRes.data)
    } catch (err) {
      console.error('Eroare la încărcarea dashboard-ului', err)
    } finally {
      setLoading(false)
    }

    // Recomandările se încarcă separat (mai puțin urgente)
    try {
      const { data } = await api.get('/tasks/recommended')
      setRecommended(data)
    } catch {
      setRecommended([])
    } finally {
      setLoadingRec(false)
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ProfileSkeleton />
          <ProfileSkeleton />
          <ProfileSkeleton />
          <ProfileSkeleton />
        </div>
      </Layout>
    )
  }

  const rank = getRank(profile?.elo_rating || 1200)

  return (
    <Layout>

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text-primary">
          Bună, <span className="text-accent-purple">{profile?.username}</span>! 👋
        </h1>

      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-4 mb-6">

        <div className="bg-surface border border-surface-hover rounded-2xl p-4 text-center">
          <div className="flex justify-center mb-2">
            <Zap size={20} style={{ color: rank.color }} />
          </div>
          <p className="text-2xl font-bold text-text-primary">
            {Math.round(profile?.elo_rating || 1200)}
          </p>
          <p className="text-text-muted text-xs mt-1" style={{ color: rank.color }}>
            {rank.name}
          </p>
        </div>

        <div className="bg-surface border border-surface-hover rounded-2xl p-4 text-center">
          <div className="flex justify-center m-2">
            <Target size={20} className="text-success" />
          </div>
          <p className="text-2xl font-bold text-text-primary">
            {profile?.stats?.total_correct || 0}
          </p>
          <p className="text-text-muted text-xs mt-1">Corecte</p>
        </div>

        <div className="bg-surface border border-surface-hover rounded-2xl p-4 text-center">
          <div className="flex justify-center mb-2">
            <Shield size={20} className="text-accent-blue" />
          </div>
          <p className="text-2xl font-bold text-text-primary">
            {profile?.stats?.accuracy_percent || 0}%
          </p>
          <p className="text-text-muted text-xs mt-1">Acuratețe</p>
        </div>

      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <StreakWidget streak={profile?.current_streak || 0} />
        <DailyGoalWidget
          goal={dailyGoal}
          onClaimed={loadDashboard}
        />
      </div>

      {/* ELO Chart */}
      <div className="mb-6">
        <EloChart history={history} />
      </div>

      {/* Recommended */}
      <RecommendedTasks tasks={recommended} loading={loadingRec} />
    </Layout>
  )
}