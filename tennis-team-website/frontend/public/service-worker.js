// Service Worker for TV UitWijk Tennis Team PWA
// This file enables offline support and caching for the PWA

const CACHE_NAME = 'tv-uitwijk-tennis-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.png',
  '/logo-192.png',
  '/logo-512.png',
  '/logo-192-maskable.png',
  '/logo-512-maskable.png',
  '/assets/js/main.js',
  '/assets/css/main.css',
];

// Install service worker and cache assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Caching assets for TV UitWijk Tennis Team PWA');
        return cache.addAll(ASSETS_TO_CACHE);
      })
      .catch((error) => {
        console.error('Error caching assets:', error);
      })
  );
});

// Fetch from cache or network
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached response if available
        if (response) {
          return response;
        }
        
        // Otherwise fetch from network and cache
        return fetch(event.request)
          .then((response) => {
            // Clone the response (streams can only be read once)
            const responseClone = response.clone();
            
            // Cache the response
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseClone);
              });
            
            return response;
          });
      })
  );
});

// Activate service worker and clean up old caches
self.addEventListener('activate', (event) => {
  const cacheWhitelist = [CACHE_NAME];
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Listen for push notifications (for future implementation)
self.addEventListener('push', (event) => {
  const data = event.data?.json();
  const title = data?.title || 'TV UitWijk Tennis Team';
  const options = {
    body: data?.body || 'You have a new notification',
    icon: '/logo-192.png',
    badge: '/favicon.png',
    data: data?.url || '/',
  };
  
  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.notification.data) {
    clients.openWindow(event.notification.data);
  } else {
    clients.openWindow('/');
  }
});
