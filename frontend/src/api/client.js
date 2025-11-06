// Base API client

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class APIClient {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  getToken() {
    return localStorage.getItem('token')
  }

  setToken(token) {
    localStorage.setItem('token', token)
  }

  removeToken() {
    localStorage.removeItem('token')
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`

    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    const token = this.getToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      })

      // Handle 204 No Content
      if (response.status === 204) {
        return null
      }

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Request failed')
      }

      return data
    } catch (error) {
      console.error('API Error:', error)
      throw error
    }
  }

  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' })
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' })
  }
}

export const api = new APIClient()
