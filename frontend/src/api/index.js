import axios from 'axios'
import { toastEvents } from './toastBus'

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
        const stored = localStorage.getItem('kec_user')
        const username = stored ? JSON.parse(stored).username : null
        if (username) {
          await axios.post('/api/auth/bypass-login', { username }, { withCredentials: true })
          err.config._retried = true
          _restoring = false
          return api.request(err.config)
        }
      } catch (e) { /* silent */ }
      _restoring = false
    }

    // Global Error Notification
    const msg = err.response?.data?.message || 'Server connection lost. Please try again.'
    if (status !== 401) {
      toastEvents.emit(msg, 'error')
    }
    
    return Promise.reject(err)
  }
)

export default api
