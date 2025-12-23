<template>
  <div class="min-h-screen bg-background-secondary flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <!-- Preloader -->
    <Preloader />
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="text-center">
        <div class="w-16 h-16 bg-apple-blue rounded-3xl flex items-center justify-center mx-auto mb-6">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h2 class="text-3xl font-bold text-gray-900 mb-2">Hoş Geldiniz</h2>
        <p class="text-gray-600 text-lg">Hesabınıza giriş yapın</p>
      </div>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="card-elevated">
        <form @submit.prevent="handleLogin" class="space-y-6">
          <div v-if="message" :class="messageClass" class="p-4 rounded-2xl">
            <div class="flex items-center">
              <svg v-if="messageClass.includes('red')" class="w-5 h-5 text-apple-red mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <svg v-else class="w-5 h-5 text-apple-green mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm font-medium">{{ message }}</p>
            </div>
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              E-posta Adresi
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="input-field"
              placeholder="ornek@email.com"
            />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              Şifre
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="input-field"
              placeholder="••••••••"
            />
          </div>

          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input
                id="remember-me"
                type="checkbox"
                class="h-4 w-4 text-apple-blue focus:ring-apple-blue border-gray-300 rounded"
              />
              <label for="remember-me" class="ml-2 block text-sm text-gray-700">
                Beni hatırla
              </label>
            </div>

            <div class="text-sm">
              <a href="#" class="font-medium text-apple-blue hover:text-blue-600 transition-colors">
                Şifremi unuttum
              </a>
            </div>
          </div>

          <div>
            <button
              type="submit"
              :disabled="loading"
              class="btn-primary w-full"
            >
              <span v-if="loading" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Giriş yapılıyor...
              </span>
              <span v-else>Giriş Yap</span>
            </button>
          </div>

          <div class="divider"></div>

          <div class="text-center">
            <p class="text-sm text-gray-600">
              Hesabınız yok mu?
              <NuxtLink to="/register" class="font-medium text-apple-blue hover:text-blue-600 transition-colors">
                Kayıt olun
              </NuxtLink>
            </p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  layout: false,
  middleware: 'guest'
})

const authStore = useAuthStore()
const router = useRouter()

const form = ref({
  email: '',
  password: ''
})

const loading = ref(false)
const message = ref('')
const messageClass = ref('')

const handleLogin = async () => {
  loading.value = true
  message.value = ''
  
  const result = await authStore.login(form.value)
  
  if (result.success) {
    message.value = result.message
    messageClass.value = 'bg-apple-green/10 text-apple-green border border-apple-green/20'
    await router.push('/dashboard')
  } else {
    message.value = result.message
    messageClass.value = 'bg-apple-red/10 text-apple-red border border-apple-red/20'
  }
  
  loading.value = false
}
</script>