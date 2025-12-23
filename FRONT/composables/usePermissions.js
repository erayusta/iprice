export const usePermissions = () => {
  const authStore = useAuthStore()
  
  // Belirli bir yetkiye sahip mi kontrol et
  const hasPermission = (permission) => {
    try {
      if (!authStore.user || !authStore.user.permissions) {
        return false
      }
      return authStore.user.permissions.includes(permission)
    } catch (error) {
      console.warn('Permission check failed:', error)
      return false
    }
  }
  
  // Kullanıcının yetkilerini al
  const getUserPermissions = () => {
    try {
      if (!authStore.user?.permissions) return []
      return authStore.user.permissions
    } catch (error) {
      console.warn('Get permissions failed:', error)
      return []
    }
  }
  
  // Birden fazla yetkiden birine sahip mi kontrol et
  const hasAnyPermission = (permissions) => {
    try {
      return permissions.some(permission => hasPermission(permission))
    } catch (error) {
      console.warn('Has any permission check failed:', error)
      return false
    }
  }
  
  // Tüm yetkilere sahip mi kontrol et
  const hasAllPermissions = (permissions) => {
    try {
      return permissions.every(permission => hasPermission(permission))
    } catch (error) {
      console.warn('Has all permissions check failed:', error)
      return false
    }
  }
  
  return {
    getUserPermissions,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions
  }
}
