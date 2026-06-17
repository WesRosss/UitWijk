import axios from 'axios'

// Create axios instance with default configuration
const instance = axios.create({
  baseURL: import.meta.env.VUE_APP_API_URL || '/api',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
})

// Request interceptor
instance.interceptors.request.use(
  (config) => {
    // Add any request modifications here
    // For example, add auth token if available
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
instance.interceptors.response.use(
  (response) => {
    // Modify response data here if needed
    return response
  },
  (error) => {
    // Handle errors globally
    if (error.response) {
      // Server responded with a status code outside 2xx
      const status = error.response.status
      
      switch (status) {
        case 401:
          // Unauthorized - token might be expired
          console.warn('Unauthorized - please login again')
          break
        case 403:
          // Forbidden - user doesn't have permission
          console.warn('Forbidden - insufficient permissions')
          break
        case 404:
          // Not found
          console.warn('Resource not found')
          break
        case 500:
          // Server error
          console.error('Server error')
          break
        default:
          console.error(`HTTP Error: ${status}`)
      }
    } else if (error.request) {
      // Request was made but no response received
      console.error('No response received from server')
    } else {
      // Something happened in setting up the request
      console.error('Request setup error:', error.message)
    }
    
    return Promise.reject(error)
  }
)

export default instance