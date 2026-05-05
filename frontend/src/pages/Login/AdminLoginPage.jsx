import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { Shield, Lock, User, AlertCircle, Building2 } from 'lucide-react'
import './AdminLoginPage.css'

export default function AdminLoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { user, login } = useAuth()
  const navigate = useNavigate()

  // Redirect if already logged in
  useEffect(() => {
    if (user) {
      navigate('/dashboard', { replace: true })
    }
  }, [user, navigate])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      // Role is hardcoded to 'admin' for this page
      const user = await login(username, password, 'admin')
      if (user.role !== 'admin') {
        setError('Access Denied: This portal is restricted to System Administrators.')
        setLoading(false)
        return
      }
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err.response?.data?.message || 'Authentication Failed: Invalid Admin Credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="admin-login-wrapper">
      <div className="admin-login-card fade-in">
        <div className="admin-brand">
          <div className="admin-icon-box">
            <Shield size={32} color="#d4af37" />
          </div>
          <h2>ADMINISTRATOR ACCESS</h2>
          <p>Institutional Management System</p>
        </div>

        {error && (
          <div className="admin-error">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}
        
        <form className="admin-form" onSubmit={handleSubmit}>
          <div className="admin-input">
            <label><User size={12} /> Admin Username</label>
            <input 
              type="text" 
              value={username} 
              onChange={e => setUsername(e.target.value)} 
              placeholder="Username"
              required autoFocus
            />
          </div>

          <div className="admin-input">
            <label><Lock size={12} /> Password</label>
            <input 
              type="password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              placeholder="••••••••"
              required 
            />
          </div>

          <button type="submit" className="admin-login-btn" disabled={loading}>
            {loading ? 'Authenticating...' : 'Sign In to Console'}
          </button>
        </form>
        
        <div className="admin-footer">
          <Building2 size={14} />
          <span>KINGS ENGINEERING COLLEGE</span>
        </div>
      </div>
    </div>
  )
}
