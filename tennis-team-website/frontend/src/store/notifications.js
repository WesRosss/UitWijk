import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/plugins/axios'

export const useNotificationStore = defineStore('notifications', () => {
  // State
  const notifications = ref([])
  const unreadCount = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const total = ref(0)
  const isLoading = ref(false)
  const error = ref(null)
  const hasMore = computed(() => {
    return notifications.value.length < total.value
  })
  
  // Getters
  const unreadNotifications = computed(() => {
    return notifications.value.filter(n => !n.is_read)
  })
  
  const recentNotifications = computed(() => {
    return notifications.value.slice(0, 5)
  })
  
  // Actions
  const fetchNotifications = async (reset = true) => {
    if (reset) {
      page.value = 1
      notifications.value = []
    }
    
    isLoading.value = true
    error.value = null
    
    try {
      const response = await axios.get('/api/notifications/', {
        params: {
          page: page.value,
          page_size: pageSize.value,
          ordering: '-created_at'
        }
      })
      
      total.value = response.data.count
      
      if (reset) {
        notifications.value = response.data.results
      } else {
        notifications.value = [...notifications.value, ...response.data.results]
      }
      
      page.value += 1
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch notifications'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const fetchMoreNotifications = async () => {
    if (!hasMore.value || isLoading.value) return
    return fetchNotifications(false)
  }
  
  const fetchUnreadCount = async () => {
    try {
      const response = await axios.get('/api/notifications/unread-count/')
      unreadCount.value = response.data.count
      return true
    } catch (err) {
      console.error('Failed to fetch unread count:', err)
      return false
    }
  }
  
  const markAsRead = async (notificationId) => {
    try {
      await axios.patch(`/api/notifications/${notificationId}/mark-read/`)
      
      // Update local state
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index !== -1) {
        notifications.value[index].is_read = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
      
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to mark notification as read'
      throw err
    }
  }
  
  const markAllAsRead = async () => {
    try {
      await axios.post('/api/notifications/mark-all-read/')
      
      // Update local state
      notifications.value.forEach(n => {
        n.is_read = true
      })
      unreadCount.value = 0
      
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to mark all notifications as read'
      throw err
    }
  }
  
  const deleteNotification = async (notificationId) => {
    try {
      await axios.delete(`/api/notifications/${notificationId}/`)
      
      // Update local state
      notifications.value = notifications.value.filter(n => n.id !== notificationId)
      
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete notification'
      throw err
    }
  }
  
  const deleteAllNotifications = async () => {
    try {
      await axios.post('/api/notifications/delete-all/')
      
      // Update local state
      notifications.value = []
      unreadCount.value = 0
      
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete all notifications'
      throw err
    }
  }
  
  const createNotification = async (notificationData) => {
    try {
      const response = await axios.post('/api/notifications/', notificationData)
      
      // Add to local state
      notifications.value.unshift(response.data)
      if (!response.data.is_read) {
        unreadCount.value += 1
      }
      
      return response.data
    } catch (err) {
      error.value = err.response?.data || 'Failed to create notification'
      throw err
    }
  }
  
  const updateNotificationPreferences = async (preferences) => {
    try {
      await axios.post('/api/notifications/preferences/', { preferences })
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update notification preferences'
      throw err
    }
  }
  
  const getNotificationPreferences = async () => {
    try {
      const response = await axios.get('/api/notifications/preferences/')
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to get notification preferences'
      throw err
    }
  }
  
  const clearError = () => {
    error.value = null
  }
  
  return {
    // State
    notifications,
    unreadCount,
    page,
    pageSize,
    total,
    isLoading,
    error,
    hasMore,
    
    // Getters
    unreadNotifications,
    recentNotifications,
    
    // Actions
    fetchNotifications,
    fetchMoreNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    deleteAllNotifications,
    createNotification,
    updateNotificationPreferences,
    getNotificationPreferences,
    clearError
  }
})