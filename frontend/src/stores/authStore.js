import { create } from 'zustand'
import { authAPI, api } from '../api'

export const useAuthStore = create((set) => ({
  user: null,
  token: api.getToken(),
  loading: false,
  error: null,

  login: async (email, password) => {
    set({ loading: true, error: null })
    try {
      const response = await authAPI.login(email, password)
      const user = await authAPI.getMe()
      set({ user, token: response.access_token, loading: false })
      return user
    } catch (error) {
      set({ error: error.message, loading: false })
      throw error
    }
  },

  register: async (email, password) => {
    set({ loading: true, error: null })
    try {
      await authAPI.register(email, password)
      // Auto-login after registration
      return await useAuthStore.getState().login(email, password)
    } catch (error) {
      set({ error: error.message, loading: false })
      throw error
    }
  },

  logout: () => {
    authAPI.logout()
    set({ user: null, token: null })
  },

  loadUser: async () => {
    const token = api.getToken()
    if (!token) {
      set({ user: null, token: null })
      return
    }

    try {
      const user = await authAPI.getMe()
      set({ user, token })
    } catch (error) {
      // Token is invalid
      authAPI.logout()
      set({ user: null, token: null })
    }
  },
}))
