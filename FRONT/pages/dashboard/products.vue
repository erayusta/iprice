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
  <div v-else-if="!hasPermission('products_url.show')" class="flex items-center justify-center min-h-screen">
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
            <button 
              @click="downloadUrlsAsExcel" 
              :disabled="isDownloadingUrls"
              class="btn btn-primary flex items-center"
            >
              <svg v-if="!isDownloadingUrls" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <svg v-else class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span v-if="!isDownloadingUrls">URL'leri İndir</span>
              <span v-else>İndiriliyor...</span>
            </button>
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
              @click="openDeleteAllUrlsModal" 
              class="btn btn-danger"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Tüm URL'leri Temizle
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Filters -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
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
            <label class="block text-sm font-medium text-gray-700 mb-2">Marka ..</label>
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
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Görsel</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ürün Bilgileri</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">MPN</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tanımlı URL Sayısı</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">İşlemler</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="product in filteredProducts" :key="product.id" class="hover:bg-gray-50">
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
                      <div v-if="product.gtin" class="truncate">GTIN: {{ product.gtin }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ product.mpn || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {{ product.company_product_urls_count || 0 }} URL
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button 
                    v-if="hasPermission('products_url.edit')"
                    @click="openEditModal(product)" 
                    class="text-apple-blue hover:text-blue-700"
                  >
                    Düzenle
                  </button>
                  <span v-else class="text-gray-400">Yetki yok</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Edit Product Modal -->
    <div v-if="showEditModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeEditModal"></div>
        <div class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <div class="bg-white px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900">
                Ürün Düzenle: {{ editingProduct?.title }}
              </h3>
              <button type="button" @click="closeEditModal" class="text-gray-400 hover:text-gray-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          
          <div class="bg-white px-6 py-6">
            <!-- Companies and URLs -->
            <div class="space-y-6">
              <div v-for="company in companies" :key="company.id" class="border border-gray-200 rounded-lg p-4">
                <div class="flex items-center justify-between mb-3">
                  <div class="flex items-center space-x-2">
                    <h4 class="text-md font-semibold text-gray-800">{{ company.company_name }}</h4>
                    <span v-if="company.is_marketplace" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Marketplace
                    </span>
                  </div>
                  <div v-if="company.is_marketplace" class="flex items-center space-x-2">
                    <span class="text-sm text-gray-500">
                      {{ getUrlsForCompany(company.id).length }}/10 URL
                    </span>
                    <button 
                      @click="addUrlForCompany(company.id)" 
                      :disabled="getUrlsForCompany(company.id).length >= 10"
                      class="text-sm text-apple-blue hover:text-blue-700 flex items-center space-x-1 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                      </svg>
                      <span>URL Ekle</span>
                    </button>
                    <button 
                      v-if="company.company_name.toLowerCase().includes('trendyol')"
                      @click="openTrendyolAI(company.id)" 
                      class="text-sm text-purple-600 hover:text-purple-700 flex items-center space-x-1"
                      title="Trendyol AI ile benzer ürünleri bul"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                      <span>Trendyol AI</span>
                    </button>
                  </div>
                </div>
                
                <!-- URLs for this company -->
                <div class="space-y-3">
                  <div 
                    v-for="(urlData, index) in getUrlsForCompany(company.id)" 
                    :key="`${company.id}-${index}`"
                    class="flex items-center space-x-2"
                  >
                    <input 
                      v-model="urlData.url"
                      type="url" 
                      class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-apple-blue focus:border-apple-blue"
                      :placeholder="`${company.company_name} URL ${index + 1}`"
                    />
                    <button 
                      v-if="getUrlsForCompany(company.id).length > 1 || !company.is_marketplace"
                      @click="removeUrlForCompany(company.id, index)" 
                      class="text-red-500 hover:text-red-700 p-1"
                      :title="company.is_marketplace ? 'URL\'yi Kaldır' : 'URL\'yi Temizle'"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="bg-gray-50 px-6 py-4 flex justify-end space-x-3">
            <button type="button" @click="closeEditModal" class="btn btn-secondary">
              İptal
            </button>
            <button 
              @click="saveUrls" 
              :disabled="isSaving" 
              class="btn btn-primary"
            >
              <span v-if="isSaving">Kaydediliyor...</span>
              <span v-else>Kaydet</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Trendyol AI Modal -->
    <div v-if="showTrendyolAIModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeTrendyolAIModal"></div>
        <div class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-6xl sm:w-full">
          <div class="bg-white px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                  <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-900">
                    Trendyol AI - Benzer Ürün Bulucu
                  </h3>
                  <p class="text-sm text-gray-500">
                    {{ editingProduct?.title }} için benzer ürünler aranıyor...
                  </p>
                </div>
              </div>
              <button type="button" @click="closeTrendyolAIModal" class="text-gray-400 hover:text-gray-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          
          <div class="bg-white px-6 py-6">
            <!-- Loading State -->
            <div v-if="isTrendyolAILoading" class="flex items-center justify-center py-12">
              <div class="text-center">
                <div class="w-20 h-20 bg-gradient-to-r from-purple-100 to-purple-200 rounded-full flex items-center justify-center mx-auto mb-6">
                  <svg class="w-10 h-10 text-purple-600 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </div>
                <h3 class="text-xl font-semibold text-gray-900 mb-3">AI Analizi Yapılıyor</h3>
                <p class="text-gray-600 mb-4">Trendyol'da benzer ürünler aranıyor ve AI analizi yapılıyor...</p>
                
                <!-- Progress Steps -->
                <div class="space-y-2 text-sm text-gray-500">
                  <div class="flex items-center justify-center space-x-2">
                    <div class="w-2 h-2 bg-purple-600 rounded-full animate-pulse"></div>
                    <span>Trendyol'da ürünler aranıyor...</span>
                  </div>
                  <div class="flex items-center justify-center space-x-2">
                    <div class="w-2 h-2 bg-purple-600 rounded-full animate-pulse" style="animation-delay: 0.5s"></div>
                    <span>AI benzerlik analizi yapılıyor...</span>
                  </div>
                  <div class="flex items-center justify-center space-x-2">
                    <div class="w-2 h-2 bg-purple-600 rounded-full animate-pulse" style="animation-delay: 1s"></div>
                    <span>Sonuçlar hazırlanıyor...</span>
                  </div>
                </div>
                
                <!-- Animated Dots -->
                <div class="mt-6 flex items-center justify-center space-x-2">
                  <div class="w-3 h-3 bg-purple-600 rounded-full animate-bounce"></div>
                  <div class="w-3 h-3 bg-purple-600 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                  <div class="w-3 h-3 bg-purple-600 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                </div>
              </div>
            </div>

            <!-- Results -->
            <div v-else-if="trendyolAIResults" class="space-y-6">
              <!-- Summary -->
              <div class="bg-purple-50 rounded-lg p-4">
                <div class="flex items-center justify-between">
                  <div>
                    <h4 class="text-lg font-semibold text-purple-900">AI Analiz Sonuçları</h4>
                    <p class="text-sm text-purple-700">
                      {{ trendyolAIResults.total_products_found }} ürün bulundu, 
                      {{ trendyolAIResults.similar_products_found }} benzer ürün tespit edildi
                    </p>
                  </div>
                  <div class="text-right">
                    <div class="text-2xl font-bold text-purple-900">
                      %{{ Math.round(trendyolAIResults.similarity_threshold * 100) }}
                    </div>
                    <div class="text-sm text-purple-700">Benzerlik Eşiği</div>
                  </div>
                </div>
                
                <!-- Arama URL'si -->
                <div class="mt-4 p-3 bg-white rounded-lg border border-purple-200">
                  <div class="flex items-center space-x-2 mb-2">
                    <svg class="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    <span class="text-sm font-medium text-purple-800">Arama URL'si:</span>
                  </div>
                  <a 
                    :href="getTrendyolSearchUrl(editingProduct?.title)" 
                    target="_blank"
                    class="text-sm text-blue-600 hover:text-blue-800 hover:underline break-all"
                  >
                    {{ getTrendyolSearchUrl(editingProduct?.title) }}
                  </a>
                </div>
              </div>

              <!-- All Products -->
              <div v-if="trendyolAIResults.all_products && trendyolAIResults.all_products.length > 0">
                <h4 class="text-lg font-semibold text-gray-900 mb-4">Tüm Ürünler ({{ trendyolAIResults.all_products.length }})</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div 
                    v-for="(product, index) in trendyolAIResults.all_products" 
                    :key="`all-${index}`"
                    class="border rounded-lg p-4 hover:shadow-md transition-shadow"
                    :class="{ 
                      'bg-gradient-to-r from-purple-50 to-purple-100 border-purple-300 shadow-purple-100': product.similarity_percentage >= 50,
                      'bg-yellow-50 border-yellow-200': product.similarity_percentage >= 20 && product.similarity_percentage < 50,
                      'border-gray-200': product.similarity_percentage < 20
                    }"
                  >
                    <div class="flex items-start space-x-3">
                      <div class="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                        <img 
                          v-if="product.image_url" 
                          :src="product.image_url" 
                          :alt="product.name"
                          class="w-full h-full object-cover"
                          @error="handleImageError"
                        />
                        <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                        </div>
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-start justify-between">
                          <h5 class="text-sm font-medium text-gray-900 truncate flex-1">{{ product.name }}</h5>
                          <!-- Benzerlik Badge -->
                          <div v-if="product.similarity_percentage > 0" class="ml-2 flex-shrink-0">
                            <span 
                              class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                              :class="{
                                'bg-purple-100 text-purple-800': product.similarity_percentage >= 50,
                                'bg-yellow-100 text-yellow-800': product.similarity_percentage >= 20 && product.similarity_percentage < 50
                              }"
                            >
                              %{{ Math.round(product.similarity_percentage) }} Benzer
                            </span>
                          </div>
                        </div>
                        <p class="text-sm text-gray-500">{{ product.brand }}</p>
                        
                        <!-- Fiyat ve Rating Bilgileri -->
                        <div class="flex items-center space-x-2 mt-1">
                          <span v-if="product.price" class="text-sm font-semibold text-green-600">
                            {{ product.price }}
                          </span>
                          <span v-if="product.rating" class="text-sm text-yellow-600 flex items-center">
                            <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                            </svg>
                            {{ product.rating }}
                          </span>
                        </div>
                        
                        <!-- Benzerlik Oranı ve Progress Bar -->
                        <div class="mt-3" v-if="product.similarity_percentage > 0">
                          <div class="flex items-center justify-between mb-1">
                            <span class="text-xs text-gray-600">Benzerlik Oranı</span>
                            <span class="text-xs font-semibold" :class="{
                              'text-purple-600': product.similarity_percentage >= 50,
                              'text-yellow-600': product.similarity_percentage >= 20 && product.similarity_percentage < 50
                            }">
                              %{{ Math.round(product.similarity_percentage || 0) }}
                            </span>
                          </div>
                          <div class="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              class="h-2 rounded-full transition-all duration-500"
                              :class="{
                                'bg-gradient-to-r from-purple-500 to-purple-600': product.similarity_percentage >= 50,
                                'bg-gradient-to-r from-yellow-400 to-yellow-500': product.similarity_percentage >= 20 && product.similarity_percentage < 50
                              }"
                              :style="{ width: (product.similarity_percentage || 0) + '%' }"
                            ></div>
                          </div>
                        </div>
                        
                        <!-- Action Buttons -->
                        <div class="flex items-center justify-between mt-3">
                          <button 
                            @click="addTrendyolProductToUrls(product)"
                            class="text-xs bg-purple-600 text-white px-3 py-1 rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-1"
                          >
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                            </svg>
                            <span>URL Ekle</span>
                          </button>
                          <a 
                            :href="product.link" 
                            target="_blank"
                            class="text-xs text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                          >
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                            <span>Görüntüle</span>
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- No Results -->
              <div v-else-if="!trendyolAIResults.all_products || trendyolAIResults.all_products.length === 0" class="text-center py-8">
                <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0118 12a7.962 7.962 0 00-3 1.291m-6-1.291a7.962 7.962 0 00-3 1.291" />
                  </svg>
                </div>
                <h3 class="text-lg font-medium text-gray-900 mb-2">Benzer Ürün Bulunamadı</h3>
                <p class="text-gray-600">Bu ürün için Trendyol'da benzer ürün bulunamadı.</p>
              </div>
            </div>

            <!-- Error State -->
            <div v-else-if="trendyolAIError" class="text-center py-8">
              <div class="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg class="w-10 h-10 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 class="text-xl font-semibold text-gray-900 mb-3">AI Analizi Başarısız</h3>
              <p class="text-gray-600 mb-6 max-w-md mx-auto">{{ trendyolAIError }}</p>
              
              <!-- Error Details -->
              <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 max-w-md mx-auto">
                <div class="flex items-start space-x-2">
                  <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div class="text-sm text-red-700">
                    <p class="font-medium">Olası Çözümler:</p>
                    <ul class="mt-1 space-y-1 text-xs">
                      <li>• AI servisinin çalıştığından emin olun</li>
                      <li>• İnternet bağlantınızı kontrol edin</li>
                      <li>• Ürün adını daha spesifik yazın</li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <div class="flex items-center justify-center space-x-3">
                <button 
                  @click="retryTrendyolAI"
                  class="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>Tekrar Dene</span>
                </button>
                <button 
                  @click="closeTrendyolAIModal"
                  class="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Kapat
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete All URLs Confirmation Modal -->
    <div v-if="showDeleteAllUrlsModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeDeleteAllUrlsModal"></div>
        <div class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-md sm:w-full">
          <div class="bg-white px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900">
                Tüm URL'leri Temizle
              </h3>
              <button type="button" @click="closeDeleteAllUrlsModal" class="text-gray-400 hover:text-gray-600">
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
              Tüm ürün URL'lerini silmek istediğinizden emin misiniz? Bu işlem <strong>company_products_urls</strong> tablosundaki tüm kayıtları kalıcı olarak silecektir.
            </p>
            <p class="text-sm text-red-600 font-medium">
              Bu işlem geri alınamaz!
            </p>
          </div>
          <div class="bg-gray-50 px-6 py-4 flex justify-end space-x-3">
            <button type="button" @click="closeDeleteAllUrlsModal" class="btn btn-secondary">
              İptal
            </button>
            <button 
              @click="confirmDeleteAllUrls" 
              :disabled="isDeletingAllUrls"
              class="btn btn-danger"
            >
              <span v-if="isDeletingAllUrls">Siliniyor...</span>
              <span v-else>Tümünü Sil</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import * as XLSX from 'xlsx'

definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

// Import composables
// useCompaniesApi ayrı bir composable, useApi'den değil

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
const companies = ref([])
const productUrls = ref({}) // { companyId: [{ url: '', id?: number }] }
const searchQuery = ref('')
const selectedBrand = ref('')
const selectedProductType = ref('')
const showEditModal = ref(false)
const editingProduct = ref(null)
const isSaving = ref(false)
const showDeleteAllUrlsModal = ref(false)
const isDeletingAllUrls = ref(false)
const isDownloadingUrls = ref(false)

// Trendyol AI Modal
const showTrendyolAIModal = ref(false)
const isTrendyolAILoading = ref(false)
const trendyolAIResults = ref(null)
const trendyolAIError = ref(null)
const currentTrendyolCompanyId = ref(null)

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

  return filtered
})

// Methods
const fetchProducts = async () => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get('/user-products')
    products.value = response.data || []
  } catch (error) {
    console.error('Ürünler yüklenirken hata:', error)
    products.value = []
  }
}

const fetchCompanies = async () => {
  try {
    console.log('fetchCompanies başladı...')
    const companiesApi = useCompaniesApi()
    const response = await companiesApi.list()
    console.log('Companies API response:', response)
    companies.value = response.data || response
    console.log('Companies yüklendi:', companies.value.length, 'firma')
  } catch (error) {
    console.error('Firmalar yüklenirken hata:', error)
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
  // Reset to first page when filtering
}

const filterByAnalysis = () => {
  // Reset to first page when filtering
}

const fetchProductUrls = async (productId) => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get('/products', { query: { product_id: productId } })
    
    // Initialize all companies with empty URLs first
    const urlsByCompany = {}
    companies.value.forEach(company => {
      urlsByCompany[company.id] = [{ url: '', id: null }]
    })
    
    // Then fill in existing URLs
    if (response.success && response.data && Array.isArray(response.data)) {
      // Group URLs by company
      const urlsByCompanyId = {}
      response.data.forEach(urlItem => {
        const companyId = urlItem.company_id
        if (!urlsByCompanyId[companyId]) {
          urlsByCompanyId[companyId] = []
        }
        urlsByCompanyId[companyId].push({
          id: urlItem.id,
          url: urlItem.url
        })
      })
      
      // Update the productUrls with existing URLs
      Object.keys(urlsByCompanyId).forEach(companyId => {
        urlsByCompany[companyId] = urlsByCompanyId[companyId]
      })
    }
    
    productUrls.value = urlsByCompany
  } catch (error) {
    console.error('Ürün URL\'leri yüklenirken hata:', error)
    productUrls.value = {}
  }
}


const openEditModal = async (product) => {
  console.log('openEditModal başladı, product:', product)
  editingProduct.value = product
  showEditModal.value = true
  
  // Companies ve product URLs'i paralel olarak yükle
  await Promise.all([
    fetchCompanies(),
    fetchProductUrls(product.id)
  ])
  
  console.log('Modal açıldı, companies sayısı:', companies.value.length)
  console.log('Modal açıldı, productUrls:', productUrls.value)
  
  // URL'ye sahip firmaları en üstte göster
  sortCompaniesByUrlStatus()
}

const closeEditModal = () => {
  showEditModal.value = false
  editingProduct.value = null
  productUrls.value = {}
}

const sortCompaniesByUrlStatus = () => {
  // URL'ye sahip firmaları en üstte göster
  companies.value.sort((a, b) => {
    const aHasUrl = getUrlsForCompany(a.id).some(urlData => urlData.url && urlData.url.trim())
    const bHasUrl = getUrlsForCompany(b.id).some(urlData => urlData.url && urlData.url.trim())
    
    // URL'ye sahip olanlar önce gelsin
    if (aHasUrl && !bHasUrl) return -1
    if (!aHasUrl && bHasUrl) return 1
    
    // İkisi de aynı durumda ise alfabetik sırala
    return a.company_name.localeCompare(b.company_name)
  })
}

// Delete all URLs modal functions
const openDeleteAllUrlsModal = () => {
  showDeleteAllUrlsModal.value = true
}

const closeDeleteAllUrlsModal = () => {
  showDeleteAllUrlsModal.value = false
}

const getUrlsForCompany = (companyId) => {
  if (!productUrls.value[companyId]) {
    productUrls.value[companyId] = [{ url: '', id: null }]
  }
  return productUrls.value[companyId]
}

const addUrlForCompany = (companyId) => {
  if (!productUrls.value[companyId]) {
    productUrls.value[companyId] = []
  }
  
  // Marketplace'ler için maksimum 10 URL sınırı
  const company = companies.value.find(c => c.id == companyId)
  const maxUrls = company && company.is_marketplace ? 10 : 1
  
  if (productUrls.value[companyId].length >= maxUrls) {
    alert(`Maksimum ${maxUrls} URL ekleyebilirsiniz`)
    return
  }
  
  productUrls.value[companyId].push({ url: '', id: null })
}

const removeUrlForCompany = (companyId, index) => {
  if (productUrls.value[companyId] && productUrls.value[companyId].length > index) {
    productUrls.value[companyId].splice(index, 1)
    // Eğer tüm URL'ler silinirse, en az bir boş URL bırak
    if (productUrls.value[companyId].length === 0) {
      productUrls.value[companyId] = [{ url: '', id: null }]
    }
  }
}


const saveUrls = async () => {
  isSaving.value = true
  try {
    const { $api } = useNuxtApp()
    
    // Önce mevcut URL'leri veritabanından çek
    const existingUrlsResponse = await $api.get('/products', { query: { product_id: editingProduct.value.id } })
    const existingUrlsByCompany = {}
    
    if (existingUrlsResponse.success && existingUrlsResponse.data && Array.isArray(existingUrlsResponse.data)) {
      existingUrlsResponse.data.forEach(urlItem => {
        const companyId = urlItem.company_id.toString()
        if (!existingUrlsByCompany[companyId]) {
          existingUrlsByCompany[companyId] = []
        }
        existingUrlsByCompany[companyId].push({
          id: urlItem.id,
          url: urlItem.url
        })
      })
    }
    
    // Save URLs for each company
    for (const [companyId, urlList] of Object.entries(productUrls.value)) {
      const company = companies.value.find(c => c.id == companyId)
      const validUrls = urlList.filter(urlData => urlData.url && urlData.url.trim())
      
      // Frontend'deki mevcut URL ID'lerini topla
      const frontendUrlIds = new Set(
        urlList
          .filter(urlData => urlData.id)
          .map(urlData => urlData.id)
      )
      
      // Veritabanındaki bu firma için mevcut URL'leri al
      const existingCompanyUrls = existingUrlsByCompany[companyId.toString()] || []
      
      // Silinecek URL'leri bul (veritabanında var ama frontend'de yok)
      const urlsToDelete = existingCompanyUrls.filter(existingUrl => 
        !frontendUrlIds.has(existingUrl.id)
      )
      
      // Silinecek URL'leri sil
      for (const urlToDelete of urlsToDelete) {
        try {
          await $api.products.delete(urlToDelete.id)
        } catch (error) {
          console.error(`URL silme hatası (ID: ${urlToDelete.id}):`, error)
        }
      }
      
      if (validUrls.length === 0) {
        // Tüm URL'ler silindi, devam et
        continue
      }
      
      if (company && company.is_marketplace) {
        // Marketplace için toplu kaydetme
        const urlsToCreate = validUrls.filter(urlData => !urlData.id).map(urlData => urlData.url)
        const urlsToUpdate = validUrls.filter(urlData => urlData.id)
        
        // Yeni URL'leri toplu olarak kaydet
        if (urlsToCreate.length > 0) {
          await $api.products.marketplaceUrls({
            company_id: companyId,
            product_id: editingProduct.value.id,
            urls: urlsToCreate
          })
        }
        
        // Mevcut URL'leri güncelle
        for (const urlData of urlsToUpdate) {
          await $api.products.update(urlData.id, {
            url: urlData.url,
            company_id: companyId,
            product_id: editingProduct.value.id
          })
        }
      } else {
        // Normal firma için tek URL
        const urlData = validUrls[0] || { url: '', id: null }
        
        if (urlData.id) {
          if (urlData.url && urlData.url.trim()) {
            // Update existing URL
            await $api.products.update(urlData.id, {
              url: urlData.url,
              company_id: companyId,
              product_id: editingProduct.value.id
            })
          }
        } else if (urlData.url && urlData.url.trim()) {
          // Create new URL
          await $api.products.create({
            url: urlData.url,
            company_id: companyId,
            product_id: editingProduct.value.id
          })
        }
      }
    }
    
    alert('URL\'ler başarıyla kaydedildi!')
    closeEditModal()
  } catch (error) {
    console.error('URL kaydetme hatası:', error)
    if (error.data && error.data.message) {
      alert(error.data.message)
    } else {
      alert('URL\'ler kaydedilirken bir hata oluştu')
    }
  } finally {
    isSaving.value = false
  }
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
}

// Trendyol AI Functions
const openTrendyolAI = async (companyId) => {
  currentTrendyolCompanyId.value = companyId
  showTrendyolAIModal.value = true
  trendyolAIResults.value = null
  trendyolAIError.value = null
  isTrendyolAILoading.value = true
  
  try {
    // AI similarity finder API'sine istek gönder
    const config = useRuntimeConfig()
    const response = await $fetch(`${config.public.trendyolAiService}/search/quick`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        product_name: editingProduct.value.title,
        max_products: 50,
        similarity_threshold: 0.3
      })
    })
    
    if (response.success) {
      trendyolAIResults.value = response
      isTrendyolAILoading.value = false
    } else {
      trendyolAIError.value = response.message || 'AI analizi başarısız oldu'
      isTrendyolAILoading.value = false
    }
  } catch (error) {
    console.error('Trendyol AI hatası:', error)
    trendyolAIError.value = 'AI servisine bağlanılamadı. Lütfen servisin çalıştığından emin olun.'
    isTrendyolAILoading.value = false
  }
}

const closeTrendyolAIModal = () => {
  showTrendyolAIModal.value = false
  trendyolAIResults.value = null
  trendyolAIError.value = null
  currentTrendyolCompanyId.value = null
}

const retryTrendyolAI = () => {
  if (currentTrendyolCompanyId.value) {
    openTrendyolAI(currentTrendyolCompanyId.value)
  }
}

const getTrendyolSearchUrl = (productName) => {
  if (!productName) return 'https://www.trendyol.com'
  // Python quote_plus ile aynı sonucu vermek için boşlukları + ile değiştir
  const encoded = encodeURIComponent(productName).replace(/%20/g, '+')
  return `https://www.trendyol.com/sr?q=${encoded}`
}

const addTrendyolProductToUrls = (product) => {
  if (!currentTrendyolCompanyId.value) return
  
  // Yeni URL ekle
  addUrlForCompany(currentTrendyolCompanyId.value)
  
  // Son eklenen URL'i güncelle
  const urls = getUrlsForCompany(currentTrendyolCompanyId.value)
  const lastUrl = urls[urls.length - 1]
  if (lastUrl) {
    lastUrl.url = product.link
  }
  
  // Başarı mesajı
  alert(`${product.name} URL'si eklendi!`)
}

const confirmDeleteAllUrls = async () => {
  isDeletingAllUrls.value = true
  try {
    const { $api } = useNuxtApp()
    const response = await $api.products.deleteAll()
    
    if (response.success) {
      alert(`Tüm URL'ler başarıyla silindi! ${response.deleted_count} URL silindi.`)
      closeDeleteAllUrlsModal()
      // Refresh the page to update the data
      await fetchProducts()
    } else {
      alert('Silme işlemi başarısız: ' + response.message)
    }
    
  } catch (error) {
    console.error('Tüm URL\'ler silinirken hata:', error)
    alert('Tüm URL\'ler silinirken bir hata oluştu.')
  } finally {
    isDeletingAllUrls.value = false
  }
}

const downloadUrlsAsExcel = async () => {
  isDownloadingUrls.value = true
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get('/products/export-urls')
    
    if (response.success && response.data) {
      // Create workbook
      const wb = XLSX.utils.book_new()
      
      // Convert data to worksheet
      const ws = XLSX.utils.aoa_to_sheet(response.data)
      
      // Set column widths
      ws['!cols'] = [
        { wch: 20 }, // MPN
        { wch: 30 }, // Firma Adı
        { wch: 50 }  // URL
      ]
      
      // Add worksheet to workbook
      XLSX.utils.book_append_sheet(wb, ws, 'URL\'ler')
      
      // Generate file name
      const fileName = response.filename || 'urun_urls_' + new Date().toISOString().slice(0, 19).replace(/:/g, '-') + '.xlsx'
      
      // Write and download file
      XLSX.writeFile(wb, fileName)
      
      alert(`${response.count || 0} URL başarıyla Excel dosyasına aktarıldı!`)
    } else {
      alert('URL\'ler indirilirken bir hata oluştu: ' + (response.message || 'Bilinmeyen hata'))
    }
  } catch (error) {
    console.error('URL indirme hatası:', error)
    alert('URL\'ler indirilirken bir hata oluştu.')
  } finally {
    isDownloadingUrls.value = false
  }
}

// Watch for filter changes
watch([searchQuery, selectedBrand, selectedProductType], () => {
  // Filters are reactive, no need to do anything
})

// Lifecycle
onMounted(async () => {
  try {
    // Kısa bir delay ile yetki kontrolünün tamamlanmasını bekle
    await new Promise(resolve => setTimeout(resolve, 200))
    isCheckingPermissions.value = false
    
    await fetchProducts()
    await fetchCompanies()
    await fetchProfiles()
  } catch (error) {
    console.error('Page initialization failed:', error)
    isCheckingPermissions.value = false
  }
})
</script>