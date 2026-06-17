<template>
  <v-container class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="10" md="8" lg="6" xl="4">
        <v-card class="elevation-12 pa-8" max-width="500">
          <v-card-title class="text-h4 text-center mb-8">
            Login
          </v-card-title>
          
          <v-form @submit.prevent="login" ref="loginForm">
            <v-card-text>
              <v-alert
                v-if="error"
                type="error"
                class="mb-6"
                dismissible
                @input="error = null"
              >
                {{ error }}
              </v-alert>
              
              <v-text-field
                v-model="form.username"
                label="Username"
                prepend-inner-icon="mdi-account"
                :rules="[requiredRule, usernameRule]"
                required
                outlined
                rounded
                class="mb-4"
              ></v-text-field>
              
              <v-text-field
                v-model="form.password"
                label="Password"
                prepend-inner-icon="mdi-lock"
                :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                :type="showPassword ? 'text' : 'password'"
                @click:append="showPassword = !showPassword"
                :rules="[requiredRule, passwordRule]"
                required
                outlined
                rounded
                class="mb-4"
              ></v-text-field>
              
              <v-checkbox
                v-model="form.rememberMe"
                label="Remember me"
                class="mb-4"
              ></v-checkbox>
            </v-card-text>
            
            <v-card-actions class="px-6 pb-6">
              <v-btn
                color="primary"
                type="submit"
                :loading="isLoading"
                block
                large
                rounded
              >
                <v-icon left>mdi-login</v-icon>
                Login
              </v-btn>
            </v-card-actions>
            
            <v-card-text class="text-center">
              <v-divider class="mb-4"></v-divider>
              
              <v-btn text to="/forgot-password" class="text-caption">
                Forgot password?
              </v-btn>
              
              <span class="mx-2 text-caption">or</span>
              
              <v-btn text to="/register" class="text-caption">
                Create an account
              </v-btn>
            </v-card-text>
          </v-form>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'

export default {
  name: 'LoginView',
  
  setup() {
    const router = useRouter()
    const route = useRoute()
    const authStore = useAuthStore()
    
    // State
    const form = ref({
      username: '',
      password: '',
      rememberMe: false
    })
    
    const showPassword = ref(false)
    const error = ref(null)
    const isLoading = ref(false)
    const loginForm = ref(null)
    
    // Computed
    const isAuthenticated = computed(() => authStore.isAuthenticated)
    
    // Validation rules
    const requiredRule = value => !!value || 'This field is required'
    const usernameRule = value => {
      if (!value) return true
      if (value.length < 3) return 'Username must be at least 3 characters'
      if (value.length > 150) return 'Username must be less than 150 characters'
      return true
    }
    const passwordRule = value => {
      if (!value) return true
      if (value.length < 8) return 'Password must be at least 8 characters'
      return true
    }
    
    // Methods
    const login = async () => {
      // Validate form
      const { valid } = await loginForm.value.validate()
      if (!valid) return
      
      error.value = null
      isLoading.value = true
      
      try {
        await authStore.login({
          username: form.value.username,
          password: form.value.password
        })
        
        // Redirect to dashboard or original page
        const redirect = route.query.redirect || '/dashboard'
        router.push(redirect)
        
      } catch (err) {
        error.value = err.message || 'Login failed. Please check your credentials.'
      } finally {
        isLoading.value = false
      }
    }
    
    // Check if already authenticated
    onMounted(() => {
      if (isAuthenticated.value) {
        router.push('/dashboard')
      }
    })
    
    return {
      form,
      showPassword,
      error,
      isLoading,
      loginForm,
      requiredRule,
      usernameRule,
      passwordRule,
      login,
    }
  }
}
</script>

<style scoped>
.v-card {
  border-radius: 12px;
}

.v-text-field {
  font-size: 14px;
}

.v-btn {
  text-transform: none;
  letter-spacing: 0;
}
</style>