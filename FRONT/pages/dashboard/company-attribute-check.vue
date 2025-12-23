<template>
  <!-- Loading State -->
  <div v-if="isCheckingPermissions" class="flex items-center justify-center min-h-screen">
    <div class="text-center">
      <svg class="animate-spin -ml-1 mr-3 h-8 w-8 text-apple-blue mx-auto mb-4" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="text-gray-600">Yetkiler kontrol ediliyor...</p>
    </div>
  </div>

  <!-- Access Denied -->
  <div v-else-if="!hasPermission('companies.attribute')" class="flex items-center justify-center min-h-screen">
    <div class="text-center">
      <div class="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg class="w-12 h-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Erişim Reddedildi</h1>
      <p class="text-gray-600">Bu sayfaya erişim yetkiniz bulunmuyor.</p>
    </div>
  </div>
  
  <!-- Main Content -->
  <div v-else class="space-y-6">
    <!-- Page Header -->
    <div class="card-elevated">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 mb-2">
            Firma Attribute Kontrolü 📊
          </h1>
          <p class="text-gray-600 text-lg">
            Hangi firmada hangi attribute'ların tanımlı olduğunu kontrol edin.
          </p>
        </div>
        <div class="hidden md:block">
          <div class="w-20 h-20 bg-gradient-to-br from-green-500 to-green-600 rounded-3xl flex items-center justify-center">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="card-elevated">
      <div class="flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div class="flex-1 max-w-md">
          <div class="relative">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Attribute ara..."
              class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
            />
            <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
        <div class="flex gap-3">
          <select v-model="selectedCompany" class="px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent">
            <option value="">Tüm Firmalar</option>
            <option v-for="company in companies" :key="company.id" :value="company.id">
              {{ company.company_name }}
            </option>
          </select>
          <button 
            @click="refreshData" 
            :disabled="isLoading"
            class="btn btn-secondary"
          >
            <svg class="w-5 h-5 mr-2" :class="{ 'animate-spin': isLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Yenile
          </button>
          <button 
            @click="showDeleteModal = true" 
            :disabled="isLoading || summary.defined === 0"
            class="btn btn-danger"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Tüm Tanımlı Attribute'ları Sil
          </button>
        </div>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="card-elevated">
        <div class="flex items-center">
          <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Tanımlı</p>
            <p class="text-2xl font-bold text-gray-900">{{ summary.defined }}</p>
          </div>
        </div>
      </div>
      
      <div class="card-elevated">
        <div class="flex items-center">
          <div class="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Tanımsız</p>
            <p class="text-2xl font-bold text-gray-900">{{ summary.undefined }}</p>
          </div>
        </div>
      </div>
      
      <div class="card-elevated">
        <div class="flex items-center">
          <div class="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Devre Dışı</p>
            <p class="text-2xl font-bold text-gray-900">{{ summary.disabled }}</p>
          </div>
        </div>
      </div>
      
      <div class="card-elevated">
        <div class="flex items-center">
          <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Toplam</p>
            <p class="text-2xl font-bold text-gray-900">{{ summary.total }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Attribute Matrix Table -->
    <div class="card-elevated">
      <div class="overflow-x-auto">
        <div v-if="isLoading" class="flex items-center justify-center py-12">
          <svg class="animate-spin -ml-1 mr-3 h-8 w-8 text-apple-blue" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span class="text-gray-600 ml-3">Yükleniyor...</span>
        </div>
        
        <div v-else-if="filteredAttributes.length === 0" class="text-center py-12">
          <div class="text-gray-500">
            <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <p class="text-lg font-medium mb-2">Attribute bulunamadı</p>
            <p class="text-sm">Henüz attribute eklenmemiş veya arama kriterlerinize uygun attribute yok.</p>
          </div>
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-gray-200">
                <th class="text-left py-4 px-6 font-semibold text-gray-900 sticky left-0 bg-white z-10 min-w-48">
                  Attribute Adı
                </th>
                <th 
                  v-for="company in filteredCompanies" 
                  :key="company.id"
                  class="text-center py-4 px-4 font-semibold text-gray-900 min-w-32"
                  :title="company.company_name"
                >
                  <div class="flex flex-col items-center space-y-2">
                    <div class="w-12 h-12 rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center">
                      <img v-if="company.company_logo" :src="company.company_logo" :alt="company.company_name" class="w-full h-full object-cover" />
                      <svg v-else class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                    </div>
                    <div v-if="!company.company_logo" class="transform -rotate-45 origin-center whitespace-nowrap text-xs">
                      {{ company.company_name }}
                    </div>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="attribute in filteredAttributes" :key="attribute.id" class="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td class="py-4 px-6 sticky left-0 bg-white z-10 font-medium text-gray-900 min-w-48">
                  <div class="flex items-center">
                    <div class="w-8 h-8 rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center mr-3">
                      <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                    </div>
                    <div>
                      <div class="font-medium">{{ attribute.name }}</div>
                    </div>
                  </div>
                </td>
                <td 
                  v-for="company in filteredCompanies" 
                  :key="`${attribute.id}-${company.id}`"
                  class="text-center py-4 px-4"
                >
                  <div class="flex items-center justify-center">
                    <!-- Tanımlı (✓) -->
                    <div v-if="getAttributeStatus(company.id, attribute.id) === 'defined'" class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                      <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <!-- Devre Dışı (-) -->
                    <div v-else-if="getAttributeStatus(company.id, attribute.id) === 'disabled'" class="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                      <span class="text-yellow-600 font-bold text-lg">-</span>
                    </div>
                    <!-- Tanımsız (X) -->
                    <div v-else class="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                      <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div
      v-if="message"
      :class="[
        'fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 max-w-sm',
        messageType === 'success' ? 'bg-green-100 text-green-800 border border-green-200' : 'bg-red-100 text-red-800 border border-red-200'
      ]"
    >
      <div class="flex items-center gap-2">
        <svg v-if="messageType === 'success'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        <span>{{ message }}</span>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl">
        <div class="text-center">
          <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          
          <h3 class="text-xl font-bold text-gray-900 mb-4">
            Tüm Tanımlı Attribute'ları Sil
          </h3>
          
          <p class="text-gray-600 mb-6">
            Bu işlem tüm firmalardaki <strong>{{ summary.defined }}</strong> tanımlı attribute'ı kalıcı olarak silecektir. 
            Bu işlem geri alınamaz!
          </p>
          
          <div class="flex gap-3 justify-center">
            <button 
              @click="showDeleteModal = false" 
              :disabled="isDeleting"
              class="px-6 py-3 border border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              İptal
            </button>
            <button 
              @click="deleteAllDefinedAttributes" 
              :disabled="isDeleting"
              class="px-6 py-3 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center"
            >
              <svg v-if="isDeleting" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isDeleting ? 'Siliniyor...' : 'Evet, Sil' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  middleware: 'auth',
  layout: 'dashboard'
})

// Reactive data
const isCheckingPermissions = ref(true)
const isLoading = ref(false)
const isDeleting = ref(false)
const showDeleteModal = ref(false)
const searchQuery = ref('')
const selectedCompany = ref('')
const message = ref('')
const messageType = ref('')

// Permissions composable
let hasPermission
try {
  const permissions = usePermissions()
  hasPermission = permissions.hasPermission
} catch (error) {
  console.warn('Permissions composable failed:', error)
  hasPermission = () => false
}

// Data
const companies = ref([])
const attributes = ref([])
const attributeMatrix = ref({}) // { company_id: { attribute_id: { status, value } } }

// Computed
const filteredCompanies = computed(() => {
  let filtered = companies.value

  // Company filter
  if (selectedCompany.value) {
    filtered = filtered.filter(company => company.id == selectedCompany.value)
  }

  return filtered
})

const filteredAttributes = computed(() => {
  let filtered = attributes.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(attribute => 
      attribute.name.toLowerCase().includes(query) ||
      (attribute.description && attribute.description.toLowerCase().includes(query))
    )
  }

  return filtered
})

const summary = computed(() => {
  let defined = 0
  let undefined = 0
  let disabled = 0
  let total = 0

  companies.value.forEach(company => {
    attributes.value.forEach(attribute => {
      const status = getAttributeStatus(company.id, attribute.id)
      total++
      
      if (status === 'defined') defined++
      else if (status === 'disabled') disabled++
      else undefined++
    })
  })

  return { defined, undefined, disabled, total }
})

// Methods
const getAttributeStatus = (companyId, attributeId) => {
  const companyData = attributeMatrix.value[companyId]
  if (!companyData || !companyData[attributeId]) {
    return 'undefined'
  }
  
  const attrData = companyData[attributeId]
  
  // Value -1 ise devre dışı
  if (attrData.value === '-1') {
    return 'disabled'
  }
  
  // Value yoksa veya boşsa tanımsız
  if (!attrData.value || attrData.value.trim() === '') {
    return 'undefined'
  }
  
  // Value varsa tanımlı
  return 'defined'
}

const fetchData = async () => {
  isLoading.value = true
  try {
    const config = useRuntimeConfig()
    
    // Paralel olarak verileri çek
    const [companiesRes, attributesRes, matrixRes] = await Promise.all([
      $fetch(`${config.public.apiBase}/companies`, {
        headers: {
          'Authorization': `Bearer ${useAuthStore().token}`
        }
      }),
      $fetch(`${config.public.apiBase}/attributes`, {
        headers: {
          'Authorization': `Bearer ${useAuthStore().token}`
        }
      }),
      $fetch(`${config.public.apiBase}/company-attribute/matrix`, {
        headers: {
          'Authorization': `Bearer ${useAuthStore().token}`
        }
      })
    ])
    
    companies.value = companiesRes.data
    attributes.value = attributesRes.data
    attributeMatrix.value = matrixRes.data
    
  } catch (error) {
    console.error('Veri yüklenirken hata:', error)
  } finally {
    isLoading.value = false
  }
}

const refreshData = async () => {
  await fetchData()
}

const showMessage = (text, type = 'success') => {
  message.value = text
  messageType.value = type
  setTimeout(() => {
    message.value = ''
    messageType.value = ''
  }, 5000)
}

const deleteAllDefinedAttributes = async () => {
  isDeleting.value = true
  try {
    const config = useRuntimeConfig()
    
    const response = await $fetch(`${config.public.apiBase}/company-attribute/delete-all-defined`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${useAuthStore().token}`
      }
    })
    
    if (response.success) {
      // Başarı mesajı göster
      showMessage(response.message, 'success')
      
      // Modalı kapat
      showDeleteModal.value = false
      
      // Verileri yenile
      await fetchData()
    } else {
      throw new Error(response.message || 'Silme işlemi başarısız')
    }
    
  } catch (error) {
    console.error('Silme işlemi hatası:', error)
    showMessage(error.message || 'Silme işlemi sırasında bir hata oluştu', 'error')
  } finally {
    isDeleting.value = false
  }
}

// Lifecycle
onMounted(async () => {
  try {
    // Kısa bir delay ile yetki kontrolünün tamamlanmasını bekle
    await new Promise(resolve => setTimeout(resolve, 200))
    isCheckingPermissions.value = false
    
    await fetchData()
  } catch (error) {
    console.error('Page initialization failed:', error)
    isCheckingPermissions.value = false
  }
})
</script>
