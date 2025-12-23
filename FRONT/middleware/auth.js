export default defineNuxtRouteMiddleware((to, from) => {
  const authStore = useAuthStore()
  
  // Client-side'da auth durumunu kontrol et
  if (process.client) {
    authStore.checkAuth()
    
    // Eğer kullanıcı giriş yapmamışsa login sayfasına yönlendir
    if (!authStore.isLoggedIn) {
      return navigateTo('/login')
    }
  } else {
    // Server-side'da sadece cookie kontrolü yap, store'u güncelleme
    const token = useCookie('auth_token')
    const user = useCookie('user')
    
    if (!token.value || !user.value) {
      return navigateTo('/login')
    }
    
    // Server-side'da store'u güncellemeye gerek yok, sadece cookie varlığını kontrol et
    // Store güncellemesi client-side'da yapılacak
  }
})

