<template>
  <div class="p-6 overflow-visible">
    <!-- Loading State -->
    <div v-if="isLoadingProducts" class="flex items-center justify-center min-h-[600px]">
      <div class="text-center">
        <!-- Animated Chart Icon -->
        <div class="relative w-24 h-24 mx-auto mb-6">
          <div class="absolute inset-0 flex items-end justify-around space-x-2">
            <div class="w-4 bg-gradient-to-t from-blue-500 to-blue-300 rounded-t-lg animate-bounce" style="animation-delay: 0s; animation-duration: 1s; height: 40%;"></div>
            <div class="w-4 bg-gradient-to-t from-purple-500 to-purple-300 rounded-t-lg animate-bounce" style="animation-delay: 0.2s; animation-duration: 1s; height: 70%;"></div>
            <div class="w-4 bg-gradient-to-t from-pink-500 to-pink-300 rounded-t-lg animate-bounce" style="animation-delay: 0.4s; animation-duration: 1s; height: 55%;"></div>
            <div class="w-4 bg-gradient-to-t from-green-500 to-green-300 rounded-t-lg animate-bounce" style="animation-delay: 0.6s; animation-duration: 1s; height: 85%;"></div>
          </div>
        </div>
        
        <!-- Loading Text -->
        <div class="space-y-3">
          <h3 class="text-xl font-bold text-gray-800">Fiyat Analizi Hazırlanıyor</h3>
          <p class="text-gray-500">Rakip fiyatları karşılaştırılıyor...</p>
          
          <!-- Progress Dots -->
          <div class="flex justify-center space-x-2 mt-4">
            <div class="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style="animation-delay: 0s;"></div>
            <div class="w-2 h-2 bg-purple-500 rounded-full animate-pulse" style="animation-delay: 0.2s;"></div>
            <div class="w-2 h-2 bg-pink-500 rounded-full animate-pulse" style="animation-delay: 0.4s;"></div>
            <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse" style="animation-delay: 0.6s;"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Products State -->
    <div v-else-if="!isLoadingProducts && products.length === 0" class="flex items-center justify-center min-h-[400px]">
      <div class="text-center">
        <div class="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">Henüz ürün bulunmuyor</h3>
        <p class="text-gray-600">Fiyat analizi yapmak için önce ürün eklemeniz gerekiyor.</p>
      </div>
    </div>

    <!-- Enhanced Price Matrix -->
    <div v-else class="overflow-visible">
      <!-- Filter Header with Toggle -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-200 mb-6 overflow-hidden">
        <!-- Filter Header -->
        <div class="p-4 bg-gradient-to-r from-blue-50 to-purple-50 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <button 
                @click="showFilters = !showFilters"
                class="flex items-center space-x-2 text-gray-700 hover:text-gray-900 transition-colors"
              >
                <div class="p-2 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
                  <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                  </svg>
                </div>
          <div>
                  <h3 class="text-base font-semibold text-gray-900">Filtreler</h3>
                  <p class="text-xs text-gray-500">{{ activeFilterCount }} filtre aktif</p>
                </div>
                <svg 
                  class="w-5 h-5 text-gray-400 transition-transform duration-200"
                  :class="{ 'rotate-180': showFilters }"
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
            
            <!-- Active Filters Display -->
            <div v-if="activeFilterCount > 0" class="flex items-center space-x-2">
              <div class="flex flex-wrap gap-2">
                <span v-if="searchQuery" class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  {{ searchQuery }}
                </span>
                <span v-if="selectedBrand" class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                  {{ selectedBrand }}
                </span>
                <span v-if="selectedAnalysis" class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Özel Analiz
                </span>
                <span v-if="showOnlyWithData" class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                  Veri Olanlar
                </span>
                <span v-if="showOnlyInStock" class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Stoğu Olanlar
                </span>
                <span v-if="selectedCompanies.length > 0" class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                  {{ selectedCompanies.length }} Firma
                </span>
                <span v-if="sortByPrice" class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                  Fiyata Göre Sıralı
                </span>
              </div>
              <button 
                @click="clearFilters"
                class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Filtreleri Temizle"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>
        
        <!-- Collapsible Filter Content -->
        <transition
          enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="max-h-0 opacity-0"
          enter-to-class="max-h-[500px] opacity-100"
          leave-active-class="transition-all duration-200 ease-in"
          leave-from-class="max-h-[500px] opacity-100"
          leave-to-class="max-h-0 opacity-0"
        >
          <div v-show="showFilters" class="overflow-hidden">
            <div class="p-6 space-y-6">
              <!-- Search and Quick Filters -->
              <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <!-- Search -->
                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    <svg class="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    Arama
                  </label>
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Ürün adı veya MPN ile ara..."
                      class="w-full border border-gray-300 rounded-xl shadow-sm py-2.5 pl-10 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
              <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
                    <button 
                      v-if="searchQuery"
                      @click="searchQuery = ''"
                      class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
            </div>
          </div>
                
                <!-- Brand -->
          <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    <svg class="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                    </svg>
                    Marka
                  </label>
            <select 
              v-model="selectedBrand" 
                    class="w-full border border-gray-300 rounded-xl shadow-sm py-2.5 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            >
              <option value="">Tüm Markalar</option>
              <option v-for="brand in brands" :key="brand" :value="brand">{{ brand }}</option>
            </select>
          </div>
                
                <!-- Custom Profile -->
          <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    <svg class="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    Özel Analiz
                  </label>
            <select 
              v-model="selectedAnalysis" 
              @change="filterByAnalysis"
                    class="w-full border border-gray-300 rounded-xl shadow-sm py-2.5 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            >
              <option value="">Tüm Analizler</option>
              <option v-for="profile in profiles" :key="profile.id" :value="profile.id">
                {{ profile.name }}
              </option>
            </select>
          </div>
        </div>
              
              <!-- Advanced Filters -->
              <div class="pt-4 border-t border-gray-200">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <!-- Company Filter -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      <svg class="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                      Firma Seçimi
                    </label>
                    <div class="border border-gray-300 rounded-xl p-3 max-h-[200px] overflow-y-auto bg-gray-50">
                      <div class="space-y-2">
                        <label 
                          v-for="company in companies" 
                          :key="company.id"
                          class="flex items-center space-x-2 p-2 hover:bg-white rounded-lg cursor-pointer transition-colors"
                        >
                          <input 
                            type="checkbox"
                            :value="company.id"
                            v-model="selectedCompanies"
                            class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <span class="text-sm text-gray-700 flex-1">{{ company.name }}</span>
                          <span v-if="company.isMarketplace" class="flex-shrink-0 w-2 h-2 bg-green-500 rounded-full" title="Marketplace"></span>
                        </label>
          </div>
        </div>
      </div>

                  <!-- Options -->
                  <div class="md:col-span-2">
                    <label class="block text-sm font-medium text-gray-700 mb-3">
                      <svg class="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                      </svg>
                      Görünüm Seçenekleri
                    </label>
                    <div class="space-y-3">
                      <label class="flex items-center space-x-3 p-3 bg-white border border-gray-200 rounded-xl hover:bg-blue-50 hover:border-blue-300 cursor-pointer transition-all">
                        <input 
                          v-model="showOnlyWithData" 
                          type="checkbox"
                          class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <div class="flex-1">
                          <span class="text-sm font-medium text-gray-900">Sadece veri olan ürünler</span>
                          <p class="text-xs text-gray-500 mt-0.5">En az 1 firmada fiyat verisi olan ürünleri göster</p>
                        </div>
                      </label>
                      
                      <label class="flex items-center space-x-3 p-3 bg-white border border-gray-200 rounded-xl hover:bg-green-50 hover:border-green-300 cursor-pointer transition-all">
                        <input 
                          v-model="showOnlyInStock" 
                          type="checkbox"
                          class="w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-green-500"
                        />
                        <div class="flex-1">
                          <span class="text-sm font-medium text-gray-900">Sadece stoğu olan ürünler</span>
                          <p class="text-xs text-gray-500 mt-0.5">Stok durumu "in stock" olan ürünleri göster</p>
                        </div>
                      </label>
                      
                      <label class="flex items-center space-x-3 p-3 bg-white border border-gray-200 rounded-xl hover:bg-purple-50 hover:border-purple-300 cursor-pointer transition-all">
                        <input 
                          v-model="sortByPrice" 
                          type="checkbox"
                          class="w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                        />
                        <div class="flex-1">
                          <span class="text-sm font-medium text-gray-900">Fiyata göre sırala</span>
                          <p class="text-xs text-gray-500 mt-0.5">Her ürün için firmaları fiyata göre artan sırada göster</p>
                        </div>
                      </label>
                      
                      <div class="flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl border border-gray-200">
                        <div class="flex items-center space-x-3">
                          <div class="p-2 bg-white rounded-lg shadow-sm">
                            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          </div>
                          <div>
                            <p class="text-sm font-medium text-gray-700">{{ filteredProductCount }} ürün gösteriliyor</p>
                            <p class="text-xs text-gray-500">{{ companies.length }} firmadan {{ filteredCompanies.length }} firma seçili</p>
                          </div>
                        </div>
                        <button 
                          @click="clearFilters"
                          class="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-lg shadow-sm hover:shadow-md transition-all duration-200"
                        >
                          <svg class="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                          Sıfırla
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </div>

      <div class="bg-white rounded-2xl shadow-lg border border-gray-200 [overflow:visible_!important]">
        <!-- Table Header with Scroll Indicator -->
        <div class="bg-gradient-to-r from-gray-50 to-blue-50 border-b border-gray-200 p-4">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">Fiyat Analiz</h3>
            <div class="flex items-center space-x-4 text-sm text-gray-600">
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>Marketplace</span>
              </div>
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span>Normal Firma</span>
              </div>
              <div class="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full">
                ← Kaydırarak tüm firmaları görün
              </div>
            </div>
          </div>
        </div>

        <div class="overflow-x-auto overflow-y-visible">
          <!-- Fiyata Göre Sıralı Görünüm -->
          <table v-if="sortByPrice" class="w-full overflow-visible" @click="closeAllPopups">
            <thead class="bg-gray-50 border-b border-gray-200 overflow-visible">
              <tr class="overflow-visible">
                <th class="px-8 py-6 text-left text-sm font-semibold text-gray-900 w-[45%]">
                  <div class="flex items-center space-x-3">
                    <div class="p-2 bg-blue-100 rounded-lg">
                      <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                      </svg>
                    </div>
                    <span>Ürünler</span>
                  </div>
                </th>
                <th class="px-6 py-6 text-left text-sm font-semibold text-gray-900 w-[55%]">
                  <div class="flex items-center space-x-3">
                    <div class="p-2 bg-purple-100 rounded-lg">
                      <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                      </svg>
                    </div>
                    <span>Firmalar ve Fiyatlar (Artan Sırada)</span>
                  </div>
                </th>
              </tr>
            </thead>
            
            <tbody class="divide-y divide-gray-100 overflow-visible">
              <tr v-for="product in displayedProducts" :key="product.id" class="group overflow-visible">
                <!-- Ürün Bilgisi -->
                <td class="px-3 py-3 bg-white overflow-visible">
                  <div class="relative p-3 rounded-xl border-2 border-gray-200 bg-gray-50 transition-all duration-200 hover:shadow-md overflow-visible flex-shrink-0 w-[280px]">
                    <div class="flex items-center justify-between">
                      <div class="flex items-center space-x-2 flex-1 min-w-0">
                        <div class="relative flex-shrink-0">
                          <a 
                            :href="product.link" 
                            target="_blank" 
                            class="block transition-transform hover:scale-105"
                            title="Ürünü görüntüle"
                          >
                            <img :src="product.image" :alt="product.name" class="w-12 h-12 rounded-lg object-cover border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                          </a>
                          <div 
                            v-if="product.availability"
                            :class="[
                              'absolute -top-1 -right-1 px-1 py-0.5 rounded-full text-[8px] font-bold shadow-md border-2 border-white',
                              product.availability.toLowerCase() === 'in stock' 
                                ? 'bg-green-500 text-white' 
                                : 'bg-red-500 text-white'
                            ]"
                            :title="product.availability.toLowerCase() === 'in stock' ? 'Stokta Var' : 'Stokta Yok'"
                          >
                            {{ product.availability.toLowerCase() === 'in stock' ? '✓' : '✗' }}
                          </div>
                        </div>
                        <div class="min-w-0 flex-1">
                          <h3 
                            :class="[
                              'font-medium text-gray-900 text-sm cursor-pointer hover:text-blue-600 transition-colors',
                              !expandedProducts.has(product.id) ? 'truncate' : ''
                            ]"
                            @click="toggleProductName(product.id)"
                            :title="product.name"
                          >
                            {{ product.name }}
                          </h3>
                          <p class="text-xs text-gray-500 mb-1">{{ product.brand }}</p>
                          <div>
                            <div v-if="product.myPrice > 0" class="text-lg font-bold text-gray-900">
                              {{ product.myPrice.toLocaleString() }} ₺
                            </div>
                            <div v-else class="text-xs text-red-500 font-medium">
                              Fiyat Girilmemiş
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <!-- Action Buttons -->
                      <div class="flex flex-col space-y-1 ml-2 flex-shrink-0">
                        <!-- Hızlı Tara Butonu -->
                        <button
                          @click.stop="quickScanProduct(product.id)"
                          :disabled="isQuickScanning[product.id]"
                          class="p-1 rounded-full bg-blue-100 hover:bg-blue-200 disabled:bg-blue-50 transition-colors"
                          :title="'Bu ürün için tüm URL\'leri hızlı tara'"
                        >
                          <svg v-if="!isQuickScanning[product.id]" class="w-3 h-3 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                          <svg v-else class="w-3 h-3 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                        </button>
                        
                        <!-- Ürün Link Butonu -->
                        <a 
                          :href="product.link" 
                          target="_blank"
                          class="p-1 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
                          title="Ürünü Görüntüle"
                        >
                          <svg class="w-3 h-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                          </svg>
                        </a>
                      </div>
                    </div>
                  </div>
                </td>
                
                <!-- Firma Fiyat Listesi -->
                <td class="px-3 py-3 bg-white overflow-visible">
                  <div 
                    v-if="getProductCompanyPrices(product.id).length > 0" 
                    class="flex gap-3 overflow-x-auto overflow-y-visible pb-2 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100 p-3"
                  >
                    <div 
                      v-for="(item, index) in getProductCompanyPrices(product.id)" 
                      :key="`${product.id}-${item.company.id}`"
                      class="relative p-3 rounded-xl border-2 transition-all duration-200 hover:shadow-md flex-shrink-0 w-[280px] overflow-visible"
                      :class="item.hasPrice ? (item.price > product.myPrice ? 'bg-green-50 border-green-200' : item.price < product.myPrice ? 'bg-red-50 border-red-200' : 'bg-gray-50 border-gray-200') : 'bg-blue-50 border-blue-200'"
                    >
                      <!-- Sıra Numarası Badge -->
                      <div class="absolute -top-2 -left-2 w-6 h-6 rounded-full bg-purple-600 text-white text-xs font-bold flex items-center justify-center shadow-md">
                        {{ index + 1 }}
                      </div>
                      
                      <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-2 flex-1 min-w-0">
                          <img 
                            :src="item.company.logo" 
                            :alt="item.company.name" 
                            class="w-8 h-8 rounded-lg object-cover border border-gray-200 flex-shrink-0"
                          >
                          <div class="min-w-0 flex-1">
                            <div class="flex items-center space-x-2">
                              <div class="font-medium text-sm text-gray-900 truncate">
                                {{ item.company.name }}
                              </div>
                              <!-- Stok Durumu Badge -->
                              <div 
                                v-if="item.priceInfo?.availability !== null && item.priceInfo?.availability !== undefined"
                                :class="[
                                  'px-1.5 py-0.5 rounded-full text-[9px] font-bold border',
                                  item.priceInfo.availability 
                                    ? 'bg-green-100 text-green-700 border-green-300' 
                                    : 'bg-red-100 text-red-700 border-red-300'
                                ]"
                                :title="item.priceInfo.availability ? 'Stokta Var' : 'Stokta Yok'"
                              >
                                {{ item.priceInfo.availability ? '✓' : '✗' }}
                              </div>
                            </div>
                            <div v-if="item.hasPrice" class="text-lg font-bold" :class="getPriceColor(product.myPrice, item.price)">
                              {{ item.price.toLocaleString() }} ₺
                            </div>
                            <div v-else class="text-xs text-blue-600 font-medium">
                              Link var, fiyat yok.
                            </div>
                            <div v-if="item.hasPrice && getPriceDifference(product.myPrice, item.price)" class="text-xs font-medium" :class="getPriceColor(product.myPrice, item.price)">
                              {{ getPriceDifference(product.myPrice, item.price) > 0 ? '+' : '' }}{{ getPriceDifference(product.myPrice, item.price) }}%
                              <span class="text-[10px] ml-1" :class="getLastUpdateTextColor(product.myPrice, item.price)">{{ formatLastUpdateShort(getProductInfo(product.id, item.company.id).lastUpdate) }}</span>
                            </div>
                          </div>
                        </div>
                        
                        <!-- Action Buttons -->
                        <div class="flex flex-col space-y-1 ml-2 flex-shrink-0">
                          <!-- Marketplace Sellers -->
                          <button 
                            v-if="item.company.isMarketplace && item.priceInfo?.sellerCount"
                            @click.stop="openPopup('sellers', product.id, item.company.id, $event)"
                            class="p-1 rounded-full bg-slate-100 hover:bg-slate-200 transition-colors"
                            title="Satıcıları Gör"
                          >
                            <svg class="w-3 h-3 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                            </svg>
                          </button>
                          
                          <!-- Info -->
                          <button 
                            @click.stop="openPopup('info', product.id, item.company.id, $event)"
                            class="p-1 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
                            :class="{ 'bg-gray-200': isPopupOpen('info', product.id, item.company.id) }"
                            title="Detaylı Bilgi"
                          >
                            <svg class="w-3 h-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          </button>
                          
                          <!-- Link -->
                          <button 
                            @click.stop="openPopup('link', product.id, item.company.id, $event)"
                            class="p-1 rounded-full bg-blue-100 hover:bg-blue-200 transition-colors"
                            :class="{ 'bg-blue-200': isPopupOpen('link', product.id, item.company.id) }"
                            title="Bağlantılar"
                          >
                            <svg class="w-3 h-3 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                            </svg>
                          </button>
                          
                          <!-- All Prices -->
                          <button 
                            v-if="getProductPrice(product.id, item.company.id) && getProductPrice(product.id, item.company.id).all_prices && getProductPrice(product.id, item.company.id).all_prices.length > 1"
                            @click.stop="openPopup('prices', product.id, item.company.id, $event)"
                            class="relative p-1 rounded-full bg-green-100 hover:bg-green-200 transition-colors"
                            :class="{ 'bg-green-200': isPopupOpen('prices', product.id, item.company.id) }"
                            title="Tüm Fiyatlar"
                          >
                            <svg class="w-3 h-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <!-- Badge -->
                            <span class="absolute -top-0.5 -right-0.5 bg-green-600 text-white text-[8px] font-bold rounded-full w-3.5 h-3.5 flex items-center justify-center">
                              {{ getProductPrice(product.id, item.company.id).all_prices.length }}
                            </span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-center py-8 text-gray-400">
                    <svg class="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                    </svg>
                    <p class="text-sm">Bu ürün için veri bulunmuyor</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          
          <!-- Normal Matris Görünüm -->
          <table v-else class="w-full" @click="closePopup">
            <!-- Enhanced Header Row -->
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-6 py-6 text-left text-sm font-semibold text-gray-900 min-w-[250px] sticky left-0 bg-gray-50 z-[5] border-r border-gray-200">
                  <div class="flex items-center space-x-3">
                    <div class="p-2 bg-blue-100 rounded-lg">
                      <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                      </svg>
                    </div>
                    <span>Ürünler</span>
                  </div>
                </th>
                <th 
                  v-for="company in filteredCompanies" 
                  :key="company.id" 
                  class="px-2 py-2 text-center text-sm font-semibold text-gray-900 min-w-[180px] hover:bg-gray-100 transition-colors cursor-pointer"
                  @click="openCompanyUrl(company.url)"
                  :title="company.url ? 'Firma sitesine git' : ''"
                >
                  <div class="flex flex-col items-center space-y-3">
                    <div class="relative">
                      <img :src="company.logo" :alt="company.name" class="w-12 h-12 rounded-xl object-cover shadow-sm border-2 border-white">
                      <div 
                        class="absolute -top-1 -right-1 w-4 h-4 rounded-full border-2 border-white"
                        :class="company.isMarketplace ? 'bg-green-500' : 'bg-blue-500'"
                      ></div>
                    </div>
                    <div class="text-center">
                      <div class="font-medium text-gray-900 text-sm">{{ company.name }}</div>
                     
                    </div>
                  </div>
                </th>
              </tr>
            </thead>
            
            <!-- Enhanced Data Rows -->
            <tbody class="divide-y divide-gray-100 overflow-visible">
              <tr v-for="product in displayedProducts" :key="product.id" class="group overflow-visible">
                <!-- Enhanced Product Column -->
                <td class="px-6 py-6 sticky left-0 bg-white z-[5] border-r border-gray-200">
                  <div class="flex items-center space-x-4">
                    <div class="relative">
                      <a 
                        :href="product.link" 
                        target="_blank" 
                        class="block transition-transform hover:scale-105"
                        title="Ürünü görüntüle"
                      >
                        <img :src="product.image" :alt="product.name" class="w-16 h-16 rounded-xl object-cover shadow-sm border-2 border-gray-100 hover:shadow-md transition-shadow">
                      </a>
                      <!-- Stock Badge -->
                      <div 
                        v-if="product.availability"
                        :class="[
                          'absolute -top-1 -right-1 px-2 py-0.5 rounded-full text-[10px] font-bold shadow-lg border-2 border-white',
                          product.availability.toLowerCase() === 'in stock' 
                            ? 'bg-green-500 text-white' 
                            : 'bg-red-500 text-white'
                        ]"
                        :title="product.availability.toLowerCase() === 'in stock' ? 'Stokta Var' : 'Stokta Yok'"
                      >
                        {{ product.availability.toLowerCase() === 'in stock' ? '✓' : '✗' }}
                      </div>
                    </div>
                    <div class="flex-1">
                      <h3 
                        class="font-semibold text-gray-900 text-sm cursor-pointer hover:text-blue-600 transition-colors"
                        @click="product.name.length > 60 ? toggleProductName(product.id) : null"
                        :title="product.name.length > 60 ? (expandedProducts.has(product.id) ? 'Kısaltmak için tıklayın' : 'Tamamını görmek için tıklayın') : ''"
                      >
                        {{ product.name.length > 60 && !expandedProducts.has(product.id) ? product.name.substring(0, 60) + '...' : product.name }}
                      </h3>
                      <p class="text-sm text-gray-500">{{ product.brand }}</p>
                      <div class="mt-2">
                        <div v-if="product.myPrice > 0" class="text-lg font-bold text-gray-900">
                          {{ product.myPrice.toLocaleString() }} ₺
                        </div>
                        <div v-else class="text-lg font-bold text-red-500">
                          Fiyat Girilmemiş
                        </div>
                      </div>
                    </div>
                  </div>
                </td>
                
                
                <!-- Enhanced Price Columns -->
                <td 
                  v-for="company in filteredCompanies" 
                  :key="`${product.id}-${company.id}`" 
                  class="px-0 py-0 text-center overflow-visible relative"
                  :style="{ 
                    height: 'inherit', 
                    zIndex: (isInfoPopupOpen(product.id, company.id) || isLinkInfoOpen(product.id, company.id)) ? 1000 : 'auto' 
                  }"
                >
                  <!-- Veri Var -->
                  <div 
                    v-if="getProductPrice(product.id, company.id)" 
                    class="flex absolute inset-0"
                    :style="{ backgroundColor: getPriceBgColor(product.myPrice, company.isMarketplace ? getProductPrice(product.id, company.id).lowestPrice : getProductPrice(product.id, company.id).price) }"
                  >
                    <!-- Main Content Area (80% width) -->
                    <div class="w-[80%] flex items-center justify-center">
                      <div class="space-y-3">
                        <!-- Marketplace Price with Enhanced Details -->
                        <div v-if="company.isMarketplace" class="flex flex-col items-center space-y-3">
                          <div class="relative">
                            <div v-if="getProductPrice(product.id, company.id).lowestPrice">
                              <div class="flex items-center justify-center space-x-2">
                              <div class="text-2xl font-bold" :class="getPriceColor(product.myPrice, getProductPrice(product.id, company.id).lowestPrice)">
                                {{ getProductPrice(product.id, company.id).lowestPrice.toLocaleString() }} ₺
                                </div>
                                <div v-if="getProductPrice(product.id, company.id).has_cheaper_price && getProductPrice(product.id, company.id).cheapest_price" 
                                     class="flex items-center space-x-1 px-2 py-0.5 bg-orange-100 rounded-full">
                                  <svg class="w-3 h-3 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                  </svg>
                                  <span class="text-[10px] font-bold text-orange-600">{{ getProductPrice(product.id, company.id).cheapest_price.toLocaleString() }} ₺</span>
                                </div>
                              </div>
                              <div class="flex items-center justify-center space-x-2 mt-1">
                                <div v-if="getPriceDifference(product.myPrice, getProductPrice(product.id, company.id).lowestPrice)" class="text-xs font-medium" :class="getPriceColor(product.myPrice, getProductPrice(product.id, company.id).lowestPrice)">
                                  {{ getPriceDifference(product.myPrice, getProductPrice(product.id, company.id).lowestPrice) > 0 ? '+' : '' }}{{ getPriceDifference(product.myPrice, getProductPrice(product.id, company.id).lowestPrice) }}%
                                  <span class="text-[10px] ml-1" :class="getLastUpdateTextColor(product.myPrice, getProductPrice(product.id, company.id).lowestPrice)">{{ formatLastUpdateShort(getProductInfo(product.id, company.id).lastUpdate) }}</span>
                                </div>
                                <!-- Stok Durumu Badge -->
                                <div 
                                  v-if="getProductPrice(product.id, company.id).availability !== null && getProductPrice(product.id, company.id).availability !== undefined"
                                  :class="[
                                    'px-1.5 py-0.5 rounded-full text-[9px] font-bold border',
                                    getProductPrice(product.id, company.id).availability 
                                      ? 'bg-green-100 text-green-700 border-green-300' 
                                      : 'bg-red-100 text-red-700 border-red-300'
                                  ]"
                                  :title="getProductPrice(product.id, company.id).availability ? 'Stokta Var' : 'Stokta Yok'"
                                >
                                  {{ getProductPrice(product.id, company.id).availability ? '✓' : '✗' }}
                                </div>
                              </div>
                            </div>
                            <div v-else class="text-center">
                              <span class="text-sm text-gray-400 font-medium">—</span>
                            </div>
                          </div>
                        </div>
                    
                        <!-- Normal Company Price -->
                        <div v-else class="flex flex-col items-center space-y-2">
                          <div v-if="getProductPrice(product.id, company.id).price">
                            <div class="flex items-center justify-center space-x-2">
                            <div class="text-2xl font-bold" :class="getPriceColor(product.myPrice, getProductPrice(product.id, company.id).price)">
                              {{ getProductPrice(product.id, company.id).price.toLocaleString() }} ₺
                              </div>
                              <div v-if="getProductPrice(product.id, company.id).has_cheaper_price && getProductPrice(product.id, company.id).cheapest_price" 
                                   class="flex items-center space-x-1 px-2 py-0.5 bg-orange-100 rounded-full">
                                <svg class="w-3 h-3 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                </svg>
                                <span class="text-[10px] font-bold text-orange-600">{{ getProductPrice(product.id, company.id).cheapest_price.toLocaleString() }} ₺</span>
                              </div>
                            </div>
                            <div class="flex items-center justify-center space-x-2 mt-1">
                              <div v-if="getPriceDifference(product.myPrice, getProductPrice(product.id, company.id).price)" class="text-xs font-medium" :class="getPriceColor(product.myPrice, getProductPrice(product.id, company.id).price)">
                                {{ getPriceDifference(product.myPrice, getProductPrice(product.id, company.id).price) > 0 ? '+' : '' }}{{ getPriceDifference(product.myPrice, getProductPrice(product.id, company.id).price) }}%
                                <span class="text-[10px] ml-1" :class="getLastUpdateTextColor(product.myPrice, getProductPrice(product.id, company.id).price)">{{ formatLastUpdateShort(getProductInfo(product.id, company.id).lastUpdate) }}</span>
                              </div>
                              <!-- Stok Durumu Badge -->
                              <div 
                                v-if="getProductPrice(product.id, company.id).availability !== null && getProductPrice(product.id, company.id).availability !== undefined"
                                :class="[
                                  'px-1.5 py-0.5 rounded-full text-[9px] font-bold border',
                                  getProductPrice(product.id, company.id).availability 
                                    ? 'bg-green-100 text-green-700 border-green-300' 
                                    : 'bg-red-100 text-red-700 border-red-300'
                                ]"
                                :title="getProductPrice(product.id, company.id).availability ? 'Stokta Var' : 'Stokta Yok'"
                              >
                                {{ getProductPrice(product.id, company.id).availability ? '✓' : '✗' }}
                              </div>
                            </div>
                          </div>
                          <div v-else class="text-center">
                            <span class="text-sm text-gray-400 font-medium">—</span>
                          </div>
                        </div>
                    </div>
                  </div>
                  
                    <!-- Link Area (20% width) -->
                    <div class="w-[20%] flex flex-col items-center justify-center border-l border-gray-100 ml-3 relative bg-white/80 backdrop-blur-sm">
                    <!-- Icons Container -->
                    <div class="flex flex-col items-center space-y-2">
                      <!-- Marketplace Sellers Button (only for marketplace) -->
                      <button 
                        v-if="company.isMarketplace && getProductPrice(product.id, company.id).sellerCount"
                        @click.stop="openPopup('sellers', product.id, company.id, $event)"
                        class="group/sellers relative p-1.5 rounded-full bg-slate-100 hover:bg-slate-200 transition-colors duration-200"
                        title="Satıcıları Gör"
                      >
                        <svg class="w-3.5 h-3.5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                        <!-- Badge -->
                        <span class="absolute -top-0.5 -right-0.5 bg-slate-600 text-white text-[8px] font-bold rounded-full w-3.5 h-3.5 flex items-center justify-center">
                          {{ getProductPrice(product.id, company.id).sellerCount }}
                        </span>
                      </button>
                      
                      <!-- Info Icon -->
                      <button 
                        @click.stop="openPopup('info', product.id, company.id, $event)"
                        class="group/info relative p-1.5 rounded-full bg-gray-100 group-hover/info:bg-gray-200 transition-colors duration-200"
                        :class="{ 'bg-gray-200': isPopupOpen('info', product.id, company.id) }"
                        title="Detaylı Bilgi"
                      >
                        <svg class="w-3 h-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </button>

                      <!-- Link Icon -->
                      <button 
                        @click.stop="openPopup('link', product.id, company.id, $event)"
                        class="group/link relative p-1.5 rounded-full hover:bg-blue-50 transition-all duration-200"
                        :class="{ 'bg-blue-50': isPopupOpen('link', product.id, company.id) }"
                        title="Bağlantılar"
                      >
                        <svg class="w-3.5 h-3.5 text-blue-600 group-hover/link:text-blue-700 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                        </svg>
                      </button>

                      <!-- All Prices Icon -->
                      <button 
                        v-if="getProductPrice(product.id, company.id) && getProductPrice(product.id, company.id).all_prices && getProductPrice(product.id, company.id).all_prices.length > 1"
                        @click.stop="openPopup('prices', product.id, company.id, $event)"
                        class="group/prices relative p-1.5 rounded-full hover:bg-green-50 transition-all duration-200"
                        :class="{ 'bg-green-50': isPopupOpen('prices', product.id, company.id) }"
                        title="Tüm Fiyatlar"
                      >
                        <svg class="w-3.5 h-3.5 text-green-600 group-hover/prices:text-green-700 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <!-- Badge -->
                        <span class="absolute -top-0.5 -right-0.5 bg-green-600 text-white text-[8px] font-bold rounded-full w-3.5 h-3.5 flex items-center justify-center">
                          {{ getProductPrice(product.id, company.id).all_prices.length }}
                        </span>
                      </button>
                    </div>
                    </div>
                  </div>
                  
                  <!-- Fiyat Yok ama Link Var -->
                  <div 
                    v-else-if="getProductLinks(product.id, company.id).length > 0" 
                    class="flex absolute inset-0"
                    style="background-color: #f0fbfe;"
                  >
                    <!-- Boş Alan (80% width) -->
                    <div class="w-[80%] flex items-center justify-center">
                      <div class="text-center">
                        <span class="text-sm text-gray-400 font-medium">—</span>
                      </div>
                    </div>
                    
                    <!-- Link Area (20% width) -->
                    <div class="w-[20%] flex flex-col items-center justify-center border-l border-gray-100 ml-3 relative bg-white/80 backdrop-blur-sm">
                      <div class="flex flex-col items-center space-y-2">
                        <!-- Info Icon -->
                        <button 
                          @click.stop="openPopup('info', product.id, company.id, $event)"
                          class="group/info relative p-1.5 rounded-full bg-gray-100 group-hover/info:bg-gray-200 transition-colors duration-200"
                          :class="{ 'bg-gray-200': isPopupOpen('info', product.id, company.id) }"
                          title="Detaylı Bilgi"
                        >
                          <svg class="w-3 h-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                        </button>
                        
                        <!-- Link Icon -->
                        <button 
                          @click.stop="openPopup('link', product.id, company.id, $event)"
                          class="group/link relative p-1.5 rounded-full hover:bg-blue-50 transition-all duration-200"
                          :class="{ 'bg-blue-50': isPopupOpen('link', product.id, company.id) }"
                          title="Bağlantılar"
                        >
                          <svg class="w-3.5 h-3.5 text-blue-600 group-hover/link:text-blue-700 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                          </svg>
                        </button>
                    </div>
                    </div>
                  </div>
                  
                  <!-- Hiçbir Veri Yok -->
                  <div v-else class="flex absolute inset-0 bg-gray-50/30">
                    <div class="w-full flex items-center justify-center group/empty">
                      <div class="relative">
                        <!-- Minimal Dot -->
                        <div class="w-1.5 h-1.5 bg-gray-300 rounded-full group-hover/empty:bg-gray-400 transition-colors"></div>
                        
                        <!-- Hover Tooltip -->
                        <div class="absolute left-1/2 -translate-x-1/2 top-full mt-2 opacity-0 group-hover/empty:opacity-100 transition-opacity pointer-events-none">
                          <div class="bg-gray-800 text-white text-[10px] px-2 py-1 rounded whitespace-nowrap">
                            Veri yok
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Load More Button -->
        <div v-if="hasMoreProducts" class="bg-gray-50 px-6 py-4 border-t border-gray-200">
          <div class="flex justify-center">
            <button 
              @click="loadMoreProducts"
              :disabled="isLoadingMore"
              class="btn btn-secondary flex items-center space-x-2"
            >
              <svg v-if="isLoadingMore" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
              <span>{{ isLoadingMore ? 'Yükleniyor...' : 'Daha Fazla Yükle' }}</span>
            </button>
          </div>
          <p class="text-center text-sm text-gray-500 mt-2">
            {{ displayedProducts.length }} / {{ products.length }} ürün gösteriliyor
          </p>
        </div>
      </div>
  </div>

    <!-- Click Outside to Close (Background Overlay) -->
    <div 
      v-if="activePopup.isOpen" 
      class="fixed inset-0 z-[9998] bg-black/30 backdrop-blur-[2px] transition-all duration-300" 
      @click="closePopup"
    ></div>

    <!-- Unified Popup -->
    <div 
      v-if="activePopup.isOpen" 
      class="fixed z-[9999] bg-white border border-gray-200 rounded-xl shadow-2xl overflow-hidden transition-all duration-200"
      :style="activePopup.position"
      @click.stop
    >
      <!-- Info Popup Content -->
      <div v-if="activePopup.type === 'info'" class="p-4 min-w-[320px] max-w-[450px]">
        <div class="space-y-3">
          <div class="border-b border-gray-100 pb-3">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center space-x-2">
                <div class="p-2 bg-blue-100 rounded-lg">
                  <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h4 class="text-sm font-bold text-gray-900">Ürün Bilgileri</h4>
              </div>
              <button 
                @click.stop="closePopup"
                class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <svg class="w-4 h-4 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <!-- Ürün ve Firma Bilgisi -->
            <div class="space-y-1.5 pl-2">
              <div class="flex items-start space-x-2">
                <svg class="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
                <div class="flex-1">
                  <p class="text-xs font-medium text-gray-900 line-clamp-2">{{ products.find(p => p.id === activePopup.productId)?.name }}</p>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                <p class="text-xs font-medium text-blue-600">{{ companies.find(c => c.id === activePopup.companyId)?.name }}</p>
              </div>
            </div>
          </div>
          
          <div class="space-y-2">
            <div class="flex items-center justify-between text-xs py-2 px-3 bg-gray-50 rounded-lg">
              <span class="text-gray-600 font-medium">Son güncelleme:</span>
              <span class="font-semibold text-gray-900">{{ getProductInfo(activePopup.productId, activePopup.companyId).lastUpdate }}</span>
            </div>
          </div>
          
          <div class="border-t border-gray-100 pt-3">
            <div class="flex items-center space-x-2 mb-2">
              <svg class="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              </svg>
              <h5 class="text-sm font-bold text-gray-900">Fiyat Geçmişi</h5>
            </div>
            
            <!-- Loading State -->
            <div v-if="getProductInfo(activePopup.productId, activePopup.companyId).loading" class="flex items-center justify-center py-8">
              <svg class="animate-spin h-6 w-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            
            <!-- Empty State -->
            <div v-else-if="getProductInfo(activePopup.productId, activePopup.companyId).priceHistory.length === 0" class="text-center py-6">
              <svg class="w-10 h-10 mx-auto text-gray-300 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span class="text-xs text-gray-400">Fiyat geçmişi bulunamadı</span>
            </div>
            
            <!-- Data -->
            <div v-else>
              <!-- Price Comparison Chart -->
              <div class="mb-3">
                <PriceComparisonChart 
                  :price-history="getProductInfo(activePopup.productId, activePopup.companyId).priceHistory"
                  :my-price="products.find(p => p.id === activePopup.productId)?.myPrice"
                  :competitor-price="getProductPrice(activePopup.productId, activePopup.companyId)?.price || getProductPrice(activePopup.productId, activePopup.companyId)?.lowestPrice"
                />
              </div>
              
              <!-- Price History List -->
              <div class="space-y-1.5 max-h-40 overflow-y-auto pr-2">
                <div 
                  v-for="(history, index) in getProductInfo(activePopup.productId, activePopup.companyId).priceHistory" 
                  :key="index"
                  class="flex items-center justify-between text-xs py-2 px-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <span class="text-gray-600">{{ history.date }}</span>
                  <span class="font-bold text-gray-900">{{ history.price.toLocaleString() }} ₺</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Link Popup Content -->
      <div v-else-if="activePopup.type === 'link'" class="p-4 min-w-[300px] max-w-[400px]">
        <div class="space-y-3">
          <div class="border-b border-gray-100 pb-3">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center space-x-2">
                <div class="p-2 bg-blue-100 rounded-lg">
                  <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                </div>
                <h4 class="text-sm font-bold text-gray-900">Bağlantılar</h4>
              </div>
              <button 
                @click.stop="closePopup"
                class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <svg class="w-4 h-4 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <!-- Ürün ve Firma Bilgisi -->
            <div class="space-y-1.5 pl-2">
              <div class="flex items-start space-x-2">
                <svg class="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
                <div class="flex-1">
                  <p class="text-xs font-medium text-gray-900 line-clamp-2">{{ products.find(p => p.id === activePopup.productId)?.name }}</p>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                <p class="text-xs font-medium text-blue-600">{{ companies.find(c => c.id === activePopup.companyId)?.name }}</p>
              </div>
            </div>
          </div>
          
          <div v-if="getProductLinks(activePopup.productId, activePopup.companyId).length > 0" class="space-y-2">
            <a 
              v-for="(link, index) in getProductLinks(activePopup.productId, activePopup.companyId)" 
              :key="index"
              :href="link.url" 
              target="_blank"
              class="flex items-center space-x-2 p-2.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg hover:text-blue-800 transition-all group"
            >
              <svg class="w-4 h-4 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              <span class="truncate font-medium">{{ link.name }}</span>
            </a>
          </div>
          <div v-else class="text-center py-4">
            <svg class="w-10 h-10 mx-auto text-gray-300 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <span class="text-xs text-gray-400">Link bulunamadı</span>
          </div>
        </div>
      </div>

      <!-- All Prices Popup Content -->
      <div v-else-if="activePopup.type === 'prices'" class="p-4 min-w-[400px] max-w-[600px]">
        <div class="space-y-3">
          <div class="flex items-center justify-between border-b border-gray-100 pb-3">
            <div class="flex items-center space-x-2">
              <div class="p-2 bg-green-100 rounded-lg">
                <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h4 class="text-sm font-bold text-gray-900">Tüm Fiyatlar</h4>
                <p class="text-xs text-gray-500">{{ companies.find(c => c.id === activePopup.companyId)?.name }}</p>
              </div>
            </div>
            <button 
              @click.stop="closePopup"
              class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg class="w-4 h-4 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <!-- Loading State -->
          <div v-if="getProductPrices(activePopup.productId, activePopup.companyId).loading" class="flex items-center justify-center py-8">
            <svg class="animate-spin h-6 w-6 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          
          <!-- Empty State -->
          <div v-else-if="!getProductPrices(activePopup.productId, activePopup.companyId).data || getProductPrices(activePopup.productId, activePopup.companyId).data.prices.length === 0" class="text-center py-6">
            <svg class="w-10 h-10 mx-auto text-gray-300 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="text-xs text-gray-400">Fiyat bulunamadı</span>
          </div>
          
          <!-- Prices List -->
          <div v-else class="space-y-2 max-h-96 overflow-y-auto">
            <div 
              v-for="(price, index) in getProductPrices(activePopup.productId, activePopup.companyId).data.prices" 
              :key="price.id" 
              class="flex items-center justify-between p-3 rounded-lg border transition-all"
              :class="[
                price.is_latest ? 'bg-blue-50 border-blue-200' : 'bg-gray-50 border-gray-200',
                price.is_cheapest ? 'ring-2 ring-orange-300' : ''
              ]"
            >
              <div class="flex items-center space-x-3 flex-1">
                <div class="flex flex-col">
                  <div class="flex items-center space-x-2">
                    <span class="text-lg font-bold text-gray-900">{{ parseFloat(price.value).toLocaleString() }} ₺</span>
                    <span v-if="price.is_latest" class="px-2 py-0.5 bg-blue-600 text-white text-[10px] font-bold rounded-full">En Yeni</span>
                    <span v-if="price.is_cheapest" class="px-2 py-0.5 bg-orange-600 text-white text-[10px] font-bold rounded-full">En Ucuz</span>
                  </div>
                  <div class="flex items-center space-x-2 mt-1">
                    <span class="text-xs text-gray-500">Attribute ID: {{ price.attribute_id }}</span>
                    <span class="text-xs text-gray-400">•</span>
                    <span class="text-xs text-gray-500">{{ formatDate(price.updated_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Summary -->
          <div v-if="getProductPrices(activePopup.productId, activePopup.companyId).data" class="border-t border-gray-100 pt-3 mt-3">
            <div class="grid grid-cols-2 gap-3 text-xs">
              <div class="bg-blue-50 p-2 rounded-lg">
                <div class="text-gray-600 font-medium">En Yeni Fiyat</div>
                <div class="text-lg font-bold text-blue-600 mt-1">
                  {{ getProductPrices(activePopup.productId, activePopup.companyId).data.latest_price ? parseFloat(getProductPrices(activePopup.productId, activePopup.companyId).data.latest_price.value).toLocaleString() : '—' }} ₺
                </div>
              </div>
              <div class="bg-orange-50 p-2 rounded-lg">
                <div class="text-gray-600 font-medium">En Ucuz Fiyat</div>
                <div class="text-lg font-bold text-orange-600 mt-1">
                  {{ getProductPrices(activePopup.productId, activePopup.companyId).data.cheapest_price ? parseFloat(getProductPrices(activePopup.productId, activePopup.companyId).data.cheapest_price.value).toLocaleString() : '—' }} ₺
                </div>
              </div>
            </div>
            <div class="mt-2 text-center text-xs text-gray-500">
              Toplam {{ getProductPrices(activePopup.productId, activePopup.companyId).data.total_count }} fiyat bulundu
            </div>
          </div>
        </div>
      </div>

      <!-- Sellers Popup Content -->
      <div v-else-if="activePopup.type === 'sellers'" class="p-4 min-w-[350px] max-w-[500px]">
        <div class="space-y-3">
          <div class="flex items-center justify-between border-b border-gray-100 pb-3">
            <div class="flex items-center space-x-2">
              <div class="p-2 bg-slate-100 rounded-lg">
                <svg class="w-4 h-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div>
                <h4 class="text-sm font-bold text-gray-900">Satıcılar</h4>
                <p class="text-xs text-gray-500">{{ companies.find(c => c.id === activePopup.companyId)?.name }}</p>
              </div>
            </div>
            <button 
              @click.stop="closePopup"
              class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg class="w-4 h-4 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="space-y-2 max-h-96 overflow-y-auto">
            <div 
              v-for="seller in getProductPrice(activePopup.productId, activePopup.companyId)?.sellers || []" 
              :key="seller.id" 
              class="flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg border border-gray-200 hover:shadow-md transition-all"
            >
              <div class="flex items-center space-x-3">
                <img :src="seller.logo" :alt="seller.name" class="w-10 h-10 rounded-lg object-cover border-2 border-white shadow-sm">
                <div>
                  <h5 class="font-semibold text-sm text-gray-900">{{ seller.name }}</h5>
                  <div class="flex items-center space-x-2 mt-0.5">
                    <div class="flex items-center space-x-1">
                      <span class="text-yellow-500 text-xs">⭐</span>
                      <span class="text-xs font-medium text-gray-700">{{ seller.rating }}</span>
                    </div>
                    <span class="text-xs text-gray-500">({{ seller.reviewCount }})</span>
                  </div>
                </div>
              </div>
              <div class="text-right">
                <p class="text-lg font-bold text-gray-900">{{ seller.price.toLocaleString() }} ₺</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import PriceComparisonChart from '~/components/PriceComparisonChart.vue'

definePageMeta({
  layout: 'dashboard',
  middleware: ['auth']
})

useHead({
  title: 'Fiyat Analiz'
})

// Real products from API
const products = ref([])
const isLoadingProducts = ref(true)
const isLoadingMore = ref(false)
const currentPage = ref(1)
const perPage = ref(20)
const hasMoreProducts = ref(true)

// Filter states
const selectedBrand = ref('')
const selectedAnalysis = ref('')
const searchQuery = ref('')
const profiles = ref([])
const showOnlyWithData = ref(true)
const showOnlyInStock = ref(false)
const selectedCompanies = ref([])
const showFilters = ref(false)
const sortByPrice = ref(true)

// Product name expansion
const expandedProducts = ref(new Set())

// Unified popup state
const activePopup = ref({
  isOpen: false,
  type: null, // 'info', 'link', 'sellers'
  productId: null,
  companyId: null,
  position: { top: '0px', left: '0px' }
})

const productLinks = ref({})

// Product info states
const productInfoData = ref({}) // { 'productId-companyId': { loading, data } }
const productInfoCache = ref({}) // Cache for API responses

// Product prices states (tüm fiyatlar için)
const productPricesData = ref({}) // { 'productId-companyId': { loading, data } }

const companies = ref([])

// Price data matrix (productId -> companyId -> price data)
const priceData = ref({})

// Additional reactive data
const lastUpdate = ref('2 dakika önce')
const isQuickScanning = ref({}) // { productId: boolean }

// Computed properties
const activeFilterCount = computed(() => {
  let count = 0
  if (searchQuery.value) count++
  if (selectedBrand.value) count++
  if (selectedAnalysis.value) count++
  if (showOnlyWithData.value) count++
  if (showOnlyInStock.value) count++
  if (selectedCompanies.value.length > 0) count++
  if (sortByPrice.value) count++
  return count
})

const filteredProductCount = computed(() => {
  return displayedProducts.value.length
})

const brands = computed(() => {
  const brandSet = new Set()
  products.value.forEach(product => {
    if (product.brand) brandSet.add(product.brand)
  })
  return Array.from(brandSet).sort()
})

const filteredCompanies = computed(() => {
  // Firma filtresi seçiliyse sadece seçilenleri göster
  if (selectedCompanies.value.length > 0) {
    return companies.value.filter(c => selectedCompanies.value.includes(c.id))
  }
  return companies.value
})

// Her ürün için firma-fiyat listesi (fiyata göre sıralama için)
const getProductCompanyPrices = (productId) => {
  const result = []
  
  filteredCompanies.value.forEach(company => {
    const priceInfo = priceData.value[productId]?.[company.id]
    const links = productLinks.value[productId]?.[company.id] || []
    
    // Fiyat varsa
    if (priceInfo) {
      const price = company.isMarketplace ? priceInfo.lowestPrice : priceInfo.price
      if (price) {
        result.push({
          company,
          price,
          hasPrice: true,
          hasLink: links.length > 0,
          priceInfo
        })
      } else if (links.length > 0 && !sortByPrice.value) {
        // Fiyat yok ama link var (mavi) - sadece sortByPrice kapalıysa göster
        result.push({
          company,
          price: null,
          hasPrice: false,
          hasLink: true,
          priceInfo
        })
      }
    } else if (links.length > 0 && !sortByPrice.value) {
      // Fiyat bilgisi yok ama link var (mavi) - sadece sortByPrice kapalıysa göster
      result.push({
        company,
        price: null,
        hasPrice: false,
        hasLink: true,
        priceInfo: null
      })
    }
  })
  
  // Fiyata göre sırala: önce fiyatı olanlar (artan), sonra sadece linki olanlar
  result.sort((a, b) => {
    if (a.hasPrice && !b.hasPrice) return -1
    if (!a.hasPrice && b.hasPrice) return 1
    if (a.hasPrice && b.hasPrice) return a.price - b.price
    return 0
  })
  
  return result
}

// Filtered and paginated products for rendering
const displayedProducts = computed(() => {
  let filtered = products.value

  // Search filter (name and mpn)
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(product => {
      const name = (product.name || '').toLowerCase()
      const mpn = (product.mpn || '').toLowerCase()
      return name.includes(query) || mpn.includes(query)
    })
  }

  // Brand filter
  if (selectedBrand.value) {
    filtered = filtered.filter(product => product.brand === selectedBrand.value)
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

  // "Sadece veri olan ürünler" filtresi
  if (showOnlyWithData.value) {
    filtered = filtered.filter(product => {
      const productPrices = priceData.value[product.id]
      if (!productPrices || Object.keys(productPrices).length === 0) {
        return false
      }
      
      // Eğer firma seçimi yapılmışsa, sadece seçilen firmalarda verisi olan ürünleri göster
      if (selectedCompanies.value.length > 0) {
        return selectedCompanies.value.some(companyId => 
          productPrices[companyId] && (
            productPrices[companyId].price || 
            productPrices[companyId].lowestPrice
          )
        )
      }
      
      // Firma seçimi yapılmamışsa, herhangi bir firmada verisi olan ürünleri göster
      return true
    })
  }

  // "Sadece stoğu olan ürünler" filtresi
  if (showOnlyInStock.value) {
    filtered = filtered.filter(product => {
      // availability "in stock" ise stokta var demektir
      return product.availability && product.availability.toLowerCase() === 'in stock'
    })
  }

  const endIndex = currentPage.value * perPage.value
  return filtered.slice(0, endIndex)
})

// Methods
const fetchCompanies = async () => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('price-analysis.company-list'))
    
    if (response.success && response.data) {
      // API'den gelen verileri dönüştür
      companies.value = response.data.map(company => {
        // marketplace: "trendyol", "hepsiburada" gibi isimler = true, "false"/null/"" = false
        const isMarketplace = !!(company.marketplace && company.marketplace !== 'false')
        
        return {
          id: company.id,
          name: company.name,
          url: company.url,
          isMarketplace: isMarketplace,
          logo: company.company_logo || `https://www.${company.url?.replace(/^https?:\/\/(www\.)?/, '').split('/')[0]}/favicon.ico`
        }
      })
      
      console.log('🏢 Companies yüklendi:', companies.value.length)
      console.log('🆔 İlk 3 company ID:', companies.value.slice(0, 3).map(c => ({ id: c.id, name: c.name, isMarketplace: c.isMarketplace })))
    }
  } catch (error) {
    console.error('Şirketler yüklenirken hata:', error)
    companies.value = []
  }
}

const fetchPriceSummary = async () => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('price-analysis.price-summary'))
    
    console.log('🔍 API Response:', response)
    console.log('🔍 Response data count:', response.data?.length)
    
    if (response.success && response.data) {
      // priceData objesini oluştur
      const priceMatrix = {}
      
      response.data.forEach((item, index) => {
        const productId = item.product_id
        const companyId = item.company_id
        const price = parseFloat(item.value)
        
        if (index < 3) {
          console.log(`📦 Item ${index}:`, { productId, companyId, price, rawValue: item.value, has_cheaper_price: item.has_cheaper_price, cheapest_price: item.cheapest_price })
        }
        
        // Product için obje yoksa oluştur
        if (!priceMatrix[productId]) {
          priceMatrix[productId] = {}
        }
        
        // Company bilgisini bul (marketplace mi değil mi)
        const company = companies.value.find(c => c.id === companyId)
        const isMarketplace = company?.isMarketplace || false
        
        // Stok bilgisini al (availability boolean olarak geliyor)
        const availability = item.availability !== null && item.availability !== undefined 
          ? (item.availability === true || item.availability === 1 || item.availability === '1' || item.availability === 'true')
          : null
        
        // Fiyat verisini yerleştir (yeni API yanıtından gelen ek bilgilerle)
        if (isMarketplace) {
          // Marketplace için lowestPrice olarak kaydet
          priceMatrix[productId][companyId] = {
            lowestPrice: price,
            sellerCount: 0,
            inStock: availability !== null ? availability : true,
            availability: availability,
            availability_updated_at: item.availability_updated_at || null,
            availability_job_id: item.availability_job_id || null,
            sellers: [],
            updated_at: item.updated_at,
            has_cheaper_price: item.has_cheaper_price || false,
            cheapest_price: item.cheapest_price ? parseFloat(item.cheapest_price) : null,
            all_prices: item.all_prices || [],
            total_price_count: item.total_price_count || 1
          }
        } else {
          // Normal şirket için price olarak kaydet
          priceMatrix[productId][companyId] = {
            price: price,
            inStock: availability !== null ? availability : true,
            availability: availability,
            availability_updated_at: item.availability_updated_at || null,
            availability_job_id: item.availability_job_id || null,
            updated_at: item.updated_at,
            has_cheaper_price: item.has_cheaper_price || false,
            cheapest_price: item.cheapest_price ? parseFloat(item.cheapest_price) : null,
            all_prices: item.all_prices || [],
            total_price_count: item.total_price_count || 1
          }
        }
      })
      
      priceData.value = priceMatrix
      console.log('✅ Price data yüklendi:', priceMatrix)
      console.log('📊 Product ID\'leri:', Object.keys(priceMatrix))
      console.log('🏢 İlk product için company ID\'leri:', Object.keys(priceMatrix[Object.keys(priceMatrix)[0]] || {}))
    }
  } catch (error) {
    console.error('❌ Fiyat özeti yüklenirken hata:', error)
    priceData.value = {}
  }
}

const fetchCompanyUrls = async () => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('price-analysis.company-url-list'))
    
    console.log('🔗 Company URLs Response:', response)
    
    if (response.success && response.data) {
      const linksMatrix = {}
      
      response.data.forEach((item, index) => {
        const productId = item.product_id
        const companyId = item.company_id
        const url = item.url
        
        if (index < 3) {
          console.log(`🔗 Link ${index}:`, { productId, companyId, url })
        }
        
        // Product için obje yoksa oluştur
        if (!linksMatrix[productId]) {
          linksMatrix[productId] = {}
        }
        
        // Company için array yoksa oluştur
        if (!linksMatrix[productId][companyId]) {
          linksMatrix[productId][companyId] = []
        }
        
        // URL'i ekle
        const company = companies.value.find(c => c.id === companyId)
        linksMatrix[productId][companyId].push({
          name: company?.name || 'Link',
          url: url
        })
      })
      
      productLinks.value = linksMatrix
      console.log('✅ Product links yüklendi:', linksMatrix)
      console.log('🔗 Link sayısı:', response.data.length)
    }
  } catch (error) {
    console.error('❌ URL listesi yüklenirken hata:', error)
    productLinks.value = {}
  }
}

const fetchProducts = async () => {
  try {
    isLoadingProducts.value = true
    const { $api } = useNuxtApp()
    // Sadece aktif ürünleri getir (is_active = 1)
    const response = await $api.get('/user-products', {
      query: {
        is_active: 1
      }
    })
    
    if (response.data) {
      // API'den gelen verileri dönüştür
      products.value = response.data.map((product, index) => {
        // Debug için ilk birkaç ürünü logla
        if (index < 3) {
          console.log('🔍 Product data:', {
            id: product.id,
            title: product.title,
            price: product.price,
            sale_price: product.sale_price,
            web_price: product.web_price
          })
        }
        
        // Fiyat önceliği: sale_price > price > web_price
        let myPrice = 0
        if (product.sale_price && parseFloat(product.sale_price) > 0) {
          myPrice = parseFloat(product.sale_price)
        } else if (product.price && parseFloat(product.price) > 0) {
          myPrice = parseFloat(product.price)
        } else if (product.web_price && parseFloat(product.web_price) > 0) {
          myPrice = parseFloat(product.web_price)
        }
        
        return {
          id: product.id,
          name: product.title,
          brand: product.brand?.name || 'Bilinmeyen Marka',
          mpn: product.mpn || '',
          image: product.image || 'https://upload.wikimedia.org/wikipedia/commons/1/14/No_Image_Available.jpg',
          link: product.link || '#',
          myPrice: myPrice,
          availability: product.availability || null
        }
      })
      
      console.log('🛍️ Products yüklendi:', products.value.length)
      console.log('🆔 İlk 3 product ID:', products.value.slice(0, 3).map(p => ({ id: p.id, name: p.name, myPrice: p.myPrice })))
      
      // Pagination kontrolü
      hasMoreProducts.value = products.value.length > perPage.value
    }
  } catch (error) {
    console.error('Ürünler yüklenirken hata:', error)
    // Hata durumunda boş array
    products.value = []
  } finally {
    isLoadingProducts.value = false
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

const loadMoreProducts = () => {
  if (isLoadingMore.value || !hasMoreProducts.value) return
  
  isLoadingMore.value = true
  
  // Simulate loading delay
  setTimeout(() => {
    currentPage.value++
    hasMoreProducts.value = displayedProducts.value.length < products.value.length
    isLoadingMore.value = false
  }, 500)
}

const filterByAnalysis = () => {
  currentPage.value = 1 // Reset to first page when filtering
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedBrand.value = ''
  selectedAnalysis.value = ''
  showOnlyWithData.value = true  // Varsayılan olarak seçili kal
  showOnlyInStock.value = false
  selectedCompanies.value = []
  sortByPrice.value = true  // Varsayılan olarak seçili kal
  currentPage.value = 1
  showFilters.value = false
  
  // LocalStorage'i de temizle
  try {
    localStorage.removeItem('priceAnalysis_selectedCompanies')
  } catch (error) {
    console.error('LocalStorage temizleme hatası:', error)
  }
}

const toggleProductName = (productId) => {
  if (expandedProducts.value.has(productId)) {
    expandedProducts.value.delete(productId)
  } else {
    expandedProducts.value.add(productId)
  }
}

// Watch for filter changes to reset pagination
watch([selectedBrand, selectedAnalysis, searchQuery, showOnlyWithData, showOnlyInStock, selectedCompanies, sortByPrice], () => {
  currentPage.value = 1
})

// Watch selectedCompanies and save to localStorage
watch(selectedCompanies, (newValue) => {
  try {
    if (newValue && newValue.length > 0) {
      localStorage.setItem('priceAnalysis_selectedCompanies', JSON.stringify(newValue))
    } else {
      localStorage.removeItem('priceAnalysis_selectedCompanies')
    }
  } catch (error) {
    console.error('LocalStorage kaydetme hatası:', error)
  }
}, { deep: true })

const getProductPrice = (productId, companyId) => {
  const result = priceData.value[productId]?.[companyId] || null
  
  // İlk birkaç kontrolde debug
  if (Math.random() < 0.01) { // %1 ihtimalle log at (çok spam olmasın)
    console.log(`🔍 getProductPrice(${productId}, ${companyId}):`, result)
    console.log('📊 priceData keys:', Object.keys(priceData.value))
  }
  
  return result
}

const showMarketplaceDetails = (productId, companyId, event) => {
  openPopup('sellers', productId, companyId, event)
}

const applyFilters = () => {
  console.log('Filters applied:', {
    brand: selectedBrand.value,
    analysis: selectedAnalysis.value
  })
}

const getPriceColor = (myPrice, competitorPrice) => {
  if (!competitorPrice) return 'text-gray-400'
  
  if (competitorPrice > myPrice) {
    return 'text-green-600' // Yeşil - rakip daha pahalı
  } else if (competitorPrice === myPrice) {
    return 'text-gray-900' // Siyah - aynı fiyat
  } else {
    return 'text-red-600' // Kırmızı - rakip daha ucuz
  }
}

const getPriceBgColor = (myPrice, competitorPrice) => {
  if (!competitorPrice) return ''
  
  if (competitorPrice > myPrice) {
    return '#f2fef0' // Yeşilimsi - rakip daha pahalı (benim lehime)
  } else if (competitorPrice < myPrice) {
    return '#fef0f0' // Kırmızımsı - rakip daha ucuz (benim aleyhime)
  }
  
  return '' // Aynı fiyat ise normal
}

const getPriceDifference = (myPrice, competitorPrice) => {
  if (!competitorPrice || !myPrice) return null
  
  const difference = ((competitorPrice - myPrice) / myPrice) * 100
  return difference.toFixed(1)
}

const getLastUpdateTextColor = (myPrice, competitorPrice) => {
  if (!competitorPrice) return 'text-gray-500'
  
  if (competitorPrice > myPrice) {
    return 'text-green-600' // Yeşil card için yeşil text
  } else if (competitorPrice < myPrice) {
    return 'text-red-600' // Kırmızı card için kırmızı text
  } else {
    return 'text-gray-500' // Aynı fiyat için gri text
  }
}

// Unified popup methods
const openPopup = async (type, productId, companyId, event) => {
  // Aynı popup açıksa kapat
  if (activePopup.value.isOpen && 
      activePopup.value.type === type && 
      activePopup.value.productId === productId && 
      activePopup.value.companyId === companyId) {
    closePopup()
    return
  }
  
  // Ekranın ortasında konumlandır
  const position = {
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)'
  }
  
  // Popup'ı aç
  activePopup.value = {
    isOpen: true,
    type,
    productId,
    companyId,
    position
  }
  
  // Eğer info popup'ıysa fiyat geçmişini çek
  if (type === 'info') {
    await fetchProductInfo(productId, companyId)
  }
  
  // Eğer prices popup'ıysa tüm fiyatları çek
  if (type === 'prices') {
    await fetchProductPrices(productId, companyId)
  }
}

const closePopup = () => {
  activePopup.value.isOpen = false
}

const isPopupOpen = (type, productId, companyId) => {
  return activePopup.value.isOpen && 
         activePopup.value.type === type && 
         activePopup.value.productId === productId && 
         activePopup.value.companyId === companyId
}

const getProductLinks = (productId, companyId) => {
  return productLinks.value[productId]?.[companyId] || []
}

const fetchProductInfo = async (productId, companyId) => {
  const key = `${productId}-${companyId}`
  
  // Cache'de varsa direkt dön
  if (productInfoCache.value[key]) {
    return productInfoCache.value[key]
  }
  
  // Loading state
  productInfoData.value[key] = { loading: true, data: null }
  
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('price-analysis.price-history'), {
      params: {
        company_id: companyId,
        product_id: productId
      }
    })
    
    if (response.success && response.data) {
      const data = {
        priceHistory: response.data.map(item => ({
          date: new Date(item.created_at).toLocaleDateString('tr-TR'),
          price: parseFloat(item.value),
          jobId: item.job_id,
          createdAt: item.created_at
        })),
        lastUpdate: response.data.length > 0 
          ? formatLastUpdate(response.data[0].created_at)
          : 'Bilinmiyor'
      }
      
      // Cache'e kaydet
      productInfoCache.value[key] = data
      productInfoData.value[key] = { loading: false, data }
      
      return data
    }
  } catch (error) {
    console.error('Ürün bilgisi yüklenirken hata:', error)
    productInfoData.value[key] = { loading: false, data: null }
  }
  
  return null
}

const formatLastUpdate = (dateString) => {
  if (!dateString) return '-'
  
  try {
    // Tarihi parse et (dateString zaten +0300 timezone bilgisi içeriyor)
    const sourceDate = new Date(dateString)
    
    // Şu anki zamanı al (local timezone'da)
    const now = new Date()
    
    // Zaman farkını hesapla (milisaniye cinsinden)
    // Date objeleri zaten UTC timestamp kullanıyor, direkt karşılaştırma yapabiliriz
    const diffMs = now.getTime() - sourceDate.getTime()
    
    // Gelecek zamanlar için "az önce" göster
    if (diffMs < 0) {
      return 'az önce'
    }
    
    // Saniye cinsinden fark
    const diffSec = Math.floor(diffMs / 1000)
    
    if (diffSec < 60) {
      return diffSec <= 0 ? 'az önce' : `${diffSec} saniye önce`
    }
    
    const diffMinutes = Math.floor(diffSec / 60)
    if (diffMinutes < 60) {
      return `${diffMinutes} dakika önce`
    }
    
    const diffHours = Math.floor(diffSec / 3600)
    if (diffHours < 24) {
      return `${diffHours} saat önce`
    }
    
    const diffDays = Math.floor(diffSec / 86400)
    if (diffDays < 30) {
      return `${diffDays} gün önce`
    }
    
    // 30 günden fazla ise tarih formatında göster
    return sourceDate.toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch (error) {
    console.error('Tarih formatlama hatası:', error, dateString)
    return '-'
  }
}

const formatLastUpdateShort = (formattedString) => {
  if (!formattedString || formattedString === '-') return '-'
  
  // Zaten formatlanmış string'i kısa formata çevir
  if (formattedString === 'az önce') {
    return 'az önce'
  }
  if (formattedString.includes('dakika önce')) {
    const minutes = formattedString.match(/(\d+) dakika önce/)?.[1]
    return minutes ? `${minutes}dk` : formattedString
  }
  if (formattedString.includes('saat önce')) {
    const hours = formattedString.match(/(\d+) saat önce/)?.[1]
    return hours ? `${hours}sa` : formattedString
  }
  if (formattedString.includes('gün önce')) {
    const days = formattedString.match(/(\d+) gün önce/)?.[1]
    return days ? `${days}g` : formattedString
  }
  if (formattedString.includes('saniye önce')) {
    const seconds = formattedString.match(/(\d+) saniye önce/)?.[1]
    return seconds ? `${seconds}sn` : formattedString
  }
  
  return formattedString
}

const fetchProductPrices = async (productId, companyId) => {
  const key = `${productId}-${companyId}`
  
  // Zaten yükleniyorsa veya yüklenmişse bekle
  if (productPricesData.value[key]?.loading || productPricesData.value[key]?.data) {
    return productPricesData.value[key]?.data
  }
  
  // Loading state
  productPricesData.value[key] = { loading: true, data: null }
  
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('price-analysis.product-prices'), {
      params: {
        company_id: companyId,
        product_id: productId
      }
    })
    
    if (response.success && response.data) {
      productPricesData.value[key] = { loading: false, data: response.data }
      return response.data
    }
  } catch (error) {
    console.error('Ürün fiyatları yüklenirken hata:', error)
    productPricesData.value[key] = { loading: false, data: null }
  }
  
  return null
}

const getProductPrices = (productId, companyId) => {
  const key = `${productId}-${companyId}`
  return productPricesData.value[key] || { loading: false, data: null }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return dateString
  }
}

const getProductInfo = (productId, companyId) => {
  const key = `${productId}-${companyId}`
  
  // updated_at'i price-summary'den al
  const priceInfo = priceData.value[productId]?.[companyId]
  const lastUpdate = priceInfo?.updated_at 
    ? formatLastUpdate(priceInfo.updated_at) 
    : 'Bilinmiyor'
  
  // productInfoData'dan veya cache'den al
  const cached = productInfoCache.value[key]
  if (cached) {
    return { ...cached, lastUpdate }
  }
  
  const infoData = productInfoData.value[key]
  if (infoData?.data) {
    return { ...infoData.data, lastUpdate }
  }
  
  // Default değer
  return {
    lastUpdate,
    priceHistory: [],
    loading: infoData?.loading || false
  }
}

const openCompanyUrl = (url) => {
  if (url) {
    window.open(url, '_blank')
  }
}

// Quick scan product function
const quickScanProduct = async (productId) => {
  try {
    // Set loading state
    isQuickScanning.value[productId] = true
    
    const { $api } = useNuxtApp()
    const scanningApi = useScanningApi()
    
    const response = await scanningApi.quickScanProduct(productId)
    
    if (response.success) {
      // Success message
      const message = response.message || `${response.total_items || 0} URL için hızlı tarama başlatıldı`
      
      // Show success notification (you can use your notification system here)
      alert(`✅ ${message}\n\nJob ID: ${response.job_id || 'N/A'}`)
      
      console.log('✅ Hızlı tarama başlatıldı:', {
        productId,
        jobId: response.job_id,
        totalItems: response.total_items
      })
    } else {
      // Error message
      alert(`❌ ${response.message || 'Hızlı tarama başlatılamadı'}`)
      console.error('❌ Hızlı tarama hatası:', response)
    }
  } catch (error) {
    console.error('❌ Hızlı tarama hatası:', error)
    alert('❌ Hızlı tarama başlatılırken hata oluştu: ' + (error.message || 'Bilinmeyen hata'))
  } finally {
    // Clear loading state
    isQuickScanning.value[productId] = false
  }
}

// Lifecycle
onMounted(async () => {
  // LocalStorage'den kayıtlı firma seçimlerini yükle
  try {
    const savedCompanies = localStorage.getItem('priceAnalysis_selectedCompanies')
    if (savedCompanies) {
      const parsed = JSON.parse(savedCompanies)
      if (Array.isArray(parsed)) {
        selectedCompanies.value = parsed
        console.log('📦 LocalStorage\'den firma seçimleri yüklendi:', parsed)
      }
    }
  } catch (error) {
    console.error('LocalStorage okuma hatası:', error)
  }
  
  // Önce companies yükle (fetchPriceSummary ve fetchCompanyUrls'de kullanılıyor)
  await fetchCompanies()
  
  // Sonra diğerlerini paralel yükle
  await Promise.all([
    fetchPriceSummary(),
    fetchCompanyUrls(),
    fetchProducts(),
    fetchProfiles()
  ])
})
</script>
