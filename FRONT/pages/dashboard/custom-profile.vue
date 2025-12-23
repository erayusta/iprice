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
  <div v-else-if="!hasPermission('privateanalysis.show')" class="flex items-center justify-center min-h-screen">
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
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 mb-2">Özel Analizler</h1>
          <p class="text-gray-600">Kişiselleştirilmiş ürün listeleri oluşturun ve yönetin.</p>
        </div>
        <button 
          v-if="hasPermission('privateanalysis.add')"
          @click="openCreateModal" 
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Yeni Profil
        </button>
      </div>
    </div>

    <!-- Profiles Grid -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      <p class="text-gray-500 mt-2">Yükleniyor...</p>
    </div>

    <div v-else-if="profiles.length === 0" class="text-center py-12">
      <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">Henüz profil yok</h3>
      <p class="text-gray-500 mb-4">İlk özel analizlerinizi oluşturmak için yukarıdaki butona tıklayın.</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="profile in profiles" 
        :key="profile.id"
        class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <h3 class="text-lg font-semibold text-gray-900">{{ profile.name }}</h3>
              <span v-if="profile.is_shared" class="px-2 py-0.5 text-xs bg-green-100 text-green-700 rounded-full">Paylaşılan</span>
            </div>
            <p class="text-sm text-gray-500 mb-2">{{ profile.description || 'Açıklama yok' }}</p>
            <div class="flex items-center gap-4 text-sm text-gray-500">
              <span class="flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
                {{ profile.products_count || 0 }} ürün
              </span>
              <span class="flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ formatDate(profile.created_at) }}
              </span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button 
              v-if="profile.is_owner && hasPermission('privateanalysis.edit')"
              @click="openShareModal(profile)"
              class="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
              title="Paylaş"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
              </svg>
            </button>
            <button 
              v-if="profile.is_owner && hasPermission('privateanalysis.edit')"
              @click="openEditModal(profile)"
              class="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button 
              v-if="profile.is_owner && hasPermission('privateanalysis.delete')"
              @click="deleteProfile(profile.id)"
              class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
        
        <div class="flex gap-2">
          <NuxtLink 
            v-if="hasPermission('privateanalysis.view')"
            :to="`/dashboard/custom-profile-detail?id=${profile.id}`"
            class="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-center py-2 px-4 rounded-lg transition-colors"
          >
            Profili Görüntüle
          </NuxtLink>
        </div>
      </div>
    </div>

    <!-- Create Profile Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-md mx-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Yeni Profil Oluştur</h3>
          <button @click="closeCreateModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="createProfile" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Profil Adı</label>
            <input 
              v-model="newProfile.name" 
              type="text" 
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Örn: Favori Ürünlerim"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Açıklama</label>
            <textarea 
              v-model="newProfile.description" 
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Bu profilin amacını açıklayın..."
            ></textarea>
          </div>

          <div class="flex gap-3 pt-4">
            <button 
              type="button" 
              @click="closeCreateModal" 
              class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              İptal
            </button>
            <button 
              type="submit" 
              :disabled="isCreating" 
              class="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white px-4 py-2 rounded-lg transition-colors"
            >
              {{ isCreating ? 'Oluşturuluyor...' : 'Oluştur' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-md mx-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Profili Düzenle</h3>
          <button @click="closeEditModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="updateProfile" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Profil Adı</label>
            <input 
              v-model="editingProfile.name" 
              type="text" 
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Açıklama</label>
            <textarea 
              v-model="editingProfile.description" 
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            ></textarea>
          </div>

          <div class="flex gap-3 pt-4">
            <button 
              type="button" 
              @click="closeEditModal" 
              class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              İptal
            </button>
            <button 
              type="submit" 
              :disabled="isUpdating" 
              class="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white px-4 py-2 rounded-lg transition-colors"
            >
              {{ isUpdating ? 'Güncelleniyor...' : 'Güncelle' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Share Profile Modal -->
    <div v-if="showShareModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Profili Paylaş</h3>
          <button @click="closeShareModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Paylaşılan Kullanıcılar Listesi -->
        <div v-if="sharedUsers.length > 0" class="mb-6">
          <h4 class="text-sm font-medium text-gray-700 mb-3">Paylaşılan Kullanıcılar</h4>
          <div class="space-y-2">
            <div 
              v-for="user in sharedUsers" 
              :key="user.id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div>
                <p class="text-sm font-medium text-gray-900">{{ user.name }}</p>
                <p class="text-xs text-gray-500">{{ user.email }}</p>
                <p class="text-xs text-gray-400 mt-1">Paylaşıldı: {{ formatDate(user.shared_at) }}</p>
              </div>
              <button 
                @click="removeShare(user.id)"
                class="p-2 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Paylaşımı Kaldır"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Kullanıcı Seçimi -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Kullanıcı Seç</label>
          <div v-if="isLoadingUsers" class="text-center py-4">
            <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
            <p class="text-gray-500 mt-2 text-sm">Kullanıcılar yükleniyor...</p>
          </div>
          <div v-else-if="availableUsers.length === 0" class="text-center py-4 text-gray-500 text-sm">
            Paylaşılabilecek kullanıcı bulunamadı
          </div>
          <div v-else class="space-y-2 max-h-60 overflow-y-auto">
            <div 
              v-for="user in availableUsers" 
              :key="user.id"
              @click="shareWithUser(user.id)"
              class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 cursor-pointer transition-colors"
            >
              <div>
                <p class="text-sm font-medium text-gray-900">{{ user.name }}</p>
                <p class="text-xs text-gray-500">{{ user.email }}</p>
              </div>
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </div>
          </div>
        </div>

        <div class="flex gap-3 pt-4 mt-4 border-t">
          <button 
            type="button" 
            @click="closeShareModal" 
            class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Kapat
          </button>
        </div>
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
  title: 'Özel Analizler - Admin Panel'
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
const profiles = ref([])
const isLoading = ref(false)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showShareModal = ref(false)
const isCreating = ref(false)
const isUpdating = ref(false)
const isLoadingUsers = ref(false)
const availableUsers = ref([])
const sharedUsers = ref([])
const sharingProfileId = ref(null)

const newProfile = reactive({
  name: '',
  description: ''
})

const editingProfile = reactive({
  id: null,
  name: '',
  description: ''
})

// Methods
const fetchProfiles = async () => {
  try {
    isLoading.value = true
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('custom-profiles.list'))
    
    if (response.success) {
      profiles.value = response.data || []
    } else {
      console.error('Profiller yüklenirken hata:', response.message)
    }
  } catch (error) {
    console.error('Profiller yüklenirken hata:', error)
  } finally {
    isLoading.value = false
  }
}

const openCreateModal = () => {
  showCreateModal.value = true
  newProfile.name = ''
  newProfile.description = ''
}

const closeCreateModal = () => {
  showCreateModal.value = false
  newProfile.name = ''
  newProfile.description = ''
}

const openEditModal = (profile) => {
  editingProfile.id = profile.id
  editingProfile.name = profile.name
  editingProfile.description = profile.description || ''
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editingProfile.id = null
  editingProfile.name = ''
  editingProfile.description = ''
}

const createProfile = async () => {
  try {
    isCreating.value = true
    const { $api } = useNuxtApp()
    const response = await $api.post($api.getEndpoint('custom-profiles.create'), {
      name: newProfile.name,
      description: newProfile.description
    })
    
    if (response.success) {
      closeCreateModal()
      await fetchProfiles()
    } else {
      alert('Profil oluşturulurken hata: ' + response.message)
    }
  } catch (error) {
    console.error('Profil oluşturma hatası:', error)
    alert('Profil oluşturulurken bir hata oluştu')
  } finally {
    isCreating.value = false
  }
}

const updateProfile = async () => {
  try {
    isUpdating.value = true
    const { $api } = useNuxtApp()
    const response = await $api.put($api.getEndpoint('custom-profiles.update', editingProfile.id), {
      name: editingProfile.name,
      description: editingProfile.description
    })
    
    if (response.success) {
      closeEditModal()
      await fetchProfiles()
    } else {
      alert('Profil güncellenirken hata: ' + response.message)
    }
  } catch (error) {
    console.error('Profil güncelleme hatası:', error)
    alert('Profil güncellenirken bir hata oluştu')
  } finally {
    isUpdating.value = false
  }
}

const deleteProfile = async (profileId) => {
  if (!confirm('Bu profili silmek istediğinizden emin misiniz?')) {
    return
  }

  try {
    const { $api } = useNuxtApp()
    const response = await $api.delete($api.getEndpoint('custom-profiles.delete', profileId))
    
    if (response.success) {
      await fetchProfiles()
    } else {
      alert('Profil silinirken hata: ' + response.message)
    }
  } catch (error) {
    console.error('Profil silme hatası:', error)
    alert('Profil silinirken bir hata oluştu')
  }
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('tr-TR')
}

const openShareModal = async (profile) => {
  sharingProfileId.value = profile.id
  showShareModal.value = true
  await loadShareData()
}

const closeShareModal = () => {
  showShareModal.value = false
  sharingProfileId.value = null
  availableUsers.value = []
  sharedUsers.value = []
}

const loadShareData = async () => {
  if (!sharingProfileId.value) return
  
  try {
    isLoadingUsers.value = true
    const { $api } = useNuxtApp()
    
    // Paylaşılan kullanıcıları getir
    const sharedResponse = await $api.get($api.getEndpoint('custom-profiles.sharedUsers', sharingProfileId.value))
    if (sharedResponse.success) {
      sharedUsers.value = sharedResponse.data || []
    }
    
    // Kullanılabilir kullanıcıları getir
    const availableResponse = await $api.get($api.getEndpoint('custom-profiles.availableUsers', sharingProfileId.value))
    if (availableResponse.success) {
      availableUsers.value = availableResponse.data || []
    }
  } catch (error) {
    console.error('Paylaşım bilgileri yüklenirken hata:', error)
    alert('Paylaşım bilgileri yüklenirken bir hata oluştu')
  } finally {
    isLoadingUsers.value = false
  }
}

const shareWithUser = async (userId) => {
  if (!sharingProfileId.value) return
  
  try {
    const { $api } = useNuxtApp()
    const response = await $api.post($api.getEndpoint('custom-profiles.share', sharingProfileId.value), {
      user_id: userId
    })
    
    if (response.success) {
      await loadShareData()
    } else {
      alert('Profil paylaşılırken hata: ' + response.message)
    }
  } catch (error) {
    console.error('Profil paylaşma hatası:', error)
    alert('Profil paylaşılırken bir hata oluştu')
  }
}

const removeShare = async (userId) => {
  if (!confirm('Bu kullanıcıyla paylaşımı kaldırmak istediğinizden emin misiniz?')) {
    return
  }
  
  if (!sharingProfileId.value) return
  
  try {
    const { $api } = useNuxtApp()
    const response = await $api.post($api.getEndpoint('custom-profiles.unshare', sharingProfileId.value), {
      user_id: userId
    })
    
    if (response.success) {
      await loadShareData()
    } else {
      alert('Paylaşım kaldırılırken hata: ' + response.message)
    }
  } catch (error) {
    console.error('Paylaşım kaldırma hatası:', error)
    alert('Paylaşım kaldırılırken bir hata oluştu')
  }
}

// Lifecycle
onMounted(async () => {
  try {
    // Kısa bir delay ile yetki kontrolünün tamamlanmasını bekle
    await new Promise(resolve => setTimeout(resolve, 200))
    isCheckingPermissions.value = false
    
    await fetchProfiles()
  } catch (error) {
    console.error('Page initialization failed:', error)
    isCheckingPermissions.value = false
  }
})
</script>
