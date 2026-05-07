import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Arena from './pages/Arena'
import TaskSolve from './pages/TaskSolve'
import Leaderboard from './pages/Leaderboard'
import Profile from './pages/Profile'
import Login from './pages/Login'
import Register from './pages/Register'
import { Link } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      
      <nav className="bg-surface border-b border-surface-hover px-6 py-3 flex gap-6">
        <Link to="/dashboard"   className="text-text-secondary hover:text-text-primary transition-colors">Dashboard</Link>
        <Link  to="/arena"       className="text-text-secondary hover:text-text-primary transition-colors">Arena</Link >
        <Link  to="/leaderboard" className="text-text-secondary hover:text-text-primary transition-colors">Leaderboard</Link >
        <Link  to="/profile"     className="text-text-secondary hover:text-text-primary transition-colors">Profil</Link >
        <Link  to="/login"       className="text-text-secondary hover:text-text-primary transition-colors">Login</Link >
      </nav>

      {/* Routers */}
      <main className="min-h-screen bg-base">
        <Routes>
          <Route path="/"            element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard"   element={<Dashboard />} />
          <Route path="/arena"       element={<Arena />} />
          <Route path="/arena/:id"   element={<TaskSolve />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/profile"     element={<Profile />} />
          <Route path="/login"       element={<Login />} />
          <Route path="/register"    element={<Register />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}

export default App