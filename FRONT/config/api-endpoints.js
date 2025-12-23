/**
 * API Endpoint Konfigürasyonu
 * Tüm API endpoint'leri bu dosyada tanımlanır
 */

export const API_ENDPOINTS = {
  // Auth endpoints
  auth: {
    login: '/auth/login',
    register: '/auth/register',
    logout: '/auth/logout',
    refresh: '/auth/refresh',
    me: '/auth/me',
    forgotPassword: '/auth/forgot-password',
    resetPassword: '/auth/reset-password'
  },

  // User endpoints
  users: {
    list: '/users',
    create: '/users',
    get: (id) => `/users/${id}`,
    update: (id) => `/users/${id}`,
    delete: (id) => `/users/${id}`,
    profile: '/users/profile',
    updateProfile: '/users/profile'
  },

  // Company endpoints
  companies: {
    list: '/companies',
    create: '/companies',
    get: (id) => `/companies/${id}`,
    update: (id) => `/companies/${id}`,
    delete: (id) => `/companies/${id}`,
    search: '/companies/search',
    attributes: (id) => `/companies/${id}/attributes`,
    products: (id) => `/companies/${id}/products`
  },

  // Product endpoints
  products: {
    list: '/products',
    create: '/products',
    get: (id) => `/products/${id}`,
    update: (id) => `/products/${id}`,
    delete: (id) => `/products/${id}`,
    deleteAll: '/products/delete-all',
    search: '/products/search',
    byCompany: (companyId) => `/products/company/${companyId}`,
    scan: '/products/scan',
    bulkUpdate: '/products/bulk-update',
    marketplaceUrls: '/products/marketplace-urls'
  },

  // Brand endpoints
  brands: {
    list: '/brands',
    create: '/brands',
    get: (id) => `/brands/${id}`,
    update: (id) => `/brands/${id}`,
    delete: (id) => `/brands/${id}`,
    search: '/brands/search'
  },

  // Category endpoints
  categories: {
    list: '/categories',
    create: '/categories',
    get: (id) => `/categories/${id}`,
    update: (id) => `/categories/${id}`,
    delete: (id) => `/categories/${id}`,
    tree: '/categories/tree'
  },

  // Scanning endpoints
  scanning: {
    'quick-scan': '/scanning/quick-scan',
    'demo-scan': '/scanning/demo-scan',
    'profile-scan': '/scanning/profile-scan',
    'scheduled-scans': '/scanning/scheduled-scans',
    'operations': '/scanning/operations',
    'job-details': (id) => `/scanning/job-details/${id}`,
    'job-json': (id) => `/scanning/job-json/${id}`,
    'job-status': (id) => `/scanning/job-status/${id}`,
    'scraper-data': (jobId) => `/scanning/scraper-data/${jobId}`,
    'retry-scan': '/scanning/retry-scan',
    'retry-bulk-scan': '/scanning/retry-bulk-scan',
    'quick-scan-product': '/scanning/quick-scan-product',
    'companies': '/scanning/companies',
    'purge-queues': '/scanning/purge-queues',
    'chrome-quick-scan': '/chrome-extension/quick-scan',
    'chrome-profile-scan': '/chrome-extension/profile-scan'
  },

  // CronJob endpoints
  'cron-jobs': {
    list: '/cron-jobs',
    create: '/cron-jobs',
    get: (id) => `/cron-jobs/${id}`,
    update: (id) => `/cron-jobs/${id}`,
    delete: (id) => `/cron-jobs/${id}`,
    toggle: (id) => `/cron-jobs/${id}/toggle`,
    'run-scheduled': '/cron-jobs/run-scheduled'
  },

  // Reports endpoints
  reports: {
    dashboard: '/reports/dashboard',
    products: '/reports/products',
    companies: '/reports/companies',
    scanning: '/reports/scanning',
    export: '/reports/export'
  },

  // Settings endpoints
  settings: {
    get: '/settings',
    update: '/settings',
    reset: '/settings/reset'
  },

  // File upload endpoints
  upload: {
    image: '/upload/image',
    csv: '/upload/csv',
    excel: '/upload/excel'
  },

  // Crawler endpoints
  crawlers: {
    list: '/crawlers',
    create: '/crawlers',
    get: (id) => `/crawlers/${id}`,
    update: (id) => `/crawlers/${id}`,
    delete: (id) => `/crawlers/${id}`
  },

  // Server endpoints
  servers: {
    list: '/servers',
    create: '/servers',
    get: (id) => `/servers/${id}`,
    update: (id) => `/servers/${id}`,
    delete: (id) => `/servers/${id}`
  },

  // Attributes endpoints
  attributes: {
    list: '/attributes',
    create: '/attributes',
    get: (id) => `/attributes/${id}`,
    update: (id) => `/attributes/${id}`,
    delete: (id) => `/attributes/${id}`
  },

  // Company attributes endpoints
  'company-attributes': {
    list: '/company-attributes',
    create: '/company-attributes',
    get: (id) => `/company-attributes/${id}`,
    update: (id) => `/company-attributes/${id}`,
    delete: (id) => `/company-attributes/${id}`
  },

  // Custom profiles endpoints
  'custom-profiles': {
    list: '/custom-profiles',
    create: '/custom-profiles',
    get: (id) => `/custom-profiles/${id}`,
    update: (id) => `/custom-profiles/${id}`,
    delete: (id) => `/custom-profiles/${id}`,
    products: (id) => `/custom-profiles/${id}/products`,
    share: (id) => `/custom-profiles/${id}/share`,
    unshare: (id) => `/custom-profiles/${id}/unshare`,
    sharedUsers: (id) => `/custom-profiles/${id}/shared-users`,
    availableUsers: (id) => `/custom-profiles/${id}/available-users`
  },

  // Price Analysis endpoints
  'price-analysis': {
    'company-list': '/price-analysis/company-list',
    'price-summary': '/price-analysis/price-summary',
    'company-url-list': '/price-analysis/company-url-list',
    'price-history': '/price-analysis/price-history',
    'product-prices': '/price-analysis/product-prices'
  },

}

/**
 * API endpoint'ini almak için yardımcı fonksiyon
 * @param {string} path - Endpoint path'i (örn: 'auth.login')
 * @param {...any} params - Endpoint parametreleri
 * @returns {string} Tam API endpoint URL'i
 */
export function getApiEndpoint(path, ...params) {
  const pathParts = path.split('.')
  let endpoint = API_ENDPOINTS
  
  // Nested path'i takip et
  for (const part of pathParts) {
    if (endpoint[part]) {
      endpoint = endpoint[part]
    } else {
      throw new Error(`API endpoint bulunamadı: ${path}`)
    }
  }
  
  // Eğer fonksiyon ise parametrelerle çağır
  if (typeof endpoint === 'function') {
    return endpoint(...params)
  }
  
  return endpoint
}

/**
 * Tüm endpoint'leri export et
 */
export default API_ENDPOINTS
