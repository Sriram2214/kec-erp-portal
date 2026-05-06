import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
})

// ── Auto-restore server session on 401 (Vercel serverless cold-start) ──
let _restoring = false
api.interceptors.response.use(
  res => res,
  async err => {
    const status = err.response?.status
    if (status === 401 && !err.config._retried && !_restoring) {
      _restoring = true
      try {
        // Detect which user was last logged in from the page
        const stored = localStorage.getItem('kec_user')
        const username = stored ? JSON.parse(stored).username : null
        if (username) {
          await axios.post('/api/auth/bypass-login', { username }, { withCredentials: true })
          err.config._retried = true
          _restoring = false
          return api.request(err.config)
        }
      } catch (e) {
        // silent
      }
      _restoring = false
    }
    return Promise.reject(err)
  }
)

export default api
