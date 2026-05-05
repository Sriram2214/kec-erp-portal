import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import './StudentLogin.css'

export default function StudentLogin() {
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
      if (user.role !== 'student' && user.role !== 'admin') {
        setError('Unauthorized: This portal is for KEC Students only.')
        return
      }
      navigate('/dashboard')
    } catch (err) {
      setError('Invalid Student Credentials')
    }
  }

  return (
    <div className="std-login-page">
      <div className="std-login-card fade-in">
        <div className="std-header">
          <div className="std-logo">🎓</div>
          <h2>STUDENT HUB</h2>
          <p>Kings Engineering College Portal</p>
        </div>
        
        {error && <div className="std-error">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="std-field">
            <label>REGISTER NUMBER</label>
            <input type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="e.g. 911221104001" required />
          </div>
          <div className="std-field">
            <label>PASSWORD</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required />
          </div>
          <button type="submit" className="std-btn">ENTER PORTAL</button>
        </form>
      </div>
    </div>
  )
}
