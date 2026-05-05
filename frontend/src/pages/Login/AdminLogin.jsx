import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import './AdminLogin.css'

export default function AdminLogin() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const user = await login(username, password)
      if (user.role !== 'admin') {
        setError('Access Denied: This portal is for System Administrators only.')
        return
      }
      navigate('/dashboard')
    } catch (err) {
      setError('Invalid Admin Credentials')
    }
  }

  return (
    <div className="adm-login-page">
      <div className="adm-login-card fade-in">
        <div className="adm-header">
          <div className="adm-logo">🛡️</div>
          <h2>ADMIN CONSOLE</h2>
          <p>KEC Institutional Management</p>
        </div>
        
        {error && <div className="adm-error">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="adm-field">
            <label>ADMINISTRATOR ID</label>
            <input type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="Username" required />
          </div>
          <div className="adm-field">
            <label>SECURITY KEY</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required />
          </div>
          <button type="submit" className="adm-btn">AUTHORIZE LOGIN</button>
        </form>
      </div>
    </div>
  )
}
