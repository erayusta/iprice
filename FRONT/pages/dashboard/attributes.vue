<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="card-elevated">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 mb-2">
            🏷️ Attribute Ayarları
          </h1>
          <p class="text-gray-600 text-lg">
            Attribute'ları yönetin, ekleyin ve düzenleyin
          </p>
        </div>
        <div class="hidden md:block">
          <div class="w-20 h-20 bg-gradient-to-br from-apple-blue to-apple-indigo rounded-3xl flex items-center justify-center">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="card-elevated">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div class="relative">
            <input 
              v-model="searchQuery"
              type="text" 
              placeholder="Attribute ara..."
              class="w-64 px-4 py-2 pl-10 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-apple-blue focus:border-transparent"
            />
            <svg class="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
        <div class="flex items-center space-x-3">
          <button 
            v-if="attributes.length > 0"
            @click="deleteAllAttributes"
            class="bg-red-600 text-white px-6 py-2 rounded-xl font-medium hover:bg-red-700 transition-colors flex items-center space-x-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            <span>Tümünü Temizle</span>
          </button>
          <button 
            @click="openAddModal"
            class="bg-apple-blue text-white px-6 py-2 rounded-xl font-medium hover:bg-apple-blue/90 transition-colors flex items-center space-x-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <span>Yeni Attribute</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Attributes Table -->
    <div class="card-elevated">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-200">
              <th class="text-left py-4 px-6 font-semibold text-gray-900">Attribute</th>
              <th class="text-left py-4 px-6 font-semibold text-gray-900">Açıklama</th>
              <th class="text-left py-4 px-6 font-semibold text-gray-900">Oluşturulma</th>
              <th class="text-right py-4 px-6 font-semibold text-gray-900">İşlemler</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading" class="border-b border-gray-100">
              <td colspan="4" class="py-8 text-center">
                <div class="flex items-center justify-center space-x-2">
                  <svg class="animate-spin h-5 w-5 text-apple-blue" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span class="text-gray-600">Yükleniyor...</span>
                </div>
              </td>
            </tr>
            <tr v-else-if="filteredAttributes.length === 0" class="border-b border-gray-100">
              <td colspan="4" class="py-8 text-center text-gray-500">
                <div class="flex flex-col items-center space-y-2">
                  <svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                  <p>Henüz attribute bulunmuyor</p>
                  <button 
                    @click="openAddModal"
                    class="text-apple-blue hover:text-apple-blue/80 font-medium"
                  >
                    İlk attribute'ı ekleyin
                  </button>
                </div>
              </td>
            </tr>
            <tr v-else v-for="attribute in filteredAttributes" :key="attribute.id" class="border-b border-gray-100 hover:bg-gray-50">
              <td class="py-4 px-6">
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 bg-apple-blue/10 rounded-lg flex items-center justify-center">
                    <svg class="w-4 h-4 text-apple-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                    </svg>
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">{{ attribute.name }}</p>
                    <p class="text-sm text-gray-500">ID: {{ attribute.id }}</p>
                  </div>
                </div>
              </td>
              <td class="py-4 px-6">
                <p class="text-gray-700">{{ attribute.description || 'Açıklama yok' }}</p>
              </td>
              <td class="py-4 px-6">
                <p class="text-sm text-gray-500">{{ formatDate(attribute.created_at) }}</p>
              </td>
              <td class="py-4 px-6">
                <div class="flex items-center justify-end space-x-2">
                  <button 
                    @click="openEditModal(attribute)"
                    class="p-2 text-gray-500 hover:text-apple-blue transition-colors"
                    title="Düzenle"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button 
                    @click="deleteAttribute(attribute)"
                    class="p-2 text-gray-500 hover:text-red-600 transition-colors"
                    title="Sil"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md mx-4">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-900">
            {{ editingAttribute ? 'Attribute Düzenle' : 'Yeni Attribute' }}
          </h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <form @submit.prevent="saveAttribute" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Attribute Adı</label>
            <input 
              v-model="form.name"
              type="text" 
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-apple-blue focus:border-transparent"
              placeholder="Örn: price, stock, title"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Açıklama</label>
            <textarea 
              v-model="form.description"
              rows="3"
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-apple-blue focus:border-transparent"
              placeholder="Bu attribute'ın ne için kullanıldığını açıklayın..."
            ></textarea>
          </div>
          
          <div class="flex space-x-3 pt-4">
            <button 
              type="button"
              @click="closeModal"
              class="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors"
            >
              İptal
            </button>
            <button 
              type="submit"
              :disabled="loading"
              class="flex-1 bg-apple-blue text-white px-4 py-3 rounded-xl hover:bg-apple-blue/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="loading" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Kaydediliyor...
              </span>
              <span v-else>{{ editingAttribute ? 'Güncelle' : 'Ekle' }}</span>
            </button>
          </div>
        </form>
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
const attributes = ref([])
const loading = ref(false)
const searchQuery = ref('')
const showModal = ref(false)
const editingAttribute = ref(null)
const form = ref({
  name: '',
  description: ''
})
const message = ref('')
const messageType = ref('')

// Computed
const filteredAttributes = computed(() => {
  if (!searchQuery.value) return attributes.value
  return attributes.value.filter(attr => 
    attr.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    (attr.description && attr.description.toLowerCase().includes(searchQuery.value.toLowerCase()))
  )
})

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

const loadAttributes = async () => {
  try {
    loading.value = true
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('attributes.list'))
    
    if (response.success) {
      attributes.value = response.data || []
    } else {
      showMessage('Attribute\'lar yüklenemedi.', 'error')
    }
  } catch (error) {
    console.error('Load attributes error:', error)
    showMessage('Attribute\'lar yüklenemedi.', 'error')
  } finally {
    loading.value = false
  }
}

const openAddModal = () => {
  editingAttribute.value = null
  form.value = {
    name: '',
    description: ''
  }
  showModal.value = true
}

const openEditModal = (attribute) => {
  editingAttribute.value = attribute
  form.value = {
    name: attribute.name,
    description: attribute.description || ''
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingAttribute.value = null
  form.value = {
    name: '',
    description: ''
  }
}

const saveAttribute = async () => {
  try {
    loading.value = true
    const { $api } = useNuxtApp()
    
    let response
    if (editingAttribute.value) {
      response = await $api.put($api.getEndpoint('attributes.update', editingAttribute.value.id), form.value)
    } else {
      response = await $api.post($api.getEndpoint('attributes.create'), form.value)
    }
    
    if (response.success) {
      showMessage(
        editingAttribute.value ? 'Attribute güncellendi!' : 'Attribute eklendi!', 
        'success'
      )
      closeModal()
      loadAttributes()
    } else {
      showMessage(response.message || 'İşlem başarısız.', 'error')
    }
  } catch (error) {
    console.error('Save attribute error:', error)
    showMessage('İşlem başarısız.', 'error')
  } finally {
    loading.value = false
  }
}

const deleteAttribute = async (attribute) => {
  if (!confirm(`"${attribute.name}" attribute'ını silmek istediğinizden emin misiniz?`)) {
    return
  }
  
  try {
    loading.value = true
    const { $api } = useNuxtApp()
    const response = await $api.delete($api.getEndpoint('attributes.delete', attribute.id))
    
    if (response.success) {
      showMessage('Attribute silindi!', 'success')
      loadAttributes()
    } else {
      showMessage(response.message || 'Silme işlemi başarısız.', 'error')
    }
  } catch (error) {
    console.error('Delete attribute error:', error)
    showMessage('Silme işlemi başarısız.', 'error')
  } finally {
    loading.value = false
  }
}

const deleteAllAttributes = async () => {
  if (!confirm(`Tüm attribute'ları silmek istediğinizden emin misiniz? Bu işlem geri alınamaz!`)) {
    return
  }
  
  try {
    loading.value = true
    const { $api } = useNuxtApp()
    const response = await $api.delete('/attributes/delete-all')
    
    if (response.success) {
      showMessage(`Tüm attribute'lar silindi! (${response.deleted_count} adet)`, 'success')
      loadAttributes()
    } else {
      showMessage(response.message || 'Silme işlemi başarısız.', 'error')
    }
  } catch (error) {
    console.error('Delete all attributes error:', error)
    showMessage('Silme işlemi başarısız.', 'error')
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('tr-TR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Lifecycle
onMounted(() => {
  loadAttributes()
})
</script>
