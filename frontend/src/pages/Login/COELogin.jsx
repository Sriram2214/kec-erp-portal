import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { ShieldCheck, Lock, User, AlertCircle, GraduationCap } from 'lucide-react'
import './COELogin.css'

export default function COELogin() {
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
      const user = await login(username, password)
      if (user.role !== 'coe' && user.role !== 'admin') {
        setError('Unauthorized: This portal is for COE / Examination Control access only.')
        setLoading(false)
        return
      }
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError('Authentication Failed: Invalid COE Credentials or System Offline')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="coe-login-wrapper">
      <div className="coe-login-glass fade-in">
        <div className="coe-brand">
          <div className="coe-icon-orb">
            <GraduationCap size={40} color="#d4af37" />
          </div>
          <h1>COE PRIVATE ACCESS</h1>
          <div className="institution-tag">KINGS ENGINEERING COLLEGE (9112)</div>
        </div>

        <div className="coe-security-banner">
          <ShieldCheck size={16} />
          <span>Restricted Examination Control Portal</span>
        </div>
        
        {error && (
          <div className="coe-error-bubble">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}
        
        <form className="coe-login-form" onSubmit={handleSubmit}>
          <div className="coe-input-group">
            <label><User size={14} /> EXAM CONTROL ID</label>
            <input 
              type="text" 
              value={username} 
              onChange={e => setUsername(e.target.value)} 
              placeholder="ENTER OFFICE ID"
              required 
            />
          </div>

          <div className="coe-input-group">
            <label><Lock size={14} /> ACCESS PASSCODE</label>
            <input 
              type="password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              placeholder="••••••••"
              required 
            />
          </div>

          <button type="submit" className="coe-auth-btn" disabled={loading}>
            {loading ? 'AUTHORIZING...' : 'AUTHORIZE ACCESS'}
          </button>
        </form>
        
        <div className="coe-security-footer">
          <div className="footer-warning">SYSTEM AUDIT ACTIVE</div>
          <div className="footer-trace">IP TRACE & BIOMETRIC LOGGING ENABLED FOR ALL SESSIONS</div>
        </div>
      </div>
    </div>
  )
}
