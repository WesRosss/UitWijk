<template>
  <v-container class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" md="8" lg="6">
        <v-card class="elevation-12 pa-8" v-if="!isAuthenticated">
          <v-card-title class="text-h4 text-center mb-8">
            Welcome to Tennis Team Website
          </v-card-title>
          
          <v-card-text class="text-center">
            <v-avatar size="120" color="primary" class="mb-4">
              <v-icon size="60" color="white">mdi-tennis</v-icon>
            </v-avatar>
            
            <p class="text-h6 mb-4">Competition Management System</p>
            <p class="text-body-1 mb-8">
              Manage your tennis team competitions, matches, and players with ease.
            </p>
            
            <v-btn
              color="primary"
              size="large"
              to="/login"
              block
              class="mb-4"
            >
              <v-icon left>mdi-login</v-icon>
              Login
            </v-btn>
            
            <v-btn
              color="secondary"
              size="large"
              to="/register"
              block
              outlined
            >
              <v-icon left>mdi-account-plus</v-icon>
              Register
            </v-btn>
          </v-card-text>
          
          <v-card-actions class="justify-center">
            <v-btn text to="/features">
              Learn More
            </v-btn>
          </v-card-actions>
        </v-card>
        
        <v-card class="elevation-12 pa-8" v-else>
          <v-card-title class="text-h4 text-center mb-8">
            Dashboard
          </v-card-title>
          
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6" lg="3" v-for="stat in stats" :key="stat.title">
                <v-card class="pa-4" :color="stat.color" dark>
                  <v-card-title class="text-h5">{{ stat.value }}</v-card-title>
                  <v-card-subtitle>{{ stat.title }}</v-card-subtitle>
                  <v-card-actions>
                    <v-icon>{{ stat.icon }}</v-icon>
                  </v-card-actions>
                </v-card>
              </v-col>
            </v-row>
            
            <v-row class="mt-8">
              <v-col cols="12" md="6">
                <v-card class="pa-6">
                  <v-card-title class="text-h6">Upcoming Matches</v-card-title>
                  <v-card-text>
                    <v-list two-line>
                      <v-list-item v-for="match in upcomingMatches" :key="match.id">
                        <v-list-item-avatar :color="getMatchStatusColor(match.status)">
                          <v-icon dark>mdi-calendar</v-icon>
                        </v-list-item-avatar>
                        <v-list-item-content>
                          <v-list-item-title>{{ match.team_names }}</v-list-item-title>
                          <v-list-item-subtitle>
                            {{ formatDate(match.match_date) }} at {{ match.start_time }}
                          </v-list-item-subtitle>
                        </v-list-item-content>
                        <v-list-item-action>
                          <v-btn :to="`/matches/${match.id}`" text>
                            <v-icon>mdi-information</v-icon>
                          </v-btn>
                        </v-list-item-action>
                      </v-list-item>
                    </v-list>
                    <p v-if="upcomingMatches.length === 0" class="text-center text--secondary">
                      No upcoming matches
                    </p>
                  </v-card-text>
                </v-card>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-card class="pa-6">
                  <v-card-title class="text-h6">Recent Notifications</v-card-title>
                  <v-card-text>
                    <v-list two-line>
                      <v-list-item v-for="notification in recentNotifications" :key="notification.id">
                        <v-list-item-avatar :color="notification.is_read ? 'grey' : 'primary'">
                          <v-icon dark v-if="!notification.is_read">mdi-email</v-icon>
                          <v-icon v-else>mdi-email-open</v-icon>
                        </v-list-item-avatar>
                        <v-list-item-content>
                          <v-list-item-title>{{ notification.title }}</v-list-item-title>
                          <v-list-item-subtitle>
                            {{ truncate(notification.message, 50) }}
                          </v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                    </v-list>
                    <p v-if="recentNotifications.length === 0" class="text-center text--secondary">
                      No recent notifications
                    </p>
                  </v-card-text>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn text to="/notifications">
                      View All
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useNotificationStore } from '@/store/notifications'
import { format } from 'date-fns'

export default {
  name: 'HomeView',
  
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()
    
    // State
    const upcomingMatches = ref([])
    const stats = ref([
      { title: 'Total Matches', value: 0, icon: 'mdi-calendar', color: 'primary' },
      { title: 'Upcoming', value: 0, icon: 'mdi-calendar-clock', color: 'info' },
      { title: 'Teams', value: 0, icon: 'mdi-account-group', color: 'success' },
      { title: 'Players', value: 0, icon: 'mdi-account-multiple', color: 'warning' },
    ])
    
    // Computed
    const isAuthenticated = computed(() => authStore.isAuthenticated)
    const recentNotifications = computed(() => notificationStore.recentNotifications)
    
    // Methods
    const formatDate = (dateString) => {
      if (!dateString) return ''
      try {
        const date = new Date(dateString)
        return format(date, 'MMM dd, yyyy')
      } catch {
        return dateString
      }
    }
    
    const truncate = (text, length) => {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }
    
    const getMatchStatusColor = (status) => {
      const colors = {
        'scheduled': 'primary',
        'confirmed': 'success',
        'cancelled': 'error',
        'completed': 'grey',
        'postponed': 'warning'
      }
      return colors[status] || 'primary'
    }
    
    const fetchDashboardData = async () => {
      try {
        // Fetch matches
        const matchesResponse = await fetch('/api/matches/?limit=5&status=scheduled,confirmed')
        const matchesData = await matchesResponse.json()
        upcomingMatches.value = matchesData.results || []
        
        // Update stats
        stats.value[0].value = matchesData.count || 0
        stats.value[1].value = upcomingMatches.value.length
        
        // Fetch teams (placeholder - implement API endpoint)
        // const teamsResponse = await fetch('/api/teams/')
        // const teamsData = await teamsResponse.json()
        // stats.value[2].value = teamsData.count || 0
        
        // Fetch players (placeholder)
        // const playersResponse = await fetch('/api/players/')
        // const playersData = await playersResponse.json()
        // stats.value[3].value = playersData.count || 0
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      }
    }
    
    // Load data on mount
    onMounted(() => {
      if (isAuthenticated.value) {
        fetchDashboardData()
        notificationStore.fetchNotifications()
      }
    })
    
    return {
      isAuthenticated,
      upcomingMatches,
      stats,
      recentNotifications,
      formatDate,
      truncate,
      getMatchStatusColor,
    }
  }
}
</script>

<style scoped>
.v-card {
  border-radius: 12px;
}

.v-avatar {
  border: 4px solid;
  border-color: rgba(255, 255, 255, 0.3);
}
</style>