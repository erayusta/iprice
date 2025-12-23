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
  <div v-else-if="!hasPermission('companies.show')" class="flex items-center justify-center min-h-screen">
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
            Firmalar 🏢
          </h1>
          <p class="text-gray-600 text-lg">
            Firma yönetimi ve takibi için bu sayfayı kullanabilirsiniz.
          </p>
        </div>
        <div class="hidden md:block">
          <div class="w-20 h-20 bg-gradient-to-br from-apple-blue to-apple-indigo rounded-3xl flex items-center justify-center">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
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
              placeholder="Firma ara..."
              class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
            />
            <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
        <div class="flex gap-3">
          <select v-model="selectedCrawler" class="px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent">
            <option value="">Tüm Crawler'lar</option>
            <option v-for="crawler in crawlers" :key="crawler.id" :value="crawler.id">
              {{ crawler.name }}
            </option>
          </select>
          <button 
            v-if="hasPermission('companies.add')"
            @click="() => openModal()" 
            class="btn btn-primary"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Yeni Firma
          </button>
          <button 
            v-if="hasPermission('companies.attribute')"
            @click="navigateToAttributeCheck" 
            class="btn btn-secondary"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Firma Attribute Kontrolü
          </button>
        </div>
      </div>
    </div>

    <!-- Companies Table -->
    <div class="card-elevated">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-200">
              <th class="text-left py-4 px-6 font-semibold text-gray-900">Logo</th>
              <th class="text-left py-4 px-6 font-semibold text-gray-900">Firma Adı</th>
              <th class="text-left py-4 px-6 font-semibold text-gray-900">Web Sitesi</th>
              <th class="text-left py-4 px-6 font-semibold text-gray-900">Crawler</th>
              <th class="text-left py-4 px-6 font-semibold text-gray-900">Server</th>
              <th class="text-left py-4 px-6 font-semibold text-gray-900">Marketplace</th>
              <th class="text-left py-4 px-6 font-semibold text-gray-900">Screenshot</th>
              <th class="text-left py-4 px-6 font-semibold text-gray-900">Proxy</th>
              <th class="text-left py-4 px-6 font-semibold text-gray-900">Oluşturulma</th>
              <th class="text-right py-4 px-6 font-semibold text-gray-900">İşlemler</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="isLoading" class="border-b border-gray-100">
              <td colspan="10" class="text-center py-12">
                <div class="flex items-center justify-center">
                  <svg class="animate-spin -ml-1 mr-3 h-8 w-8 text-apple-blue" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span class="text-gray-600">Yükleniyor...</span>
                </div>
              </td>
            </tr>
            <tr v-else-if="filteredCompanies.length === 0" class="border-b border-gray-100">
              <td colspan="10" class="text-center py-12">
                <div class="text-gray-500">
                  <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  <p class="text-lg font-medium mb-2">Firma bulunamadı</p>
                  <p class="text-sm">Henüz firma eklenmemiş veya arama kriterlerinize uygun firma yok.</p>
                </div>
              </td>
            </tr>
            <tr v-else v-for="company in filteredCompanies" :key="company.id" class="border-b border-gray-100 hover:bg-gray-50 transition-colors">
              <td class="py-4 px-6">
                <div class="w-12 h-12 rounded-xl overflow-hidden bg-gray-100 flex items-center justify-center">
                  <img v-if="company.company_logo" :src="company.company_logo" :alt="company.company_name" class="w-full h-full object-cover" />
                  <svg v-else class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
              </td>
              <td class="py-4 px-6">
                <div class="font-medium text-gray-900">{{ company.company_name }}</div>
              </td>
              <td class="py-4 px-6">
                <a v-if="company.company_site" :href="company.company_site" target="_blank" class="text-apple-blue hover:text-apple-indigo flex items-center">
                  <span class="truncate max-w-32">{{ company.company_site }}</span>
                  <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
                <span v-else class="text-gray-400">-</span>
              </td>
              <td class="py-4 px-6">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="getCrawlerColor(company.crawler_id)">
                  {{ getCrawlerName(company.crawler_id) }}
                </span>
              </td>
              <td class="py-4 px-6">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" 
                      :class="getServerName(company.server_id).toLowerCase() === 'local' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'">
                  {{ getServerName(company.server_id) }}
                </span>
              </td>
              <td class="py-4 px-6">
                <span v-if="company.is_marketplace" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                  Evet
                </span>
                <span v-else class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                  Hayır
                </span>
              </td>
              <td class="py-4 px-6">
                <span v-if="company.screenshot_required" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                  Evet
                </span>
                <span v-else class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                  Hayır
                </span>
              </td>
              <td class="py-4 px-6">
                <span v-if="company.use_proxy" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                  <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                  Aktif
                </span>
                <span v-else class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                  Kapalı
                </span>
              </td>
              <td class="py-4 px-6 text-sm text-gray-500">
                {{ formatDate(company.created_at) }}
              </td>
              <td class="py-4 px-6">
                <div class="flex items-center justify-end space-x-2">
                  <button 
                    v-if="hasPermission('companies.edit')"
                    @click="editCompany(company)" 
                    class="p-2 text-gray-400 hover:text-apple-blue transition-colors" 
                    title="Düzenle"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button 
                    v-if="hasPermission('companies.attribute')"
                    @click="openAttributesModal(company)" 
                    class="p-2 text-gray-400 hover:text-green-500 transition-colors" 
                    title="Attribute Ayarları"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </button>
                  <button 
                    v-if="hasPermission('companies.delete')"
                    @click="deleteCompany(company)" 
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

    <!-- Add Company Modal -->
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
                  {{ editingCompany ? 'Firma Düzenle' : 'Yeni Firma Ekle' }}
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
              <!-- Company Name -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Firma Adı</label>
                <input 
                  v-model="form.company_name" 
                  type="text" 
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                  placeholder="Firma adını girin"
                />
              </div>

              <!-- Company Logo (Drag & Drop) -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Firma Görseli</label>
                <div 
                  @drop="handleDrop" 
                  @dragover.prevent 
                  @dragenter.prevent
                  class="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-apple-blue transition-colors cursor-pointer"
                  :class="{ 'border-apple-blue bg-apple-blue/5': isDragOver }"
                >
                  <div v-if="!selectedFile" class="space-y-4">
                    <svg class="w-12 h-12 text-gray-400 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <div>
                      <p class="text-sm text-gray-600">Dosyayı buraya sürükleyin veya</p>
                      <button type="button" @click="selectFile" class="text-apple-blue hover:text-apple-indigo font-medium">
                        dosya seçin
                      </button>
                    </div>
                    <p class="text-xs text-gray-500">PNG, JPG, GIF (Max 10MB)</p>
                  </div>
                  <div v-else class="space-y-2">
                    <img :src="previewUrl" alt="Preview" class="w-20 h-20 object-cover rounded-lg mx-auto" />
                    <p class="text-sm text-gray-600">{{ selectedFile.name }}</p>
                    <button type="button" @click="removeFile" class="text-red-500 hover:text-red-700 text-sm">
                      Kaldır
                    </button>
                  </div>
                </div>
                <input ref="fileInput" type="file" @change="handleFileSelect" accept="image/*" class="hidden" />
              </div>

              <!-- Company Site -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Firma Web Sitesi</label>
                <input 
                  v-model="form.company_site" 
                  type="url" 
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                  placeholder="https://example.com"
                />
              </div>

              <!-- Crawler Selection -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Crawler</label>
                <select 
                  v-model="form.crawler_id" 
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                >
                  <option value="">Crawler seçin</option>
                  <option v-for="crawler in crawlers" :key="crawler.id" :value="crawler.id">
                    {{ crawler.name }}
                  </option>
                </select>
              </div>

              <!-- Server Selection -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Server</label>
                <select 
                  v-model="form.server_id" 
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                >
                  <option v-for="server in servers" :key="server.id" :value="server.id">
                    {{ server.name }} - {{ server.description }}
                  </option>
                </select>
              </div>

              <!-- Screenshot Required -->
              <div>
                <label class="flex items-center">
                  <input 
                    v-model="form.screenshot_required" 
                    type="checkbox" 
                    class="rounded border-gray-300 text-apple-blue focus:ring-apple-blue"
                  />
                  <span class="ml-2 text-sm font-medium text-gray-700">Ekran görüntüsü alınsın mı?</span>
                </label>
              </div>

              <!-- Marketplace -->
              <div>
                <label class="flex items-center">
                  <input 
                    v-model="form.is_marketplace" 
                    type="checkbox" 
                    class="rounded border-gray-300 text-apple-blue focus:ring-apple-blue"
                  />
                  <span class="ml-2 text-sm font-medium text-gray-700">Marketplace mi?</span>
                </label>
              </div>

              <!-- Use Proxy -->
              <div>
                <label class="flex items-center">
                  <input 
                    v-model="form.use_proxy" 
                    type="checkbox" 
                    class="rounded border-gray-300 text-apple-blue focus:ring-apple-blue"
                  />
                  <span class="ml-2 text-sm font-medium text-gray-700">Proxy kullanılsın mı?</span>
                </label>
              </div>

              <!-- Proxy Selection -->
              <div v-if="form.use_proxy">
                <label class="block text-sm font-medium text-gray-700 mb-2">Proxy Seçimi</label>
                <select 
                  v-model="form.proxy_id" 
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                >
                  <option value="">Proxy seçin</option>
                  <option v-for="proxy in proxies" :key="proxy.id" :value="proxy.id" :disabled="!proxy.is_active">
                    {{ proxy.name }} {{ !proxy.is_active ? '(Pasif)' : '' }}
                  </option>
                </select>
                <p v-if="proxies.length === 0" class="text-sm text-gray-500 mt-1">
                  Henüz proxy ayarı bulunmuyor. 
                  <NuxtLink to="/dashboard/proxy-settings" class="text-apple-blue hover:text-apple-indigo">
                    Proxy ayarları
                  </NuxtLink>
                  sayfasından proxy ekleyebilirsiniz.
                </p>
              </div>
            </div>

            <!-- Modal footer -->
            <div class="bg-gray-50 px-6 py-4 flex justify-end space-x-3">
              <button type="button" @click="closeModal" class="btn btn-secondary">
                İptal
              </button>
              <button type="submit" :disabled="isSubmitting" class="btn btn-primary">
                <span v-if="isSubmitting">Kaydediliyor...</span>
                <span v-else>{{ editingCompany ? 'Güncelle' : 'Firma Ekle' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Attributes Modal -->
    <div v-if="showAttributesModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeAttributesModal"></div>

        <!-- Modal panel -->
        <div class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <div class="bg-white px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900">
                {{ selectedCompany?.company_name }} - Attribute Ayarları
              </h3>
              <button type="button" @click="closeAttributesModal" class="text-gray-400 hover:text-gray-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <div class="bg-white px-6 py-6">
            <div class="space-y-6">
              <div v-for="attribute in attributes" :key="attribute.id" class="border border-gray-200 rounded-xl p-4">
                <div class="flex items-center justify-between mb-3">
                  <h4 class="font-semibold text-gray-800">{{ attribute.name }}</h4>
                  <label class="flex items-center">
                    <input 
                      v-model="getCompanyAttribute(attribute.id).enabled" 
                      type="checkbox" 
                      class="rounded border-gray-300 text-apple-blue focus:ring-apple-blue"
                    />
                    <span class="ml-2 text-sm text-gray-600">Aktif</span>
                  </label>
                </div>
                
                <div v-if="getCompanyAttribute(attribute.id).enabled" class="space-y-3">
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Tip</label>
                      <select 
                        v-model="getCompanyAttribute(attribute.id).type" 
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-apple-blue focus:border-transparent"
                      >
                        <option value="class">Class</option>
                        <option value="xpath">XPath</option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Value</label>
                      <input 
                        v-model="getCompanyAttribute(attribute.id).value" 
                        type="text" 
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-apple-blue focus:border-transparent"
                        placeholder=".price, //div[@class='price'], etc."
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-gray-50 px-6 py-4 flex justify-end space-x-3">
            <button type="button" @click="closeAttributesModal" class="btn btn-secondary">
              İptal
            </button>
            <button @click="saveAttributes" :disabled="isSavingAttributes" class="btn btn-primary">
              <span v-if="isSavingAttributes">Kaydediliyor...</span>
              <span v-else>Kaydet</span>
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

// Permissions composable
let hasPermission
try {
  const permissions = usePermissions()
  hasPermission = permissions.hasPermission
} catch (error) {
  console.warn('Permissions composable failed:', error)
  hasPermission = () => false
}
const showModal = ref(false)
const isSubmitting = ref(false)
const isDragOver = ref(false)
const isLoading = ref(false)
const selectedFile = ref(null)
const previewUrl = ref('')
const fileInput = ref(null)
const editingCompany = ref(null)

// Attributes modal
const showAttributesModal = ref(false)
const selectedCompany = ref(null)
const isSavingAttributes = ref(false)
const attributes = ref([])
const companyAttributes = ref({}) // { attribute_id: { enabled, type, value } }

// Search and filter
const searchQuery = ref('')
const selectedCrawler = ref('')

// Form data
const form = reactive({
  company_name: '',
  company_logo: null,
  company_site: '',
  crawler_id: '',
  server_id: 1, // Default to local server
  screenshot_required: false,
  is_marketplace: false,
  use_proxy: false,
  proxy_id: null
})

// Data
const companies = ref([])
const crawlers = ref([])
const servers = ref([])
const proxies = ref([])

// Computed
const filteredCompanies = computed(() => {
  let filtered = companies.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(company => 
      company.company_name.toLowerCase().includes(query) ||
      (company.company_site && company.company_site.toLowerCase().includes(query))
    )
  }

  // Crawler filter
  if (selectedCrawler.value) {
    filtered = filtered.filter(company => company.crawler_id == selectedCrawler.value)
  }

  return filtered
})

// Get crawler name by ID
const getCrawlerName = (crawlerId) => {
  const crawler = crawlers.value.find(c => c.id === crawlerId)
  return crawler ? crawler.name : 'Bilinmiyor'
}

// Get crawler color by ID
const getCrawlerColor = (crawlerId) => {
  const crawler = crawlers.value.find(c => c.id === crawlerId)
  if (!crawler) return 'bg-gray-100 text-gray-800'
  
  const colors = {
    'Scrapy': 'bg-blue-100 text-blue-800',
    'Selenium': 'bg-green-100 text-green-800', 
    'Playwright': 'bg-purple-100 text-purple-800'
  }
  
  return colors[crawler.name] || 'bg-gray-100 text-gray-800'
}

// Get server name by ID
const getServerName = (serverId) => {
  const server = servers.value.find(s => s.id === serverId)
  return server ? server.name : 'Local'
}

// Modal functions
const openModal = async (company = null) => {
  showModal.value = true
  
  if (company) {
    // Edit mode - populate form
    editingCompany.value = company
    form.company_name = company.company_name
    form.company_site = company.company_site || ''
    form.crawler_id = company.crawler_id
    form.server_id = company.server_id || 1
    form.screenshot_required = company.screenshot_required || false
    form.is_marketplace = company.is_marketplace || false
    form.use_proxy = company.use_proxy || false
    form.proxy_id = company.proxy_id || null
    form.company_logo = null // Yeni logo seçilene kadar null
    
    // Set preview if logo exists (but don't set selectedFile to a fake File object)
    if (company.company_logo) {
      previewUrl.value = company.company_logo
      // Display için bir flag kullan, File objesi değil
      selectedFile.value = { name: 'Mevcut logo', isExisting: true }
    } else {
      selectedFile.value = null
      previewUrl.value = ''
    }
  } else {
    // Add mode - reset everything
    editingCompany.value = null
    resetForm()
  }
  
  await fetchCrawlers()
  await fetchServers()
  await fetchProxies()
}

const closeModal = () => {
  showModal.value = false
  editingCompany.value = null
  resetForm()
}

const resetForm = () => {
  form.company_name = ''
  form.company_logo = null
  form.company_site = ''
  form.crawler_id = ''
  form.server_id = 1
  form.screenshot_required = false
  form.is_marketplace = false
  form.use_proxy = false
  form.proxy_id = null
  selectedFile.value = null
  previewUrl.value = ''
  isDragOver.value = false
  editingCompany.value = null
}

// File handling
const selectFile = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (event) => {
  event.preventDefault()
  isDragOver.value = false
  
  const files = event.dataTransfer.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

const processFile = (file) => {
  // Validate file type
  if (!file.type.startsWith('image/')) {
    alert('Lütfen sadece resim dosyası seçin.')
    return
  }
  
  // Validate file size (10MB)
  if (file.size > 10 * 1024 * 1024) {
    alert('Dosya boyutu 10MB\'dan küçük olmalıdır.')
    return
  }
  
  selectedFile.value = file
  form.company_logo = file
  
  // Create preview URL
  previewUrl.value = URL.createObjectURL(file)
}

const removeFile = () => {
  selectedFile.value = null
  form.company_logo = null
  previewUrl.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// API functions
const fetchCompanies = async () => {
  isLoading.value = true
  try {
    const companiesApi = useCompaniesApi()
    const response = await companiesApi.list()
    companies.value = response.data || response
  } catch (error) {
    console.error('Firmalar yüklenirken hata:', error)
  } finally {
    isLoading.value = false
  }
}

const fetchCrawlers = async () => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('crawlers.list'))
    crawlers.value = response.data || response
  } catch (error) {
    console.error('Crawlers yüklenirken hata:', error)
  }
}

const fetchServers = async () => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('servers.list'))
    servers.value = response.data || response
  } catch (error) {
    console.error('Servers yüklenirken hata:', error)
  }
}

const fetchProxies = async () => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get('/proxy-settings')
    proxies.value = response.data || response
  } catch (error) {
    console.error('Proxy\'ler yüklenirken hata:', error)
  }
}

const submitForm = async () => {
  isSubmitting.value = true
  
  try {
    const companiesApi = useCompaniesApi()
    const formData = new FormData()
    formData.append('company_name', form.company_name)
    formData.append('company_site', form.company_site)
    formData.append('crawler_id', form.crawler_id)
    formData.append('server_id', form.server_id)
    formData.append('screenshot_required', form.screenshot_required ? '1' : '0')
    formData.append('is_marketplace', form.is_marketplace ? '1' : '0')
    formData.append('use_proxy', form.use_proxy ? '1' : '0')
    if (form.proxy_id) {
      formData.append('proxy_id', form.proxy_id)
    }
    
    // Sadece gerçek bir File objesi varsa company_logo ekle
    // Edit modunda mevcut logo varsa ve değiştirilmediyse ekleme
    if (form.company_logo && form.company_logo instanceof File) {
      console.log('📎 Logo dosyası ekleniyor:', {
        name: form.company_logo.name,
        size: form.company_logo.size,
        type: form.company_logo.type
      })
      formData.append('company_logo', form.company_logo)
    } else {
      console.log('⚠️ Logo dosyası eklenmiyor:', {
        hasLogo: !!form.company_logo,
        isFile: form.company_logo instanceof File,
        logoValue: form.company_logo
      })
    }
    
    // FormData içeriğini debug için logla
    console.log('📤 FormData içeriği:')
    for (let [key, value] of formData.entries()) {
      if (value instanceof File) {
        console.log(`  ${key}:`, `File(${value.name}, ${value.size} bytes)`)
      } else {
        console.log(`  ${key}:`, value)
      }
    }
    
    if (editingCompany.value) {
      // Laravel'de PUT request için _method field ekle
      formData.append('_method', 'PUT')
      await companiesApi.update(editingCompany.value.id, formData)
    } else {
      await companiesApi.create(formData)
    }
    
    // Success
    alert(editingCompany.value ? 'Firma başarıyla güncellendi!' : 'Firma başarıyla eklendi!')
    closeModal()
    await fetchCompanies() // Refresh list
    
  } catch (error) {
    console.error('Firma işlemi sırasında hata:', error)
    
    // Hata mesajını daha detaylı göster
    if (error.response?.data?.errors) {
      const errors = Object.values(error.response.data.errors).flat()
      alert('Hata: ' + errors.join('\n'))
    } else if (error.response?.data?.message) {
      alert('Hata: ' + error.response.data.message)
    } else {
      alert('İşlem sırasında bir hata oluştu.')
    }
  } finally {
    isSubmitting.value = false
  }
}

const editCompany = (company) => {
  openModal(company)
}

const deleteCompany = async (company) => {
  if (!confirm(`${company.company_name} firmasını silmek istediğinizden emin misiniz?`)) {
    return
  }
  
  try {
    const companiesApi = useCompaniesApi()
    await companiesApi.delete(company.id)
    
    alert('Firma başarıyla silindi!')
    await fetchCompanies() // Refresh list
    
  } catch (error) {
    console.error('Firma silinirken hata:', error)
    alert('Firma silinirken bir hata oluştu.')
  }
}

// Attributes modal functions
const openAttributesModal = async (company) => {
  selectedCompany.value = company
  showAttributesModal.value = true
  
  await fetchAttributes()
  await fetchCompanyAttributes(company.id)
}

const closeAttributesModal = () => {
  showAttributesModal.value = false
  selectedCompany.value = null
  companyAttributes.value = {}
}

const fetchAttributes = async () => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('attributes.list'))
    attributes.value = response.data || response
  } catch (error) {
    console.error('Attributes yüklenirken hata:', error)
  }
}

const fetchCompanyAttributes = async (companyId) => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('company-attributes.list'), {
      query: { company_id: companyId }
    })
    const data = response.data || response
    
    // Initialize company attributes
    companyAttributes.value = {}
    attributes.value.forEach(attr => {
      const existing = data.find(ca => ca.attribute_id === attr.id)
      companyAttributes.value[attr.id] = {
        enabled: !!existing,
        type: existing?.type || 'class',
        value: existing?.value || ''
      }
    })
  } catch (error) {
    console.error('Company attributes yüklenirken hata:', error)
    // Initialize with default values
    companyAttributes.value = {}
    attributes.value.forEach(attr => {
      companyAttributes.value[attr.id] = {
        enabled: false,
        type: 'class',
        value: ''
      }
    })
  }
}

const getCompanyAttribute = (attributeId) => {
  if (!companyAttributes.value[attributeId]) {
    companyAttributes.value[attributeId] = {
      enabled: false,
      type: 'class',
      value: ''
    }
  }
  return companyAttributes.value[attributeId]
}

const saveAttributes = async () => {
  isSavingAttributes.value = true
  
  try {
    const { $api } = useNuxtApp()
    
    // Prepare data for API
    const attributesToSave = []
    Object.keys(companyAttributes.value).forEach(attributeId => {
      const attr = companyAttributes.value[attributeId]
      if (attr.enabled && attr.value.trim()) {
        attributesToSave.push({
          attribute_id: parseInt(attributeId),
          type: attr.type,
          value: attr.value.trim()
        })
      }
    })
    
    await $api.post($api.getEndpoint('company-attributes.create'), {
      company_id: selectedCompany.value.id,
      attributes: attributesToSave
    })
    
    alert('Attribute ayarları başarıyla kaydedildi!')
    closeAttributesModal()
    
  } catch (error) {
    console.error('Attributes kaydedilirken hata:', error)
    alert('Attributes kaydedilirken bir hata oluştu.')
  } finally {
    isSavingAttributes.value = false
  }
}

// Navigation functions
const navigateToAttributeCheck = () => {
  navigateTo('/dashboard/company-attribute-check')
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
    
    // Paralel olarak verileri yükle
    await Promise.all([
      fetchCompanies(),
      fetchCrawlers(),
      fetchServers()
    ])
  } catch (error) {
    console.error('Page initialization failed:', error)
    isCheckingPermissions.value = false
  }
  
  // Drag and drop event listeners
  document.addEventListener('dragenter', (e) => {
    e.preventDefault()
    isDragOver.value = true
  })
  
  document.addEventListener('dragleave', (e) => {
    e.preventDefault()
    if (!e.relatedTarget) {
      isDragOver.value = false
    }
  })
  
  document.addEventListener('drop', (e) => {
    e.preventDefault()
    isDragOver.value = false
  })
})
</script>