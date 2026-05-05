import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
})

api.interceptors.response.use(
  res => res,
  err => {
    // We let the AuthContext handle 401s via state rather than hard redirect
    return Promise.reject(err)
  }
)

export default api
