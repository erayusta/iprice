<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="card-elevated">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 mb-2">
            Roller 🛡️
          </h1>
          <p class="text-gray-600 text-lg">
            Sistem rollerini yönetmek ve yetkilendirme ayarlarını düzenlemek için bu sayfayı kullanabilirsiniz.
          </p>
        </div>
        <div class="hidden md:block">
          <div class="w-20 h-20 bg-gradient-to-br from-apple-blue to-apple-indigo rounded-3xl flex items-center justify-center">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="card-elevated">
      <div class="p-6">
        <div class="flex flex-wrap gap-3">
          <button 
            @click="activeTab = 'permissions'"
            :class="activeTab === 'permissions' ? 'bg-apple-blue text-white shadow-lg' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            class="flex items-center space-x-2 px-6 py-3 rounded-xl font-medium transition-all duration-200"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            <span>Yetki Ekle</span>
          </button>
          
          <button 
            @click="activeTab = 'permissions-list'"
            :class="activeTab === 'permissions-list' ? 'bg-apple-blue text-white shadow-lg' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            class="flex items-center space-x-2 px-6 py-3 rounded-xl font-medium transition-all duration-200"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <span>Yetkiler</span>
          </button>
          
          <button 
            @click="activeTab = 'roles'"
            :class="activeTab === 'roles' ? 'bg-apple-blue text-white shadow-lg' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            class="flex items-center space-x-2 px-6 py-3 rounded-xl font-medium transition-all duration-200"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <span>Roller</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Yetki Ekle Tab -->
    <div v-if="activeTab === 'permissions'" class="card-elevated">
      <div class="p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Yeni Yetki Ekle</h3>
        <form @submit.prevent="addPermission" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Yetki Adı</label>
              <input 
                v-model="permissionForm.name" 
                type="text" 
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                placeholder="Örn: companies.create"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Grup</label>
              <input 
                v-model="permissionForm.group" 
                type="text" 
                class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                placeholder="Örn: Firma Yönetimi"
              />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Açıklama</label>
            <textarea 
              v-model="permissionForm.description" 
              rows="3"
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
              placeholder="Yetki açıklaması"
            ></textarea>
          </div>
          <div class="flex justify-end">
            <button type="submit" :disabled="isSubmittingPermission" class="btn btn-primary">
              <span v-if="isSubmittingPermission">Ekleniyor...</span>
              <span v-else>Yetki Ekle</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Yetkiler Listesi Tab -->
    <div v-if="activeTab === 'permissions-list'" class="card-elevated">
      <div class="p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-gray-900">Mevcut Yetkiler</h3>
          <div class="flex gap-3">
            <select v-model="permissionGroupFilter" class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-apple-blue focus:border-transparent">
              <option value="">Tüm Gruplar</option>
              <option v-for="group in permissionGroups" :key="group" :value="group">{{ group }}</option>
            </select>
            <input 
              v-model="permissionSearchQuery" 
              type="text" 
              placeholder="Yetki ara..."
              class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-apple-blue focus:border-transparent"
            />
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="permission in filteredPermissions" :key="permission.id" class="border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <h4 class="font-semibold text-gray-900">{{ permission.name }}</h4>
                <p class="text-sm text-gray-600 mt-1">{{ permission.description }}</p>
                <span v-if="permission.group" class="inline-block mt-2 px-2 py-1 bg-apple-blue/10 text-apple-blue text-xs rounded-full">
                  {{ permission.group }}
                </span>
              </div>
              <button @click="deletePermission(permission)" class="p-1 text-gray-400 hover:text-red-500 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Roller Tab -->
    <div v-if="activeTab === 'roles'" class="space-y-6">
      <!-- Rol Ekle -->
      <div class="card-elevated">
        <div class="p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Yeni Rol Ekle</h3>
          <form @submit.prevent="addRole" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Rol Adı</label>
                <input 
                  v-model="roleForm.name" 
                  type="text" 
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                  placeholder="Rol adı"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Açıklama</label>
                <input 
                  v-model="roleForm.description" 
                  type="text" 
                  class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-apple-blue focus:border-transparent transition-colors"
                  placeholder="Rol açıklaması"
                />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Yetkiler</label>
              
              <!-- Yetki Grup Filtresi -->
              <div class="mb-4">
                <select v-model="permissionGroupFilter" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-apple-blue focus:border-transparent">
                  <option value="">Tüm Gruplar</option>
                  <option v-for="group in permissionGroups" :key="group" :value="group">{{ group }}</option>
                </select>
              </div>
              
              <!-- Yetki Listesi -->
              <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-h-48 overflow-y-auto border border-gray-300 rounded-lg p-4">
                <label v-for="permission in filteredPermissionsForRole" :key="permission.id" class="flex items-center space-x-2">
                  <input 
                    v-model="roleForm.permissions" 
                    :value="permission.id" 
                    type="checkbox" 
                    class="rounded border-gray-300 text-apple-blue focus:ring-apple-blue"
                  />
                  <span class="text-sm text-gray-700">{{ permission.name }}</span>
                </label>
              </div>
              
              <!-- Seçilen Yetki Sayısı -->
              <div class="mt-2 text-sm text-gray-600">
                <span class="font-medium">{{ roleForm.permissions.length }}</span> yetki seçildi
              </div>
            </div>
            <div class="flex items-center">
              <input 
                v-model="roleForm.is_default" 
                type="checkbox" 
                class="rounded border-gray-300 text-apple-blue focus:ring-apple-blue"
              />
              <span class="ml-2 text-sm font-medium text-gray-700">Varsayılan rol</span>
            </div>
            <div class="flex justify-end">
              <button type="submit" :disabled="isSubmittingRole" class="btn btn-primary">
                <span v-if="isSubmittingRole">Ekleniyor...</span>
                <span v-else>Rol Ekle</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Roller Listesi -->
      <div class="card-elevated">
        <div class="p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-6">Mevcut Roller</h3>
          
          <div v-if="isLoadingRoles" class="text-center py-12">
            <div class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-3 h-8 w-8 text-apple-blue" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span class="text-gray-600">Yükleniyor...</span>
            </div>
          </div>

          <div v-else class="space-y-4">
            <div v-for="role in roles" :key="role.id" class="border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3">
                    <h4 class="font-semibold text-gray-900">{{ role.name }}</h4>
                    <span v-if="role.is_default" class="px-2 py-1 bg-apple-blue/10 text-apple-blue text-xs rounded-full">
                      Varsayılan
                    </span>
                  </div>
                  <p class="text-sm text-gray-600 mt-1">{{ role.description }}</p>
                  <div class="flex items-center space-x-4 mt-3">
                    <span class="text-sm text-gray-500">
                      <strong>{{ role.users_count || 0 }}</strong> kullanıcı
                    </span>
                    <button @click="viewRoleUsers(role)" class="text-sm text-apple-blue hover:text-apple-indigo">
                      Kullanıcıları görüntüle
                    </button>
                  </div>
                </div>
                <div class="flex items-center space-x-2">
                  <button @click="editRole(role)" class="p-2 text-gray-400 hover:text-apple-blue transition-colors" title="Düzenle">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button v-if="!role.is_default" @click="deleteRole(role)" class="p-2 text-gray-400 hover:text-red-500 transition-colors" title="Sil">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Kullanıcılar Modal -->
    <div v-if="showUsersModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeUsersModal"></div>
        <div class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900">
                {{ selectedRole?.name }} - Kullanıcılar
              </h3>
              <button @click="closeUsersModal" class="text-gray-400 hover:text-gray-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          <div class="bg-white px-6 py-6">
            <div v-if="roleUsers.length === 0" class="text-center py-8">
              <p class="text-gray-500">Bu role sahip kullanıcı bulunmuyor.</p>
            </div>
            <div v-else class="space-y-3">
              <div v-for="user in roleUsers" :key="user.id" class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <div class="w-10 h-10 bg-apple-blue rounded-full flex items-center justify-center">
                  <span class="text-white font-medium text-sm">{{ user.name.charAt(0).toUpperCase() }}</span>
                </div>
                <div class="flex-1">
                  <p class="font-medium text-gray-900">{{ user.name }}</p>
                  <p class="text-sm text-gray-500">{{ user.email }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  middleware: 'auth',
  layout: 'dashboard'
})

// Reactive data
const activeTab = ref('permissions')
const isLoadingRoles = ref(false)
const isSubmittingPermission = ref(false)
const isSubmittingRole = ref(false)

// Permission form
const permissionForm = reactive({
  name: '',
  description: '',
  group: ''
})

// Role form
const roleForm = reactive({
  name: '',
  description: '',
  is_default: false,
  permissions: []
})

// Data
const permissions = ref([])
const roles = ref([])
const roleUsers = ref([])
const selectedRole = ref(null)
const showUsersModal = ref(false)

// Filters
const permissionSearchQuery = ref('')
const permissionGroupFilter = ref('')

// Computed
const filteredPermissions = computed(() => {
  let filtered = permissions.value

  if (permissionSearchQuery.value) {
    const query = permissionSearchQuery.value.toLowerCase()
    filtered = filtered.filter(permission => 
      permission.name.toLowerCase().includes(query) ||
      (permission.description && permission.description.toLowerCase().includes(query))
    )
  }

  if (permissionGroupFilter.value) {
    filtered = filtered.filter(permission => permission.group === permissionGroupFilter.value)
  }

  return filtered
})

const permissionGroups = computed(() => {
  const groups = [...new Set(permissions.value.map(p => p.group).filter(Boolean))]
  return groups.sort()
})

const filteredPermissionsForRole = computed(() => {
  let filtered = permissions.value

  if (permissionGroupFilter.value) {
    filtered = filtered.filter(permission => permission.group === permissionGroupFilter.value)
  }

  return filtered
})

// API functions
const fetchPermissions = async () => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('permissions.list'))
    permissions.value = response.data
  } catch (error) {
    console.error('Yetkiler yüklenirken hata:', error)
  }
}

const fetchRoles = async () => {
  isLoadingRoles.value = true
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('roles.list'))
    roles.value = response.data
  } catch (error) {
    console.error('Roller yüklenirken hata:', error)
  } finally {
    isLoadingRoles.value = false
  }
}

const addPermission = async () => {
  isSubmittingPermission.value = true
  try {
    const { $api } = useNuxtApp()
    await $api.post($api.getEndpoint('permissions.create'), permissionForm)
    
    alert('Yetki başarıyla eklendi!')
    resetPermissionForm()
    await fetchPermissions()
  } catch (error) {
    console.error('Yetki eklenirken hata:', error)
    alert('Yetki eklenirken bir hata oluştu.')
  } finally {
    isSubmittingPermission.value = false
  }
}

const addRole = async () => {
  isSubmittingRole.value = true
  try {
    const { $api } = useNuxtApp()
    await $api.post($api.getEndpoint('roles.create'), roleForm)
    
    alert('Rol başarıyla eklendi!')
    resetRoleForm()
    await fetchRoles()
  } catch (error) {
    console.error('Rol eklenirken hata:', error)
    alert('Rol eklenirken bir hata oluştu.')
  } finally {
    isSubmittingRole.value = false
  }
}

const deletePermission = async (permission) => {
  if (!confirm(`${permission.name} yetkisini silmek istediğinizden emin misiniz?`)) {
    return
  }
  
  try {
    const { $api } = useNuxtApp()
    await $api.delete($api.getEndpoint('permissions.delete', permission.id))
    
    alert('Yetki başarıyla silindi!')
    await fetchPermissions()
  } catch (error) {
    console.error('Yetki silinirken hata:', error)
    alert('Yetki silinirken bir hata oluştu.')
  }
}

const deleteRole = async (role) => {
  if (!confirm(`${role.name} rolünü silmek istediğinizden emin misiniz?`)) {
    return
  }
  
  try {
    const { $api } = useNuxtApp()
    await $api.delete($api.getEndpoint('roles.delete', role.id))
    
    alert('Rol başarıyla silindi!')
    await fetchRoles()
  } catch (error) {
    console.error('Rol silinirken hata:', error)
    alert('Rol silinirken bir hata oluştu.')
  }
}

const viewRoleUsers = async (role) => {
  selectedRole.value = role
  showUsersModal.value = true
  
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get($api.getEndpoint('roles.users', role.id))
    roleUsers.value = response.data
  } catch (error) {
    console.error('Kullanıcılar yüklenirken hata:', error)
    roleUsers.value = []
  }
}

const closeUsersModal = () => {
  showUsersModal.value = false
  selectedRole.value = null
  roleUsers.value = []
}

const editRole = (role) => {
  // TODO: Implement role editing
  alert('Rol düzenleme özelliği yakında eklenecek!')
}

// Form reset functions
const resetPermissionForm = () => {
  permissionForm.name = ''
  permissionForm.description = ''
  permissionForm.group = ''
}

const resetRoleForm = () => {
  roleForm.name = ''
  roleForm.description = ''
  roleForm.is_default = false
  roleForm.permissions = []
  permissionGroupFilter.value = ''
}

// Lifecycle
onMounted(async () => {
  await fetchPermissions()
  await fetchRoles()
})
</script>
