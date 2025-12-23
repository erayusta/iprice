<template>
  <div 
    class="fixed inset-y-0 left-0 z-50 bg-background-primary border-r border-gray-200 transform transition-all duration-300 ease-in-out" 
    :class="[
      isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
      isCollapsed ? 'w-20' : 'w-64'
    ]"
  >
    <!-- Sidebar Header -->
    <div class="flex items-center h-16 px-6 border-b border-gray-200" :class="isCollapsed ? 'justify-center' : 'justify-between'">
      <div class="flex items-center space-x-3">
        <button @click="toggleCollapse" class="w-8 h-8 bg-apple-blue rounded-xl flex items-center justify-center hover:bg-blue-600 transition-colors cursor-pointer">
          <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
          </svg>
        </button>
        <h1 v-show="!isCollapsed" class="text-xl font-semibold text-gray-900 transition-opacity duration-300">iPrice</h1>
      </div>
      <button @click="toggleSidebar" class="lg:hidden p-2 rounded-xl hover:bg-gray-100 transition-colors">
        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
      <div class="space-y-1">
        <h3 v-show="!isCollapsed" class="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Ana Menü</h3>
        
        <NuxtLink to="/dashboard" class="nav-item" :class="[{ 'nav-item-active': $route.path === '/dashboard' }, isCollapsed ? 'justify-center' : '']">
          <svg class="w-5 h-5" :class="isCollapsed ? '' : 'mr-3'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5a2 2 0 012-2h4a2 2 0 012 2v6H8V5z" />
          </svg>
          <span v-show="!isCollapsed">Anasayfa</span>
        </NuxtLink>


        <NuxtLink 
          v-if="hasPermission('companies.show')" 
          to="/dashboard/companies" 
          class="nav-item" 
          :class="[{ 'nav-item-active': $route.path === '/dashboard/companies' }, isCollapsed ? 'justify-center' : '']"
        >
          <svg class="w-5 h-5" :class="isCollapsed ? '' : 'mr-3'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
          <span v-show="!isCollapsed">Firmalar</span>
        </NuxtLink>

        <!-- Ürünler Dropdown -->
        <div v-if="hasPermission('products.show')" class="relative">
          <button 
            v-if="!isCollapsed"
            @click="toggleProductsDropdown" 
            class="nav-item w-full flex items-center justify-between"
            :class="{ 'nav-item-active': $route.path === '/dashboard/products' || $route.path === '/dashboard/user-products' }"
          >
            <div class="flex items-center">
              <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
              <span>Ürünler</span>
            </div>
            <svg 
              class="w-4 h-4 transition-transform duration-200" 
              :class="{ 'rotate-180': showProductsDropdown }"
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          <NuxtLink 
            v-else
            to="/dashboard/products" 
            class="nav-item justify-center"
            :class="{ 'nav-item-active': $route.path === '/dashboard/products' || $route.path === '/dashboard/user-products' }"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </NuxtLink>
          
          <!-- Dropdown Menu -->
          <div 
            v-show="showProductsDropdown && !isCollapsed" 
            class="ml-8 mt-2 space-y-1 transition-all duration-200"
          >
            <NuxtLink 
              v-if="hasPermission('products_url.show')"
              to="/dashboard/products" 
              class="nav-item text-sm" 
              :class="{ 'nav-item-active': $route.path === '/dashboard/products' }"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.102 1.101" />
              </svg>
              Ürün URL
            </NuxtLink>
            
            <NuxtLink 
              v-if="hasPermission('product_list.show')"
              to="/dashboard/user-products" 
              class="nav-item text-sm" 
              :class="{ 'nav-item-active': $route.path === '/dashboard/user-products' }"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              Ürün Listesi
            </NuxtLink>
          </div>
        </div>

        <NuxtLink 
          v-if="hasPermission('brands.show')" 
          to="/dashboard/brands" 
          class="nav-item" 
          :class="[{ 'nav-item-active': $route.path === '/dashboard/brands' }, isCollapsed ? 'justify-center' : '']"
        >
          <svg class="w-5 h-5" :class="isCollapsed ? '' : 'mr-3'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
          <span v-show="!isCollapsed">Markalar</span>
        </NuxtLink>

        <NuxtLink 
          to="/dashboard/price-analysis" 
          class="nav-item" 
          :class="[{ 'nav-item-active': $route.path === '/dashboard/price-analysis' }, isCollapsed ? 'justify-center' : '']"
        >
          <svg class="w-5 h-5" :class="isCollapsed ? '' : 'mr-3'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span v-show="!isCollapsed">Fiyat Analiz</span>
        </NuxtLink>

        <!-- İşlemler Dropdown -->
        <div v-if="hasPermission('operations.show')" class="relative">
          <button 
            v-if="!isCollapsed"
            @click="toggleOperationsDropdown" 
            class="nav-item w-full flex items-center justify-between"
            :class="{ 'nav-item-active': $route.path === '/dashboard/scanning' || $route.path === '/dashboard/custom-profile' || $route.path === '/dashboard/attributes' || $route.path === '/dashboard/proxy-settings' }"
          >
            <div class="flex items-center">
              <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
              <span>İşlemler</span>
            </div>
            <svg 
              class="w-4 h-4 transition-transform duration-200" 
              :class="{ 'rotate-180': showOperationsDropdown }"
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          <NuxtLink 
            v-else
            to="/dashboard/scanning" 
            class="nav-item justify-center"
            :class="{ 'nav-item-active': $route.path === '/dashboard/scanning' || $route.path === '/dashboard/custom-profile' || $route.path === '/dashboard/attributes' || $route.path === '/dashboard/proxy-settings' }"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
          </NuxtLink>
          
          <!-- Dropdown Menu -->
          <div 
            v-show="showOperationsDropdown && !isCollapsed" 
            class="ml-8 mt-2 space-y-1 transition-all duration-200"
          >
            <NuxtLink 
              v-if="hasPermission('scan.show')"
              to="/dashboard/scanning" 
              class="nav-item text-sm" 
              :class="{ 'nav-item-active': $route.path === '/dashboard/scanning' }"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Tarama
            </NuxtLink>
            
            <NuxtLink 
              v-if="hasPermission('privateanalysis.show')"
              to="/dashboard/custom-profile" 
              class="nav-item text-sm" 
              :class="{ 'nav-item-active': $route.path === '/dashboard/custom-profile' }"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Özel Analiz
            </NuxtLink>
            
            <NuxtLink 
              to="/dashboard/attributes" 
              class="nav-item text-sm" 
              :class="{ 'nav-item-active': $route.path === '/dashboard/attributes' }"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
              Attribute Ayarları
            </NuxtLink>
            
            <NuxtLink 
              to="/dashboard/proxy-settings" 
              class="nav-item text-sm" 
              :class="{ 'nav-item-active': $route.path === '/dashboard/proxy-settings' }"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9" />
              </svg>
              Proxy Ayarları
            </NuxtLink>
          </div>
        </div>
      </div>

      <div v-show="!isCollapsed" class="divider my-6"></div>

      <div class="space-y-1">
        <h3 v-show="!isCollapsed" class="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Ayarlar</h3>
        
        <!-- Üye Dropdown -->
        <div class="relative">
          <button 
            v-if="!isCollapsed"
            @click="toggleMemberDropdown" 
            class="nav-item w-full flex items-center justify-between"
            :class="{ 'nav-item-active': $route.path === '/dashboard/members' || $route.path === '/dashboard/roles' || $route.path === '/dashboard/role-assignments' }"
          >
            <div class="flex items-center">
              <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
              </svg>
              <span>Kullanıcı İşlemleri</span>
            </div>
            <svg 
              class="w-4 h-4 transition-transform duration-200" 
              :class="{ 'rotate-180': showMemberDropdown }"
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          <NuxtLink 
            v-else
            to="/dashboard/members" 
            class="nav-item justify-center"
            :class="{ 'nav-item-active': $route.path === '/dashboard/members' || $route.path === '/dashboard/roles' || $route.path === '/dashboard/role-assignments' }"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
            </svg>
          </NuxtLink>
          
          <!-- Dropdown Menu -->
          <div 
            v-show="showMemberDropdown && !isCollapsed" 
            class="ml-8 mt-2 space-y-1 transition-all duration-200"
          >
            <NuxtLink 
              to="/dashboard/members" 
              class="nav-item text-sm" 
              :class="{ 'nav-item-active': $route.path === '/dashboard/members' }"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              Kullanıcılar
            </NuxtLink>
            
            <NuxtLink 
              to="/dashboard/roles" 
              class="nav-item text-sm" 
              :class="{ 'nav-item-active': $route.path === '/dashboard/roles' }"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Roller
            </NuxtLink>
            
           
          </div>
        </div>

      </div>
    </nav>

    <!-- User Profile -->
    <div class="p-4 border-t border-gray-200">
      <div class="flex items-center p-3 rounded-xl hover:bg-gray-50 transition-colors cursor-pointer" :class="isCollapsed ? 'justify-center' : 'space-x-3'">
        <div class="w-10 h-10 bg-apple-blue rounded-xl flex items-center justify-center flex-shrink-0">
          <span class="text-white font-medium text-sm">{{ userInitials }}</span>
        </div>
        <div v-show="!isCollapsed" class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900 truncate">{{ authStore.user?.name || 'User' }}</p>
          <p class="text-xs text-gray-500 truncate">{{ authStore.user?.email || 'user@example.com' }}</p>
        </div>
        <button v-show="!isCollapsed" @click="handleLogout" class="p-2 rounded-xl hover:bg-gray-100 transition-colors">
          <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </button>
      </div>
    </div>
  </div>

  <!-- Mobile Overlay -->
  <div v-if="isOpen" @click="toggleSidebar" class="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"></div>
</template>

<script setup>
const authStore = useAuthStore()
const { hasPermission } = usePermissions()

const isOpen = ref(false)
const isCollapsed = ref(false)
const showProductsDropdown = ref(false)
const showOperationsDropdown = ref(false)
const showMemberDropdown = ref(false)

// Load sidebar state from localStorage on mount
onMounted(() => {
  if (process.client) {
    const savedState = localStorage.getItem('sidebarCollapsed')
    if (savedState !== null) {
      isCollapsed.value = savedState === 'true'
    }
  }
})

const toggleSidebar = () => {
  isOpen.value = !isOpen.value
}

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
  
  // Save state to localStorage
  if (process.client) {
    localStorage.setItem('sidebarCollapsed', isCollapsed.value.toString())
  }
  
  // Close all dropdowns when collapsing
  if (isCollapsed.value) {
    showProductsDropdown.value = false
    showOperationsDropdown.value = false
    showMemberDropdown.value = false
  }
}

const toggleProductsDropdown = () => {
  showProductsDropdown.value = !showProductsDropdown.value
}

const toggleOperationsDropdown = () => {
  showOperationsDropdown.value = !showOperationsDropdown.value
}

const toggleMemberDropdown = () => {
  showMemberDropdown.value = !showMemberDropdown.value
}

const userInitials = computed(() => {
  if (!authStore.user?.name) return 'U'
  return authStore.user.name.split(' ').map(n => n[0]).join('').toUpperCase()
})

const handleLogout = async () => {
  await authStore.logout()
}

// Close sidebar on route change (mobile)
watch(() => useRoute().path, () => {
  isOpen.value = false
})

// Expose toggle functions and state for parent components
defineExpose({
  toggleSidebar,
  isCollapsed
})
</script>
