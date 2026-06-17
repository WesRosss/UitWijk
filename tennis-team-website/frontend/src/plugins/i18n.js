import { createI18n } from 'vue-i18n'

// Import translations
import en from '@/locales/en.json'
import nl from '@/locales/nl.json'

// Create i18n instance
const i18n = createI18n({
  legacy: false, // Use Composition API
  locale: 'en', // Default locale
  fallbackLocale: 'en', // Fallback locale
  messages: {
    en,
    nl,
  },
  datetimeFormats: {
    en: {
      short: {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      },
      long: {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long',
        hour: '2-digit',
        minute: '2-digit',
      },
    },
    nl: {
      short: {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      },
      long: {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long',
        hour: '2-digit',
        minute: '2-digit',
      },
    },
  },
  numberFormats: {
    en: {
      currency: {
        style: 'currency',
        currency: 'EUR',
      },
    },
    nl: {
      currency: {
        style: 'currency',
        currency: 'EUR',
      },
    },
  },
})

export default i18n