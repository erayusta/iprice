export default defineNuxtRouteMiddleware((to, from) => {
  const authStore = useAuthStore()
  
  // Client-side'da auth durumunu kontrol et
  if (process.client) {
    authStore.checkAuth()
  }
  
  // Eğer kullanıcı giriş yapmışsa dashboard'a yönlendir
  if (authStore.isLoggedIn) {
    return navigateTo('/dashboard')
  }
})

