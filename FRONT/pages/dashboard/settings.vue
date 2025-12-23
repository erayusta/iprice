<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="card-elevated">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 mb-2">
            ⚙️ Ayarlar
          </h1>
          <p class="text-gray-600 text-lg">
            Hesap ayarlarınızı ve API token'larınızı yönetin
          </p>
        </div>
        <div class="hidden md:block">
          <div class="w-20 h-20 bg-gradient-to-br from-apple-blue to-apple-indigo rounded-3xl flex items-center justify-center">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Sections -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- iPrice API Token Section -->
      <div class="card-elevated">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-900">🔑 iPrice API Token</h3>
          <div class="w-12 h-12 bg-apple-blue/10 rounded-2xl flex items-center justify-center">
            <svg class="w-6 h-6 text-apple-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
            </svg>
          </div>
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Mevcut Token
            </label>
            <div class="flex items-center space-x-2">
              <input 
                :type="showToken ? 'text' : 'password'" 
                :value="userToken" 
                readonly
                class="flex-1 px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 text-sm font-mono"
                placeholder="Token oluşturuluyor..."
              />
              <button 
                @click="showToken = !showToken"
                class="px-3 py-3 text-gray-500 hover:text-gray-700 transition-colors"
              >
                <svg v-if="!showToken" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                </svg>
              </button>
              <button 
                @click="copyToken"
                class="px-3 py-3 text-gray-500 hover:text-gray-700 transition-colors"
                title="Token'ı kopyala"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </button>
            </div>
          </div>
          
          <div class="flex space-x-3">
            <button 
              @click="generateNewToken"
              :disabled="loading"
              class="flex-1 bg-apple-blue text-white px-4 py-3 rounded-xl font-medium hover:bg-apple-blue/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="loading" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Oluşturuluyor...
              </span>
              <span v-else>🔄 Yeni Token Oluştur</span>
            </button>
            
            <button 
              @click="testToken"
              :disabled="loading || !userToken"
              class="flex-1 bg-apple-green text-white px-4 py-3 rounded-xl font-medium hover:bg-apple-green/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="testing" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Test ediliyor...
              </span>
              <span v-else>🔗 Token'ı Test Et</span>
            </button>
          </div>
          
          <div class="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h4 class="text-sm font-medium text-blue-900 mb-1">Chrome Eklentisi İçin</h4>
                <p class="text-sm text-blue-700">
                  Bu token'ı Chrome eklentinizin config sayfasında "iPrice API Token" alanına yapıştırın.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Account Information -->
      <div class="card-elevated">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-900">👤 Hesap Bilgileri</h3>
          <div class="w-12 h-12 bg-apple-green/10 rounded-2xl flex items-center justify-center">
            <svg class="w-6 h-6 text-apple-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Ad Soyad</label>
            <input 
              type="text" 
              :value="authStore.user?.name" 
              readonly
              class="w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 text-gray-600"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">E-posta</label>
            <input 
              type="email" 
              :value="authStore.user?.email" 
              readonly
              class="w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 text-gray-600"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Token Oluşturma Tarihi</label>
            <input 
              type="text" 
              :value="tokenCreatedAt" 
              readonly
              class="w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 text-gray-600"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Usage Statistics -->
    <div class="card-elevated">
      <h3 class="text-lg font-semibold text-gray-900 mb-6">📊 Kullanım İstatistikleri</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="text-center p-6 bg-gradient-to-br from-apple-blue/5 to-apple-blue/10 rounded-2xl">
          <div class="w-12 h-12 bg-apple-blue/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg class="w-6 h-6 text-apple-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h4 class="text-2xl font-bold text-gray-900 mb-1">{{ stats.totalAttributes || 0 }}</h4>
          <p class="text-sm text-gray-600">Toplam Attribute</p>
        </div>
        
        <div class="text-center p-6 bg-gradient-to-br from-apple-green/5 to-apple-green/10 rounded-2xl">
          <div class="w-12 h-12 bg-apple-green/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg class="w-6 h-6 text-apple-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h4 class="text-2xl font-bold text-gray-900 mb-1">{{ stats.todayAttributes || 0 }}</h4>
          <p class="text-sm text-gray-600">Bugün Eklenen</p>
        </div>
        
        <div class="text-center p-6 bg-gradient-to-br from-apple-orange/5 to-apple-orange/10 rounded-2xl">
          <div class="w-12 h-12 bg-apple-orange/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg class="w-6 h-6 text-apple-orange" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h4 class="text-2xl font-bold text-gray-900 mb-1">{{ stats.lastActivity || 'Henüz yok' }}</h4>
          <p class="text-sm text-gray-600">Son Aktivite</p>
        </div>
      </div>
    </div>

    <!-- Status Messages -->
    <div v-if="message" :class="messageClass" class="p-4 rounded-xl">
      <div class="flex items-center">
        <svg v-if="messageType === 'success'" class="w-5 h-5 text-green-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <svg v-else-if="messageType === 'error'" class="w-5 h-5 text-red-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="font-medium">{{ message }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  middleware: 'auth',
  layout: 'dashboard'
})

const authStore = useAuthStore()

// Reactive data
const showToken = ref(false)
const loading = ref(false)
const testing = ref(false)
const userToken = ref('')
const tokenCreatedAt = ref('')
const stats = ref({
  totalAttributes: 0,
  todayAttributes: 0,
  lastActivity: null
})
const message = ref('')
const messageType = ref('')

// Computed
const messageClass = computed(() => {
  if (messageType.value === 'success') {
    return 'bg-green-50 border border-green-200 text-green-800'
  } else if (messageType.value === 'error') {
    return 'bg-red-50 border border-red-200 text-red-800'
  }
  return 'bg-gray-50 border border-gray-200 text-gray-800'
})

// Methods
const showMessage = (text, type = 'info') => {
  message.value = text
  messageType.value = type
  setTimeout(() => {
    message.value = ''
    messageType.value = ''
  }, 5000)
}

const generateNewToken = async () => {
  try {
    loading.value = true
    const { $api } = useNuxtApp()
    const response = await $api.post('/user/generate-token')
    
    if (response.success) {
      userToken.value = response.token
      tokenCreatedAt.value = new Date().toLocaleString('tr-TR')
      showMessage('Yeni token başarıyla oluşturuldu!', 'success')
    } else {
      showMessage('Token oluşturulurken bir hata oluştu.', 'error')
    }
  } catch (error) {
    console.error('Token generation error:', error)
    showMessage('Token oluşturulurken bir hata oluştu.', 'error')
  } finally {
    loading.value = false
  }
}

const testToken = async () => {
  try {
    testing.value = true
    const { $api } = useNuxtApp()
    const response = await $api.post('/user/test-token')
    
    if (response.success) {
      showMessage('Token başarıyla test edildi!', 'success')
    } else {
      showMessage('Token test edilemedi.', 'error')
    }
  } catch (error) {
    console.error('Token test error:', error)
    showMessage('Token test edilemedi.', 'error')
  } finally {
    testing.value = false
  }
}

const copyToken = async () => {
  try {
    await navigator.clipboard.writeText(userToken.value)
    showMessage('Token panoya kopyalandı!', 'success')
  } catch (error) {
    console.error('Copy error:', error)
    showMessage('Token kopyalanamadı.', 'error')
  }
}

const loadUserData = async () => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get('/user/profile')
    
    if (response.success) {
      userToken.value = response.user.iprice_token || ''
      tokenCreatedAt.value = response.user.token_created_at ? 
        new Date(response.user.token_created_at).toLocaleString('tr-TR') : 
        'Henüz oluşturulmadı'
      stats.value = response.stats || stats.value
    }
  } catch (error) {
    console.error('Load user data error:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadUserData()
})
</script>
