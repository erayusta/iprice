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
  <div v-else-if="!hasPermission('brands.show')" class="flex items-center justify-center min-h-screen">
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
            Markalar 🏷️
          </h1>
          <p class="text-gray-600 text-lg">
            Marka yönetimi ve takibi için bu sayfayı kullanabilirsiniz.
          </p>
        </div>
        <div class="hidden md:block">
          <div class="w-20 h-20 bg-gradient-to-br from-purple-500 to-purple-600 rounded-3xl flex items-center justify-center">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Search and Filter Bar -->
    <div class="card-elevated">
      <div class="flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div class="flex-1 max-w-md">
          <div class="relative">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Marka ara..."
              class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
            />
            <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
        <div class="flex gap-3">
          <select v-model="statusFilter" class="px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent">
            <option value="">Tüm Durumlar</option>
            <option value="active">Aktif</option>
            <option value="inactive">Pasif</option>
          </select>
          <button 
            v-if="hasPermission('brands.add')"
            @click="openModal()" 
            class="btn btn-primary"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Yeni Marka
          </button>
          <button 
            v-if="hasPermission('brands.delete')"
            @click="openDeleteAllModal" 
            class="btn btn-danger"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Tüm Markaları Sil
          </button>
        </div>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="card-elevated">
        <div class="flex items-center">
          <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Aktif Markalar</p>
            <p class="text-2xl font-bold text-gray-900">{{ summary.active }}</p>
          </div>
        </div>
      </div>
      
      <div class="card-elevated">
        <div class="flex items-center">
          <div class="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Pasif Markalar</p>
            <p class="text-2xl font-bold text-gray-900">{{ summary.inactive }}</p>
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

    <!-- Brands Table -->
    <div class="card-elevated">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-200">
              <th class="text-left py-4 px-6 font-semibold text-gray-900">Marka Adı</th>
              <th class="text-left py-4 px-6 font-semibold text-gray-900">Slug</th>
              <th class="text-left py-4 px-6 font-semibold text-gray-900">Durum</th>
              <th class="text-left py-4 px-6 font-semibold text-gray-900">Ürün Sayısı</th>
              <th class="text-left py-4 px-6 font-semibold text-gray-900">Oluşturulma</th>
              <th class="text-right py-4 px-6 font-semibold text-gray-900">İşlemler</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="isLoading" class="border-b border-gray-100">
              <td colspan="6" class="text-center py-12">
                <div class="flex items-center justify-center">
                  <svg class="animate-spin -ml-1 mr-3 h-8 w-8 text-apple-blue" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span class="text-gray-600">Yükleniyor...</span>
                </div>
              </td>
            </tr>
            <tr v-else-if="filteredBrands.length === 0" class="border-b border-gray-100">
              <td colspan="6" class="text-center py-12">
                <div class="text-gray-500">
                  <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                  <p class="text-lg font-medium mb-2">Marka bulunamadı</p>
                  <p class="text-sm">Henüz marka eklenmemiş veya arama kriterlerinize uygun marka yok.</p>
                </div>
              </td>
            </tr>
            <tr v-else v-for="brand in filteredBrands" :key="brand.id" class="border-b border-gray-100 hover:bg-gray-50 transition-colors">
              <td class="py-4 px-6">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mr-3">
                    <span class="text-white font-bold text-sm">{{ brand.name.charAt(0).toUpperCase() }}</span>
                  </div>
                  <div class="font-medium text-gray-900">{{ brand.name }}</div>
                </div>
              </td>
              <td class="py-4 px-6">
                <span class="text-sm text-gray-500 font-mono">{{ brand.slug }}</span>
              </td>
              <td class="py-4 px-6">
                <span 
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="brand.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
                >
                  {{ brand.is_active ? 'Aktif' : 'Pasif' }}
                </span>
              </td>
              <td class="py-4 px-6">
                <span class="text-sm text-gray-900">{{ brand.user_products_count || 0 }}</span>
              </td>
              <td class="py-4 px-6 text-sm text-gray-500">
                {{ formatDate(brand.created_at) }}
              </td>
              <td class="py-4 px-6">
                <div class="flex items-center justify-end space-x-2">
                  <button 
                    v-if="hasPermission('brands.edit')"
                    @click="editBrand(brand)" 
                    class="p-2 text-gray-400 hover:text-apple-blue transition-colors" 
                    title="Düzenle"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button 
                    v-if="hasPermission('brands.delete')"
                    @click="deleteBrand(brand)" 
                    class="p-2 text-gray-400 hover:text-red-500 transition-colors" 
                    title="Sil"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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

    <!-- Add/Edit Brand Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeModal"></div>

        <!-- Modal panel -->
        <div class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <form @submit.prevent="submitForm">
            <!-- Modal header -->
            <div class="bg-white px-6 py-4 border-b border-gray-200">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold text-gray-900">
                  {{ editingBrand ? 'Marka Düzenle' : 'Yeni Marka Ekle' }}
                </h3>
                <button type="button" @click="closeModal" class="text-gray-400 hover:text-gray-600">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Modal body -->
            <div class="bg-white px-6 py-6 space-y-6">
              <!-- Brand Name -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Marka Adı</label>
                <input 
                  v-model="form.name" 
                  type="text" 
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                  placeholder="Marka adını girin"
                />
              </div>

              <!-- Brand Slug -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Slug</label>
                <input 
                  v-model="form.slug" 
                  type="text" 
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                  placeholder="marka-adi"
                />
                <p class="mt-1 text-xs text-gray-500">Boş bırakılırsa otomatik oluşturulur</p>
              </div>

              <!-- Active Status -->
              <div>
                <label class="flex items-center">
                  <input 
                    v-model="form.is_active" 
                    type="checkbox" 
                    class="rounded border-gray-300 text-apple-blue focus:ring-apple-blue"
                  />
                  <span class="ml-2 text-sm font-medium text-gray-700">Aktif</span>
                </label>
              </div>
            </div>

            <!-- Modal footer -->
            <div class="bg-gray-50 px-6 py-4 flex justify-end space-x-3">
              <button type="button" @click="closeModal" class="btn btn-secondary">
                İptal
              </button>
              <button type="submit" :disabled="isSubmitting" class="btn btn-primary">
                <span v-if="isSubmitting">Kaydediliyor...</span>
                <span v-else>{{ editingBrand ? 'Güncelle' : 'Marka Ekle' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Delete All Brands Confirmation Modal -->
    <div v-if="showDeleteAllModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeDeleteAllModal"></div>
        <div class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-md sm:w-full">
          <div class="bg-white px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900">
                Tüm Markaları Sil
              </h3>
              <button type="button" @click="closeDeleteAllModal" class="text-gray-400 hover:text-gray-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          <div class="bg-white px-6 py-6">
            <div class="flex items-center mb-4">
              <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mr-4">
                <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div>
                <h4 class="text-lg font-medium text-gray-900">Dikkat!</h4>
                <p class="text-sm text-gray-500">Bu işlem geri alınamaz</p>
              </div>
            </div>
            <p class="text-gray-700 mb-4">
              Tüm markaları silmek istediğinizden emin misiniz? Bu işlem <strong>{{ brands.length }}</strong> markayı kalıcı olarak silecektir.
            </p>
            <p class="text-sm text-red-600 font-medium">
              Bu işlem geri alınamaz!
            </p>
          </div>
          <div class="bg-gray-50 px-6 py-4 flex justify-end space-x-3">
            <button type="button" @click="closeDeleteAllModal" class="btn btn-secondary">
              İptal
            </button>
            <button 
              @click="confirmDeleteAll" 
              :disabled="isDeletingAll"
              class="btn btn-danger"
            >
              <span v-if="isDeletingAll">Siliniyor...</span>
              <span v-else>Tümünü Sil</span>
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
const searchQuery = ref('')
const statusFilter = ref('')
const showModal = ref(false)
const isSubmitting = ref(false)
const editingBrand = ref(null)
const showDeleteAllModal = ref(false)
const isDeletingAll = ref(false)

// Permissions composable
let hasPermission
try {
  const permissions = usePermissions()
  hasPermission = permissions.hasPermission
} catch (error) {
  console.warn('Permissions composable failed:', error)
  hasPermission = () => false
}

// Form data
const form = reactive({
  name: '',
  slug: '',
  is_active: true
})

// Data
const brands = ref([])

// Computed
const filteredBrands = computed(() => {
  let filtered = brands.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(brand => 
      brand.name.toLowerCase().includes(query) ||
      brand.slug.toLowerCase().includes(query)
    )
  }

  // Status filter
  if (statusFilter.value) {
    const isActive = statusFilter.value === 'active'
    filtered = filtered.filter(brand => brand.is_active === isActive)
  }

  return filtered
})

const summary = computed(() => {
  const active = brands.value.filter(brand => brand.is_active).length
  const inactive = brands.value.filter(brand => !brand.is_active).length
  const total = brands.value.length

  return { active, inactive, total }
})

// Modal functions
const openModal = (brand = null) => {
  showModal.value = true
  
  if (brand) {
    // Edit mode - populate form
    editingBrand.value = brand
    form.name = brand.name
    form.slug = brand.slug
    form.is_active = brand.is_active
  } else {
    // Add mode - reset everything
    editingBrand.value = null
    resetForm()
  }
}

const closeModal = () => {
  showModal.value = false
  editingBrand.value = null
  resetForm()
}

// Delete all modal functions
const openDeleteAllModal = () => {
  showDeleteAllModal.value = true
}

const closeDeleteAllModal = () => {
  showDeleteAllModal.value = false
}

const resetForm = () => {
  form.name = ''
  form.slug = ''
  form.is_active = true
}

// API functions
const fetchBrands = async () => {
  isLoading.value = true
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('brands.list'))
    
    if (response.success) {
      brands.value = response.data
    } else {
      console.error('API Error:', response.message)
    }
  } catch (error) {
    console.error('Markalar yüklenirken hata:', error)
  } finally {
    isLoading.value = false
  }
}

const submitForm = async () => {
  isSubmitting.value = true
  
  try {
    const { $api } = useNuxtApp()
    
    // Prepare form data
    const formData = {
      name: form.name,
      slug: form.slug || null, // Let backend generate if empty
      is_active: form.is_active
    }
    
    let response
    if (editingBrand.value) {
      response = await $api.put($api.getEndpoint('brands.update', editingBrand.value.id), formData)
    } else {
      response = await $api.post($api.getEndpoint('brands.create'), formData)
    }
    
    if (response.success) {
      alert(editingBrand.value ? 'Marka başarıyla güncellendi!' : 'Marka başarıyla eklendi!')
      closeModal()
      await fetchBrands() // Refresh list
    } else {
      alert('İşlem başarısız: ' + response.message)
    }
    
  } catch (error) {
    console.error('Marka işlemi sırasında hata:', error)
    alert('İşlem sırasında bir hata oluştu.')
  } finally {
    isSubmitting.value = false
  }
}

const editBrand = (brand) => {
  openModal(brand)
}

const deleteBrand = async (brand) => {
  if (!confirm(`${brand.name} markasını silmek istediğinizden emin misiniz?`)) {
    return
  }
  
  try {
    const { $api } = useNuxtApp()
    const response = await $api.delete($api.getEndpoint('brands.delete', brand.id))
    
    if (response.success) {
      alert('Marka başarıyla silindi!')
      await fetchBrands() // Refresh list
    } else {
      alert('Silme işlemi başarısız: ' + response.message)
    }
    
  } catch (error) {
    console.error('Marka silinirken hata:', error)
    alert('Marka silinirken bir hata oluştu.')
  }
}

const confirmDeleteAll = async () => {
  isDeletingAll.value = true
  try {
    const { $api } = useNuxtApp()
    const response = await $api.delete('/brands/delete-all')
    
    if (response.success) {
      alert(`Tüm markalar başarıyla silindi! ${response.deleted_count} marka silindi.`)
      closeDeleteAllModal()
      await fetchBrands() // Refresh list
    } else {
      alert('Silme işlemi başarısız: ' + response.message)
    }
    
  } catch (error) {
    console.error('Tüm markalar silinirken hata:', error)
    alert('Tüm markalar silinirken bir hata oluştu.')
  } finally {
    isDeletingAll.value = false
  }
}

// Utility functions
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('tr-TR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Lifecycle
onMounted(async () => {
  try {
    // Kısa bir delay ile yetki kontrolünün tamamlanmasını bekle
    await new Promise(resolve => setTimeout(resolve, 200))
    isCheckingPermissions.value = false
    
    await fetchBrands()
  } catch (error) {
    console.error('Page initialization failed:', error)
    isCheckingPermissions.value = false
  }
})
</script>
