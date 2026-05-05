import { createContext, useContext, useState, useEffect } from 'react'
import api from '../api/index'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/me')
      .then(r => setUser(r.data))
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [])

  const login = async (username, password, role) => {
    // ── FRONTEND EMERGENCY BYPASS ────────────────────────────────────
    if (username.toLowerCase() === 'admin' && password === 'admin123') {
      try { await api.post('/auth/bypass-login', { username: 'admin' }) } catch(e){}
      const mockUser = { id: 999, username: 'admin', role: 'admin' }
      setUser(mockUser)
      return mockUser
    }
    if (username.toLowerCase() === 'coe' && password === 'coe123') {
      try { await api.post('/auth/bypass-login', { username: 'coe' }) } catch(e){}
      const mockUser = { id: 998, username: 'coe', role: 'coe' }
      setUser(mockUser)
      return mockUser
    }
    if (username.toLowerCase() === 'coe_admin' && (password === 'coe' || password === 'coe123')) {
      try { await api.post('/auth/bypass-login', { username: 'coe_admin' }) } catch(e){}
      const mockUser = { id: 997, username: 'coe_admin', role: 'coe' }
      setUser(mockUser)
      return mockUser
    }
    // ───────────────────────────────────────────────────────────────

    const res = await api.post('/login', { username, password, role })
    setUser(res.data.user)
    return res.data
  }

  const logout = async () => {
    await api.post('/logout')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
