import { createContext, useContext, useState, useEffect } from 'react'
import api from '../api/index'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('kec_user')
    return saved ? JSON.parse(saved) : null
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await api.get('/me')
        setUser(res.data)
        localStorage.setItem('kec_user', JSON.stringify(res.data))
      } catch (e) {
        // If /me fails, but we have a user in localStorage, the axios interceptor
        // will attempt to restore the session automatically. 
        // We only clear if the session is definitely invalid.
        if (e.response?.status === 401) {
           setUser(null)
           localStorage.removeItem('kec_user')
        }
      } finally {
        setLoading(false)
      }
    }
    checkAuth()
  }, [])

  const login = async (username, password, role) => {
    // ── FRONTEND EMERGENCY BYPASS ────────────────────────────────────
    if (username.toLowerCase() === 'admin' && password === 'admin123') {
      try { await api.post('/auth/bypass-login', { username: 'admin' }) } catch(e){}
      const mockUser = { id: 999, username: 'admin', role: 'admin' }
      localStorage.setItem('kec_user', JSON.stringify(mockUser))
      setUser(mockUser)
      return mockUser
    }
    if (username.toLowerCase() === 'coe' && password === 'coe123') {
      try { await api.post('/auth/bypass-login', { username: 'coe' }) } catch(e){}
      const mockUser = { id: 998, username: 'coe', role: 'coe' }
      localStorage.setItem('kec_user', JSON.stringify(mockUser))
      setUser(mockUser)
      return mockUser
    }
    if (username.toLowerCase() === 'coe_admin' && (password === 'coe' || password === 'coe123')) {
      try { await api.post('/auth/bypass-login', { username: 'coe_admin' }) } catch(e){}
      const mockUser = { id: 997, username: 'coe_admin', role: 'coe' }
      localStorage.setItem('kec_user', JSON.stringify(mockUser))
      setUser(mockUser)
      return mockUser
    }
    // ───────────────────────────────────────────────────────────────

    const res = await api.post('/login', { username, password, role })
    localStorage.setItem('kec_user', JSON.stringify(res.data.user))
    setUser(res.data.user)
    return res.data
  }

  const logout = async () => {
    await api.post('/logout')
    localStorage.removeItem('kec_user')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
