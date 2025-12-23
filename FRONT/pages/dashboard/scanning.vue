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
  <div v-else-if="!hasPermission('scan.show')" class="flex items-center justify-center min-h-screen">
    <div class="text-center">
      <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Erişim Reddedildi</h1>
      <p class="text-gray-600 mb-6">Bu sayfaya erişim yetkiniz bulunmuyor.</p>
      <NuxtLink to="/dashboard" class="inline-flex items-center px-4 py-2 bg-apple-blue text-white rounded-lg hover:bg-blue-700 transition-colors">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Ana Sayfaya Dön
      </NuxtLink>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="p-6">
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Tarama</h1>
      <p class="text-gray-600">Ürün tarama işlemlerini buradan yönetebilirsiniz.</p>
    </div>

    <!-- Quick Scan Section -->
    <div v-if="hasPermission('scan.fast')" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold text-gray-900">Hızlı Tarama</h2>
        <!-- Dropdown Button -->
        <div class="relative" ref="scanDropdownRef">
          <button
            @click.stop="showScanDropdown = !showScanDropdown"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors shadow-sm"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <span>Tarama İşlemi</span>
            <svg class="w-4 h-4 transition-transform" :class="{ 'rotate-180': showScanDropdown }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <!-- Dropdown Menu -->
          <div
            v-if="showScanDropdown"
            class="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50"
          >
            <button
              v-if="false"
              @click="showQuickScanModal = true; showScanDropdown = false"
              class="w-full px-4 py-3 flex items-center gap-3 text-left hover:bg-gray-50 transition-colors"
            >
              <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">Hızlı Tarama</p>
                <p class="text-xs text-gray-500">Genel veya firma bazlı tarama</p>
              </div>
            </button>

            <button
              v-if="false"
              @click="showDemoScanModal = true; showScanDropdown = false"
              class="w-full px-4 py-3 flex items-center gap-3 text-left hover:bg-gray-50 transition-colors"
            >
              <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">Demo Tarama</p>
                <p class="text-xs text-gray-500">Kendi URL'lerinizle test taraması</p>
              </div>
            </button>

            <button
              v-if="false"
              @click="showProfileScanModal = true; showScanDropdown = false"
              class="w-full px-4 py-3 flex items-center gap-3 text-left hover:bg-gray-50 transition-colors"
            >
              <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">Profil Tarama</p>
                <p class="text-xs text-gray-500">Özel analiz profili ile tarama</p>
              </div>
            </button>

            <button
              @click="showChromeScanModal = true; showScanDropdown = false"
              class="w-full px-4 py-3 flex items-center gap-3 text-left hover:bg-gray-50 transition-colors"
            >
              <div class="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">Chrome Tarama</p>
                <p class="text-xs text-gray-500">Chrome extension ile tarama</p>
              </div>
            </button>

            <div class="border-t border-gray-200 my-1"></div>

            <button
              @click="showPurgeQueuesModal = true; showScanDropdown = false"
              class="w-full px-4 py-3 flex items-center gap-3 text-left hover:bg-red-50 transition-colors text-red-600"
            >
              <div class="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium">Taramaları Durdur</p>
                <p class="text-xs text-red-500">Tüm aktif taramaları sonlandır</p>
              </div>
            </button>
          </div>
        </div>
      </div>
      <p class="text-gray-600 text-sm">Anlık tarama işlemi başlatır. Demo tarama her firmadan en fazla 10 URL ile sınırlıdır.</p>
    </div>

    <!-- Cron Job Management Section -->
    <div v-if="hasPermission('scan.plan')" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-semibold text-gray-900">Planlı Taramalar (Cron Jobs)</h2>
        <button
          @click="showAddCronModal = true"
          class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Cron Job Ekle
        </button>
      </div>

      <!-- Cron Jobs List -->
      <div v-if="isLoadingCronJobs" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p class="text-gray-500 mt-2">Yükleniyor...</p>
      </div>

      <div v-else-if="cronJobs.length === 0" class="text-center py-8">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Henüz cron job yok</h3>
        <p class="text-gray-500">İlk cron job'ınızı eklemek için yukarıdaki butona tıklayın.</p>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="cronJob in cronJobs"
          :key="cronJob.id"
          class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 class="font-medium text-gray-900">
                  {{ cronJob.scan_type === 'all' ? 'Genel Tarama' : (cronJob.company ? cronJob.company.company_name : 'Bilinmeyen Firma') }}
                </h3>
                <p class="text-sm text-gray-500">Her gün {{ cronJob.time }} saatinde çalışır</p>
                <div class="flex items-center gap-2 mt-1">
                  <span :class="[
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                    cronJob.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  ]">
                    {{ cronJob.active ? 'Aktif' : 'Pasif' }}
                  </span>
                  <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                    {{ cronJob.scan_type === 'all' ? 'Genel' : 'Firma Bazlı' }}
                  </span>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button
                @click="editCronJob(cronJob)"
                class="text-blue-600 hover:text-blue-700 p-2 rounded-lg hover:bg-blue-50 transition-colors"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button
                @click="toggleCronJob(cronJob.id)"
                :class="[
                  'p-2 rounded-lg transition-colors',
                  cronJob.active 
                    ? 'text-orange-600 hover:text-orange-700 hover:bg-orange-50' 
                    : 'text-green-600 hover:text-green-700 hover:bg-green-50'
                ]"
              >
                <svg v-if="cronJob.active" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
              <button
                @click="deleteCronJob(cronJob.id)"
                class="text-red-600 hover:text-red-700 p-2 rounded-lg hover:bg-red-50 transition-colors"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Scan Operations History Section -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-semibold text-gray-900">İşlem Geçmişi</h2>
        <button
          @click="loadScanOperations"
          class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Yenile
        </button>
      </div>

      <!-- Operations Table -->
      <div v-if="isLoadingOperations" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p class="text-gray-500 mt-2">Yükleniyor...</p>
      </div>

      <div v-else-if="scanOperations.length === 0" class="text-center py-8">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Henüz işlem geçmişi yok</h3>
        <p class="text-gray-500">Tarama işlemleri burada görüntülenecek.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Job ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">İşlem Tarihi</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Durum</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">İlerleme</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">İşlemler</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="operation in scanOperations" :key="operation.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                  #{{ operation.id }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatDateTime(operation.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span 
                  v-if="getStatusNormalized(operation.status) === 'pending'"
                  class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800"
                >
                  Başlamadı
                </span>
                <span 
                  v-else-if="getStatusNormalized(operation.status) === 'worker'"
                  class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800 animate-pulse"
                >
                  İşleniyor
                </span>
                <span 
                  v-else-if="getStatusNormalized(operation.status) === 'finish'"
                  class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800"
                >
                  Bitti
                </span>
                <span 
                  v-else
                  class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800"
                >
                  {{ operation.status || 'Bilinmeyen' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <!-- İlerleme bar'ı sadece worker durumunda göster -->
                <div v-if="getStatusNormalized(operation.status) === 'worker'" class="w-full">
                  <div class="flex items-center gap-2">
                    <div class="flex-1 bg-gray-200 rounded-full h-2.5">
                      <div 
                        class="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                        :style="{ width: getProgressPercentage(operation) + '%' }"
                      ></div>
                    </div>
                    <span class="text-xs font-medium text-gray-700 min-w-[3rem] text-right">
                      {{ getProgressPercentage(operation) }}%
                    </span>
                  </div>
                  <div class="text-xs text-gray-500 mt-1">
                    {{ jobFoundCounts[operation.id] || 0 }} / {{ operation.total_urls || 0 }}
                  </div>
                </div>
                <span v-else-if="getStatusNormalized(operation.status) === 'finish'" class="text-xs text-gray-500">
                  {{ jobFoundCounts[operation.id] || 0 }} / {{ operation.total_urls || 0 }}
                </span>
                <span v-else class="text-xs text-gray-400">-</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center gap-2">
                  <button
                    @click="showJobDetails(operation.id)"
                    class="text-blue-600 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 px-3 py-1 rounded-lg transition-colors"
                  >
                    Detay
                  </button>
                  <button
                    @click="showMatchingModalFunc(operation.id)"
                    class="text-green-600 hover:text-green-900 bg-green-50 hover:bg-green-100 px-3 py-1 rounded-lg transition-colors"
                  >
                    Eşleştirme
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="scanOperations.length > 0" class="mt-6 flex items-center justify-between">
        <!-- Per page selector -->
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-700">Sayfa başına:</span>
          <select 
            v-model="perPage" 
            @change="changePerPage(perPage)"
            class="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="5">5</option>
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
          </select>
          <span class="text-sm text-gray-500">
            Toplam {{ totalItems }} kayıt
          </span>
        </div>

        <!-- Pagination controls -->
        <div class="flex items-center gap-2">
          <button
            @click="prevPage"
            :disabled="!pagination.has_prev"
            :class="[
              'px-3 py-1 text-sm rounded-lg transition-colors',
              pagination.has_prev 
                ? 'bg-gray-100 hover:bg-gray-200 text-gray-700' 
                : 'bg-gray-50 text-gray-400 cursor-not-allowed'
            ]"
          >
            Önceki
          </button>

          <!-- Page numbers -->
          <div class="flex items-center gap-1">
            <button
              v-for="page in Math.min(5, totalPages)"
              :key="page"
              @click="goToPage(page)"
              :class="[
                'px-3 py-1 text-sm rounded-lg transition-colors',
                currentPage === page
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              ]"
            >
              {{ page }}
            </button>
            
            <span v-if="totalPages > 5" class="px-2 text-gray-500">...</span>
            
            <button
              v-if="totalPages > 5 && currentPage < totalPages - 2"
              @click="goToPage(totalPages)"
              class="px-3 py-1 text-sm rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors"
            >
              {{ totalPages }}
            </button>
          </div>

          <button
            @click="nextPage"
            :disabled="!pagination.has_next"
            :class="[
              'px-3 py-1 text-sm rounded-lg transition-colors',
              pagination.has_next 
                ? 'bg-gray-100 hover:bg-gray-200 text-gray-700' 
                : 'bg-gray-50 text-gray-400 cursor-not-allowed'
            ]"
          >
            Sonraki
          </button>
        </div>
      </div>
    </div>

    <!-- Quick Scan Modal -->
    <div
      v-if="showQuickScanModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeQuickScanModal"
    >
      <div class="bg-white rounded-xl p-6 w-full max-w-md mx-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">
            {{ isChromeScan ? 'Chrome Extension - Hızlı Tarama' : 'Hızlı Tarama' }}
          </h3>
          <button @click="closeQuickScanModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div v-if="isChromeScan" class="mb-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <p class="text-sm text-orange-700">
              Chrome Extension API kullanılarak tarama başlatılacak.
            </p>
          </div>
        </div>

        <form @submit.prevent="startQuickScan" class="space-y-4">
          <!-- Company Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Tarama Türü</label>
            <select
              v-model="quickScanCompany"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Genel</option>
              <option
                v-for="company in companies"
                :key="company.id"
                :value="company.id"
              >
                {{ company.company_name }}
              </option>
            </select>
          </div>

          <div class="flex gap-3 pt-4">
            <button
              type="button"
              @click="closeQuickScanModal"
              class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              İptal
            </button>
            <button
              type="submit"
              :disabled="isQuickScanLoading"
              class="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white px-4 py-2 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <svg v-if="isQuickScanLoading" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isQuickScanLoading ? 'Başlatılıyor...' : 'Tarama Başlat' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Profile Scan Modal -->
    <div
      v-if="showProfileScanModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeProfileScanModal"
    >
      <div class="bg-white rounded-xl p-6 w-full max-w-md mx-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">
            {{ isChromeScan ? 'Chrome Extension - Profil Tarama' : 'Profil Tarama' }}
          </h3>
          <button @click="closeProfileScanModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div v-if="isChromeScan" class="mb-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <p class="text-sm text-orange-700">
              Chrome Extension API kullanılarak tarama başlatılacak.
            </p>
          </div>
        </div>

        <form @submit.prevent="startProfileScan" class="space-y-4">
          <!-- Profile Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Özel Analiz</label>
            <select
              v-model="profileScanProfileId"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">Profil Seçin</option>
              <option
                v-for="profile in profiles"
                :key="profile.id"
                :value="profile.id"
              >
                {{ profile.name }}
              </option>
            </select>
          </div>

          <div class="flex gap-3 pt-4">
            <button
              type="button"
              @click="closeProfileScanModal"
              class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              İptal
            </button>
            <button
              type="submit"
              :disabled="isProfileScanLoading"
              class="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-green-300 text-white px-4 py-2 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <svg v-if="isProfileScanLoading" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isProfileScanLoading ? 'Başlatılıyor...' : 'Tarama Başlat' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Chrome Scan Modal -->
    <div
      v-if="showChromeScanModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeChromeScanModal"
    >
      <div class="bg-white rounded-xl p-6 w-full max-w-md mx-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Chrome Tarama</h3>
          <button @click="closeChromeScanModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="mb-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-sm text-orange-700">
              Chrome extension ile tarama yapmak için bir tarama türü seçin.
            </p>
          </div>
        </div>

        <div class="space-y-3">
          <button
            @click="openQuickScanFromChrome"
            class="w-full px-4 py-4 flex items-center gap-4 text-left hover:bg-blue-50 border-2 border-gray-200 hover:border-blue-300 rounded-lg transition-all"
          >
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="flex-1">
              <p class="text-base font-semibold text-gray-900">Hızlı Tarama</p>
              <p class="text-sm text-gray-500 mt-1">Genel veya firma bazlı tarama</p>
            </div>
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>

          <button
            @click="openProfileScanFromChrome"
            class="w-full px-4 py-4 flex items-center gap-4 text-left hover:bg-green-50 border-2 border-gray-200 hover:border-green-300 rounded-lg transition-all"
          >
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div class="flex-1">
              <p class="text-base font-semibold text-gray-900">Profil Tarama</p>
              <p class="text-sm text-gray-500 mt-1">Özel analiz profili ile tarama</p>
            </div>
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <div class="flex gap-3 pt-4 mt-4">
          <button
            type="button"
            @click="closeChromeScanModal"
            class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            İptal
          </button>
        </div>
      </div>
    </div>

    <!-- Demo Scan Modal -->
    <div
      v-if="showDemoScanModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto"
      style="display: none;"
      @click.self="closeDemoScanModal"
    >
      <div class="bg-white rounded-xl p-6 w-full max-w-2xl mx-4 my-8">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Demo Tarama</h3>
          <button @click="closeDemoScanModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="mb-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-sm text-purple-700">
              Kendi URL'lerinizi girerek demo tarama yapabilirsiniz. Her satıra bir URL yazın.
            </p>
          </div>
        </div>

        <form @submit.prevent="startDemoScan" class="space-y-4">
          <!-- URL Input -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              URL'ler
              <span class="text-gray-500 font-normal">(Her satıra bir URL)</span>
            </label>
            <textarea
              v-model="demoScanUrls"
              rows="10"
              required
              placeholder="https://example.com/product1&#10;https://example.com/product2&#10;https://example.com/product3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent font-mono text-sm"
            ></textarea>
            <p class="text-xs text-gray-500 mt-1">
              {{ demoScanUrls ? demoScanUrls.split('\n').filter(u => u.trim()).length : 0 }} URL
            </p>
          </div>

          <!-- Company Selection (Optional) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Firma 
              <span class="text-gray-500 font-normal">(Opsiyonel - URL'ler hangi firmaya ait?)</span>
            </label>
            <select
              v-model="demoScanCompany"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">Belirtilmemiş</option>
              <option
                v-for="company in companies"
                :key="company.id"
                :value="company.id"
              >
                {{ company.company_name }}
              </option>
            </select>
          </div>

          <div class="flex gap-3 pt-4">
            <button
              type="button"
              @click="closeDemoScanModal"
              class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              İptal
            </button>
            <button
              type="submit"
              :disabled="isDemoScanLoading"
              class="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-300 text-white px-4 py-2 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <svg v-if="isDemoScanLoading" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isDemoScanLoading ? 'Başlatılıyor...' : 'Demo Tarama Başlat' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add/Edit Cron Job Modal -->
    <div
      v-if="showAddCronModal || showEditCronModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeCronModal"
    >
      <div class="bg-white rounded-xl p-6 w-full max-w-md mx-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">
            {{ showEditCronModal ? 'Cron Job Düzenle' : 'Cron Job Ekle' }}
          </h3>
          <button @click="closeCronModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="saveCronJob" class="space-y-4">
          <!-- Time Input -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Saat</label>
            <input
              v-model="cronJobForm.time"
              type="time"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <!-- Scan Type Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Tarama Türü</label>
            <select
              v-model="cronJobForm.scan_type"
              required
              @change="onScanTypeChange"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Genel Tarama</option>
              <option value="company">Firma Bazlı Tarama</option>
            </select>
          </div>

          <!-- Company Selection (only if company type selected) -->
          <div v-if="cronJobForm.scan_type === 'company'">
            <label class="block text-sm font-medium text-gray-700 mb-2">Firma</label>
            <select
              v-model="cronJobForm.company_id"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Firma Seçin</option>
              <option
                v-for="company in companies"
                :key="company.id"
                :value="company.id"
              >
                {{ company.company_name }}
              </option>
            </select>
          </div>

          <!-- Active Status -->
          <div>
            <label class="flex items-center">
              <input
                v-model="cronJobForm.active"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              />
              <span class="ml-2 text-sm text-gray-700">Aktif</span>
            </label>
          </div>

          <div class="flex gap-3 pt-4">
            <button
              type="button"
              @click="closeCronModal"
              class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              İptal
            </button>
            <button
              type="submit"
              :disabled="isSavingCronJob"
              class="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white px-4 py-2 rounded-lg transition-colors"
            >
              {{ isSavingCronJob ? 'Kaydediliyor...' : (showEditCronModal ? 'Güncelle' : 'Ekle') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Job Details Modal -->
    <div
      v-if="showJobDetailsModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeJobDetailsModal"
    >
      <div class="bg-white rounded-xl p-6 w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Job Detayları - #{{ selectedJobId }}</h3>
          <button @click="closeJobDetailsModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div v-if="isLoadingJobDetails" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p class="text-gray-500 mt-2">Yükleniyor...</p>
        </div>

        <div v-else-if="jobDetails">
          <!-- Job Info -->
          <div class="bg-gray-50 rounded-lg p-4 mb-6">
            <h4 class="font-medium text-gray-900 mb-3">Job Bilgileri</h4>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-500">Job ID:</span>
                <span class="ml-2 font-medium">{{ jobDetails.job_data.id }}</span>
              </div>
              <div>
                <span class="text-gray-500">Oluşturulma Tarihi:</span>
                <span class="ml-2 font-medium">{{ formatDateTime(jobDetails.job_data.created_at) }}</span>
              </div>
              <div>
                <span class="text-gray-500">Toplam URL:</span>
                <span class="ml-2 font-medium">{{ jobDetails.job_data.count }}</span>
              </div>
              <div>
                <span class="text-gray-500">JSON Dosyası:</span>
                <span class="ml-2 font-medium text-blue-600">{{ jobDetails.job_data.json_path }}</span>
              </div>
            </div>
            
            <!-- İlerleme Durumu (RabbitMQ Queue Status) -->
            <div class="mt-6">
              <div class="flex items-center justify-between mb-3">
                <h4 class="font-medium text-gray-900">RabbitMQ Queue Durumu</h4>
                <button
                  @click="loadJobStatus(selectedJobId)"
                  :disabled="isLoadingJobStatus"
                  class="text-blue-600 hover:text-blue-700 text-sm flex items-center gap-1"
                >
                  <svg v-if="isLoadingJobStatus" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <svg v-else class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>Yenile</span>
                </button>
              </div>

              <!-- Progress Bar -->
              <div v-if="jobStatus" class="mb-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-gray-700">İlerleme</span>
                  <span class="text-sm text-gray-600">{{ jobStatus.progress.percentage }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2.5">
                  <div 
                    class="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                    :style="{ width: jobStatus.progress.percentage + '%' }"
                  ></div>
                </div>
                <div class="flex items-center justify-between mt-2 text-xs text-gray-500">
                  <span>İşlenen: {{ jobStatus.progress.processed }} / {{ jobStatus.total_urls }}</span>
                  <span>Kalan: {{ jobStatus.progress.remaining }}</span>
                </div>
              </div>

              <!-- Queue Statistics -->
              <div v-if="jobStatus" class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                <div class="bg-blue-50 rounded-lg p-3">
                  <div class="text-xs text-blue-600 font-medium mb-1">Bekleyen</div>
                  <div class="text-lg font-bold text-blue-900">{{ jobStatus.progress.pending }}</div>
                </div>
                <div class="bg-yellow-50 rounded-lg p-3">
                  <div class="text-xs text-yellow-600 font-medium mb-1">İşleniyor</div>
                  <div class="text-lg font-bold text-yellow-900">{{ jobStatus.progress.processing }}</div>
                </div>
                <div class="bg-green-50 rounded-lg p-3">
                  <div class="text-xs text-green-600 font-medium mb-1">Tamamlandı</div>
                  <div class="text-lg font-bold text-green-900">{{ jobStatus.progress.completed }}</div>
                </div>
                <div class="bg-red-50 rounded-lg p-3">
                  <div class="text-xs text-red-600 font-medium mb-1">Hata</div>
                  <div class="text-lg font-bold text-red-900">{{ jobStatus.progress.error }}</div>
                </div>
              </div>

              <!-- Queue Details Table -->
              <div v-if="jobStatus && jobStatus.stats.queues.length > 0" class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200 text-sm">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Queue</th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Server</th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Durum</th>
                      <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Job Mesajı</th>
                      <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Toplam</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="(queue, idx) in jobStatus.stats.queues" :key="idx" class="hover:bg-gray-50">
                      <td class="px-3 py-2 text-gray-900 font-mono text-xs">{{ queue.queue }}</td>
                      <td class="px-3 py-2 text-gray-600">
                        <span class="inline-flex px-2 py-0.5 text-xs font-semibold rounded-full bg-gray-100">
                          {{ queue.server }}
                        </span>
                      </td>
                      <td class="px-3 py-2">
                        <span :class="[
                          'inline-flex px-2 py-0.5 text-xs font-semibold rounded-full',
                          queue.type === 'completed' ? 'bg-green-100 text-green-800' :
                          queue.type === 'error' ? 'bg-red-100 text-red-800' :
                          'bg-blue-100 text-blue-800'
                        ]">
                          {{ queue.type === 'completed' ? 'Tamamlandı' : 
                             queue.type === 'error' ? 'Hata' : 'İşleniyor' }}
                        </span>
                      </td>
                      <td class="px-3 py-2 text-right font-medium text-gray-900">{{ queue.count }}</td>
                      <td class="px-3 py-2 text-right text-gray-500">
                        {{ queue.total_messages }}
                        <span v-if="queue.unacked > 0" class="text-xs text-yellow-600 ml-1">
                          ({{ queue.unacked }} unacked)
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- No Queue Status -->
              <div v-else-if="jobStatus && jobStatus.stats.queues.length === 0" class="text-center py-4 text-gray-500 text-sm">
                Bu job için queue'da mesaj bulunamadı. İşlem tamamlanmış olabilir.
              </div>

              <!-- Loading State -->
              <div v-else-if="isLoadingJobStatus" class="text-center py-4">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                <p class="text-gray-500 text-sm mt-2">Queue durumu kontrol ediliyor...</p>
              </div>

              <!-- Error State -->
              <div v-if="jobStatusError" class="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
                {{ jobStatusError }}
              </div>
            </div>

            <div class="mt-4">
              <button
                @click="loadJobJson(selectedJobId)"
                :disabled="isLoadingJobJson"
                class="bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-300 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
              >
                <svg v-if="isLoadingJobJson" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ isLoadingJobJson ? 'Yükleniyor...' : 'Veriyi Gör' }}</span>
              </button>
              <p v-if="jobJsonError" class="text-red-600 text-sm mt-2">{{ jobJsonError }}</p>
            </div>
          </div>

          <!-- Job Details Table -->
          <div v-if="jobDetails.job_details && jobDetails.job_details.length > 0">
            <h4 class="font-medium text-gray-900 mb-3">Job Detayları</h4>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company ID</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product ID</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Application ID</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Server</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">URL</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">MPN</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Screenshot</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Marketplace</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="detail in jobDetails.job_details" :key="detail.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ detail.company_id }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ detail.product_id }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ detail.application_id }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ detail.server_name }}</td>
                    <td class="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">{{ detail.url }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ detail.npm }}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span :class="[
                        'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                        detail.screenshot ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      ]">
                        {{ detail.screenshot ? 'Evet' : 'Hayır' }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span :class="[
                        'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                        detail.marketplace ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                      ]">
                        {{ detail.marketplace ? 'Evet' : 'Hayır' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Parsed JSON Table -->
          <div v-if="jobJsonData" class="mt-6">
            <div class="flex items-center justify-between mb-3">
              <h4 class="font-medium text-gray-900">JSON’dan Anlamlandırılan Veriler</h4>
              <button
                @click="showJsonCode = !showJsonCode"
                class="text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-2 text-sm"
              >
                <svg v-if="!showJsonCode" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <span>{{ showJsonCode ? 'Tabloya Dön' : 'JSON Kodu Gör' }}</span>
              </button>
            </div>
            
            <!-- Table View -->
            <div v-if="!showJsonCode" class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50" v-if="jobJsonHeaders.length">
                  <tr>
                    <th v-for="h in jobJsonHeaders" :key="h" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ h }}</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="(row, idx) in jobJsonRows" :key="idx" class="hover:bg-gray-50">
                    <td v-for="h in jobJsonHeaders" :key="h" class="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                      {{ formatCell(row[h]) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <!-- JSON Code View -->
            <div v-else class="bg-gray-900 rounded-lg p-4 overflow-auto max-h-[500px] relative">
              <button
                @click="copyJsonCode"
                class="absolute top-2 right-2 text-gray-400 hover:text-gray-100 bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-2 text-sm z-10"
                :title="jsonCopied ? 'Kopyalandı!' : 'Kodu Kopyala'"
              >
                <svg v-if="!jsonCopied" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span>{{ jsonCopied ? 'Kopyalandı!' : 'Kodu Kopyala' }}</span>
              </button>
              <pre class="text-sm text-gray-100 whitespace-pre-wrap"><code>{{ formattedJsonCode }}</code></pre>
            </div>
          </div>

          <div v-else class="text-center py-8">
            <p class="text-gray-500">Bu job için detay bulunamadı.</p>
          </div>
        </div>

        <div v-else class="text-center py-8">
          <p class="text-gray-500">Job detayları yüklenirken hata oluştu.</p>
        </div>
      </div>
    </div>

    <!-- Matching Modal -->
    <div
      v-if="showMatchingModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeMatchingModal"
    >
      <div class="bg-white rounded-xl p-6 w-full max-w-6xl mx-4 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Eşleştirme - Job #{{ matchingJobId }}</h3>
          <button @click="closeMatchingModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div v-if="isLoadingMatching" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p class="text-gray-500 mt-2">Yükleniyor...</p>
        </div>

        <div v-else>
          <!-- Veriyi Gör Butonu -->
          <div class="mb-4">
            <button
              @click="performMatching"
              class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              Veriyi Gör
            </button>
          </div>

          <!-- Eşleştirme Sonuçları -->
          <div v-if="matchingResults.found.length > 0 || matchingResults.notFound.length > 0 || matchingResults.noData.length > 0" class="space-y-6">
            <!-- Bulunan Veriler -->
            <div v-if="matchingResults.found.length > 0">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-md font-semibold text-green-700">
                  ✅ Bulunan Veriler ({{ matchingResults.found.length }})
                </h4>
                <div class="flex items-center gap-2">
                  <span class="text-sm text-gray-500">Sayfa başına:</span>
                  <select 
                    v-model.number="matchingFoundPerPage" 
                    @change="matchingFoundCurrentPage = 1"
                    class="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    <option :value="10">10</option>
                    <option :value="25">25</option>
                    <option :value="50">50</option>
                    <option :value="100">100</option>
                  </select>
                </div>
              </div>
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-green-50">
                    <tr>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">data_id</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">process_id</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Scraper Data</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="item in paginatedFound" :key="item.data_id" class="hover:bg-gray-50">
                      <td class="px-4 py-3 text-sm text-gray-900">{{ item.data_id }}</td>
                      <td class="px-4 py-3 text-sm text-gray-900">{{ item.process_id }}</td>
                      <td class="px-4 py-3 text-sm">
                        <button
                          @click="viewScraperData(item.process_id)"
                          class="text-blue-600 hover:text-blue-900 underline"
                        >
                          Görüntüle
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <!-- Pagination -->
              <div v-if="matchingFoundTotalPages > 1" class="mt-4 flex items-center justify-between">
                <div class="text-sm text-gray-500">
                  Sayfa {{ matchingFoundCurrentPage }} / {{ matchingFoundTotalPages }} (Toplam {{ matchingResults.found.length }} kayıt)
                </div>
                <div class="flex items-center gap-2">
                  <button
                    @click="matchingFoundCurrentPage = Math.max(1, matchingFoundCurrentPage - 1)"
                    :disabled="matchingFoundCurrentPage === 1"
                    :class="[
                      'px-3 py-1 text-sm rounded-lg transition-colors',
                      matchingFoundCurrentPage === 1 
                        ? 'bg-gray-50 text-gray-400 cursor-not-allowed' 
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                    ]"
                  >
                    Önceki
                  </button>
                  <button
                    @click="matchingFoundCurrentPage = Math.min(matchingFoundTotalPages, matchingFoundCurrentPage + 1)"
                    :disabled="matchingFoundCurrentPage === matchingFoundTotalPages"
                    :class="[
                      'px-3 py-1 text-sm rounded-lg transition-colors',
                      matchingFoundCurrentPage === matchingFoundTotalPages 
                        ? 'bg-gray-50 text-gray-400 cursor-not-allowed' 
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                    ]"
                  >
                    Sonraki
                  </button>
                </div>
              </div>
            </div>

            <!-- Veri Alınamamış -->
            <div v-if="matchingResults.noData.length > 0">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-md font-semibold text-orange-700">
                  ⚠️ Veri Alınamamış ({{ matchingResults.noData.length }})
                </h4>
                <div class="flex items-center gap-2">
                  <span class="text-sm text-gray-500">Sayfa başına:</span>
                  <select 
                    v-model.number="matchingNoDataPerPage" 
                    @change="matchingNoDataCurrentPage = 1"
                    class="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  >
                    <option :value="10">10</option>
                    <option :value="25">25</option>
                    <option :value="50">50</option>
                    <option :value="100">100</option>
                  </select>
                </div>
              </div>
              <div class="mb-4 p-4 bg-orange-50 border border-orange-200 rounded-lg">
                <p class="text-sm text-orange-700">
                  Bu veriler scraper_data tablosunda mevcut ancak scraped_data alanı boş. Bu veriler error queue'ya gönderilmiş olmalı.
                </p>
              </div>
              <div class="overflow-x-auto mb-4">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-orange-50">
                    <tr>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">data_id</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">process_id</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">İşlem</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="item in paginatedNoData" :key="item.data_id" class="hover:bg-gray-50">
                      <td class="px-4 py-3 text-sm text-gray-900">{{ item.data_id }}</td>
                      <td class="px-4 py-3 text-sm text-gray-900">{{ item.process_id }}</td>
                      <td class="px-4 py-3 text-sm">
                        <button
                          @click="retryScan(item.data_id)"
                          class="text-orange-600 hover:text-orange-900 bg-orange-50 hover:bg-orange-100 px-3 py-1 rounded-lg transition-colors"
                        >
                          Tekrar Tara
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <!-- Pagination -->
              <div v-if="matchingNoDataTotalPages > 1" class="mt-4 flex items-center justify-between">
                <div class="text-sm text-gray-500">
                  Sayfa {{ matchingNoDataCurrentPage }} / {{ matchingNoDataTotalPages }} (Toplam {{ matchingResults.noData.length }} kayıt)
                </div>
                <div class="flex items-center gap-2">
                  <button
                    @click="matchingNoDataCurrentPage = Math.max(1, matchingNoDataCurrentPage - 1)"
                    :disabled="matchingNoDataCurrentPage === 1"
                    :class="[
                      'px-3 py-1 text-sm rounded-lg transition-colors',
                      matchingNoDataCurrentPage === 1 
                        ? 'bg-gray-50 text-gray-400 cursor-not-allowed' 
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                    ]"
                  >
                    Önceki
                  </button>
                  <button
                    @click="matchingNoDataCurrentPage = Math.min(matchingNoDataTotalPages, matchingNoDataCurrentPage + 1)"
                    :disabled="matchingNoDataCurrentPage === matchingNoDataTotalPages"
                    :class="[
                      'px-3 py-1 text-sm rounded-lg transition-colors',
                      matchingNoDataCurrentPage === matchingNoDataTotalPages 
                        ? 'bg-gray-50 text-gray-400 cursor-not-allowed' 
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                    ]"
                  >
                    Sonraki
                  </button>
                </div>
              </div>
            </div>

            <!-- Bulunamayan Veriler -->
            <div v-if="matchingResults.notFound.length > 0">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-md font-semibold text-red-700">
                  ❌ Bulunamayan Veriler ({{ matchingResults.notFound.length }})
                </h4>
                <div class="flex items-center gap-2">
                  <button
                    @click="downloadNotFoundJson"
                    class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2 text-sm"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    JSON İndir
                  </button>
                  <span class="text-sm text-gray-500">Sayfa başına:</span>
                  <select 
                    v-model.number="matchingNotFoundPerPage" 
                    @change="matchingNotFoundCurrentPage = 1"
                    class="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  >
                    <option :value="10">10</option>
                    <option :value="25">25</option>
                    <option :value="50">50</option>
                    <option :value="100">100</option>
                  </select>
                </div>
              </div>
              <div class="overflow-x-auto mb-4">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-red-50">
                    <tr>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">data_id</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">İşlem</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="item in paginatedNotFound" :key="item.data_id" class="hover:bg-gray-50">
                      <td class="px-4 py-3 text-sm text-gray-900">{{ item.data_id }}</td>
                      <td class="px-4 py-3 text-sm">
                        <button
                          @click="retryScan(item.data_id)"
                          class="text-orange-600 hover:text-orange-900 bg-orange-50 hover:bg-orange-100 px-3 py-1 rounded-lg transition-colors"
                        >
                          Tekrar Tara
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <!-- Pagination -->
              <div v-if="matchingNotFoundTotalPages > 1" class="mt-4 flex items-center justify-between mb-4">
                <div class="text-sm text-gray-500">
                  Sayfa {{ matchingNotFoundCurrentPage }} / {{ matchingNotFoundTotalPages }} (Toplam {{ matchingResults.notFound.length }} kayıt)
                </div>
                <div class="flex items-center gap-2">
                  <button
                    @click="matchingNotFoundCurrentPage = Math.max(1, matchingNotFoundCurrentPage - 1)"
                    :disabled="matchingNotFoundCurrentPage === 1"
                    :class="[
                      'px-3 py-1 text-sm rounded-lg transition-colors',
                      matchingNotFoundCurrentPage === 1 
                        ? 'bg-gray-50 text-gray-400 cursor-not-allowed' 
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                    ]"
                  >
                    Önceki
                  </button>
                  <button
                    @click="matchingNotFoundCurrentPage = Math.min(matchingNotFoundTotalPages, matchingNotFoundCurrentPage + 1)"
                    :disabled="matchingNotFoundCurrentPage === matchingNotFoundTotalPages"
                    :class="[
                      'px-3 py-1 text-sm rounded-lg transition-colors',
                      matchingNotFoundCurrentPage === matchingNotFoundTotalPages 
                        ? 'bg-gray-50 text-gray-400 cursor-not-allowed' 
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                    ]"
                  >
                    Sonraki
                  </button>
                </div>
              </div>
              <div class="flex gap-2">
                <button
                  @click="retryAllScans"
                  class="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  Tümünü Tekrar Tara
                </button>
              </div>
            </div>

            <!-- Veri Alınamamış - Toplu İşlem -->
            <div v-if="matchingResults.noData.length > 0" class="mt-4">
              <div class="flex gap-2">
                <button
                  @click="retryAllNoDataScans"
                  class="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  Veri Alınamamış Tümünü Tekrar Tara
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Scraper Data Modal -->
    <div
      v-if="showScraperDataModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeScraperDataModal"
    >
      <div class="bg-white rounded-xl p-6 w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Scraper Data - Process ID: {{ selectedScraperData?.process_id }}</h3>
          <button @click="closeScraperDataModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div v-if="selectedScraperData" class="space-y-4">
          <!-- JSON Code View -->
          <div class="bg-gray-900 rounded-lg p-4 overflow-auto max-h-[70vh] relative">
            <button
              @click="copyScraperDataJson"
              class="absolute top-2 right-2 text-gray-400 hover:text-gray-100 bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-2 text-sm z-10"
              :title="scraperDataCopied ? 'Kopyalandı!' : 'Kodu Kopyala'"
            >
              <svg v-if="!scraperDataCopied" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span>{{ scraperDataCopied ? 'Kopyalandı!' : 'Kodu Kopyala' }}</span>
            </button>
            <pre class="text-sm text-gray-100 whitespace-pre-wrap"><code>{{ formattedScraperDataJson }}</code></pre>
          </div>
        </div>
      </div>
    </div>

    <!-- Purge Queues Modal -->
    <div
      v-if="showPurgeQueuesModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closePurgeQueuesModal"
    >
      <div class="bg-white rounded-xl p-6 w-full max-w-md mx-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Taramaları Durdur</h3>
          <button @click="closePurgeQueuesModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-center gap-2 mb-2">
            <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p class="text-sm font-medium text-red-800">DİKKAT!</p>
          </div>
          <p class="text-sm text-red-700">
            Bu işlem tüm RabbitMQ queue'lerini temizleyecek ve devam eden tüm taramaları durduracaktır. 
            Bu işlem geri alınamaz!
          </p>
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Server Seçimi</label>
          <select
            v-model="purgeQueuesEnvironment"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
          >
            <option value="">Tüm Server'lar (Local + Azure)</option>
            <option value="local">Sadece Local</option>
            <option value="azure">Sadece Azure</option>
          </select>
        </div>

        <div class="flex gap-3 pt-4">
          <button
            type="button"
            @click="closePurgeQueuesModal"
            class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            İptal
          </button>
          <button
            @click="confirmPurgeQueues"
            :disabled="isPurgingQueues"
            class="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-red-300 text-white px-4 py-2 rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            <svg v-if="isPurgingQueues" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isPurgingQueues ? 'Durduruluyor...' : 'Taramaları Durdur' }}
          </button>
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
  </div>
</template>

<script setup>
// Sayfa meta bilgileri
definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})

// Sayfa başlığı
useHead({
  title: 'Tarama - Admin Panel'
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
const scheduledScans = ref([])
const cronJobs = ref([])
const companies = ref([])
const scanOperations = ref([])
const isLoading = ref(false)
const isLoadingCronJobs = ref(false)
const isQuickScanLoading = ref(false)
const isDemoScanLoading = ref(false)
const isProfileScanLoading = ref(false)
const isAdding = ref(false)
const isRunningScheduled = ref(false)
const isLoadingOperations = ref(false)
const showAddModal = ref(false)
const showAddCronModal = ref(false)
const showEditCronModal = ref(false)
const showQuickScanModal = ref(false)
const showDemoScanModal = ref(false)
const showProfileScanModal = ref(false)
const showChromeScanModal = ref(false)
const showPurgeQueuesModal = ref(false)
const showJobDetailsModal = ref(false)
const isLoadingJobDetails = ref(false)
const selectedJobId = ref(null)
const jobDetails = ref(null)
const showMatchingModal = ref(false)
const isLoadingMatching = ref(false)
const matchingJobId = ref(null)
const scraperDataList = ref([])
const matchingResults = ref({
  found: [],
  notFound: [],
  noData: [],
  scraperDataMap: {}
})
// Her job için bulunan veriler sayısını sakla
const jobFoundCounts = ref({})

// Pagination state for matching tables
const matchingFoundCurrentPage = ref(1)
const matchingFoundPerPage = ref(25)
const matchingNoDataCurrentPage = ref(1)
const matchingNoDataPerPage = ref(25)
const matchingNotFoundCurrentPage = ref(1)
const matchingNotFoundPerPage = ref(25)

// Scraper data modal state
const showScraperDataModal = ref(false)
const selectedScraperData = ref(null)
const scraperDataCopied = ref(false)
const message = ref('')
const messageType = ref('success')
const isSavingCronJob = ref(false)
const editingCronJobId = ref(null)
const isPurgingQueues = ref(false)
const purgeQueuesEnvironment = ref('')
const showScanDropdown = ref(false)

// Pagination state
const currentPage = ref(1)
const perPage = ref(10)
const totalPages = ref(1)
const totalItems = ref(0)
const pagination = ref({
  current_page: 1,
  per_page: 10,
  total: 0,
  total_pages: 1,
  has_next: false,
  has_prev: false
})

const newScan = ref({
  time: '',
  company: 'all'
})

const cronJobForm = ref({
  time: '',
  scan_type: 'all',
  company_id: null,
  active: true
})

const quickScanCompany = ref('all')
const demoScanCompany = ref('')
const demoScanUrls = ref('')
const profileScanProfileId = ref('')
const profiles = ref([])
const isChromeScan = ref(false) // Chrome extension taraması mı?

// Dropdown ref for click outside
const scanDropdownRef = ref(null)

// Click outside handler
const handleClickOutside = (e) => {
  if (scanDropdownRef.value && !scanDropdownRef.value.contains(e.target)) {
    showScanDropdown.value = false
  }
}

// Worker durumundaki işlemler için polling interval
const operationsPollingInterval = ref(null)

// Worker durumundaki işlemler için canlı güncelleme
const startOperationsPolling = () => {
  // Önceki polling'i durdur
  stopOperationsPolling()
  
  // Worker durumunda işlem var mı kontrol et
  const hasWorkerOperations = scanOperations.value.some(op => getStatusNormalized(op.status) === 'worker')
  
  if (hasWorkerOperations) {
    // Her 5 saniyede bir güncelle
    operationsPollingInterval.value = setInterval(async () => {
      const hasWorker = scanOperations.value.some(op => getStatusNormalized(op.status) === 'worker')
      if (hasWorker) {
        await loadScanOperations(currentPage.value)
      } else {
        stopOperationsPolling()
      }
    }, 5000) // 5 saniye
  }
}

// Polling'i durdur
const stopOperationsPolling = () => {
  if (operationsPollingInterval.value) {
    clearInterval(operationsPollingInterval.value)
    operationsPollingInterval.value = null
  }
}

// Click outside to close dropdown
onMounted(async () => {
  try {
    // Kısa bir delay ile yetki kontrolünün tamamlanmasını bekle
    await new Promise(resolve => setTimeout(resolve, 200))
    isCheckingPermissions.value = false
    
    await loadCronJobs()
    await loadCompanies()
    await loadProfiles()
    await loadScanOperations()

    // Click outside listener for dropdown
    document.addEventListener('click', handleClickOutside)
  } catch (error) {
    console.error('Page initialization failed:', error)
    isCheckingPermissions.value = false
  }
})

// Cleanup event listener
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  // Polling'leri temizle
  stopJobStatusPolling()
  stopOperationsPolling()
})

// Load cron jobs
const loadCronJobs = async () => {
  try {
    isLoadingCronJobs.value = true
    const cronJobApi = useCronJobApi()
    const response = await cronJobApi.list()
    
    if (response.success) {
      cronJobs.value = response.data
    } else {
      showMessage('Cron job\'lar yüklenirken hata oluştu', 'error')
    }
  } catch (error) {
    console.error('Error loading cron jobs:', error)
    showMessage('Cron job\'lar yüklenirken hata oluştu', 'error')
  } finally {
    isLoadingCronJobs.value = false
  }
}

// Load companies
const loadCompanies = async () => {
  try {
    const companiesApi = useCompaniesApi()
    const response = await companiesApi.list()
    
    if (response.success) {
      companies.value = response.data
    } else {
      showMessage('Firmalar yüklenirken hata oluştu', 'error')
    }
  } catch (error) {
    console.error('Error loading companies:', error)
    showMessage('Firmalar yüklenirken hata oluştu', 'error')
  }
}

// Start quick scan
const startQuickScan = async () => {
  try {
    isQuickScanLoading.value = true
    
    // Chrome extension taraması mı?
    if (isChromeScan.value) {
      // Token al
      const token = await getUserToken()
      if (!token) {
        isQuickScanLoading.value = false
        return
      }
      
      const scanningApi = useScanningApi()
      const response = await scanningApi.chromeQuickScan({
        company_id: quickScanCompany.value === 'all' ? 'all' : String(quickScanCompany.value),
        token: token
      })
      
      if (response.success) {
        showMessage(response.message || 'Chrome extension hızlı tarama başarıyla başlatıldı', 'success')
        closeQuickScanModal()
        isChromeScan.value = false
        await loadScanOperations() // Refresh operations list
      } else {
        showMessage(response.message || 'Chrome extension hızlı tarama başlatılamadı', 'error')
      }
    } else {
      // Normal tarama
      const scanningApi = useScanningApi()
      const response = await scanningApi.quickScan({
        company_id: quickScanCompany.value === 'all' ? 'all' : String(quickScanCompany.value)
      })
      
      if (response.success) {
        showMessage(response.message, 'success')
        closeQuickScanModal()
        await loadScanOperations() // Refresh operations list
      } else {
        showMessage(response.message, 'error')
      }
    }
  } catch (error) {
    console.error('Error starting quick scan:', error)
    showMessage('Hızlı tarama başlatılırken hata oluştu', 'error')
  } finally {
    isQuickScanLoading.value = false
  }
}

// Start demo scan
const startDemoScan = async () => {
  try {
    isDemoScanLoading.value = true
    
    // Parse URLs from textarea
    const urls = demoScanUrls.value
      .split('\n')
      .map(url => url.trim())
      .filter(url => url.length > 0)
    
    if (urls.length === 0) {
      showMessage('Lütfen en az bir URL girin', 'error')
      isDemoScanLoading.value = false
      return
    }
    
    const scanningApi = useScanningApi()
    const response = await scanningApi.demoScan({
      urls: urls,
      company_id: demoScanCompany.value ? String(demoScanCompany.value) : null
    })
    
    if (response.success) {
      showMessage(response.message, 'success')
      closeDemoScanModal()
      await loadScanOperations() // Refresh operations list
    } else {
      showMessage(response.message, 'error')
    }
  } catch (error) {
    console.error('Error starting demo scan:', error)
    showMessage('Demo tarama başlatılırken hata oluştu', 'error')
  } finally {
    isDemoScanLoading.value = false
  }
}

// Start profile scan
const startProfileScan = async () => {
  try {
    isProfileScanLoading.value = true
    
    if (!profileScanProfileId.value) {
      showMessage('Lütfen bir profil seçin', 'error')
      isProfileScanLoading.value = false
      return
    }
    
    // Chrome extension taraması mı?
    if (isChromeScan.value) {
      // Token al
      const token = await getUserToken()
      if (!token) {
        isProfileScanLoading.value = false
        return
      }
      
      const scanningApi = useScanningApi()
      const response = await scanningApi.chromeProfileScan({
        profile_id: profileScanProfileId.value,
        token: token
      })
      
      if (response.success) {
        showMessage(response.message || 'Chrome extension profil taraması başarıyla başlatıldı', 'success')
        closeProfileScanModal()
        isChromeScan.value = false
        await loadScanOperations() // Refresh operations list
      } else {
        showMessage(response.message || 'Chrome extension profil taraması başlatılamadı', 'error')
      }
    } else {
      // Normal tarama
      const scanningApi = useScanningApi()
      const response = await scanningApi.profileScan({
        profile_id: profileScanProfileId.value
      })
      
      if (response.success) {
        showMessage(response.message, 'success')
        closeProfileScanModal()
        await loadScanOperations() // Refresh operations list
      } else {
        showMessage(response.message, 'error')
      }
    }
  } catch (error) {
    console.error('Error starting profile scan:', error)
    showMessage('Profil taraması başlatılırken hata oluştu', 'error')
  } finally {
    isProfileScanLoading.value = false
  }
}

// Load profiles
const loadProfiles = async () => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('custom-profiles.list'))
    
    if (response.success) {
      profiles.value = response.data || []
    } else {
      showMessage('Profiller yüklenirken hata oluştu', 'error')
    }
  } catch (error) {
    console.error('Error loading profiles:', error)
    showMessage('Profiller yüklenirken hata oluştu', 'error')
  }
}

// Add scheduled scan
const addScheduledScan = async () => {
  try {
    isAdding.value = true
    const scanningApi = useScanningApi()
    const response = await scanningApi.scheduledScans.create({
      time: newScan.value.time,
      company: newScan.value.company
    })
    
    if (response.success) {
      showMessage(response.message, 'success')
      closeModal()
      await loadScheduledScans()
    } else {
      showMessage(response.message, 'error')
    }
  } catch (error) {
    console.error('Error adding scheduled scan:', error)
    showMessage('Planlı tarama eklenirken hata oluştu', 'error')
  } finally {
    isAdding.value = false
  }
}

// Delete scheduled scan
const deleteScheduledScan = async (id) => {
  if (!confirm('Bu planlı taramayı silmek istediğinizden emin misiniz?')) {
    return
  }

  try {
    const scanningApi = useScanningApi()
    const response = await scanningApi.scheduledScans.delete(id)
    
    if (response.success) {
      showMessage(response.message, 'success')
      await loadScheduledScans()
    } else {
      showMessage(response.message, 'error')
    }
  } catch (error) {
    console.error('Error deleting scheduled scan:', error)
    showMessage('Planlı tarama silinirken hata oluştu', 'error')
  }
}

// Close modal
const closeModal = () => {
  showAddModal.value = false
  newScan.value = {
    time: '',
    company: 'all'
  }
}

// Close quick scan modal
const closeQuickScanModal = () => {
  showQuickScanModal.value = false
  quickScanCompany.value = 'all'
  isChromeScan.value = false
}

// Close demo scan modal
const closeDemoScanModal = () => {
  showDemoScanModal.value = false
  demoScanCompany.value = ''
  demoScanUrls.value = ''
}

// Close profile scan modal
const closeProfileScanModal = () => {
  showProfileScanModal.value = false
  profileScanProfileId.value = ''
  isChromeScan.value = false
}

// Close chrome scan modal
const closeChromeScanModal = () => {
  showChromeScanModal.value = false
}

// Get user token for Chrome extension API
const getUserToken = async () => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get('/user/profile')
    
    if (response.success && response.user && response.user.iprice_token) {
      return response.user.iprice_token
    }
    
    throw new Error('Token bulunamadı')
  } catch (error) {
    console.error('Token alınırken hata:', error)
    showMessage('Token alınırken hata oluştu. Lütfen ayarlardan token oluşturun.', 'error')
    return null
  }
}

// Open quick scan from chrome modal
const openQuickScanFromChrome = () => {
  showChromeScanModal.value = false
  isChromeScan.value = true // Chrome extension taraması olduğunu işaretle
  showQuickScanModal.value = true
}

// Open profile scan from chrome modal
const openProfileScanFromChrome = () => {
  showChromeScanModal.value = false
  isChromeScan.value = true // Chrome extension taraması olduğunu işaretle
  showProfileScanModal.value = true
}

// Load scan operations with pagination
const loadScanOperations = async (page = 1) => {
  try {
    isLoadingOperations.value = true
    const scanningApi = useScanningApi()
    const response = await scanningApi.operations({
      page: page,
      per_page: perPage.value
    })
    
    if (response.success) {
      scanOperations.value = response.data
      pagination.value = response.pagination
      currentPage.value = response.pagination.current_page
      totalPages.value = response.pagination.total_pages
      totalItems.value = response.pagination.total
      
      // Backend'den gelen found_count değerlerini jobFoundCounts'a kaydet
      response.data.forEach(operation => {
        if (operation.found_count !== undefined) {
          jobFoundCounts.value[operation.id] = operation.found_count
        }
      })
      
      // Worker durumundaki işlemler için polling başlat
      startOperationsPolling()
    } else {
      showMessage('İşlem geçmişi yüklenirken hata oluştu', 'error')
    }
  } catch (error) {
    console.error('Error loading scan operations:', error)
    showMessage('İşlem geçmişi yüklenirken hata oluştu', 'error')
  } finally {
    isLoadingOperations.value = false
  }
}

// Format date
const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('tr-TR')
}

// Format date and time
const formatDateTime = (dateTime) => {
  if (!dateTime) return 'N/A'
  return new Date(dateTime).toLocaleString('tr-TR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Status'u normalize et (büyük/küçük harf uyumsuzluğu için)
const getStatusNormalized = (status) => {
  if (!status) return null
  return String(status).toLowerCase().trim()
}

// İlerleme yüzdesini hesapla
const getProgressPercentage = (operation) => {
  if (!operation || !operation.total_urls || operation.total_urls === 0) {
    return 0
  }
  
  const foundCount = jobFoundCounts.value[operation.id] || 0
  const percentage = Math.round((foundCount / operation.total_urls) * 100)
  return Math.min(percentage, 100) // Maksimum %100
}

// Pagination computed properties for matching tables
const matchingFoundTotalPages = computed(() => {
  return Math.ceil(matchingResults.value.found.length / matchingFoundPerPage.value)
})

const paginatedFound = computed(() => {
  const start = (matchingFoundCurrentPage.value - 1) * matchingFoundPerPage.value
  const end = start + matchingFoundPerPage.value
  return matchingResults.value.found.slice(start, end)
})

const matchingNoDataTotalPages = computed(() => {
  return Math.ceil(matchingResults.value.noData.length / matchingNoDataPerPage.value)
})

const paginatedNoData = computed(() => {
  const start = (matchingNoDataCurrentPage.value - 1) * matchingNoDataPerPage.value
  const end = start + matchingNoDataPerPage.value
  return matchingResults.value.noData.slice(start, end)
})

const matchingNotFoundTotalPages = computed(() => {
  return Math.ceil(matchingResults.value.notFound.length / matchingNotFoundPerPage.value)
})

const paginatedNotFound = computed(() => {
  const start = (matchingNotFoundCurrentPage.value - 1) * matchingNotFoundPerPage.value
  const end = start + matchingNotFoundPerPage.value
  return matchingResults.value.notFound.slice(start, end)
})

// Show job details
const showJobDetails = async (jobId) => {
  try {
    selectedJobId.value = jobId
    showJobDetailsModal.value = true
    isLoadingJobDetails.value = true
    jobDetails.value = null
    jobStatus.value = null
    jobStatusError.value = ''

    const scanningApi = useScanningApi()
    const response = await scanningApi.jobDetails(jobId)
    
    if (response.success) {
      jobDetails.value = response.data
      // Job status'u da yükle
      await loadJobStatus(jobId)
      // Polling başlat
      startJobStatusPolling(jobId)
    } else {
      showMessage(response.message, 'error')
    }
  } catch (error) {
    console.error('Error loading job details:', error)
    showMessage('Job detayları yüklenirken hata oluştu', 'error')
  } finally {
    isLoadingJobDetails.value = false
  }
}

// Load job status from RabbitMQ
const loadJobStatus = async (jobId) => {
  try {
    isLoadingJobStatus.value = true
    jobStatusError.value = ''

    const scanningApi = useScanningApi()
    const response = await scanningApi.jobStatus(jobId)
    
    if (response.success) {
      jobStatus.value = response.data
    } else {
      jobStatusError.value = response.message || 'Job durumu alınamadı'
    }
  } catch (error) {
    console.error('Error loading job status:', error)
    jobStatusError.value = 'Job durumu yüklenirken hata oluştu'
  } finally {
    isLoadingJobStatus.value = false
  }
}

// Start polling for job status
const startJobStatusPolling = (jobId) => {
  // Önceki polling'i durdur
  stopJobStatusPolling()
  
  // Eğer job tamamlanmışsa polling başlatma
  if (jobStatus.value && jobStatus.value.progress.percentage === 100) {
    return
  }
  
  // Her 5 saniyede bir kontrol et
  jobStatusPollInterval.value = setInterval(async () => {
    await loadJobStatus(jobId)
    
    // Job tamamlandıysa polling'i durdur
    if (jobStatus.value && jobStatus.value.progress.percentage === 100) {
      stopJobStatusPolling()
    }
  }, 5000)
}

// Stop polling
const stopJobStatusPolling = () => {
  if (jobStatusPollInterval.value) {
    clearInterval(jobStatusPollInterval.value)
    jobStatusPollInterval.value = null
  }
}

// JSON viewer state and loader
const isLoadingJobJson = ref(false)
const jobJsonData = ref(null)
const jobJsonError = ref('')
const jobJsonHeaders = ref([])
const jobJsonRows = ref([])
const showJsonCode = ref(false)
const jsonCopied = ref(false)

// Job status state
const isLoadingJobStatus = ref(false)
const jobStatus = ref(null)
const jobStatusError = ref('')
const jobStatusPollInterval = ref(null)

const pickArrayData = (data) => {
  if (Array.isArray(data)) return data
  if (data && typeof data === 'object') {
    for (const key of Object.keys(data)) {
      if (Array.isArray(data[key])) return data[key]
    }
  }
  return null
}

const loadJobJson = async (jobId) => {
  try {
    isLoadingJobJson.value = true
    jobJsonError.value = ''
    jobJsonData.value = null
    jobJsonHeaders.value = []
    jobJsonRows.value = []

    const scanningApi = useScanningApi()
    const response = await scanningApi.jobJson(jobId)

    if (!response.success) {
      jobJsonError.value = response.message || 'JSON getirilemedi'
      return
    }

    jobJsonData.value = response.data.json
    const rows = pickArrayData(jobJsonData.value)

    if (rows && rows.length && typeof rows[0] === 'object') {
      const headers = Array.from(
        rows.reduce((set, row) => {
          Object.keys(row || {}).forEach(k => set.add(k))
          return set
        }, new Set())
      )
      jobJsonHeaders.value = headers
      jobJsonRows.value = rows
    }
  } catch (error) {
    console.error('Error loading job json:', error)
    jobJsonError.value = 'JSON yüklenirken hata oluştu'
  } finally {
    isLoadingJobJson.value = false
  }
}

const formatCell = (val) => {
  if (val === null || val === undefined) return ''
  if (typeof val === 'object') return JSON.stringify(val)
  return String(val)
}

// Format JSON for code view
const formattedJsonCode = computed(() => {
  if (!jobJsonData.value) return ''
  return JSON.stringify(jobJsonData.value, null, 2)
})

// Copy JSON code to clipboard
const copyJsonCode = async () => {
  try {
    await navigator.clipboard.writeText(formattedJsonCode.value)
    jsonCopied.value = true
    setTimeout(() => {
      jsonCopied.value = false
    }, 2000)
  } catch (error) {
    console.error('Failed to copy JSON:', error)
    showMessage('JSON kopyalanırken hata oluştu', 'error')
  }
}

// Close job details modal
const closeJobDetailsModal = () => {
  // Polling'i durdur
  stopJobStatusPolling()
  
  showJobDetailsModal.value = false
  selectedJobId.value = null
  jobDetails.value = null
  jobJsonData.value = null
  jobJsonHeaders.value = []
  jobJsonRows.value = []
  jobJsonError.value = ''
  showJsonCode.value = false
  jsonCopied.value = false
  jobStatus.value = null
  jobStatusError.value = ''
}

// Pagination functions
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    loadScanOperations(page)
  }
}

const nextPage = () => {
  if (pagination.value.has_next) {
    goToPage(currentPage.value + 1)
  }
}

const prevPage = () => {
  if (pagination.value.has_prev) {
    goToPage(currentPage.value - 1)
  }
}

const changePerPage = (newPerPage) => {
  perPage.value = newPerPage
  loadScanOperations(1) // Reset to first page
}

// Cron Job Management Functions
const saveCronJob = async () => {
  try {
    isSavingCronJob.value = true
    const cronJobApi = useCronJobApi()
    
    let response
    if (showEditCronModal.value) {
      response = await cronJobApi.update(editingCronJobId.value, cronJobForm.value)
    } else {
      response = await cronJobApi.create(cronJobForm.value)
    }
    
    if (response.success) {
      showMessage(response.message, 'success')
      closeCronModal()
      await loadCronJobs()
    } else {
      showMessage(response.message, 'error')
    }
  } catch (error) {
    console.error('Error saving cron job:', error)
    showMessage('Cron job kaydedilirken hata oluştu', 'error')
  } finally {
    isSavingCronJob.value = false
  }
}

const editCronJob = (cronJob) => {
  cronJobForm.value = {
    time: cronJob.time,
    scan_type: cronJob.scan_type,
    company_id: cronJob.company_id,
    active: cronJob.active
  }
  editingCronJobId.value = cronJob.id
  showEditCronModal.value = true
}

const deleteCronJob = async (id) => {
  if (!confirm('Bu cron job\'ı silmek istediğinizden emin misiniz?')) {
    return
  }

  try {
    const cronJobApi = useCronJobApi()
    const response = await cronJobApi.delete(id)
    
    if (response.success) {
      showMessage(response.message, 'success')
      await loadCronJobs()
    } else {
      showMessage(response.message, 'error')
    }
  } catch (error) {
    console.error('Error deleting cron job:', error)
    showMessage('Cron job silinirken hata oluştu', 'error')
  }
}

const toggleCronJob = async (id) => {
  try {
    const cronJobApi = useCronJobApi()
    const response = await cronJobApi.toggle(id)
    
    if (response.success) {
      showMessage(response.message, 'success')
      await loadCronJobs()
    } else {
      showMessage(response.message, 'error')
    }
  } catch (error) {
    console.error('Error toggling cron job:', error)
    showMessage('Cron job durumu değiştirilirken hata oluştu', 'error')
  }
}

const runScheduledJobs = async () => {
  try {
    isRunningScheduled.value = true
    const cronJobApi = useCronJobApi()
    const response = await cronJobApi.runScheduled()
    
    if (response.success) {
      showMessage(response.message, 'success')
      await loadScanOperations() // Refresh operations list
    } else {
      showMessage(response.message, 'error')
    }
  } catch (error) {
    console.error('Error running scheduled jobs:', error)
    showMessage('Planlı işler çalıştırılırken hata oluştu', 'error')
  } finally {
    isRunningScheduled.value = false
  }
}

const onScanTypeChange = () => {
  if (cronJobForm.value.scan_type === 'all') {
    cronJobForm.value.company_id = null
  }
}

const closeCronModal = () => {
  showAddCronModal.value = false
  showEditCronModal.value = false
  editingCronJobId.value = null
  cronJobForm.value = {
    time: '',
    scan_type: 'all',
    company_id: null,
    active: true
  }
}

// Purge queues (stop all scans)
const confirmPurgeQueues = async () => {
  try {
    isPurgingQueues.value = true
    
    const scanningApi = useScanningApi()
    const response = await scanningApi.purgeQueues({
      environment: purgeQueuesEnvironment.value || null
    })
    
    if (response.success) {
      showMessage(response.message, 'success')
      closePurgeQueuesModal()
      // Operations listesini yenile
      await loadScanOperations()
    } else {
      showMessage(response.message, 'error')
    }
  } catch (error) {
    console.error('Error purging queues:', error)
    showMessage('Taramalar durdurulurken hata oluştu', 'error')
  } finally {
    isPurgingQueues.value = false
  }
}

// Close purge queues modal
const closePurgeQueuesModal = () => {
  showPurgeQueuesModal.value = false
  purgeQueuesEnvironment.value = ''
}

// Show matching modal
const showMatchingModalFunc = async (jobId) => {
  try {
    matchingJobId.value = jobId
    showMatchingModal.value = true
    isLoadingMatching.value = true
    scraperDataList.value = []
    matchingResults.value = {
      found: [],
      notFound: [],
      noData: [],
      scraperDataMap: {}
    }

    // Scraper data'yı yükle
    const scanningApi = useScanningApi()
    const response = await scanningApi.scraperData(jobId)
    
    if (response.success) {
      scraperDataList.value = response.data
    } else {
      showMessage(response.message || 'Scraper data yüklenemedi', 'error')
    }
  } catch (error) {
    console.error('Error loading scraper data:', error)
    showMessage('Scraper data yüklenirken hata oluştu', 'error')
  } finally {
    isLoadingMatching.value = false
  }
}

// Close matching modal
const closeMatchingModal = () => {
  showMatchingModal.value = false
  matchingJobId.value = null
  scraperDataList.value = []
  matchingResults.value = {
    found: [],
    notFound: [],
    noData: [],
    scraperDataMap: {}
  }
  // Reset pagination
  matchingFoundCurrentPage.value = 1
  matchingNoDataCurrentPage.value = 1
  matchingNotFoundCurrentPage.value = 1
}

// Perform matching
const performMatching = async () => {
  try {
    if (!jobJsonData.value) {
      // Job JSON'u yükle
      await loadJobJson(matchingJobId.value)
    }

    if (!jobJsonData.value) {
      showMessage('Job JSON verisi bulunamadı', 'error')
      return
    }

    // JSON'dan data_id'leri çıkar
    const rows = pickArrayData(jobJsonData.value)
    if (!rows || !Array.isArray(rows)) {
      showMessage('Geçerli JSON verisi bulunamadı', 'error')
      return
    }

    // Scraper data'dan process_id'leri al
    const processIds = new Set(scraperDataList.value.map(item => item.process_id))
    
    // Scraper data map'i oluştur ve scraped_data kontrolü yap
    const scraperDataMap = {}
    scraperDataList.value.forEach(item => {
      scraperDataMap[item.process_id] = item
      
      // scraped_data boş mu kontrol et
      const scrapedData = item.data?.scraped_data || item.data?.original_message?.scraped_data || []
      const isScrapedDataEmpty = (
        !scrapedData ||
        (Array.isArray(scrapedData) && scrapedData.length === 0) ||
        (typeof scrapedData === 'object' && Object.keys(scrapedData).length === 0)
      )
      
      if (isScrapedDataEmpty) {
        item.hasNoData = true
      }
    })

    // Eşleştirme yap
    const found = []
    const notFound = []
    const noData = [] // scraped_data boş olanlar

    rows.forEach((row, index) => {
      const dataId = row.data_id || row.dataId || row.id
      if (!dataId) return

      if (processIds.has(dataId)) {
        const scraperData = scraperDataMap[dataId]
        // scraped_data boş mu kontrol et
        if (scraperData?.hasNoData) {
          noData.push({
            data_id: dataId,
            process_id: dataId,
            index: index,
            row: row
          })
        } else {
          found.push({
            data_id: dataId,
            process_id: dataId,
            index: index,
            row: row
          })
        }
      } else {
        notFound.push({
          data_id: dataId,
          index: index,
          row: row
        })
      }
    })

    matchingResults.value = {
      found,
      notFound,
      noData,
      scraperDataMap
    }

    // Bulunan veriler sayısını kaydet
    if (matchingJobId.value) {
      jobFoundCounts.value[matchingJobId.value] = found.length
    }

    showMessage(`Eşleştirme tamamlandı: ${found.length} bulundu, ${noData.length} veri alınamamış, ${notFound.length} bulunamadı`, 'success')
  } catch (error) {
    console.error('Error performing matching:', error)
    showMessage('Eşleştirme yapılırken hata oluştu', 'error')
  }
}

// View scraper data
const viewScraperData = (processId) => {
  const scraperData = matchingResults.value.scraperDataMap[processId]
  if (!scraperData) {
    showMessage('Scraper data bulunamadı', 'error')
    return
  }

  selectedScraperData.value = scraperData
  showScraperDataModal.value = true
  scraperDataCopied.value = false
}

// Close scraper data modal
const closeScraperDataModal = () => {
  showScraperDataModal.value = false
  selectedScraperData.value = null
  scraperDataCopied.value = false
}

// Formatted scraper data JSON
const formattedScraperDataJson = computed(() => {
  if (!selectedScraperData.value) return ''
  return JSON.stringify(selectedScraperData.value.data, null, 2)
})

// Copy scraper data JSON
const copyScraperDataJson = async () => {
  try {
    await navigator.clipboard.writeText(formattedScraperDataJson.value)
    scraperDataCopied.value = true
    setTimeout(() => {
      scraperDataCopied.value = false
    }, 2000)
  } catch (error) {
    console.error('Failed to copy JSON:', error)
    showMessage('JSON kopyalanırken hata oluştu', 'error')
  }
}

// Download not found JSON
const downloadNotFoundJson = () => {
  try {
    if (!jobJsonData.value) {
      showMessage('Job JSON verisi bulunamadı. Önce "Veriyi Gör" butonuna tıklayın.', 'error')
      return
    }

    const rows = pickArrayData(jobJsonData.value)
    if (!rows || !Array.isArray(rows)) {
      showMessage('Geçerli JSON verisi bulunamadı', 'error')
      return
    }

    // Bulunamayan verilerin data_id'lerini al
    const notFoundDataIds = matchingResults.value.notFound.map(item => item.data_id)
    
    // Job JSON'dan bu data_id'lere sahip satırları filtrele
    const notFoundData = rows.filter(row => {
      const rowDataId = row.data_id || row.dataId || row.id
      return notFoundDataIds.includes(rowDataId)
    })

    if (notFoundData.length === 0) {
      showMessage('İndirilecek veri bulunamadı', 'error')
      return
    }

    // JSON'u string'e çevir
    const jsonStr = JSON.stringify(notFoundData, null, 2)
    
    // Blob oluştur ve indir
    const blob = new Blob([jsonStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `bulunamayan-veriler-job-${matchingJobId.value}-${new Date().getTime()}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    showMessage(`${notFoundData.length} kayıt JSON olarak indirildi`, 'success')
  } catch (error) {
    console.error('Error downloading not found JSON:', error)
    showMessage('JSON indirilirken hata oluştu', 'error')
  }
}

// Retry scan for single data_id
const retryScan = async (dataId) => {
  try {
    showMessage(`Tekrar tarama başlatılıyor: ${dataId}`, 'info')
    
    // Job JSON'dan data'yı bul
    if (!jobJsonData.value) {
      await loadJobJson(matchingJobId.value)
    }
    
    if (!jobJsonData.value) {
      showMessage('Job JSON verisi bulunamadı', 'error')
      return
    }
    
    const rows = pickArrayData(jobJsonData.value)
    if (!rows || !Array.isArray(rows)) {
      showMessage('Geçerli JSON verisi bulunamadı', 'error')
      return
    }
    
    // data_id'ye göre data'yı bul
    const rowData = rows.find(row => (row.data_id || row.dataId || row.id) === dataId)
    if (!rowData) {
      showMessage('Data bulunamadı', 'error')
      return
    }
    
    // 🔥 Data'yı kopyala ve job_id'yi kaldır (yeni job oluşturulacak)
    const { job_id, ...cleanData } = rowData
    
    // API'ye gönder
    const scanningApi = useScanningApi()
    const response = await scanningApi.retryScan({ data: cleanData })
    
    if (response.success) {
      showMessage(response.message || 'Tekrar tarama başlatıldı', 'success')
      // Operations listesini yenile
      await loadScanOperations()
    } else {
      showMessage(response.message || 'Tekrar tarama başlatılamadı', 'error')
    }
  } catch (error) {
    console.error('Error retrying scan:', error)
    showMessage('Tekrar tarama başlatılırken hata oluştu', 'error')
  }
}

// Retry all scans
const retryAllScans = async () => {
  try {
    if (matchingResults.value.notFound.length === 0) {
      showMessage('Tekrar taranacak veri yok', 'info')
      return
    }

    showMessage(`${matchingResults.value.notFound.length} veri için tekrar tarama başlatılıyor...`, 'info')
    
    // Job JSON'dan data'ları bul
    if (!jobJsonData.value) {
      await loadJobJson(matchingJobId.value)
    }
    
    if (!jobJsonData.value) {
      showMessage('Job JSON verisi bulunamadı', 'error')
      return
    }
    
    const rows = pickArrayData(jobJsonData.value)
    if (!rows || !Array.isArray(rows)) {
      showMessage('Geçerli JSON verisi bulunamadı', 'error')
      return
    }
    
    // data_id'lere göre data'ları bul
    const dataIds = matchingResults.value.notFound.map(item => item.data_id)
    const dataArray = rows.filter(row => {
      const rowDataId = row.data_id || row.dataId || row.id
      return dataIds.includes(rowDataId)
    })
    
    if (dataArray.length === 0) {
      showMessage('Data bulunamadı', 'error')
      return
    }
    
    // 🔥 job_id'yi temizle (yeni job oluşturulacak)
    const cleanDataArray = dataArray.map(item => {
      const { job_id, ...rest } = item
      return rest
    })
    
    // API'ye gönder
    const scanningApi = useScanningApi()
    const response = await scanningApi.retryBulkScan({ data: cleanDataArray })
    
    if (response.success) {
      showMessage(response.message || 'Tüm veriler için tekrar tarama başlatıldı', 'success')
      // Operations listesini yenile
      await loadScanOperations()
    } else {
      showMessage(response.message || 'Tekrar tarama başlatılamadı', 'error')
    }
  } catch (error) {
    console.error('Error retrying all scans:', error)
    showMessage('Tekrar tarama başlatılırken hata oluştu', 'error')
  }
}

// Retry all no data scans
const retryAllNoDataScans = async () => {
  try {
    if (matchingResults.value.noData.length === 0) {
      showMessage('Tekrar taranacak veri yok', 'info')
      return
    }

    showMessage(`${matchingResults.value.noData.length} veri alınamamış veri için tekrar tarama başlatılıyor...`, 'info')
    
    // Job JSON'dan data'ları bul
    if (!jobJsonData.value) {
      await loadJobJson(matchingJobId.value)
    }
    
    if (!jobJsonData.value) {
      showMessage('Job JSON verisi bulunamadı', 'error')
      return
    }
    
    const rows = pickArrayData(jobJsonData.value)
    if (!rows || !Array.isArray(rows)) {
      showMessage('Geçerli JSON verisi bulunamadı', 'error')
      return
    }
    
    // data_id'lere göre data'ları bul
    const dataIds = matchingResults.value.noData.map(item => item.data_id)
    const dataArray = rows.filter(row => {
      const rowDataId = row.data_id || row.dataId || row.id
      return dataIds.includes(rowDataId)
    })
    
    if (dataArray.length === 0) {
      showMessage('Data bulunamadı', 'error')
      return
    }
    
    // 🔥 job_id'yi temizle (yeni job oluşturulacak)
    const cleanDataArray = dataArray.map(item => {
      const { job_id, ...rest } = item
      return rest
    })
    
    // API'ye gönder
    const scanningApi = useScanningApi()
    const response = await scanningApi.retryBulkScan({ data: cleanDataArray })
    
    if (response.success) {
      showMessage(response.message || 'Veri alınamamış tüm veriler için tekrar tarama başlatıldı', 'success')
      // Operations listesini yenile
      await loadScanOperations()
    } else {
      showMessage(response.message || 'Tekrar tarama başlatılamadı', 'error')
    }
  } catch (error) {
    console.error('Error retrying all no data scans:', error)
    showMessage('Tekrar tarama başlatılırken hata oluştu', 'error')
  }
}

// Show message
const showMessage = (msg, type) => {
  message.value = msg
  messageType.value = type
  
  setTimeout(() => {
    message.value = ''
  }, 5000)
}
</script>
