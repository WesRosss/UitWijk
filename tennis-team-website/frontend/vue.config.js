const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  
  // Development server configuration
  devServer: {
    port: 8080,
    host: '0.0.0.0',
    allowedHosts: 'all',
    proxy: {
      // Proxy API requests to the Django backend
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      },
      '/admin': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      },
      '/static': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      },
    },
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, Authorization',
    },
  },
  
  // Build configuration
  outputDir: 'dist',
  assetsDir: 'assets',
  publicPath: process.env.NODE_ENV === 'production' ? '/' : '/',
  
  // CSS configuration
  css: {
    extract: true,
    sourceMap: false,
    loaderOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`
      }
    }
  },
  
  // PWA configuration (optional)
  pwa: {
    name: 'Tennis Team Website',
    shortName: 'TennisTeam',
    themeColor: '#1976D2',
    msTileColor: '#1976D2',
    appleMobileWebAppCapable: 'yes',
    appleMobileWebAppStatusBarStyle: 'black',
    workboxPluginMode: 'GenerateSW',
    workboxOptions: {
      navigateFallback: '/index.html',
      runtimeCaching: [
        {
          urlPattern: /^https:\/\/backend:8000\/api\/.*/i,
          handler: 'NetworkFirst',
          options: {
            cacheName: 'api-cache',
            expiration: {
              maxEntries: 50,
              maxAgeSeconds: 24 * 60 * 60 // 24 hours
            }
          }
        }
      ]
    }
  },
  
  // Chain webpack configuration
  chainWebpack: config => {
    // Determine the correct source path (works in both local and Docker environments)
    const srcPath = require('path').resolve(__dirname, 'src')
    
    // Add alias for @ and src
    config.resolve.alias
      .set('@', srcPath)
      .set('src', srcPath)
      .set('@components', require('path').resolve(srcPath, 'components'))
      .set('@views', require('path').resolve(srcPath, 'views'))
      .set('@store', require('path').resolve(srcPath, 'store'))
      .set('@router', require('path').resolve(srcPath, 'router'))
      .set('@services', require('path').resolve(srcPath, 'services'))
      .set('@utils', require('path').resolve(srcPath, 'utils'))
      .set('@styles', require('path').resolve(srcPath, 'styles'))
    
    // Configure svg loader
    const svgRule = config.module.rule('svg')
    svgRule.uses.clear()
    svgRule
      .use('babel-loader')
      .loader('babel-loader')
      .end()
      .use('vue-svg-loader')
      .loader('vue-svg-loader')
      .options({
        svgo: {
          plugins: [
            { removeDoctype: true },
            { removeComments: true },
          ]
        }
      })
  },
  
  // Configure webpack
  configureWebpack: {
    performance: {
      hints: false
    },
    optimization: {
      splitChunks: {
        chunks: 'all'
      }
    }
  }
})