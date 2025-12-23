import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    isAuthenticated: false
  }),

  getters: {
    isLoggedIn: (state) => state.isAuthenticated && state.token !== null
  },

  actions: {
    async login(credentials) {
      try {
        const config = useRuntimeConfig()
        const response = await $fetch(`${config.public.apiBase}/auth/login`, {
          method: 'POST',
          body: credentials
        })
        
        if (response.token) {
          this.token = response.token
          this.user = response.user
          this.isAuthenticated = true
          
          // Token'ı localStorage ve cookie'ye kaydet
          if (process.client) {
            localStorage.setItem('auth_token', response.token)
            localStorage.setItem('user', JSON.stringify(response.user))
          }
          
          // Cookie'ye de kaydet (SSR için)
          const tokenCookie = useCookie('auth_token', {
            maxAge: 60 * 60 * 24 * 7, // 7 gün
            secure: true,
            sameSite: 'lax'
          })
          const userCookie = useCookie('user', {
            maxAge: 60 * 60 * 24 * 7, // 7 gün
            secure: true,
            sameSite: 'lax'
          })
          
          tokenCookie.value = response.token
          userCookie.value = JSON.stringify(response.user)
          
          return { success: true, message: 'Giriş başarılı!' }
        }
      } catch (error) {
        console.error('Login error:', error)
        return { 
          success: false, 
          message: error.data?.message || 'Giriş yapılırken bir hata oluştu' 
        }
      }
    },

    async register(userData) {
      try {
        const config = useRuntimeConfig()
        const response = await $fetch(`${config.public.apiBase}/auth/register`, {
          method: 'POST',
          body: userData
        })
        
        if (response.token) {
          this.token = response.token
          this.user = response.user
          this.isAuthenticated = true
          
          // Token'ı localStorage ve cookie'ye kaydet
          if (process.client) {
            localStorage.setItem('auth_token', response.token)
            localStorage.setItem('user', JSON.stringify(response.user))
          }
          
          // Cookie'ye de kaydet (SSR için)
          const tokenCookie = useCookie('auth_token', {
            maxAge: 60 * 60 * 24 * 7, // 7 gün
            secure: true,
            sameSite: 'lax'
          })
          const userCookie = useCookie('user', {
            maxAge: 60 * 60 * 24 * 7, // 7 gün
            secure: true,
            sameSite: 'lax'
          })
          
          tokenCookie.value = response.token
          userCookie.value = JSON.stringify(response.user)
          
          return { success: true, message: 'Kayıt başarılı!' }
        }
      } catch (error) {
        console.error('Register error:', error)
        return { 
          success: false, 
          message: error.data?.message || 'Kayıt olurken bir hata oluştu' 
        }
      }
    },

    async logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      
      if (process.client) {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user')
      }
      
      // Cookie'leri de temizle
      const tokenCookie = useCookie('auth_token')
      const userCookie = useCookie('user')
      tokenCookie.value = null
      userCookie.value = null
      
      await navigateTo('/login')
    },

    async checkAuth() {
      if (process.client) {
        // Önce localStorage'dan kontrol et
        const token = localStorage.getItem('auth_token')
        const user = localStorage.getItem('user')
        
        if (token && user) {
          this.token = token
          this.user = JSON.parse(user)
          this.isAuthenticated = true
        } else {
          // localStorage'da yoksa cookie'den kontrol et
          const tokenCookie = useCookie('auth_token')
          const userCookie = useCookie('user')
          
          if (tokenCookie.value && userCookie.value) {
            this.token = tokenCookie.value
            try {
              this.user = typeof userCookie.value === 'string' ? JSON.parse(userCookie.value) : userCookie.value
              this.isAuthenticated = true
              
              // localStorage'a da kaydet
              localStorage.setItem('auth_token', tokenCookie.value)
              localStorage.setItem('user', typeof userCookie.value === 'string' ? userCookie.value : JSON.stringify(userCookie.value))
            } catch (error) {
              console.error('JSON parse error in checkAuth:', error)
              // Cookie'leri temizle
              tokenCookie.value = null
              userCookie.value = null
            }
          }
        }
      }
    }
  }
})
