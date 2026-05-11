import { useState } from 'react'
import { setAccessToken, clearAccessToken } from '../api/axios'
import { AuthContext } from './auth-context'
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)

  function login(data) {
    setAccessToken(data.access_token)
    setUser({
      id: data.user_id,
      username: data.username,
    })
  }

  function logout() {
    clearAccessToken()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}