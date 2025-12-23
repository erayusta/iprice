# API Kullanım Kılavuzu

Bu projede API endpoint'lerini tek bir yerden yönetebilmek için merkezi bir yapı kurulmuştur.

## 📁 Dosya Yapısı

```
config/
├── api-endpoints.js          # Tüm API endpoint'lerinin tanımlandığı dosya
composables/
├── useApi.js                 # API kullanımı için composable'lar
plugins/
├── api.client.js             # API client konfigürasyonu
examples/
├── api-usage-examples.vue    # Kullanım örnekleri
```

## 🚀 Kullanım Yöntemleri

### 1. Composable ile Kullanım (Önerilen)

```vue
<script setup>
// Auth API'leri için
const authApi = useAuthApi()
const user = await authApi.me()

// Companies API'leri için
const companiesApi = useCompaniesApi()
const companies = await companiesApi.list()

// Products API'leri için
const productsApi = useProductsApi()
const products = await productsApi.search('laptop')
</script>
```

### 2. Direkt API Client Kullanımı

```vue
<script setup>
const { $api } = useNuxtApp()

// Temel HTTP metodları
const data = await $api.get('/users')
const result = await $api.post('/users', { name: 'John' })

// Endpoint helper ile
const endpoint = $api.getEndpoint('users.get', 123)
const user = await $api.get(endpoint)
</script>
```

### 3. Endpoint URL'lerini Alma

```vue
<script setup>
const { getEndpoint } = useApiEndpoints()

// Statik endpoint'ler
const loginUrl = getEndpoint('auth.login')        // '/auth/login'
const usersUrl = getEndpoint('users.list')        // '/users'

// Parametreli endpoint'ler
const userUrl = getEndpoint('users.get', 123)     // '/users/123'
const productUrl = getEndpoint('products.get', 456) // '/products/456'
</script>
```

## 🔧 Yeni Endpoint Ekleme

`config/api-endpoints.js` dosyasına yeni endpoint'ler ekleyebilirsin:

```javascript
export const API_ENDPOINTS = {
  // Mevcut endpoint'ler...
  
  // Yeni endpoint grubu
  notifications: {
    list: '/notifications',
    markAsRead: (id) => `/notifications/${id}/read`,
    delete: (id) => `/notifications/${id}`
  }
}
```

Sonra `plugins/api.client.js` dosyasına da ekle:

```javascript
const apiClient = {
  // Mevcut metodlar...
  
  notifications: {
    list: (params = {}) => customFetch(getApiEndpoint('notifications.list'), { method: 'GET', query: params }),
    markAsRead: (id) => customFetch(getApiEndpoint('notifications.markAsRead', id), { method: 'PATCH' }),
    delete: (id) => customFetch(getApiEndpoint('notifications.delete', id), { method: 'DELETE' })
  }
}
```

Ve `composables/useApi.js` dosyasına composable ekle:

```javascript
export const useNotificationsApi = () => {
  const api = useApi()
  return api.notifications
}
```

## 🌍 Environment Konfigürasyonu

API base URL'ini environment değişkeni ile kontrol edebilirsin:

```bash
# .env dosyasında
NUXT_PUBLIC_API_BASE=http://localhost:8082/api
```

Farklı ortamlar için:
- **Development**: `http://localhost:8082/api`
- **Staging**: `https://staging-api.yourdomain.com/api`
- **Production**: `https://api.yourdomain.com/api`

## 📝 Örnek Kullanımlar

### Login İşlemi
```javascript
const authApi = useAuthApi()
const response = await authApi.login({
  email: 'user@example.com',
  password: 'password123'
})
```

### Şirket Listesi
```javascript
const companiesApi = useCompaniesApi()
const companies = await companiesApi.list({
  page: 1,
  limit: 10,
  search: 'trendyol'
})
```

### Ürün Arama
```javascript
const productsApi = useProductsApi()
const results = await productsApi.search('laptop')
```

### Şirket Detayı
```javascript
const companiesApi = useCompaniesApi()
const company = await companiesApi.get(123)
```

## 🔐 Authentication

API client otomatik olarak localStorage'dan token'ı alır ve header'a ekler. 401 hatası durumunda otomatik logout yapar.

## ⚡ Avantajlar

1. **Merkezi Yönetim**: Tüm endpoint'ler tek yerde
2. **Type Safety**: Endpoint'ler merkezi olarak tanımlanmış
3. **Kolay Bakım**: URL değişiklikleri tek yerden yapılır
4. **Otomatik Auth**: Token yönetimi otomatik
5. **Error Handling**: Merkezi hata yönetimi
6. **Environment Support**: Farklı ortamlar için kolay konfigürasyon

## 🐛 Hata Ayıklama

API çağrılarında hata alırsan:

1. Browser console'da network tab'ını kontrol et
2. API base URL'inin doğru olduğundan emin ol
3. Endpoint'in `config/api-endpoints.js`'te tanımlı olduğunu kontrol et
4. Backend API'nin çalıştığından emin ol
