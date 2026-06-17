import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import i18n from './plugins/i18n'
import axios from './plugins/axios'
import './styles/main.scss'

// Create the Vue application
const app = createApp(App)

// Install plugins
app.use(createPinia())
app.use(router)
app.use(vuetify)
app.use(i18n)

// Configure axios globally
app.config.globalProperties.$axios = axios
app.config.globalProperties.$http = axios

// Error handling for axios
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error handler:', err)
  // You can add error reporting here
}

// Mount the application
app.mount('#app')