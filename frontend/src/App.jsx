import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Dashboard from './pages/Dashboard'
import Arena from './pages/Arena'
import TaskSolve from './pages/TaskSolve'
import Leaderboard from './pages/Leaderboard'
import Profile from './pages/Profile'
import Login from './pages/Login'
import Register from './pages/Register'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <nav className="bg-surface border-b border-surface-hover px-6 py-3 flex gap-6">
          <Link to="/dashboard"   className="text-text-secondary hover:text-text-primary transition-colors">Dashboard</Link>
          <Link to="/arena"       className="text-text-secondary hover:text-text-primary transition-colors">Arena</Link>
          <Link to="/leaderboard" className="text-text-secondary hover:text-text-primary transition-colors">Leaderboard</Link>
          <Link to="/profile"     className="text-text-secondary hover:text-text-primary transition-colors">Profil</Link>
          <Link to="/login"       className="text-text-secondary hover:text-text-primary transition-colors">Login</Link>
        </nav>

        <main className="min-h-screen bg-base">
          <Routes>
            <Route path="/"            element={<Navigate to="/dashboard" replace />} />
            <Route path="/login"       element={<Login />} />
            <Route path="/register"    element={<Register />} />

            <Route path="/dashboard"   element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/arena"       element={<ProtectedRoute><Arena /></ProtectedRoute>} />
            <Route path="/arena/:id"   element={<ProtectedRoute><TaskSolve /></ProtectedRoute>} />
            <Route path="/leaderboard" element={<ProtectedRoute><Leaderboard /></ProtectedRoute>} />
            <Route path="/profile"     element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          </Routes>
        </main>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App