import { useState } from 'react'
import { setAccessToken, clearAccessToken } from '../api/axios'
import { AuthContext } from './auth-context'
import api from '../api/axios'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)

  async function login(data) {
    setAccessToken(data.access_token)
    try {
      const response = await api.get('users/me')
      setUser(response.data)
      } 
      catch (error) {
      console.error("Uploading profile after entering has failed", error)
      clearAccessToken()}}

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