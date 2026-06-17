import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/plugins/axios'
import { useRouter } from 'vue-router'
import { useLocalStorage } from '@vueuse/core'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  
  // State
  const user = ref(null)
  const accessToken = useLocalStorage('access_token', null)
  const refreshToken = useLocalStorage('refresh_token', null)
  const isLoading = ref(false)
  const error = ref(null)
  
  // Getters
  const isAuthenticated = computed(() => {
    return !!accessToken.value && !!user.value
  })
  
  const userRole = computed(() => {
    return user.value?.role || null
  })
  
  const isAdmin = computed(() => {
    return userRole.value === 'admin' || user.value?.is_superuser
  })
  
  const isCoordinator = computed(() => {
    return ['admin', 'coordinator'].includes(userRole.value) || user.value?.is_superuser
  })
  
  const isPlayer = computed(() => {
    return userRole.value === 'player'
  })
  
  // Actions
  const initialize = async () => {
    if (accessToken.value) {
      try {
        // Fetch user data
        const response = await axios.get('/api/users/me/')
        user.value = response.data
        return true
      } catch (err) {
        console.error('Failed to initialize auth:', err)
        clearAuth()
        return false
      }
    }
    return false
  }
  
  const login = async (credentials) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await axios.post('/api/auth/token/', credentials)
      
      // Store tokens
      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh
      
      // Fetch user data
      const userResponse = await axios.get('/api/users/me/')
      user.value = userResponse.data
      
      // Set axios default headers
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
      
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed'
      clearAuth()
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const logout = async () => {
    isLoading.value = true
    error.value = null
    
    try {
      // Call logout endpoint if available
      await axios.post('/api/auth/logout/')
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      clearAuth()
      isLoading.value = false
    }
  }
  
  const register = async (userData) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await axios.post('/api/users/register/', userData)
      
      // Auto login after registration
      await login({
        username: userData.username,
        password: userData.password
      })
      
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Registration failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      clearAuth()
      return false
    }
    
    try {
      const response = await axios.post('/api/auth/token/refresh/', {
        refresh: refreshToken.value
      })
      
      accessToken.value = response.data.access
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`
      
      return true
    } catch (err) {
      console.error('Token refresh failed:', err)
      clearAuth()
      return false
    }
  }
  
  const updateUser = async (userData) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await axios.patch('/api/users/me/', userData)
      user.value = response.data
      return true
    } catch (err) {
      error.value = err.response?.data || 'Update failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const changePassword = async (passwordData) => {
    isLoading.value = true
    error.value = null
    
    try {
      await axios.post('/api/users/me/change-password/', passwordData)
      return true
    } catch (err) {
      error.value = err.response?.data || 'Password change failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const forgotPassword = async (email) => {
    isLoading.value = true
    error.value = null
    
    try {
      await axios.post('/api/auth/forgot-password/', { email })
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Password reset request failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const resetPassword = async (token, passwordData) => {
    isLoading.value = true
    error.value = null
    
    try {
      await axios.post(`/api/auth/reset-password/${token}/`, passwordData)
      return true
    } catch (err) {
      error.value = err.response?.data || 'Password reset failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const clearAuth = () => {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    error.value = null
    delete axios.defaults.headers.common['Authorization']
  }
  
  // Setup axios interceptors
  const setupInterceptors = () => {
    // Request interceptor
    axios.interceptors.request.use(
      async (config) => {
        if (accessToken.value) {
          config.headers.Authorization = `Bearer ${accessToken.value}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )
    
    // Response interceptor
    axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config
        
        // If 401 error and not a retry request
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true
          
          try {
            const refreshed = await refreshAccessToken()
            if (refreshed) {
              originalRequest.headers.Authorization = `Bearer ${accessToken.value}`
              return axios(originalRequest)
            }
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError)
            clearAuth()
            router.push({ name: 'login' })
            return Promise.reject(refreshError)
          }
        }
        
        return Promise.reject(error)
      }
    )
  }
  
  // Initialize interceptors
  setupInterceptors()
  
  return {
    // State
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    
    // Getters
    isAuthenticated,
    userRole,
    isAdmin,
    isCoordinator,
    isPlayer,
    
    // Actions
    initialize,
    login,
    logout,
    register,
    refreshAccessToken,
    updateUser,
    changePassword,
    forgotPassword,
    resetPassword,
    clearAuth,
    setupInterceptors
  }
})