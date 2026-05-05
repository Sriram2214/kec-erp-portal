import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import './Login.css'

const ROLES = ['Student', 'Faculty', 'Admin', 'COE']

const ROLE_META = {
  Student: { label: 'REGISTER NUMBER', placeholder: '' },
  Faculty:  { label: 'FACULTY CODE',     placeholder: '' },
  Admin:    { label: 'USERNAME',          placeholder: '' },
  COE:      { label: 'USERNAME',          placeholder: '' },
}

function ParticleCanvas() {
  const ref = useRef(null)
  useEffect(() => {
    const canvas = ref.current
    const ctx = canvas.getContext('2d')
    let w = canvas.width  = window.innerWidth
    let h = canvas.height = window.innerHeight
    const particles = Array.from({ length: 40 }, () => ({
      x: Math.random() * w, y: Math.random() * h,
      r: Math.random() * 1.5 + 0.5,
      dx: (Math.random() - 0.5) * 0.2,
      dy: (Math.random() - 0.5) * 0.2,
      o: Math.random() * 0.3 + 0.1,
    }))
    let raf
    function draw() {
      ctx.clearRect(0, 0, w, h)
      particles.forEach(p => {
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(212,175,55,${p.o})`
        ctx.fill()
        p.x += p.dx; p.y += p.dy
        if (p.x < 0 || p.x > w) p.dx *= -1
        if (p.y < 0 || p.y > h) p.dy *= -1
      })
      raf = requestAnimationFrame(draw)
    }
    draw()
    const onResize = () => {
      w = canvas.width  = window.innerWidth
      h = canvas.height = window.innerHeight
    }
    window.addEventListener('resize', onResize)
    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', onResize) }
  }, [])
  return <canvas ref={ref} className="login-particles" />
}

export default function Login() {
  const { user, login } = useAuth()
  const navigate   = useNavigate()
  const [role, setRole]         = useState('Student')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)
  const [showPwd, setShowPwd]   = useState(false)

  useEffect(() => {
    if (user) navigate('/dashboard', { replace: true })
  }, [user, navigate])

  const handleSubmit = async e => {
    e.preventDefault()
    setError(''); setLoading(true)
    try {
      await login(username, password, role)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err.response?.data?.message || 'Invalid credentials. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const meta = ROLE_META[role]

  return (
    <div className="login-root">
      <div className="login-bg-texture" />
      <ParticleCanvas />
      
      <div className="login-centered-container">
        <form className="login-card" onSubmit={handleSubmit}>
          
          <div className="login-branding">
            <div className="brand-logo-ring">
              <div className="brand-logo">
                <img src="/logo.png" alt="KEC Logo" />
              </div>
            </div>
            <h1 className="brand-name">KEC PORTAL</h1>
            <div className="brand-divider" />
            <p className="brand-tagline">EXAMINATION MANAGEMENT SYSTEM</p>
          </div>

            <div className="role-selector">
              {ROLES.map(r => (
                <button
                  key={r} type="button"
                  className={`role-btn${role === r ? ' active' : ''}`}
                  onClick={() => { setRole(r); setError('') }}
                >
                  {r.toUpperCase()}
                </button>
              ))}
            </div>

            <div className="login-fields">
              <div className="login-field-group">
                <label>{meta.label}</label>
                <input
                  type="text"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  placeholder={`Enter ${meta.label.toLowerCase()}`}
                  required autoFocus
                />
              </div>

              <div className="login-field-group">
                <label>PASSWORD</label>
                <div className="login-input-wrap">
                  <input
                    type={showPwd ? 'text' : 'password'}
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                  />
                  <button
                    type="button"
                    className="login-pwd-toggle"
                    onClick={() => setShowPwd(s => !s)}
                    tabIndex={-1}
                  >
                    {showPwd ? (
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18">
                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/>
                      </svg>
                    ) : (
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
                      </svg>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {error && <div className="login-error-msg">⚠ {error}</div>}

            <button type="submit" className="login-submit-btn" disabled={loading}>
              {loading ? <span className="login-btn-spinner" /> : <>SIGN IN <span>→</span></>}
            </button>

            <div className="login-card-footer">
              <a href="#">FORGOT PASSWORD?</a>
              <a href="#">HELP & SUPPORT</a>
            </div>
        </form>
      </div>
    </div>
  )
}
