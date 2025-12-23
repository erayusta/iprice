<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center space-x-4">
        <button
          @click="$router.back()"
          class="p-2 rounded-xl hover:bg-gray-100 transition-colors"
        >
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Kullanıcı Düzenle</h1>
          <p class="text-gray-600 mt-1">{{ user?.name || 'Kullanıcı' }} bilgilerini güncelleyin</p>
        </div>
      </div>
      <div class="flex items-center space-x-3">
        <button
          @click="resetForm"
          class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
        >
          Sıfırla
        </button>
        <button
          @click="saveUser"
          :disabled="saving || !isFormValid"
          class="bg-apple-blue text-white px-4 py-2 rounded-xl hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          <svg v-if="saving" class="animate-spin w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span>{{ saving ? 'Kaydediliyor...' : 'Kaydet' }}</span>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-apple-blue mx-auto mb-4"></div>
        <p class="text-gray-600">Kullanıcı bilgileri yükleniyor...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-6">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-red-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <div>
          <h3 class="text-sm font-medium text-red-800">Kullanıcı yüklenemedi</h3>
          <p class="text-sm text-red-700 mt-1">{{ error }}</p>
        </div>
      </div>
      <div class="mt-4">
        <button
          @click="loadUser"
          class="text-sm text-red-600 hover:text-red-800 underline"
        >
          Tekrar dene
        </button>
      </div>
    </div>

    <!-- Form -->
    <div v-else class="max-w-2xl">
      <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-lg font-medium text-gray-900">Kullanıcı Bilgileri</h2>
          <p class="text-sm text-gray-600 mt-1">Temel kullanıcı bilgilerini güncelleyin</p>
        </div>
        
        <form @submit.prevent="saveUser" class="p-6 space-y-6">
          <!-- Profile Picture -->
          <div class="flex items-center space-x-4">
            <div class="w-16 h-16 bg-apple-blue rounded-xl flex items-center justify-center">
              <span class="text-white font-medium text-xl">
                {{ getUserInitials(form.name) }}
              </span>
            </div>
            <div>
              <h3 class="text-lg font-medium text-gray-900">{{ form.name || 'Kullanıcı' }}</h3>
              <p class="text-sm text-gray-500">{{ form.email || 'email@example.com' }}</p>
            </div>
          </div>

          <!-- Name -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Ad Soyad <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-apple-blue focus:border-transparent"
              placeholder="Kullanıcı adı"
              :class="{ 'border-red-300 focus:ring-red-500 focus:border-red-500': errors.name }"
            />
            <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
          </div>

          <!-- Email -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Email <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.email"
              type="email"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-apple-blue focus:border-transparent"
              placeholder="kullanici@example.com"
              :class="{ 'border-red-300 focus:ring-red-500 focus:border-red-500': errors.email }"
            />
            <p v-if="errors.email" class="mt-1 text-sm text-red-600">{{ errors.email }}</p>
          </div>

          <!-- Password Section -->
          <div class="border-t border-gray-200 pt-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Şifre Değiştir</h3>
            <p class="text-sm text-gray-600 mb-4">Şifreyi değiştirmek istemiyorsanız bu alanları boş bırakın</p>
            
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Yeni Şifre</label>
                <input
                  v-model="form.password"
                  type="password"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-apple-blue focus:border-transparent"
                  placeholder="Yeni şifre"
                  :class="{ 'border-red-300 focus:ring-red-500 focus:border-red-500': errors.password }"
                />
                <p v-if="errors.password" class="mt-1 text-sm text-red-600">{{ errors.password }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Şifre Tekrar</label>
                <input
                  v-model="form.password_confirmation"
                  type="password"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-apple-blue focus:border-transparent"
                  placeholder="Şifre tekrar"
                  :class="{ 'border-red-300 focus:ring-red-500 focus:border-red-500': errors.password_confirmation }"
                />
                <p v-if="errors.password_confirmation" class="mt-1 text-sm text-red-600">{{ errors.password_confirmation }}</p>
              </div>
            </div>
          </div>

          <!-- Roles Section -->
          <div class="border-t border-gray-200 pt-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Roller</h3>
            <p class="text-sm text-gray-600 mb-4">Kullanıcının sahip olacağı rolleri seçin</p>
            
            <div v-if="loadingRoles" class="flex items-center justify-center py-4">
              <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-apple-blue"></div>
              <span class="ml-2 text-gray-600">Roller yükleniyor...</span>
            </div>
            
            <div v-else class="space-y-3">
              <label
                v-for="role in roles"
                :key="role.id"
                class="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                :class="{ 'bg-apple-blue bg-opacity-10 border-apple-blue': form.role_ids.includes(role.id) }"
              >
                <input
                  v-model="form.role_ids"
                  :value="role.id"
                  type="checkbox"
                  class="h-4 w-4 text-apple-blue focus:ring-apple-blue border-gray-300 rounded"
                />
                <div class="ml-3 flex-1">
                  <div class="text-sm font-medium text-gray-900">{{ role.name }}</div>
                  <div v-if="role.description" class="text-sm text-gray-500">{{ role.description }}</div>
                </div>
              </label>
              
              <p v-if="roles.length === 0" class="text-sm text-gray-500 text-center py-4">
                Henüz hiç rol tanımlanmamış
              </p>
            </div>
          </div>

          <!-- User Info -->
          <div class="border-t border-gray-200 pt-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Kullanıcı Bilgileri</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Kayıt Tarihi</label>
                <p class="text-sm text-gray-900">{{ formatDate(user?.created_at) }}</p>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Son Güncelleme</label>
                <p class="text-sm text-gray-900">{{ formatDate(user?.updated_at) }}</p>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Email Doğrulama</label>
                <div class="flex items-center">
                  <svg v-if="user?.email_verified_at" class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <svg v-else class="w-4 h-4 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  <span class="text-sm" :class="user?.email_verified_at ? 'text-green-600' : 'text-gray-500'">
                    {{ user?.email_verified_at ? 'Doğrulanmış' : 'Doğrulanmamış' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>

      <!-- Danger Zone -->
      <div class="mt-8 bg-red-50 border border-red-200 rounded-xl overflow-hidden">
        <div class="px-6 py-4 border-b border-red-200">
          <h3 class="text-lg font-medium text-red-800">Tehlikeli Bölge</h3>
          <p class="text-sm text-red-700 mt-1">Bu işlemler geri alınamaz</p>
        </div>
        
        <div class="p-6">
          <div class="flex items-center justify-between">
            <div>
              <h4 class="text-sm font-medium text-red-800">Kullanıcıyı Sil</h4>
              <p class="text-sm text-red-700 mt-1">Bu kullanıcıyı kalıcı olarak silin</p>
            </div>
            <button
              @click="deleteUser"
              class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
            >
              Kullanıcıyı Sil
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeDeleteModal"></div>
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                <svg class="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                <h3 class="text-lg leading-6 font-medium text-gray-900">
                  Kullanıcıyı Sil
                </h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500">
                    <strong>{{ user?.name }}</strong> kullanıcısını silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              @click="confirmDelete"
              :disabled="deleting"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
            >
              {{ deleting ? 'Siliniyor...' : 'Sil' }}
            </button>
            <button
              @click="closeDeleteModal"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              İptal
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()

// Page meta
definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

// Reactive data
const loading = ref(false)
const loadingRoles = ref(false)
const saving = ref(false)
const deleting = ref(false)
const error = ref(null)
const user = ref(null)
const roles = ref([])
const showDeleteModal = ref(false)

// Form data
const form = ref({
  id: null,
  name: '',
  email: '',
  password: '',
  password_confirmation: '',
  role_ids: []
})

// Form errors
const errors = ref({})

// Computed
const isFormValid = computed(() => {
  return form.value.name && form.value.email
})

// Methods
const loadUser = async () => {
  try {
    loading.value = true
    error.value = null
    
    const response = await $api.get(`/users/${route.params.id}`)
    user.value = response.data
    
    form.value = {
      id: user.value.id,
      name: user.value.name,
      email: user.value.email,
      password: '',
      password_confirmation: '',
      role_ids: user.value.roles.map(role => role.id)
    }
  } catch (err) {
    error.value = 'Kullanıcı bilgileri yüklenirken bir hata oluştu'
    console.error('Error loading user:', err)
  } finally {
    loading.value = false
  }
}

const loadRoles = async () => {
  try {
    loadingRoles.value = true
    const response = await $api.get('/users/roles/list')
    roles.value = response.data
  } catch (err) {
    console.error('Error loading roles:', err)
  } finally {
    loadingRoles.value = false
  }
}

const saveUser = async () => {
  try {
    saving.value = true
    errors.value = {}
    
    const payload = {
      name: form.value.name,
      email: form.value.email,
      role_ids: form.value.role_ids,
      password: form.value.password || '',
      password_confirmation: form.value.password_confirmation || ''
    }
    
    await $api.put(`/users/${form.value.id}`, payload)
    
    // Reload user data
    await loadUser()
    
    // Show success message (you can implement a toast notification here)
    console.log('User updated successfully')
  } catch (err) {
    if (err.response?.data?.errors) {
      errors.value = err.response.data.errors
    } else {
      console.error('Error saving user:', err)
    }
  } finally {
    saving.value = false
  }
}

const deleteUser = () => {
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  try {
    deleting.value = true
    await $api.delete(`/users/${form.value.id}`)
    
    // Redirect to members page
    await router.push('/dashboard/members')
  } catch (err) {
    console.error('Error deleting user:', err)
  } finally {
    deleting.value = false
  }
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
}

const resetForm = () => {
  if (user.value) {
    form.value = {
      id: user.value.id,
      name: user.value.name,
      email: user.value.email,
      password: '',
      password_confirmation: '',
      role_ids: user.value.roles.map(role => role.id)
    }
  }
  errors.value = {}
}

const getUserInitials = (name) => {
  if (!name) return 'U'
  return name.split(' ').map(n => n[0]).join('').toUpperCase()
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('tr-TR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(() => {
  loadUser()
  loadRoles()
})
</script>
