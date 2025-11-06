import { api } from './client'

export const authAPI = {
  async register(email, password) {
    return api.post('/api/auth/register', { email, password })
  },

  async login(email, password) {
    const response = await api.post('/api/auth/login', { email, password })
    if (response.access_token) {
      api.setToken(response.access_token)
    }
    return response
  },

  async getMe() {
    return api.get('/api/auth/me')
  },

  logout() {
    api.removeToken()
  },
}
