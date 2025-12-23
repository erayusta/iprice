// API Helper Functions for Chrome Extension
// Bu dosya backend API ile iletişim için helper fonksiyonları içerir

// API_CONFIG'i yükle (eğer ayrı dosyada ise)
// Not: Bu dosya sidepanel içinde kullanılacaksa, script tag ile yüklenmeli

/**
 * API isteği gönder
 */
async function apiRequest(endpoint, method = 'POST', data = null) {
  try {
    // API config'i al
    const baseURL = await getAPIBaseURL();
    const token = await getAPIToken();
    
    if (!token) {
      throw new Error('API token bulunamadı. Lütfen ayarlardan token girin.');
    }
    
    const url = `${baseURL}${endpoint}`;
    
    const options = {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    };
    
    // Token'ı request body'ye ekle (backend token'ı body'den bekliyor)
    if (data) {
      data.token = token;
      options.body = JSON.stringify(data);
    } else {
      options.body = JSON.stringify({ token: token });
    }
    
    const response = await fetch(url, options);
    const result = await response.json();
    
    if (!response.ok) {
      throw new Error(result.message || `API hatası: ${response.status}`);
    }
    
    return result;
  } catch (error) {
    console.error('API Request Error:', error);
    throw error;
  }
}

/**
 * API token al
 */
async function getAPIToken() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['apiToken'], (result) => {
      resolve(result.apiToken || null);
    });
  });
}

/**
 * API base URL al
 */
async function getAPIBaseURL() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['apiBaseURL'], (result) => {
      // Default URL
      const defaultURL = 'http://localhost:8000/api';
      resolve(result.apiBaseURL || defaultURL);
    });
  });
}

/**
 * Token doğrula
 */
async function validateToken(token) {
  try {
    const baseURL = await getAPIBaseURL();
    const url = `${baseURL}/chrome-extension/validate-token`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ token })
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Token validation error:', error);
    throw error;
  }
}

/**
 * Bağlantı testi yap
 */
async function testConnection() {
  try {
    const result = await apiRequest('/chrome-extension/test-connection', 'POST');
    return result;
  } catch (error) {
    throw error;
  }
}

/**
 * Etiketleri senkronize et
 */
async function syncLabels(labels) {
  try {
    const result = await apiRequest('/chrome-extension/sync-labels', 'POST', {
      labels: labels
    });
    return result;
  } catch (error) {
    throw error;
  }
}

/**
 * Etiketleri getir
 */
async function getLabels() {
  try {
    const result = await apiRequest('/chrome-extension/get-labels', 'POST');
    return result;
  } catch (error) {
    throw error;
  }
}

/**
 * Seçicileri senkronize et
 */
async function syncSelectors(selectors) {
  try {
    const result = await apiRequest('/chrome-extension/sync-selectors', 'POST', {
      selectors: selectors
    });
    return result;
  } catch (error) {
    throw error;
  }
}

/**
 * Seçicileri getir
 */
async function getSelectors(domain = null) {
  try {
    const data = domain ? { domain } : {};
    const result = await apiRequest('/chrome-extension/get-selectors', 'POST', data);
    return result;
  } catch (error) {
    throw error;
  }
}

// Export functions for use in other files
if (typeof window !== 'undefined') {
  window.apiHelper = {
    validateToken,
    testConnection,
    syncLabels,
    getLabels,
    syncSelectors,
    getSelectors,
    getAPIToken,
    getAPIBaseURL
  };
}

// Eğer module system kullanılıyorsa
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    validateToken,
    testConnection,
    syncLabels,
    getLabels,
    syncSelectors,
    getSelectors,
    getAPIToken,
    getAPIBaseURL
  };
}

