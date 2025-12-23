import { getApiEndpoint, API_ENDPOINTS } from '~/config/api-endpoints'

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  
  // API base URL'ini ayarla
  const apiBase = config.public.apiBase || 'http://localhost:8082/api'
  
  // Global $fetch konfigürasyonu
  const customFetch = $fetch.create({
    baseURL: apiBase,
    onRequest({ request, options }) {
      // Token varsa header'a ekle
      if (process.client) {
        const token = localStorage.getItem('auth_token')
        if (token) {
          options.headers = {
            ...options.headers,
            Authorization: `Bearer ${token}`
          }
        }
      }
    },
    onResponseError({ response }) {
      // 401 hatası durumunda logout yap
      if (response.status === 401 && process.client) {
        const authStore = useAuthStore()
        authStore.logout()
      }
    }
  })
  
  // API client objesi oluştur
  const apiClient = {
    // Temel HTTP metodları
    get: (url, options = {}) => customFetch(url, { method: 'GET', ...options }),
    post: (url, body, options = {}) => customFetch(url, { method: 'POST', body, ...options }),
    put: (url, body, options = {}) => customFetch(url, { method: 'PUT', body, ...options }),
    patch: (url, body, options = {}) => customFetch(url, { method: 'PATCH', body, ...options }),
    delete: (url, options = {}) => customFetch(url, { method: 'DELETE', ...options }),
    
    // Endpoint helper metodları
    getEndpoint: getApiEndpoint,
    endpoints: API_ENDPOINTS,
    
    // Kolay kullanım için endpoint metodları
    auth: {
      login: (data) => customFetch(getApiEndpoint('auth.login'), { method: 'POST', body: data }),
      register: (data) => customFetch(getApiEndpoint('auth.register'), { method: 'POST', body: data }),
      logout: () => customFetch(getApiEndpoint('auth.logout'), { method: 'POST' }),
      me: () => customFetch(getApiEndpoint('auth.me'), { method: 'GET' }),
      refresh: () => customFetch(getApiEndpoint('auth.refresh'), { method: 'POST' })
    },
    
    users: {
      list: (params = {}) => customFetch(getApiEndpoint('users.list'), { method: 'GET', query: params }),
      get: (id) => customFetch(getApiEndpoint('users.get', id), { method: 'GET' }),
      create: (data) => customFetch(getApiEndpoint('users.create'), { method: 'POST', body: data }),
      update: (id, data) => customFetch(getApiEndpoint('users.update', id), { method: 'PUT', body: data }),
      delete: (id) => customFetch(getApiEndpoint('users.delete', id), { method: 'DELETE' })
    },
    
    companies: {
      list: (params = {}) => customFetch(getApiEndpoint('companies.list'), { method: 'GET', query: params }),
      get: (id) => customFetch(getApiEndpoint('companies.get', id), { method: 'GET' }),
      create: (data) => customFetch(getApiEndpoint('companies.create'), { method: 'POST', body: data }),
      // FormData ile PUT request için POST kullan, _method field'i FormData'da olmalı
      update: (id, data) => {
        // FormData ise POST kullan (Laravel _method spoofing için)
        const method = data instanceof FormData ? 'POST' : 'PUT'
        return customFetch(getApiEndpoint('companies.update', id), { method, body: data })
      },
      delete: (id) => customFetch(getApiEndpoint('companies.delete', id), { method: 'DELETE' }),
      search: (query) => customFetch(getApiEndpoint('companies.search'), { method: 'GET', query: { q: query } }),
      attributes: (id) => customFetch(getApiEndpoint('companies.attributes', id), { method: 'GET' }),
      products: (id) => customFetch(getApiEndpoint('companies.products', id), { method: 'GET' })
    },
    
    products: {
      list: (params = {}) => customFetch(getApiEndpoint('products.list'), { method: 'GET', query: params }),
      get: (id) => customFetch(getApiEndpoint('products.get', id), { method: 'GET' }),
      create: (data) => customFetch(getApiEndpoint('products.create'), { method: 'POST', body: data }),
      update: (id, data) => customFetch(getApiEndpoint('products.update', id), { method: 'PUT', body: data }),
      delete: (id) => customFetch(getApiEndpoint('products.delete', id), { method: 'DELETE' }),
      deleteAll: () => customFetch(getApiEndpoint('products.deleteAll'), { method: 'DELETE' }),
      search: (query) => customFetch(getApiEndpoint('products.search'), { method: 'GET', query: { q: query } }),
      byCompany: (companyId) => customFetch(getApiEndpoint('products.byCompany', companyId), { method: 'GET' }),
      scan: (data) => customFetch(getApiEndpoint('products.scan'), { method: 'POST', body: data }),
      marketplaceUrls: (data) => customFetch(getApiEndpoint('products.marketplaceUrls'), { method: 'POST', body: data })
    },
    
    brands: {
      list: (params = {}) => customFetch(getApiEndpoint('brands.list'), { method: 'GET', query: params }),
      get: (id) => customFetch(getApiEndpoint('brands.get', id), { method: 'GET' }),
      create: (data) => customFetch(getApiEndpoint('brands.create'), { method: 'POST', body: data }),
      update: (id, data) => customFetch(getApiEndpoint('brands.update', id), { method: 'PUT', body: data }),
      delete: (id) => customFetch(getApiEndpoint('brands.delete', id), { method: 'DELETE' })
    },
    
    categories: {
      list: (params = {}) => customFetch(getApiEndpoint('categories.list'), { method: 'GET', query: params }),
      get: (id) => customFetch(getApiEndpoint('categories.get', id), { method: 'GET' }),
      create: (data) => customFetch(getApiEndpoint('categories.create'), { method: 'POST', body: data }),
      update: (id, data) => customFetch(getApiEndpoint('categories.update', id), { method: 'PUT', body: data }),
      delete: (id) => customFetch(getApiEndpoint('categories.delete', id), { method: 'DELETE' }),
      tree: () => customFetch(getApiEndpoint('categories.tree'), { method: 'GET' })
    },
    
    scanning: {
      quickScan: (data) => customFetch(getApiEndpoint('scanning.quick-scan'), { method: 'POST', body: data }),
      demoScan: (data) => customFetch(getApiEndpoint('scanning.demo-scan'), { method: 'POST', body: data }),
      profileScan: (data) => customFetch(getApiEndpoint('scanning.profile-scan'), { method: 'POST', body: data }),
      chromeQuickScan: (data) => customFetch(getApiEndpoint('scanning.chrome-quick-scan'), { method: 'POST', body: data }),
      chromeProfileScan: (data) => customFetch(getApiEndpoint('scanning.chrome-profile-scan'), { method: 'POST', body: data }),
      operations: (params = {}) => customFetch(getApiEndpoint('scanning.operations'), { method: 'GET', query: params }),
      jobDetails: (id) => customFetch(getApiEndpoint('scanning.job-details', id), { method: 'GET' }),
      jobJson: (id) => customFetch(getApiEndpoint('scanning.job-json', id), { method: 'GET' }),
      jobStatus: (id) => customFetch(getApiEndpoint('scanning.job-status', id), { method: 'GET' }),
      scraperData: (jobId) => customFetch(getApiEndpoint('scanning.scraper-data', jobId), { method: 'GET' }),
      retryScan: (data) => customFetch(getApiEndpoint('scanning.retry-scan'), { method: 'POST', body: data }),
      retryBulkScan: (data) => customFetch(getApiEndpoint('scanning.retry-bulk-scan'), { method: 'POST', body: data }),
      quickScanProduct: (productId) => customFetch(getApiEndpoint('scanning.quick-scan-product'), { method: 'POST', body: { product_id: productId } }),
      companies: (params = {}) => customFetch(getApiEndpoint('scanning.companies'), { method: 'GET', query: params }),
      purgeQueues: (data = {}) => customFetch(getApiEndpoint('scanning.purge-queues'), { method: 'POST', body: data }),
      scheduledScans: {
        list: (params = {}) => customFetch(getApiEndpoint('scanning.scheduled-scans'), { method: 'GET', query: params }),
        create: (data) => customFetch(getApiEndpoint('scanning.scheduled-scans'), { method: 'POST', body: data }),
        delete: (id) => customFetch(getApiEndpoint('scanning.scheduled-scans', id), { method: 'DELETE' })
      }
    },
    
    cronJobs: {
      list: (params = {}) => customFetch(getApiEndpoint('cron-jobs.list'), { method: 'GET', query: params }),
      get: (id) => customFetch(getApiEndpoint('cron-jobs.get', id), { method: 'GET' }),
      create: (data) => customFetch(getApiEndpoint('cron-jobs.create'), { method: 'POST', body: data }),
      update: (id, data) => customFetch(getApiEndpoint('cron-jobs.update', id), { method: 'PUT', body: data }),
      delete: (id) => customFetch(getApiEndpoint('cron-jobs.delete', id), { method: 'DELETE' }),
      toggle: (id) => customFetch(getApiEndpoint('cron-jobs.toggle', id), { method: 'PUT' }),
      runScheduled: () => customFetch(getApiEndpoint('cron-jobs.run-scheduled'), { method: 'POST' })
    },
    
    reports: {
      dashboard: () => customFetch(getApiEndpoint('reports.dashboard'), { method: 'GET' }),
      products: (params = {}) => customFetch(getApiEndpoint('reports.products'), { method: 'GET', query: params }),
      companies: (params = {}) => customFetch(getApiEndpoint('reports.companies'), { method: 'GET', query: params }),
      scanning: (params = {}) => customFetch(getApiEndpoint('reports.scanning'), { method: 'GET', query: params })
    }
  }
  
  return {
    provide: {
      api: apiClient
    }
  }
})