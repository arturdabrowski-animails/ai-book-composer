// API configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || ''

// Helper to build full API URL
export const getApiUrl = (path) => {
  if (!path.startsWith('/')) {
    path = '/' + path
  }
  return API_BASE_URL + path
}
