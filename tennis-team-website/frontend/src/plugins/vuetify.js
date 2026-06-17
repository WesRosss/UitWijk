import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import 'vuetify/styles'

// TV UitWijk Brand Colors
// Primary: Deep Red (#C41E3A) - Main brand color
// Secondary: Navy Blue (#003366) - Accent color  
// Accent: Gold (#FFD700) - Highlight color

// Custom theme colors for TV UitWijk
const customLightTheme = {
  dark: false,
  colors: {
    primary: '#C41E3A',      // TV UitWijk Red
    secondary: '#003366',    // TV UitWijk Navy Blue
    accent: '#FFD700',       // TV UitWijk Gold
    error: '#D32F2F',
    info: '#1976D2',
    success: '#4CAF50',
    warning: '#FF9800',
    background: '#F5F5F5',
    surface: '#FFFFFF',
    'primary-darken-1': '#A0152D',
    'secondary-darken-1': '#001933',
    'accent-darken-1': '#FFA000',
    'on-primary': '#FFFFFF',
    'on-secondary': '#FFFFFF',
    'on-accent': '#000000',
  },
}

const customDarkTheme = {
  dark: true,
  colors: {
    primary: '#E53935',      // Lighter red for dark mode
    secondary: '#1976D2',    // Lighter blue for dark mode
    accent: '#FFD700',       // Gold stays the same
    error: '#FF5252',
    info: '#2196F3',
    success: '#81C784',
    warning: '#FFC107',
    background: '#121212',
    surface: '#1E1E1E',
    'primary-darken-1': '#C41E3A',
    'secondary-darken-1': '#003366',
    'accent-darken-1': '#FFA000',
    'on-primary': '#FFFFFF',
    'on-secondary': '#FFFFFF',
    'on-accent': '#000000',
  },
}

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: customLightTheme,
      dark: customDarkTheme,
    },
    variations: {
      colors: ['primary', 'secondary', 'accent'],
      lighten: 4,
      darken: 4,
    },
  },
  defaults: {
    VBtn: {
      rounded: 'lg',
      elevation: 0,
    },
    VCard: {
      rounded: 'lg',
      elevation: 2,
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
      rounded: 'lg',
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
      rounded: 'lg',
    },
    VCheckbox: {
      density: 'comfortable',
    },
    VRadio: {
      density: 'comfortable',
    },
    VSwitch: {
      density: 'comfortable',
    },
  },
  display: {
    mobileBreakpoint: 'sm',
    thresholds: {
      xs: 0,
      sm: 600,
      md: 960,
      lg: 1280,
      xl: 1920,
    },
  },
})
