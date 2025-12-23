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
  <div v-else-if="!hasPermission('product_list.show')" class="flex items-center justify-center min-h-screen">
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
  <div v-else class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Ürünler</h1>
            <p class="mt-1 text-sm text-gray-500">XML'den import edilen ürünleri yönetin</p>
          </div>
          <div class="flex space-x-3">
            <select 
              v-model="selectedProfile" 
              @change="filterByProfile"
              class="border border-gray-300 rounded-xl shadow-sm py-2 px-3 focus:outline-none focus:ring-apple-blue focus:border-apple-blue transition-colors"
            >
              <option value="">Tüm Ürünler</option>
              <option v-for="profile in profiles" :key="profile.id" :value="profile.id">
                {{ profile.name }}
              </option>
            </select>
            <button 
              v-if="hasPermission('product_list.add')"
              @click="openAddProductModal" 
              class="btn btn-secondary"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Manuel Ürün Ekle
            </button>
            <button 
              v-if="hasPermission('product_list.xmlimport')"
              @click="openXmlImportModal" 
              class="btn btn-primary"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
              XML Import
            </button>
            <button 
              v-if="hasPermission('product_list.delete')"
              @click="openDeleteAllModal" 
              class="btn btn-danger"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Tüm Ürünleri Sil
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Filters -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Arama</label>
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Ürün adı, marka, MPN ara..."
              class="w-full border border-gray-300 rounded-xl shadow-sm py-2 px-3 focus:outline-none focus:ring-apple-blue focus:border-apple-blue transition-colors"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Marka</label>
            <select 
              v-model="selectedBrand" 
              class="w-full border border-gray-300 rounded-xl shadow-sm py-2 px-3 focus:outline-none focus:ring-apple-blue focus:border-apple-blue transition-colors"
            >
              <option value="">Tüm Markalar</option>
              <option v-for="brand in brands" :key="brand" :value="brand">{{ brand }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Ürün Tipi</label>
            <select 
              v-model="selectedProductType" 
              class="w-full border border-gray-300 rounded-xl shadow-sm py-2 px-3 focus:outline-none focus:ring-apple-blue focus:border-apple-blue transition-colors"
            >
              <option value="">Tüm Tipler</option>
              <option v-for="type in productTypes" :key="type" :value="type">{{ type }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Durum</label>
            <select 
              v-model="selectedStatus" 
              class="w-full border border-gray-300 rounded-xl shadow-sm py-2 px-3 focus:outline-none focus:ring-apple-blue focus:border-apple-blue transition-colors"
            >
              <option value="">Tümü</option>
              <option value="active">Aktif</option>
              <option value="inactive">Pasif</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Özel Analiz</label>
            <select 
              v-model="selectedAnalysis" 
              @change="filterByAnalysis"
              class="w-full border border-gray-300 rounded-xl shadow-sm py-2 px-3 focus:outline-none focus:ring-apple-blue focus:border-apple-blue transition-colors"
            >
              <option value="">Tüm Analizler</option>
              <option v-for="profile in profiles" :key="profile.id" :value="profile.id">
                {{ profile.name }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- Products Table -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-semibold text-gray-900">
              Ürünler ({{ filteredProducts.length }})
            </h3>
            <div class="flex items-center space-x-2">
              <span class="text-sm text-gray-500">Sayfa başına:</span>
              <select v-model="perPage" class="border border-gray-300 rounded-lg px-2 py-1 text-sm">
                <option value="10">10</option>
                <option value="25">25</option>
                <option value="50">50</option>
                <option value="100">100</option>
              </select>
            </div>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Görsel</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ürün Bilgileri</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Durum</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fiyat</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stok</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tarih</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">İşlemler</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr 
                v-for="product in paginatedProducts" 
                :key="product.id" 
                class="hover:bg-gray-50 transition-colors"
                :class="{ 'opacity-60': product.is_active === 0 || product.is_active === false }"
              >
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden">
                    <img 
                      v-if="product.image" 
                      :src="product.image" 
                      :alt="product.title"
                      class="w-full h-full object-cover"
                      @error="handleImageError"
                    />
                    <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                      <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="max-w-xs">
                    <div class="text-sm font-medium text-gray-900 truncate">{{ product.title }}</div>
                    <div class="text-sm text-gray-500">
                      <div v-if="product.brand && product.brand.name" class="truncate">Marka: {{ product.brand.name }}</div>
                      <div v-if="product.mpn" class="truncate">MPN: {{ product.mpn }}</div>
                      <div v-if="product.gtin" class="truncate">GTIN: {{ product.gtin }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span 
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="(product.is_active === 1 || product.is_active === true) 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'"
                  >
                    <span 
                      class="w-1.5 h-1.5 rounded-full mr-1.5"
                      :class="(product.is_active === 1 || product.is_active === true)
                        ? 'bg-green-400' 
                        : 'bg-red-400'"
                    ></span>
                    {{ (product.is_active === 1 || product.is_active === true) ? 'Aktif' : 'Pasif' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">
                    <div v-if="product.sale_price && parseFloat(product.sale_price) < parseFloat(product.price)" class="space-y-1">
                      <div class="text-lg font-semibold text-red-600">{{ formatPrice(product.sale_price) }}</div>
                      <div class="text-sm text-gray-500 line-through">{{ formatPrice(product.price) }}</div>
                    </div>
                    <div v-else-if="product.price" class="text-lg font-semibold text-gray-900">
                      {{ formatPrice(product.price) }}
                    </div>
                    <div v-else class="text-sm text-gray-500">Fiyat yok</div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span 
                    class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                    :class="getAvailabilityClass(product.availability)"
                  >
                    {{ product.availability || 'Bilinmiyor' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(product.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex items-center space-x-3">
                    <a 
                      :href="product.link" 
                      target="_blank" 
                      class="text-apple-blue hover:text-blue-700"
                    >
                      Görüntüle
                    </a>
                    <button 
                      v-if="hasPermission('product_list.edit')"
                      @click="editProduct(product)" 
                      class="text-gray-400 hover:text-apple-blue transition-colors" 
                      title="Düzenle"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button 
                      v-if="hasPermission('product_list.delete')"
                      @click="deleteProduct(product)" 
                      class="text-gray-400 hover:text-red-500 transition-colors" 
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

        <!-- Pagination -->
        <div class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
          <div class="flex-1 flex justify-between sm:hidden">
            <button 
              @click="currentPage = Math.max(1, currentPage - 1)"
              :disabled="currentPage === 1"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Önceki
            </button>
            <button 
              @click="currentPage = Math.min(totalPages, currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Sonraki
            </button>
          </div>
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                <span class="font-medium">{{ (currentPage - 1) * perPage + 1 }}</span>
                -
                <span class="font-medium">{{ Math.min(currentPage * perPage, filteredProducts.length) }}</span>
                arası, toplam
                <span class="font-medium">{{ filteredProducts.length }}</span>
                sonuçtan
              </p>
            </div>
            <div>
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button 
                  @click="currentPage = Math.max(1, currentPage - 1)"
                  :disabled="currentPage === 1"
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Önceki
                </button>
                <button 
                  v-for="page in visiblePages" 
                  :key="page"
                  @click="currentPage = page"
                  class="relative inline-flex items-center px-4 py-2 border text-sm font-medium"
                  :class="page === currentPage 
                    ? 'z-10 bg-apple-blue border-apple-blue text-white' 
                    : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'"
                >
                  {{ page }}
                </button>
                <button 
                  @click="currentPage = Math.min(totalPages, currentPage + 1)"
                  :disabled="currentPage === totalPages"
                  class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Sonraki
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- XML Import Modal -->
    <div v-if="showXmlImportModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeXmlImportModal"></div>
        <div class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <form @submit.prevent="submitXmlImport">
            <div class="bg-white px-6 py-4 border-b border-gray-200">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold text-gray-900">
                  XML Import
                </h3>
                <button type="button" @click="closeXmlImportModal" class="text-gray-400 hover:text-gray-600">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <div class="bg-white px-6 py-6 space-y-6">
              <div>
                <label for="xml_url" class="block text-sm font-medium text-gray-700 mb-2">XML URL</label>
                <input 
                  id="xml_url" 
                  v-model="xmlImportForm.xml_url" 
                  type="url" 
                  required
                  class="w-full border border-gray-300 rounded-xl shadow-sm py-2 px-3 focus:outline-none focus:ring-apple-blue focus:border-apple-blue transition-colors"
                  placeholder="https://example.com/products.xml"
                />
                <p class="mt-1 text-xs text-gray-500">XML dosyasının URL'sini girin</p>
              </div>
            </div>
            <div class="bg-gray-50 px-6 py-4 flex justify-end space-x-3">
              <button type="button" @click="closeXmlImportModal" class="btn btn-secondary">
                İptal
              </button>
              <button type="submit" :disabled="isSubmittingXml" class="btn btn-primary">
                <span v-if="isSubmittingXml">Import ediliyor...</span>
                <span v-else>Import Et</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Add/Edit Product Modal -->
    <div v-if="showProductModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeProductModal"></div>
        <div class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <form @submit.prevent="submitProduct">
            <div class="bg-white px-6 py-4 border-b border-gray-200">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-semibold text-gray-900">
                  {{ editingProduct ? 'Ürün Düzenle' : 'Yeni Ürün Ekle' }}
                </h3>
                <button type="button" @click="closeProductModal" class="text-gray-400 hover:text-gray-600">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <div class="bg-white px-6 py-6 space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Ürün Adı -->
                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Ürün Adı</label>
                  <input 
                    v-model="productForm.title" 
                    type="text" 
                    required
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                    placeholder="Ürün adını girin"
                  />
                </div>

                <!-- Ürün Görseli -->
                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Ürün Görseli</label>
                  <input 
                    v-model="productForm.image" 
                    type="url" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                    placeholder="https://example.com/image.jpg"
                  />
                </div>

                <!-- Marka -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Marka</label>
                  <input 
                    v-model="productForm.brand_name" 
                    type="text" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                    placeholder="Marka adı"
                  />
                </div>

                <!-- MPN -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">MPN</label>
                  <input 
                    v-model="productForm.mpn" 
                    type="text" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                    placeholder="Manufacturer Part Number"
                  />
                </div>

                <!-- GTIN -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">GTIN</label>
                  <input 
                    v-model="productForm.gtin" 
                    type="text" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                    placeholder="Global Trade Item Number"
                  />
                </div>

                <!-- Ürün Tipi -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Ürün Tipi</label>
                  <input 
                    v-model="productForm.product_type" 
                    type="text" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                    placeholder="Ürün kategorisi"
                  />
                </div>

                <!-- Fiyat -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Fiyat</label>
                  <input 
                    v-model="productForm.price" 
                    type="number" 
                    step="0.01"
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                    placeholder="0.00"
                  />
                </div>

                <!-- İndirimli Fiyat -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">İndirimli Fiyat</label>
                  <input 
                    v-model="productForm.sale_price" 
                    type="number" 
                    step="0.01"
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                    placeholder="0.00"
                  />
                </div>

                <!-- Stok Durumu -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Stok Durumu</label>
                  <select 
                    v-model="productForm.availability" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                  >
                    <option value="">Seçin</option>
                    <option value="in stock">Stokta</option>
                    <option value="out of stock">Stokta Yok</option>
                    <option value="limited">Sınırlı Stok</option>
                    <option value="preorder">Ön Sipariş</option>
                  </select>
                </div>

                <!-- Web Sitesi -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Web Sitesi</label>
                  <input 
                    v-model="productForm.link" 
                    type="url" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                    placeholder="https://example.com/product"
                  />
                </div>

                <!-- Durum (Aktif/Pasif) -->
                <div class="md:col-span-2">
                  <label class="flex items-center space-x-3 cursor-pointer">
                    <input 
                      v-model="productForm.is_active" 
                      type="checkbox" 
                      class="w-5 h-5 text-apple-blue border-gray-300 rounded focus:ring-apple-blue focus:ring-2"
                    />
                    <span class="text-sm font-medium text-gray-700">Ürün Aktif</span>
                    <span class="text-xs text-gray-500">(Pasif ürünler XML import'unda otomatik olarak pasif edilir)</span>
                  </label>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-6 py-4 flex justify-end space-x-3">
              <button type="button" @click="closeProductModal" class="btn btn-secondary">
                İptal
              </button>
              <button type="submit" :disabled="isSubmittingProduct" class="btn btn-primary">
                <span v-if="isSubmittingProduct">Kaydediliyor...</span>
                <span v-else>{{ editingProduct ? 'Güncelle' : 'Ürün Ekle' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Delete All Products Confirmation Modal -->
    <div v-if="showDeleteAllModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeDeleteAllModal"></div>
        <div class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-md sm:w-full">
          <div class="bg-white px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900">
                Tüm Ürünleri Sil
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
              Tüm ürünleri silmek istediğinizden emin misiniz? Bu işlem <strong>{{ products.length }}</strong> ürünü kalıcı olarak silecektir.
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
  layout: 'dashboard',
  middleware: 'auth'
})

// Reactive data
const isCheckingPermissions = ref(true)

// Permissions composable
let hasPermission
try {
  const permissions = usePermissions()
  hasPermission = permissions.hasPermission
} catch (error) {
  console.warn('Permissions composable failed:', error)
  hasPermission = () => false
}

// Reactive data
const products = ref([])
const profiles = ref([])
const selectedProfile = ref('')
const selectedAnalysis = ref('')
const searchQuery = ref('')
const selectedBrand = ref('')
const selectedProductType = ref('')
const selectedStatus = ref('')
const perPage = ref(25)
const currentPage = ref(1)
const showXmlImportModal = ref(false)
const isSubmittingXml = ref(false)
const showProductModal = ref(false)
const isSubmittingProduct = ref(false)
const editingProduct = ref(null)
const showDeleteAllModal = ref(false)
const isDeletingAll = ref(false)

const xmlImportForm = reactive({
  xml_url: 'https://www.pt.com.tr/wp-content/uploads/wpwoof-feed/xml/iprice.xml'
})

const productForm = reactive({
  title: '',
  image: '',
  brand_name: '',
  mpn: '',
  gtin: '',
  product_type: '',
  price: '',
  sale_price: '',
  availability: '',
  link: '',
  is_active: true
})

// Computed properties
const brands = computed(() => {
  const brandSet = new Set()
  products.value.forEach(product => {
    if (product.brand && product.brand.name) brandSet.add(product.brand.name)
  })
  return Array.from(brandSet).sort()
})

const productTypes = computed(() => {
  const typeSet = new Set()
  products.value.forEach(product => {
    if (product.product_type) typeSet.add(product.product_type)
  })
  return Array.from(typeSet).sort()
})

const filteredProducts = computed(() => {
  let filtered = products.value

  // Profile filter
  if (selectedProfile.value) {
    const profileProducts = profiles.value.find(p => p.id == selectedProfile.value)?.products || []
    const profileProductIds = profileProducts.map(pp => pp.product_id)
    filtered = filtered.filter(product => profileProductIds.includes(product.id))
  }

  // Analysis filter (Custom Profile)
  if (selectedAnalysis.value) {
    const analysisProducts = profiles.value.find(p => p.id == selectedAnalysis.value)?.products || []
    const analysisProductIds = analysisProducts.map(pp => pp.user_product_id)
    filtered = filtered.filter(product => analysisProductIds.includes(product.id))
    
    // Sort by custom profile order
    filtered = filtered.sort((a, b) => {
      const aIndex = analysisProductIds.indexOf(a.id)
      const bIndex = analysisProductIds.indexOf(b.id)
      return aIndex - bIndex
    })
  }

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(product => 
      product.title.toLowerCase().includes(query) ||
      (product.brand && product.brand.name && product.brand.name.toLowerCase().includes(query)) ||
      (product.mpn && product.mpn.toLowerCase().includes(query)) ||
      (product.gtin && product.gtin.toLowerCase().includes(query))
    )
  }

  // Brand filter
  if (selectedBrand.value) {
    filtered = filtered.filter(product => product.brand && product.brand.name === selectedBrand.value)
  }

  // Product type filter
  if (selectedProductType.value) {
    filtered = filtered.filter(product => product.product_type === selectedProductType.value)
  }

  // Status filter (is_active)
  if (selectedStatus.value === 'active') {
    filtered = filtered.filter(product => product.is_active === 1 || product.is_active === true)
  } else if (selectedStatus.value === 'inactive') {
    filtered = filtered.filter(product => product.is_active === 0 || product.is_active === false)
  }

  return filtered
})

const totalPages = computed(() => {
  return Math.ceil(filteredProducts.value.length / perPage.value)
})

const paginatedProducts = computed(() => {
  const start = (currentPage.value - 1) * perPage.value
  const end = start + perPage.value
  return filteredProducts.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) pages.push(i)
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 3) {
      pages.push(1)
      pages.push('...')
      for (let i = total - 4; i <= total; i++) pages.push(i)
    } else {
      pages.push(1)
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) pages.push(i)
      pages.push('...')
      pages.push(total)
    }
  }
  
  return pages
})

// Methods
const fetchProducts = async () => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get('/user-products')
    products.value = response.data || []
  } catch (error) {
    console.error('Ürünler yüklenirken hata:', error)
  }
}

const fetchProfiles = async () => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('custom-profiles.list'))
    
    if (response.success) {
      // Fetch products for each profile
      const profilesWithProducts = await Promise.all(
        response.data.map(async (profile) => {
          try {
            const productsResponse = await $api.get($api.getEndpoint('custom-profiles.products', profile.id))
            return {
              ...profile,
              products: productsResponse.success ? productsResponse.data : []
            }
          } catch (error) {
            console.error(`Profil ${profile.id} ürünleri yüklenirken hata:`, error)
            return { ...profile, products: [] }
          }
        })
      )
      profiles.value = profilesWithProducts
    }
  } catch (error) {
    console.error('Profiller yüklenirken hata:', error)
  }
}

const filterByProfile = () => {
  currentPage.value = 1 // Reset to first page when filtering
}

const filterByAnalysis = () => {
  currentPage.value = 1 // Reset to first page when filtering
}

const openXmlImportModal = () => {
  showXmlImportModal.value = true
}

const closeXmlImportModal = () => {
  showXmlImportModal.value = false
  xmlImportForm.xml_url = 'https://www.pt.com.tr/wp-content/uploads/wpwoof-feed/xml/iprice.xml'
}

// Delete all modal functions
const openDeleteAllModal = () => {
  showDeleteAllModal.value = true
}

const closeDeleteAllModal = () => {
  showDeleteAllModal.value = false
}

// Product modal functions
const openAddProductModal = () => {
  editingProduct.value = null
  resetProductForm()
  showProductModal.value = true
}

const editProduct = (product) => {
  editingProduct.value = product
  productForm.title = product.title || ''
  productForm.image = product.image || ''
  productForm.brand_name = product.brand?.name || ''
  productForm.mpn = product.mpn || ''
  productForm.gtin = product.gtin || ''
  productForm.product_type = product.product_type || ''
  productForm.price = product.price || ''
  productForm.sale_price = product.sale_price || ''
  productForm.availability = product.availability || ''
  productForm.link = product.link || ''
  // is_active: 1, true, veya boolean olabilir, normalize et
  productForm.is_active = product.is_active === 1 || product.is_active === true || product.is_active === '1'
  showProductModal.value = true
}

const closeProductModal = () => {
  showProductModal.value = false
  editingProduct.value = null
  resetProductForm()
}

const resetProductForm = () => {
  productForm.title = ''
  productForm.image = ''
  productForm.brand_name = ''
  productForm.mpn = ''
  productForm.gtin = ''
  productForm.product_type = ''
  productForm.price = ''
  productForm.sale_price = ''
  productForm.availability = ''
  productForm.link = ''
  productForm.is_active = true // Yeni ürünler varsayılan olarak aktif
}

const submitXmlImport = async () => {
  isSubmittingXml.value = true
  try {
    const { $api } = useNuxtApp()
    const response = await $api.post('/user-products/import-xml', {
      xml_url: xmlImportForm.xml_url
    })

    if (response.success) {
      // Show success message
      alert(`XML import başarılı! ${response.summary.imported} ürün eklendi.`)
      closeXmlImportModal()
      await fetchProducts() // Refresh the list
    } else {
      alert('XML import başarısız: ' + response.message)
    }
  } catch (error) {
    console.error('XML import hatası:', error)
    alert('XML import sırasında bir hata oluştu')
  } finally {
    isSubmittingXml.value = false
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

const getAvailabilityClass = (availability) => {
  if (!availability) return 'bg-gray-100 text-gray-800'
  
  const lower = availability.toLowerCase()
  if (lower.includes('in stock') || lower.includes('stokta')) {
    return 'bg-green-100 text-green-800'
  } else if (lower.includes('out of stock') || lower.includes('stokta yok')) {
    return 'bg-red-100 text-red-800'
  } else if (lower.includes('limited') || lower.includes('sınırlı')) {
    return 'bg-yellow-100 text-yellow-800'
  }
  return 'bg-gray-100 text-gray-800'
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
}

// Product CRUD operations
const submitProduct = async () => {
  isSubmittingProduct.value = true
  try {
    const config = useRuntimeConfig()
    
    // Prepare form data
    const formData = {
      title: productForm.title,
      image: productForm.image,
      brand_name: productForm.brand_name,
      mpn: productForm.mpn,
      gtin: productForm.gtin,
      product_type: productForm.product_type,
      price: productForm.price ? parseFloat(productForm.price) : null,
      sale_price: productForm.sale_price ? parseFloat(productForm.sale_price) : null,
      availability: productForm.availability,
      link: productForm.link,
      is_active: productForm.is_active ? 1 : 0 // Boolean'ı 1/0'a çevir
    }
    
    const url = editingProduct.value 
      ? `${config.public.apiBase}/user-products/${editingProduct.value.id}`
      : `${config.public.apiBase}/user-products`
    
    const method = editingProduct.value ? 'PUT' : 'POST'
    
    const response = await $fetch(url, {
      method,
      headers: {
        'Authorization': `Bearer ${useAuthStore().token}`,
        'Content-Type': 'application/json'
      },
      body: formData
    })
    
    if (response.success) {
      alert(editingProduct.value ? 'Ürün başarıyla güncellendi!' : 'Ürün başarıyla eklendi!')
      closeProductModal()
      await fetchProducts() // Refresh list
    } else {
      alert('İşlem başarısız: ' + response.message)
    }
    
  } catch (error) {
    console.error('Ürün işlemi sırasında hata:', error)
    alert('İşlem sırasında bir hata oluştu.')
  } finally {
    isSubmittingProduct.value = false
  }
}

const deleteProduct = async (product) => {
  if (!confirm(`${product.title} ürününü silmek istediğinizden emin misiniz?`)) {
    return
  }
  
  try {
    const config = useRuntimeConfig()
    const response = await $fetch(`${config.public.apiBase}/user-products/${product.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${useAuthStore().token}`
      }
    })
    
    if (response.success) {
      alert('Ürün başarıyla silindi!')
      await fetchProducts() // Refresh list
    } else {
      alert('Silme işlemi başarısız: ' + response.message)
    }
    
  } catch (error) {
    console.error('Ürün silinirken hata:', error)
    alert('Ürün silinirken bir hata oluştu.')
  }
}

const confirmDeleteAll = async () => {
  isDeletingAll.value = true
  try {
    const config = useRuntimeConfig()
    const response = await $fetch(`${config.public.apiBase}/user-products/delete-all`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${useAuthStore().token}`
      }
    })
    
    if (response.success) {
      alert(`Tüm ürünler başarıyla silindi! ${response.deleted_count} ürün silindi.`)
      closeDeleteAllModal()
      await fetchProducts() // Refresh list
    } else {
      alert('Silme işlemi başarısız: ' + response.message)
    }
    
  } catch (error) {
    console.error('Tüm ürünler silinirken hata:', error)
    alert('Tüm ürünler silinirken bir hata oluştu.')
  } finally {
    isDeletingAll.value = false
  }
}

// Watch for filter changes to reset pagination
watch([searchQuery, selectedBrand, selectedProductType, selectedStatus], () => {
  currentPage.value = 1
})

// Lifecycle
onMounted(async () => {
  try {
    // Kısa bir delay ile yetki kontrolünün tamamlanmasını bekle
    await new Promise(resolve => setTimeout(resolve, 200))
    isCheckingPermissions.value = false
    
    await fetchProducts()
    await fetchProfiles()
  } catch (error) {
    console.error('Page initialization failed:', error)
    isCheckingPermissions.value = false
  }
})
</script>
