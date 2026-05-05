import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import './Login.css'

const ROLES = ['Student', 'Faculty', 'Admin', 'COE']

const ROLE_META = {
  Student: { label: 'Register Number', placeholder: '' },
  Faculty:  { label: 'Faculty Code',     placeholder: '' },
  Admin:    { label: 'Username',          placeholder: '' },
  COE:      { label: 'Username',          placeholder: '' },
}

/* floating particle canvas */
function ParticleCanvas() {
  const ref = useRef(null)
  useEffect(() => {
    const canvas = ref.current
    const ctx = canvas.getContext('2d')
    let w = canvas.width  = canvas.offsetWidth
    let h = canvas.height = canvas.offsetHeight
    const particles = Array.from({ length: 55 }, () => ({
      x: Math.random() * w, y: Math.random() * h,
      r: Math.random() * 1.8 + 0.3,
      dx: (Math.random() - 0.5) * 0.35,
      dy: (Math.random() - 0.5) * 0.35,
      o: Math.random() * 0.5 + 0.2,
    }))
    let raf
    function draw() {
      ctx.clearRect(0, 0, w, h)
      particles.forEach(p => {
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(201,162,39,${p.o})`
        ctx.fill()
        p.x += p.dx; p.y += p.dy
        if (p.x < 0 || p.x > w) p.dx *= -1
        if (p.y < 0 || p.y > h) p.dy *= -1
      })
      raf = requestAnimationFrame(draw)
    }
    draw()
    const onResize = () => {
      w = canvas.width  = canvas.offsetWidth
      h = canvas.height = canvas.offsetHeight
    }
    window.addEventListener('resize', onResize)
    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', onResize) }
  }, [])
  return <canvas ref={ref} className="particle-canvas" />
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

  // Redirect if already logged in
  useEffect(() => {
    if (user) {
      navigate('/dashboard', { replace: true })
    }
  }, [user, navigate])

  const handleSubmit = async e => {
    e.preventDefault()
    setError('')
    setLoading(true)
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
    <div className="login-page">
      {/* Animated BG */}
      <div className="login-bg" />
      <div className="login-overlay" />
      <ParticleCanvas />

      {/* ── LEFT PANEL ── */}
      <div className="login-left">
        <div className="left-logo">
          <img src="/logo.png" alt="KEC" />
        </div>
        <h1 className="left-title">
          Kings<br />
          <span>Engineering</span><br />
          College
        </h1>
        <div className="left-divider" />
        <p className="left-tagline">
          Excellence · Innovation · Integrity
        </p>
        <p className="left-desc">
          Empowering students and faculty with a seamless,
          secure, and real-time examination management experience.
        </p>
        <div className="left-badges">
          <span>🏆 NAAC A+</span>
          <span>🎓 NBA Accredited</span>
          <span>📍 Chennai</span>
        </div>
      </div>

      {/* ── RIGHT — LOGIN CARD ── */}
      <div className="login-right">
        <form className="login-card" onSubmit={handleSubmit}>

          {/* Header */}
          <div className="card-header">
            <div className="card-logo">
              <img src="/logo.png" alt="KEC Logo" />
            </div>
            <div className="card-header-text">
              <div className="card-title">KEC Portal</div>
              <div className="card-sub">Examination Management System</div>
            </div>
          </div>

          <div className="card-divider" />

          {/* Role Tabs */}
          <div className="role-tabs">
            {ROLES.map(r => (
              <button
                key={r} type="button"
                className={`role-tab${role === r ? ' active' : ''}`}
                onClick={() => { setRole(r); setError('') }}
              >
                {r}
              </button>
            ))}
          </div>

          {/* Fields */}
          <div className="form-group">
            <label>{meta.label}</label>
            <input
              type="text"
              placeholder={meta.placeholder}
              value={username}
              onChange={e => setUsername(e.target.value)}
              required autoFocus
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <div className="pwd-wrap">
              <input
                type={showPwd ? 'text' : 'password'}
                placeholder=""
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                className="pwd-toggle"
                onClick={() => setShowPwd(s => !s)}
                tabIndex={-1}
                aria-label={showPwd ? 'Hide password' : 'Show password'}
              >
                {showPwd ? (
                  /* Eye-off SVG */
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
                    <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                ) : (
                  /* Eye SVG */
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                )}
              </button>
            </div>
          </div>

          {error && <div className="login-err">⚠ {error}</div>}

          <button type="submit" className="login-btn" disabled={loading}>
            {loading
              ? <span className="spinner" />
              : <><span>Sign In</span><span className="btn-arrow">→</span></>
            }
          </button>

          <div className="login-footer">
            <a href="#">Forgot Password?</a>
            <a href="#">Help & Support</a>
          </div>
        </form>
      </div>
    </div>
  )
}
