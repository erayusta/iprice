<template>
  <div class="min-h-screen bg-background-secondary flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="text-center">
        <div class="w-16 h-16 bg-apple-green rounded-3xl flex items-center justify-center mx-auto mb-6">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
          </svg>
        </div>
        <h2 class="text-3xl font-bold text-gray-900 mb-2">Kayıt Ol</h2>
        <p class="text-gray-600 text-lg">Yeni hesap oluşturun</p>
      </div>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="card-elevated">
        <div class="text-center py-8">
          <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">Kayıt Şu Anda Kapalı</h3>
          <p class="text-gray-600 mb-6">Yeni kullanıcı kaydı şu anda aktif değildir.</p>
          <div class="text-center">
            <p class="text-sm text-gray-600">
              Zaten hesabınız var mı?
              <NuxtLink to="/login" class="font-medium text-apple-blue hover:text-blue-600 transition-colors">
                Giriş yapın
              </NuxtLink>
            </p>
          </div>
        </div>
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
  name: '',
  email: '',
  password: '',
  password_confirmation: ''
})

const loading = ref(false)
const message = ref('')
const messageClass = ref('')

const handleRegister = async () => {
  if (form.value.password !== form.value.password_confirmation) {
    message.value = 'Şifreler eşleşmiyor'
    messageClass.value = 'bg-apple-red/10 text-apple-red border border-apple-red/20'
    return
  }

  loading.value = true
  message.value = ''
  
  const result = await authStore.register(form.value)
  
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