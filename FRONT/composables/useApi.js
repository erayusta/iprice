/**
 * API kullanımı için composable
 * Bu composable sayesinde her component'te $api'yi inject etmek zorunda kalmayız
 */

export const useApi = () => {
  const { $api } = useNuxtApp()
  
  if (!$api) {
    throw new Error('API client bulunamadı. Lütfen api.client.js plugin\'inin yüklendiğinden emin olun.')
  }
  
  return $api
}

/**
 * Belirli bir endpoint'i kullanmak için composable
 * @param {string} endpointPath - Endpoint path'i (örn: 'auth.login')
 * @returns {object} Endpoint metodları
 */
export const useApiEndpoint = (endpointPath) => {
  const api = useApi()
  const { getApiEndpoint } = api
  
  return {
    get: (params = {}) => api.get(getApiEndpoint(endpointPath), { query: params }),
    post: (body, options = {}) => api.post(getApiEndpoint(endpointPath), body, options),
    put: (body, options = {}) => api.put(getApiEndpoint(endpointPath), body, options),
    patch: (body, options = {}) => api.patch(getApiEndpoint(endpointPath), body, options),
    delete: (options = {}) => api.delete(getApiEndpoint(endpointPath), options),
    url: getApiEndpoint(endpointPath)
  }
}

/**
 * Auth API'leri için özel composable
 */
export const useAuthApi = () => {
  const api = useApi()
  return api.auth
}

/**
 * Users API'leri için özel composable
 */
export const useUsersApi = () => {
  const api = useApi()
  return api.users
}

/**
 * Companies API'leri için özel composable
 */
export const useCompaniesApi = () => {
  const api = useApi()
  return api.companies
}

/**
 * Products API'leri için özel composable
 */
export const useProductsApi = () => {
  const api = useApi()
  return api.products
}

/**
 * Brands API'leri için özel composable
 */
export const useBrandsApi = () => {
  const api = useApi()
  return api.brands
}

/**
 * Categories API'leri için özel composable
 */
export const useCategoriesApi = () => {
  const api = useApi()
  return api.categories
}


/**
 * Scanning API'leri için özel composable
 */
export const useScanningApi = () => {
  const api = useApi()
  return api.scanning
}

/**
 * CronJob API'leri için özel composable
 */
export const useCronJobApi = () => {
  const api = useApi()
  return api.cronJobs
}

/**
 * Reports API'leri için özel composable
 */
export const useReportsApi = () => {
  const api = useApi()
  return api.reports
}

/**
 * API endpoint'lerini almak için composable
 */
export const useApiEndpoints = () => {
  const api = useApi()
  return {
    getEndpoint: api.getEndpoint,
    endpoints: api.endpoints
  }
}
