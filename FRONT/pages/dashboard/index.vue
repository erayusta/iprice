<template>
  <div class="space-y-6">
    <!-- Welcome Section -->
    <div class="card-elevated">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 mb-2">
            Hoş geldin, {{ authStore.user?.name }}! 👋
          </h1>
          <p class="text-gray-600 text-lg">
            Fiyat takip sisteminize genel bakış
          </p>
        </div>
        <div class="hidden md:block">
          <div class="w-20 h-20 bg-gradient-to-br from-apple-blue to-apple-indigo rounded-3xl flex items-center justify-center">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Toplam İzlenen Ürün -->
      <div class="card-elevated">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Toplam İzlenen Ürün</p>
            <p class="text-3xl font-bold text-gray-900">{{ stats.totalProducts }}</p>
            <p class="text-sm text-apple-blue flex items-center mt-1">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12" />
              </svg>
              +{{ stats.productGrowth }}% bu ay
            </p>
          </div>
          <div class="w-12 h-12 bg-apple-blue/10 rounded-2xl flex items-center justify-center">
            <svg class="w-6 h-6 text-apple-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Toplam Rakip Firma -->
      <div class="card-elevated">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Takip Edilen Rakip</p>
            <p class="text-3xl font-bold text-gray-900">{{ stats.totalCompetitors }}</p>
            <p class="text-sm text-gray-500 flex items-center mt-1">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              Aktif rakipler
            </p>
          </div>
          <div class="w-12 h-12 bg-apple-purple/10 rounded-2xl flex items-center justify-center">
            <svg class="w-6 h-6 text-apple-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Fiyat Avantajı -->
      <div class="card-elevated">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Fiyat Avantajı</p>
            <p class="text-3xl font-bold text-gray-900">{{ stats.priceAdvantage }}%</p>
            <p class="text-sm text-apple-green flex items-center mt-1">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              {{ stats.cheaperProducts }} üründe daha ucuz
            </p>
          </div>
          <div class="w-12 h-12 bg-apple-green/10 rounded-2xl flex items-center justify-center">
            <svg class="w-6 h-6 text-apple-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Fiyat Uyarıları -->
      <div class="card-elevated">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Fiyat Uyarıları</p>
            <p class="text-3xl font-bold text-gray-900">{{ stats.priceAlerts }}</p>
            <p class="text-sm text-apple-orange flex items-center mt-1">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              Rakipler daha ucuz
            </p>
          </div>
          <div class="w-12 h-12 bg-apple-orange/10 rounded-2xl flex items-center justify-center">
            <svg class="w-6 h-6 text-apple-orange" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts and Analytics -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Price Trend Chart -->
      <div class="card-elevated">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-900">Ortalama Fiyat Farkı Trendi</h3>
          <div class="flex space-x-2">
            <button class="px-3 py-1 text-xs font-medium text-apple-blue bg-blue-50 rounded-full">7 Gün</button>
            <button class="px-3 py-1 text-xs font-medium text-gray-500 hover:text-gray-700 rounded-full">30 Gün</button>
          </div>
        </div>
        <div class="h-64 bg-gradient-to-br from-apple-blue/5 to-apple-indigo/5 rounded-2xl flex items-center justify-center">
          <div class="text-center">
            <svg class="w-16 h-16 text-apple-blue/30 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
            <p class="text-gray-500 font-medium mb-2">Fiyat Karşılaştırma Grafiği</p>
            <p class="text-sm text-gray-400">Son 7 günlük fiyat değişimleri</p>
          </div>
        </div>
      </div>

      <!-- Recent Price Changes -->
      <div class="card-elevated">
        <h3 class="text-lg font-semibold text-gray-900 mb-6">Son Fiyat Değişiklikleri</h3>
        <div class="space-y-4">
          <div v-for="change in recentPriceChanges" :key="change.id" class="flex items-center space-x-4">
            <div :class="[
              'w-10 h-10 rounded-2xl flex items-center justify-center',
              change.type === 'down' ? 'bg-apple-green/10' : 
              change.type === 'up' ? 'bg-apple-red/10' : 
              'bg-apple-orange/10'
            ]">
              <svg v-if="change.type === 'down'" class="w-5 h-5 text-apple-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
              <svg v-else-if="change.type === 'up'" class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <svg v-else class="w-5 h-5 text-apple-orange" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">{{ change.product }}</p>
              <p class="text-xs text-gray-500">{{ change.competitor }} - {{ change.time }}</p>
            </div>
            <span :class="[
              'text-sm font-semibold',
              change.type === 'down' ? 'text-apple-green' : 
              change.type === 'up' ? 'text-red-500' : 
              'text-apple-orange'
            ]">
              {{ change.change }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Competitor Comparison -->
    <div class="card-elevated">
      <h3 class="text-lg font-semibold text-gray-900 mb-6">Rakip Firma Karşılaştırması</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="competitor in competitorComparison" :key="competitor.id" 
             class="p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl border border-gray-200">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm">
                <span class="text-lg font-bold text-gray-700">{{ competitor.initial }}</span>
              </div>
              <div>
                <h4 class="font-semibold text-gray-900">{{ competitor.name }}</h4>
                <p class="text-xs text-gray-500">{{ competitor.productCount }} ürün</p>
              </div>
            </div>
          </div>
          <div class="space-y-2">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">Ortalama Fark:</span>
              <span :class="[
                'font-semibold',
                competitor.avgDiff > 0 ? 'text-apple-green' : 'text-red-500'
              ]">
                {{ competitor.avgDiff > 0 ? '+' : '' }}{{ competitor.avgDiff }}%
              </span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">Daha Ucuz:</span>
              <span class="font-medium text-gray-900">{{ competitor.cheaper }} ürün</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">Daha Pahalı:</span>
              <span class="font-medium text-gray-900">{{ competitor.expensive }} ürün</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Top Products by Price Difference -->
    <div class="card-elevated">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-lg font-semibold text-gray-900">En Çok Fark Olan Ürünler</h3>
        <NuxtLink to="/dashboard/price-analysis" class="text-sm text-apple-blue hover:text-apple-indigo font-medium">
          Tümünü Gör →
        </NuxtLink>
      </div>
      <div class="space-y-3">
        <div v-for="product in topProducts" :key="product.id" 
             class="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
          <div class="flex items-center space-x-4 flex-1 min-w-0">
            <div class="w-12 h-12 bg-white rounded-xl shadow-sm flex items-center justify-center overflow-hidden">
              <span class="text-xs text-gray-400">📦</span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-gray-900 truncate">{{ product.name }}</p>
              <p class="text-sm text-gray-500">{{ product.sku }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-6">
            <div class="text-right">
              <p class="text-sm text-gray-600">Bizim Fiyat</p>
              <p class="font-semibold text-gray-900">₺{{ product.ourPrice }}</p>
            </div>
            <div class="text-right">
              <p class="text-sm text-gray-600">Rakip Ort.</p>
              <p class="font-semibold text-gray-900">₺{{ product.competitorAvg }}</p>
            </div>
            <div class="text-right min-w-[80px]">
              <p class="text-sm text-gray-600">Fark</p>
              <p :class="[
                'font-bold text-lg',
                product.difference > 0 ? 'text-apple-green' : 'text-red-500'
              ]">
                {{ product.difference > 0 ? '+' : '' }}{{ product.difference }}%
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="card-elevated">
      <h3 class="text-lg font-semibold text-gray-900 mb-6">Hızlı İşlemler</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <NuxtLink to="/dashboard/price-analysis" class="group p-6 bg-gradient-to-br from-apple-blue/5 to-apple-blue/10 rounded-2xl hover:from-apple-blue/10 hover:to-apple-blue/20 transition-all duration-200 border border-apple-blue/20">
          <div class="text-center">
            <div class="w-12 h-12 bg-apple-blue/20 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <svg class="w-6 h-6 text-apple-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h4 class="font-medium text-gray-900 mb-1">Fiyat Analizi</h4>
            <p class="text-sm text-gray-600">Detaylı karşılaştırma</p>
          </div>
        </NuxtLink>

        <NuxtLink to="/dashboard/products" class="group p-6 bg-gradient-to-br from-apple-green/5 to-apple-green/10 rounded-2xl hover:from-apple-green/10 hover:to-apple-green/20 transition-all duration-200 border border-apple-green/20">
          <div class="text-center">
            <div class="w-12 h-12 bg-apple-green/20 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <svg class="w-6 h-6 text-apple-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <h4 class="font-medium text-gray-900 mb-1">Ürünler</h4>
            <p class="text-sm text-gray-600">Ürün yönetimi</p>
          </div>
        </NuxtLink>

        <button class="group p-6 bg-gradient-to-br from-apple-purple/5 to-apple-purple/10 rounded-2xl hover:from-apple-purple/10 hover:to-apple-purple/20 transition-all duration-200 border border-apple-purple/20">
          <div class="text-center">
            <div class="w-12 h-12 bg-apple-purple/20 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <svg class="w-6 h-6 text-apple-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
            <h4 class="font-medium text-gray-900 mb-1">Fiyat Güncelle</h4>
            <p class="text-sm text-gray-600">Manuel güncelleme</p>
          </div>
        </button>

        <NuxtLink to="/dashboard/settings" class="group p-6 bg-gradient-to-br from-apple-orange/5 to-apple-orange/10 rounded-2xl hover:from-apple-orange/10 hover:to-apple-orange/20 transition-all duration-200 border border-apple-orange/20">
          <div class="text-center">
            <div class="w-12 h-12 bg-apple-orange/20 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <svg class="w-6 h-6 text-apple-orange" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h4 class="font-medium text-gray-900 mb-1">Ayarlar</h4>
            <p class="text-sm text-gray-600">Sistem ayarları</p>
          </div>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  middleware: 'auth',
  layout: 'dashboard'
})

const authStore = useAuthStore()

// Mock Data - İstatistikler
const stats = {
  totalProducts: 247,
  productGrowth: 8.5,
  totalCompetitors: 12,
  priceAdvantage: 15.3,
  cheaperProducts: 156,
  priceAlerts: 23
}

// Mock Data - Son Fiyat Değişiklikleri
const recentPriceChanges = [
  {
    id: 1,
    product: 'iPhone 15 Pro 256GB',
    competitor: 'Trendyol',
    time: '5 dk önce',
    type: 'down',
    change: '-₺500'
  },
  {
    id: 2,
    product: 'Samsung Galaxy S24 Ultra',
    competitor: 'Hepsiburada',
    time: '15 dk önce',
    type: 'up',
    change: '+₺350'
  },
  {
    id: 3,
    product: 'AirPods Pro 2. Nesil',
    competitor: 'N11',
    time: '32 dk önce',
    type: 'alert',
    change: '-₺200'
  },
  {
    id: 4,
    product: 'MacBook Air M2',
    competitor: 'Teknosa',
    time: '1 saat önce',
    type: 'down',
    change: '-₺1,250'
  },
  {
    id: 5,
    product: 'Sony WH-1000XM5',
    competitor: 'Media Markt',
    time: '2 saat önce',
    type: 'up',
    change: '+₺450'
  }
]

// Mock Data - Rakip Firma Karşılaştırması
const competitorComparison = [
  {
    id: 1,
    name: 'Trendyol',
    initial: 'T',
    productCount: 189,
    avgDiff: 12.5,
    cheaper: 124,
    expensive: 65
  },
  {
    id: 2,
    name: 'Hepsiburada',
    initial: 'H',
    productCount: 203,
    avgDiff: 8.3,
    cheaper: 142,
    expensive: 61
  },
  {
    id: 3,
    name: 'N11',
    initial: 'N',
    productCount: 156,
    avgDiff: 15.7,
    cheaper: 98,
    expensive: 58
  },
  {
    id: 4,
    name: 'GittiGidiyor',
    initial: 'G',
    productCount: 134,
    avgDiff: -3.2,
    cheaper: 58,
    expensive: 76
  },
  {
    id: 5,
    name: 'Teknosa',
    initial: 'T',
    productCount: 178,
    avgDiff: 18.9,
    cheaper: 132,
    expensive: 46
  },
  {
    id: 6,
    name: 'Media Markt',
    initial: 'M',
    productCount: 145,
    avgDiff: 6.4,
    cheaper: 89,
    expensive: 56
  }
]

// Mock Data - En Çok Fark Olan Ürünler
const topProducts = [
  {
    id: 1,
    name: 'iPhone 15 Pro Max 1TB Titanyum',
    sku: 'APL-IP15PM-1TB-TT',
    ourPrice: '54,999',
    competitorAvg: '62,450',
    difference: 13.5
  },
  {
    id: 2,
    name: 'Samsung Galaxy S24 Ultra 512GB',
    sku: 'SAM-S24U-512-BLK',
    ourPrice: '47,999',
    competitorAvg: '51,250',
    difference: 6.8
  },
  {
    id: 3,
    name: 'MacBook Pro 16" M3 Max 64GB',
    sku: 'APL-MBP16-M3M-64',
    ourPrice: '124,999',
    competitorAvg: '118,750',
    difference: -5.0
  },
  {
    id: 4,
    name: 'Sony PlayStation 5 Slim Digital',
    sku: 'SNY-PS5-SLM-DIG',
    ourPrice: '16,999',
    competitorAvg: '18,450',
    difference: 8.5
  },
  {
    id: 5,
    name: 'Dyson V15 Detect Absolute',
    sku: 'DYS-V15-DET-ABS',
    ourPrice: '18,499',
    competitorAvg: '21,250',
    difference: 14.9
  }
]
</script>
