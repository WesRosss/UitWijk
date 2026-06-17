<template>
  <v-app>
    <!-- Navigation Drawer -->
    <v-navigation-drawer
      v-model="drawer"
      app
      :clipped="true"
      :mini-variant="miniDrawer"
      color="primary"
      dark
    >
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-avatar color="white">
            <v-img
              v-if="logoUrl"
              :src="logoUrl"
              contain
              max-height="40"
            />
            <v-icon v-else color="primary" large>mdi-tennis</v-icon>
          </v-list-item-avatar>
          <v-list-item-content>
            <v-list-item-title class="text-h6 white--text">
              TV UitWijk
            </v-list-item-title>
            <v-list-item-subtitle class="white--text">
              Tennis Team
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </template>

      <v-divider></v-divider>

      <v-list dense nav>
        <v-list-item
          v-for="item in navItems"
          :key="item.title"
          :to="item.to"
          link
          exact
          active-class="primary--text"
        >
          <v-list-item-icon>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>

      <template v-slot:append>
        <v-divider></v-divider>
        <v-list dense nav>
          <v-list-item @click="toggleTheme">
            <v-list-item-icon>
              <v-icon>{{ darkMode ? 'mdi-weather-night' : 'mdi-weather-sunny' }}</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>{{ darkMode ? 'Dark Mode' : 'Light Mode' }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          
          <v-list-item @click="logout" v-if="isAuthenticated">
            <v-list-item-icon>
              <v-icon>mdi-logout</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>Logout</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          
          <v-list-item to="/login" v-else>
            <v-list-item-icon>
              <v-icon>mdi-login</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>Login</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </template>
    </v-navigation-drawer>

    <!-- App Bar -->
    <v-app-bar
      app
      :clipped-left="true"
      color="primary"
      dark
      dense
    >
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      
      <v-toolbar-title class="text-h6">
        <span class="hidden-sm-and-down">TV UitWijk Tennis Team</span>
      </v-toolbar-title>

      <v-spacer></v-spacer>

      <!-- User Menu -->
      <v-menu
        v-if="isAuthenticated"
        bottom
        left
        offset-y
        origin="top right"
        transition="scale-transition"
      >
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            text
            v-bind="attrs"
            v-on="on"
            class="mr-2"
          >
            <v-avatar size="32" color="white" class="mr-2">
              <span class="primary--text text-caption">{{ userInitials }}</span>
            </v-avatar>
            <span class="hidden-sm-and-down">{{ userName }}</span>
            <v-icon right>mdi-chevron-down</v-icon>
          </v-btn>
        </template>

        <v-list dense>
          <v-list-item to="/profile">
            <v-list-item-icon>
              <v-icon>mdi-account</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>Profile</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          
          <v-list-item to="/settings">
            <v-list-item-icon>
              <v-icon>mdi-cog</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>Settings</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          
          <v-divider></v-divider>
          
          <v-list-item @click="logout">
            <v-list-item-icon>
              <v-icon>mdi-logout</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>Logout</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-menu>

      <!-- Notifications -->
      <v-btn icon @click="toggleNotifications" v-if="isAuthenticated">
        <v-badge
          color="accent"
          :content="unreadNotifications"
          :value="unreadNotifications"
          overlap
        >
          <v-icon>mdi-bell</v-icon>
        </v-badge>
      </v-btn>
    </v-app-bar>

    <!-- Main Content -->
    <v-main>
      <v-container fluid class="fill-height">
        <v-slide-y-transition mode="out-in">
          <router-view />
        </v-slide-y-transition>
      </v-container>
    </v-main>

    <!-- Footer -->
    <v-footer app color="primary" dark class="text-center py-2">
      <v-container>
        <span>&copy; {{ new Date().getFullYear() }} TV UitWijk Tennis Team. All rights reserved.</span>
        <v-spacer></v-spacer>
        <span class="text-caption">v1.0.0</span>
      </v-container>
    </v-footer>

    <!-- Notification Drawer -->
    <v-navigation-drawer
      v-model="notificationsDrawer"
      right
      temporary
      width="400"
      class="notifications-drawer"
    >
      <template v-slot:prepend>
        <v-toolbar flat dense class="primary" dark>
          <v-toolbar-title class="text-h6">Notifications</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn icon @click="markAllAsRead" v-if="unreadNotifications > 0">
            <v-icon>mdi-email-mark-as-unread</v-icon>
          </v-btn>
          <v-btn icon @click="notificationsDrawer = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-toolbar>
      </template>

      <v-list three-line subheader>
        <v-subheader>Recent Notifications</v-subheader>
        
        <template v-if="notifications.length > 0">
          <v-list-item
            v-for="notification in notifications"
            :key="notification.id"
            :class="{ 'unread': !notification.is_read }"
            @click="readNotification(notification)"
          >
            <v-list-item-avatar :color="notification.is_read ? 'grey' : 'primary'">
              <v-icon dark v-if="!notification.is_read">mdi-email</v-icon>
              <v-icon v-else>mdi-email-open</v-icon>
            </v-list-item-avatar>
            
            <v-list-item-content>
              <v-list-item-title>{{ notification.title }}</v-list-item-title>
              <v-list-item-subtitle>
                {{ notification.message }}
                <span class="text-caption d-block">
                  {{ formatDate(notification.created_at) }}
                </span>
              </v-list-item-subtitle>
            </v-list-item-content>
            
            <v-list-item-action>
              <v-icon :color="notification.is_read ? 'grey' : 'primary'">
                mdi-information
              </v-icon>
            </v-list-item-action>
          </v-list-item>
        </template>
        
        <v-list-item v-else>
          <v-list-item-content>
            <v-list-item-title class="text-center">
              No notifications found
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>

      <template v-slot:append>
        <div class="pa-2 text-center">
          <v-btn text @click="loadMoreNotifications" v-if="hasMoreNotifications">
            Load More
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <!-- Snackbar for global messages -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      :top="true"
      :right="true"
    >
      {{ snackbar.text }}
      <template v-slot:action="{ attrs }">
        <v-btn
          text
          v-bind="attrs"
          @click="snackbar.show = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useNotificationStore } from '@/store/notifications'
import { useTheme } from 'vuetify'
import { format } from 'date-fns'

export default {
  name: 'App',
  
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()
    const theme = useTheme()
    
    // State
    const drawer = ref(true)
    const miniDrawer = ref(false)
    const notificationsDrawer = ref(false)
    const logoUrl = ref('/logo-192.png')
    
    // Navigation items based on user role
    const navItems = computed(() => {
      const items = [
        { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/' },
        { title: 'Matches', icon: 'mdi-calendar', to: '/matches' },
        { title: 'Teams', icon: 'mdi-account-group', to: '/teams' },
      ]
      
      if (authStore.isAuthenticated) {
        if (authStore.user?.role === 'admin') {
          items.push({ title: 'Users', icon: 'mdi-account-multiple', to: '/users' })
        }
        items.push({ title: 'My Availability', icon: 'mdi-calendar-check', to: '/availability' })
        items.push({ title: 'My Assignments', icon: 'mdi-clipboard-list', to: '/assignments' })
      }
      
      return items
    })
    
    // User info
    const userName = computed(() => {
      return authStore.user ? `${authStore.user.first_name} ${authStore.user.last_name}` : 'Guest'
    })
    
    const userInitials = computed(() => {
      return authStore.user ? 
        `${authStore.user.first_name.charAt(0)}${authStore.user.last_name.charAt(0)}` : 'G'
    })
    
    const isAuthenticated = computed(() => authStore.isAuthenticated)
    
    // Dark mode
    const darkMode = computed(() => theme.global.current.value.dark)
    
    // Notifications
    const notifications = computed(() => notificationStore.notifications)
    const unreadNotifications = computed(() => notificationStore.unreadCount)
    const hasMoreNotifications = computed(() => notificationStore.hasMore)
    
    // Snackbar
    const snackbar = ref({
      show: false,
      text: '',
      color: 'info',
      timeout: 5000
    })
    
    // Methods
    const toggleTheme = () => {
      theme.global.name.value = darkMode.value ? 'light' : 'dark'
    }
    
    const toggleNotifications = () => {
      notificationsDrawer.value = !notificationsDrawer.value
      if (notificationsDrawer.value) {
        notificationStore.fetchNotifications()
      }
    }
    
    const readNotification = (notification) => {
      notificationStore.markAsRead(notification.id)
      notificationsDrawer.value = false
    }
    
    const markAllAsRead = () => {
      notificationStore.markAllAsRead()
    }
    
    const loadMoreNotifications = () => {
      notificationStore.fetchMoreNotifications()
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return ''
      try {
        const date = new Date(dateString)
        return format(date, 'MMM dd, yyyy HH:mm')
      } catch {
        return dateString
      }
    }
    
    const logout = async () => {
      try {
        await authStore.logout()
        router.push('/login')
        showSnackbar('Logged out successfully', 'success')
      } catch (error) {
        showSnackbar('Error logging out', 'error')
      }
    }
    
    const showSnackbar = (text, color = 'info') => {
      snackbar.value = {
        show: true,
        text,
        color,
        timeout: 5000
      }
    }
    
    // Load initial data
    onMounted(() => {
      if (authStore.isAuthenticated) {
        notificationStore.fetchUnreadCount()
      }
    })
    
    return {
      drawer,
      miniDrawer,
      notificationsDrawer,
      logoUrl,
      navItems,
      userName,
      userInitials,
      isAuthenticated,
      darkMode,
      notifications,
      unreadNotifications,
      hasMoreNotifications,
      snackbar,
      toggleTheme,
      toggleNotifications,
      readNotification,
      markAllAsRead,
      loadMoreNotifications,
      formatDate,
      logout,
    }
  }
}
</script>

<style lang="scss" scoped>
.v-app {
  min-height: 100vh;
}

.notifications-drawer {
  .v-list-item.unread {
    background-color: rgba(196, 30, 58, 0.05);
    border-left: 3px solid #C41E3A;
  }
  
  .v-list-item.unread:hover {
    background-color: rgba(196, 30, 58, 0.1);
  }
}

::v-deep .v-navigation-drawer__content {
  overflow-y: auto;
}
</style>
