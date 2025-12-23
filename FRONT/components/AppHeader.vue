<template>
  <header class="sticky top-0 z-40 bg-background-primary/80 backdrop-blur-xl border-b border-gray-200">
    <div class="flex items-center justify-between h-16 px-6">
      <!-- Left side -->
      <div class="flex items-center space-x-4">
        <!-- Mobile menu button -->
        <button @click="toggleSidebar" class="lg:hidden p-2 rounded-xl hover:bg-gray-100 transition-colors">
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        <!-- Page title -->
        <div>
          <h1 class="text-xl font-semibold text-gray-900">{{ pageTitle }}</h1>
          <p class="text-sm text-gray-500">{{ pageSubtitle }}</p>
        </div>
      </div>

      <!-- Right side -->
      <div class="flex items-center space-x-4">
        <!-- Search -->
        <div class="hidden md:block relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            placeholder="Search..."
            class="w-64 pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-all duration-200 text-sm"
          />
        </div>

        <!-- Notifications -->
        <button class="relative p-2 rounded-xl hover:bg-gray-100 transition-colors">
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM9 7H4l5-5v5z" />
          </svg>
          <span class="absolute top-1 right-1 w-2 h-2 bg-apple-red rounded-full"></span>
        </button>

        <!-- User menu -->
        <div class="relative">
          <button @click="toggleUserMenu" class="flex items-center space-x-3 p-2 rounded-xl hover:bg-gray-100 transition-colors">
            <div class="w-8 h-8 bg-apple-blue rounded-xl flex items-center justify-center">
              <span class="text-white font-medium text-sm">{{ userInitials }}</span>
            </div>
            <div class="hidden md:block text-left">
              <p class="text-sm font-medium text-gray-900">{{ authStore.user?.name || 'User' }}</p>
              <p class="text-xs text-gray-500">Administrator</p>
            </div>
            <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <!-- User dropdown -->
          <div v-if="showUserMenu" class="absolute right-0 mt-2 w-64 bg-background-primary rounded-2xl shadow-apple-lg border border-gray-200 py-2 z-50">
            <div class="px-4 py-3 border-b border-gray-200">
              <p class="text-sm font-medium text-gray-900">{{ authStore.user?.name || 'User' }}</p>
              <p class="text-xs text-gray-500">{{ authStore.user?.email || 'user@example.com' }}</p>
            </div>
            
            <div class="py-2">
              <NuxtLink to="/dashboard/settings" class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                <svg class="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                Profile
              </NuxtLink>
              
              <NuxtLink to="/dashboard/settings" class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                <svg class="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Settings
              </NuxtLink>
            </div>
            
            <div class="border-t border-gray-200 py-2">
              <button @click="handleLogout" class="flex items-center w-full px-4 py-2 text-sm text-apple-red hover:bg-red-50 transition-colors">
                <svg class="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Sign out
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
const authStore = useAuthStore()
const route = useRoute()

const showUserMenu = ref(false)
const sidebarRef = ref(null)

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const toggleSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.toggleSidebar()
  }
}

const userInitials = computed(() => {
  if (!authStore.user?.name) return 'U'
  return authStore.user.name.split(' ').map(n => n[0]).join('').toUpperCase()
})

const pageTitle = computed(() => {
  const titles = {
    '/dashboard': 'Anasayfa',
    '/dashboard/companies': 'Firma Yönetimi',
    '/dashboard/products': 'Ürün URL Yönetimi',
    '/dashboard/user-products': 'Ürün Listesi',
    '/dashboard/scanning': 'Tarama',
    '/dashboard/custom-profile': 'Özel Analizler',
    '/dashboard/roles': 'Rol Yönetimi',
    '/dashboard/attributes': 'Attribute Ayarları',
    '/dashboard/settings': 'Ayarlar',
    '/dashboard/profile': 'Ayarlar'
  }
  return titles[route.path] || 'Anasayfa'
})

const pageSubtitle = computed(() => {
  const subtitles = {
    '/dashboard': 'İşletmenizin genel durumu',
    '/dashboard/companies': 'Firmaları yönetin ve düzenleyin',
    '/dashboard/products': 'Ürün URL\'lerini yönetin',
    '/dashboard/user-products': 'Ürün listelerini görüntüleyin',
    '/dashboard/scanning': 'Tarama işlemlerini yönetin',
    '/dashboard/custom-profile': 'Özel analizleri oluşturun',
    '/dashboard/roles': 'Kullanıcı rollerini yönetin',
    '/dashboard/attributes': 'Attribute\'ları yönetin ve düzenleyin',
    '/dashboard/settings': 'Sistem ayarlarını yapılandırın',
    '/dashboard/profile': 'Hesap ayarlarınız'
  }
  return subtitles[route.path] || 'Hoş geldiniz'
})

const handleLogout = async () => {
  showUserMenu.value = false
  await authStore.logout()
}

// Close user menu when clicking outside
onMounted(() => {
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.relative')) {
      showUserMenu.value = false
    }
  })
})

// Expose sidebar ref
defineExpose({
  sidebarRef
})
</script>

