// API Configuration for Chrome Extension
// Bu dosyayı kendi backend URL'iniz ile güncelleyin

const API_CONFIG = {
  // Backend API base URL - Buraya kendi backend URL'inizi yazın
  baseURL: 'http://localhost:8000/api', // Örnek: 'https://api.example.com/api'
  
  // API endpoints
  endpoints: {
    validateToken: '/chrome-extension/validate-token',
    syncLabels: '/chrome-extension/sync-labels',
    getLabels: '/chrome-extension/get-labels',
    syncSelectors: '/chrome-extension/sync-selectors',
    getSelectors: '/chrome-extension/get-selectors',
    testConnection: '/chrome-extension/test-connection'
  },
  
  // API token - Storage'dan alınacak
  getToken: async () => {
    return new Promise((resolve) => {
      chrome.storage.local.get(['apiToken'], (result) => {
        resolve(result.apiToken || null);
      });
    });
  },
  
  // API token kaydet
  setToken: async (token) => {
    return new Promise((resolve) => {
      chrome.storage.local.set({ apiToken: token }, () => {
        resolve(true);
      });
    });
  },
  
  // API base URL kaydet
  setBaseURL: async (url) => {
    return new Promise((resolve) => {
      chrome.storage.local.set({ apiBaseURL: url }, () => {
        resolve(true);
      });
    });
  },
  
  // API base URL al
  getBaseURL: async () => {
    return new Promise((resolve) => {
      chrome.storage.local.get(['apiBaseURL'], (result) => {
        resolve(result.apiBaseURL || API_CONFIG.baseURL);
      });
    });
  }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
  module.exports = API_CONFIG;
}

