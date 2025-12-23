<template>
  <div class="p-6">
    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      <p class="text-gray-500 mt-2">Profil yükleniyor...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-12">
      <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">Hata Oluştu</h3>
      <p class="text-gray-500 mb-4">{{ error }}</p>
      <button 
        @click="fetchProfile" 
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
      >
        Tekrar Dene
      </button>
    </div>

    <!-- Page Header -->
    <div v-else-if="!error" class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <div class="flex items-center gap-3 mb-2">
            <NuxtLink to="/dashboard/custom-profile" class="text-gray-500 hover:text-gray-700">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </NuxtLink>
            <h1 class="text-3xl font-bold text-gray-900">{{ profile?.name || 'Profil Bulunamadı' }}</h1>
          </div>
          <p class="text-gray-600">{{ profile?.description || 'Açıklama yok' }}</p>
        </div>
        <div class="flex items-center gap-3">
          <button 
            @click="openAddProductModal" 
            class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Ürün Ekle
          </button>
        </div>
      </div>
    </div>

    <!-- Profile Stats -->
    <div v-if="!isLoading && !error" class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Toplam Ürün</p>
            <p class="text-2xl font-semibold text-gray-900">{{ profileProducts.length }}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Son Güncelleme</p>
            <p class="text-lg font-semibold text-gray-900">{{ formatDate(profile?.updated_at) }}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Sıralama</p>
            <p class="text-lg font-semibold text-gray-900">Özel</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Products List -->
    <div v-if="!isLoading && !error" class="bg-white rounded-xl shadow-sm border border-gray-200">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900">Profil Ürünleri</h3>
      </div>

      <div v-if="isLoading" class="text-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p class="text-gray-500 mt-2">Yükleniyor...</p>
      </div>

      <div v-else-if="profileProducts.length === 0" class="text-center py-12">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Henüz ürün yok</h3>
        <p class="text-gray-500 mb-4">Bu profile ürün eklemek için yukarıdaki butona tıklayın.</p>
      </div>

      <div v-else class="divide-y divide-gray-200">
        <!-- Bulk Actions -->
        <div v-if="selectedProfileProducts.length > 0" class="flex items-center justify-between p-4 bg-red-50 border-b border-red-200">
          <span class="text-red-700 font-medium">
            {{ selectedProfileProducts.length }} ürün seçildi
          </span>
          <div class="flex gap-2">
            <button 
              @click="removeSelectedProducts"
              :disabled="isRemovingProducts"
              class="bg-red-600 hover:bg-red-700 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
            >
              <svg v-if="isRemovingProducts" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span v-if="isRemovingProducts">Siliniyor...</span>
              <span v-else>Seçilenleri Sil</span>
            </button>
            <button 
              @click="selectedProfileProducts = []"
              class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
            >
              İptal
            </button>
          </div>
        </div>

        <div 
          v-for="(item, index) in profileProducts" 
          :key="item.id"
          class="p-6 hover:bg-gray-50 transition-colors"
          :class="{ 
            'ring-2 ring-red-500 bg-red-50': selectedProfileProducts.includes(item.id),
            'ring-2 ring-blue-500 bg-blue-50': draggedIndex === index,
            'ring-2 ring-green-500 bg-green-50': draggedOverIndex === index && draggedIndex !== index
          }"
          draggable="true"
          @dragstart="startDrag(index)"
          @dragover="handleDragOver($event, index)"
          @dragend="handleDragEnd"
          @drop="handleDrop($event, index)"
        >
          <div class="flex items-center gap-4">
            <!-- Selection Checkbox -->
            <input 
              type="checkbox" 
              :checked="selectedProfileProducts.includes(item.id)"
              @change="toggleProfileProductSelection(item.id)"
              class="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
            />
            
            <!-- Drag Handle -->
            <div class="flex flex-col gap-1 cursor-move hover:bg-gray-100 p-1 rounded" title="Sürükleyerek sıralayın">
              <div class="w-1 h-1 bg-gray-400 rounded-full"></div>
              <div class="w-1 h-1 bg-gray-400 rounded-full"></div>
              <div class="w-1 h-1 bg-gray-400 rounded-full"></div>
              <div class="w-1 h-1 bg-gray-400 rounded-full"></div>
            </div>

            <!-- Order Number -->
            <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm font-semibold text-blue-600">
              {{ index + 1 }}
            </div>

            <!-- Product Image -->
            <div class="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden">
              <img 
                v-if="item.product?.image" 
                :src="item.product.image" 
                :alt="item.product.title"
                class="w-full h-full object-cover"
                @error="handleImageError"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>

            <!-- Product Info -->
            <div class="flex-1 min-w-0">
              <h4 class="text-lg font-medium text-gray-900 truncate">{{ item.product?.title || 'Ürün Bulunamadı' }}</h4>
              <div class="flex items-center gap-4 mt-1 text-sm text-gray-500">
                <span v-if="item.product?.brand?.name">Marka: {{ item.product.brand.name }}</span>
                <span v-if="item.product?.mpn">MPN: {{ item.product.mpn }}</span>
                <span v-if="item.product?.price" class="text-green-600 font-semibold">
                  {{ formatPrice(item.product.price) }}
                </span>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>

    <!-- Add Product Modal -->
    <div v-if="showAddProductModal && !isLoading && !error" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Ürün Ekle</h3>
          <button @click="closeAddProductModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Search -->
        <div class="mb-6">
          <input 
            v-model="productSearchQuery" 
            type="text" 
            placeholder="Ürün ara..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <!-- Products Grid -->
        <div v-if="isLoadingProducts" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p class="text-gray-500 mt-2">Ürünler yükleniyor...</p>
        </div>

        <div v-else-if="filteredProducts.length === 0" class="text-center py-8">
          <p class="text-gray-500">Arama kriterlerinize uygun ürün bulunamadı.</p>
        </div>

        <div v-else class="space-y-4 max-h-96 overflow-y-auto">
          <!-- Select All Button -->
          <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div class="flex items-center gap-3">
              <input 
                type="checkbox" 
                :checked="selectedProducts.length === filteredProducts.length && filteredProducts.length > 0"
                :indeterminate="selectedProducts.length > 0 && selectedProducts.length < filteredProducts.length"
                @change="toggleSelectAll"
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span class="text-sm font-medium text-gray-700">
                Tümünü Seç ({{ selectedProducts.length }}/{{ filteredProducts.length }})
              </span>
            </div>
          </div>

          <!-- Products Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div 
              v-for="product in filteredProducts" 
              :key="product.id"
              class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
              :class="{ 'ring-2 ring-blue-500 bg-blue-50': selectedProducts.includes(product.id) }"
              @click="toggleProductSelection(product.id)"
            >
              <div class="flex items-start gap-3">
                <div class="w-12 h-12 bg-gray-100 rounded-lg overflow-hidden">
                  <img 
                    v-if="product.image" 
                    :src="product.image" 
                    :alt="product.title"
                    class="w-full h-full object-cover"
                    @error="handleImageError"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                </div>
                <div class="flex-1 min-w-0">
                  <h4 class="text-sm font-medium text-gray-900 truncate">{{ product.title }}</h4>
                  <div class="text-xs text-gray-500 mt-1">
                    <div v-if="product.brand?.name">{{ product.brand.name }}</div>
                    <div v-if="product.mpn">MPN: {{ product.mpn }}</div>
                    <div v-if="product.price" class="text-green-600 font-semibold">
                      {{ formatPrice(product.price) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Add Selected Button -->
          <div class="sticky bottom-0 bg-white border-t border-gray-200 p-4">
            <button 
              @click="addSelectedProducts"
              :disabled="selectedProducts.length === 0 || isAddingProducts"
              class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white px-4 py-3 rounded-lg transition-colors font-medium flex items-center justify-center gap-2"
            >
              <svg v-if="isAddingProducts" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span v-if="isAddingProducts">Ekleniyor...</span>
              <span v-else>Seçilenleri Ekle ({{ selectedProducts.length }})</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Sayfa meta bilgileri
definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

// Route params
const route = useRoute()
const profileId = route.query.id

// Sayfa başlığı
useHead({
  title: 'Profil Detayı - Admin Panel'
})

// Reactive data
const profile = ref(null)
const profileProducts = ref([])
const allProducts = ref([])
const isLoading = ref(false)
const isLoadingProducts = ref(false)
const showAddProductModal = ref(false)
const isAddingProducts = ref(false)
const isRemovingProducts = ref(false)
const productSearchQuery = ref('')
const error = ref(null)
const selectedProducts = ref([])
const selectedProfileProducts = ref([])

// Methods
const fetchProfile = async () => {
  try {
    isLoading.value = true
    error.value = null
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('custom-profiles.get', profileId))
    
    if (response.success) {
      profile.value = response.data
    } else {
      error.value = response.message || 'Profil yüklenirken hata oluştu'
    }
  } catch (err) {
    error.value = err.message || 'Profil yüklenirken hata oluştu'
  } finally {
    isLoading.value = false
  }
}

const fetchProfileProducts = async () => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('custom-profiles.products', profileId))
    
    if (response.success) {
      profileProducts.value = response.data || []
    } else {
      console.error('Profil ürünleri yüklenirken hata:', response.message)
    }
  } catch (error) {
    console.error('Profil ürünleri yüklenirken hata:', error)
  }
}

const fetchAllProducts = async () => {
  try {
    isLoadingProducts.value = true
    const { $api } = useNuxtApp()
    const response = await $api.get('/user-products')
    
    if (response.success) {
      allProducts.value = response.data || []
    } else {
      console.error('Ürünler yüklenirken hata:', response.message)
    }
  } catch (error) {
    console.error('Ürünler yüklenirken hata:', error)
  } finally {
    isLoadingProducts.value = false
  }
}

const openAddProductModal = async () => {
  showAddProductModal.value = true
  productSearchQuery.value = ''
  await fetchAllProducts()
}

const closeAddProductModal = () => {
  showAddProductModal.value = false
  productSearchQuery.value = ''
  selectedProducts.value = []
}

const toggleProductSelection = (productId) => {
  const index = selectedProducts.value.indexOf(productId)
  if (index > -1) {
    selectedProducts.value.splice(index, 1)
  } else {
    selectedProducts.value.push(productId)
  }
}

const toggleSelectAll = () => {
  if (selectedProducts.value.length === filteredProducts.value.length) {
    selectedProducts.value = []
  } else {
    selectedProducts.value = filteredProducts.value.map(p => p.id)
  }
}

const addSelectedProducts = async () => {
  if (selectedProducts.value.length === 0 || isAddingProducts.value) return
  
  isAddingProducts.value = true
  
  try {
    const { $api } = useNuxtApp()
    const response = await $api.post(`/custom-profiles/${profileId}/products/batch`, {
      product_ids: selectedProducts.value
    })
    
    closeAddProductModal()
    await fetchProfileProducts()
    await fetchProfile() // Profil bilgilerini güncelle
    
    if (response.success) {
      alert(response.message)
    } else {
      alert('Ürünler eklenirken bir hata oluştu: ' + response.message)
    }
  } catch (error) {
    console.error('Ürünler eklenirken hata:', error)
    alert('Ürünler eklenirken bir hata oluştu')
  } finally {
    isAddingProducts.value = false
  }
}


const removeProduct = async (profileProductId) => {
  if (!confirm('Bu ürünü profilden çıkarmak istediğinizden emin misiniz?')) {
    return
  }

  try {
    const { $api } = useNuxtApp()
    const response = await $api.delete(`/custom-profiles/${profileId}/products/${profileProductId}`)
    
    if (response.success) {
      await fetchProfileProducts()
      await fetchProfile() // Profil bilgilerini güncelle
      alert('Ürün profilden çıkarıldı')
    } else {
      alert('Ürün çıkarılırken hata: ' + response.message)
    }
  } catch (error) {
    console.error('Ürün çıkarma hatası:', error)
    alert('Ürün çıkarılırken bir hata oluştu')
  }
}


const reorderProducts = async (fromIndex, toIndex) => {
  try {
    // Önce UI'da sıralamayı güncelle (hızlı görünüm için)
    const item = profileProducts.value.splice(fromIndex, 1)[0]
    profileProducts.value.splice(toIndex, 0, item)
    
    // Sonra backend'e gönder
    const { $api } = useNuxtApp()
    const response = await $api.post(`/custom-profiles/${profileId}/products/reorder`, {
      from_index: fromIndex,
      to_index: toIndex
    })
    
    if (!response.success) {
      // Hata olursa geri yükle
      await fetchProfileProducts()
      alert('Sıralama güncellenirken hata: ' + response.message)
    }
  } catch (error) {
    console.error('Sıralama hatası:', error)
    // Hata olursa geri yükle
    await fetchProfileProducts()
    alert('Sıralama güncellenirken bir hata oluştu')
  }
}

const draggedIndex = ref(null)
const draggedOverIndex = ref(null)

const startDrag = (index) => {
  draggedIndex.value = index
}

const handleDragOver = (event, index) => {
  event.preventDefault()
  draggedOverIndex.value = index
}

const handleDragEnd = () => {
  if (draggedIndex.value !== null && draggedOverIndex.value !== null && 
      draggedIndex.value !== draggedOverIndex.value) {
    reorderProducts(draggedIndex.value, draggedOverIndex.value)
  }
  draggedIndex.value = null
  draggedOverIndex.value = null
}

const handleDrop = (event, index) => {
  event.preventDefault()
  if (draggedIndex.value !== null && draggedIndex.value !== index) {
    reorderProducts(draggedIndex.value, index)
  }
  draggedIndex.value = null
  draggedOverIndex.value = null
}

const toggleProfileProductSelection = (productId) => {
  const index = selectedProfileProducts.value.indexOf(productId)
  if (index > -1) {
    selectedProfileProducts.value.splice(index, 1)
  } else {
    selectedProfileProducts.value.push(productId)
  }
}

const removeSelectedProducts = async () => {
  if (selectedProfileProducts.value.length === 0) return
  
  if (!confirm(`${selectedProfileProducts.value.length} ürünü profilden çıkarmak istediğinizden emin misiniz?`)) {
    return
  }
  
  isRemovingProducts.value = true
  
  try {
    const { $api } = useNuxtApp()
    const promises = selectedProfileProducts.value.map(productId => 
      $api.delete(`/custom-profiles/${profileId}/products/${productId}`)
    )
    
    const selectedCount = selectedProfileProducts.value.length
    await Promise.all(promises)
    selectedProfileProducts.value = []
    await fetchProfileProducts()
    await fetchProfile() // Profil bilgilerini güncelle
    alert(`${selectedCount} ürün profilden çıkarıldı`)
  } catch (error) {
    console.error('Ürünler silinirken hata:', error)
    alert('Ürünler silinirken bir hata oluştu')
  } finally {
    isRemovingProducts.value = false
  }
}

const formatPrice = (price) => {
  if (!price) return 'N/A'
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY'
  }).format(price)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('tr-TR')
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
}

// Computed
const filteredProducts = computed(() => {
  // Mevcut profildeki ürünleri filtrele
  const currentProductIds = profileProducts.value.map(pp => pp.user_product_id)
  let filtered = allProducts.value.filter(product => !currentProductIds.includes(product.id))
  
  if (productSearchQuery.value) {
    const query = productSearchQuery.value.toLowerCase()
    filtered = filtered.filter(product => 
      product.title.toLowerCase().includes(query) ||
      (product.brand && product.brand.name && product.brand.name.toLowerCase().includes(query)) ||
      (product.mpn && product.mpn.toLowerCase().includes(query))
    )
  }
  
  return filtered
})

// Lifecycle
onMounted(async () => {
  if (profileId) {
    await fetchProfile()
    await fetchProfileProducts()
  } else {
    error.value = 'Profil ID bulunamadı'
  }
})
</script>
