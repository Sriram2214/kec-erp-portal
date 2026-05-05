import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import './FacultyLogin.css'

export default function FacultyLogin() {
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
      if (user.role !== 'faculty' && user.role !== 'admin') {
        setError('Unauthorized: This portal is for KEC Faculty only.')
        return
      }
      navigate('/dashboard')
    } catch (err) {
      setError('Invalid Faculty Credentials')
    }
  }

  return (
    <div className="fac-login-page">
      <div className="fac-login-card fade-in">
        <div className="fac-header">
          <div className="fac-icon">🏢</div>
          <h2>FACULTY PORTAL</h2>
          <p>Academic Management System</p>
        </div>
        
        {error && <div className="fac-error">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="fac-field">
            <label>EMPLOYEE ID</label>
            <input type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="e.g. KECF001" required />
          </div>
          <div className="fac-field">
            <label>SECURITY PASSCODE</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required />
          </div>
          <button type="submit" className="fac-btn">VERIFY & ENTER</button>
        </form>
      </div>
    </div>
  )
}
