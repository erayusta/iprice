<template>
  <div class="min-h-screen bg-background-secondary overflow-visible">
    <!-- Preloader -->
    <Preloader />
    
    <!-- Sidebar -->
    <AppSidebar ref="sidebarRef" />
    
    <!-- Main Content -->
    <div class="transition-all duration-300 overflow-visible" :class="sidebarRef?.isCollapsed ? 'lg:pl-20' : 'lg:pl-64'">
      <!-- Header -->
      <AppHeader ref="headerRef" />
      
      <!-- Page Content -->
      <main class="p-6 overflow-visible">
        <div :class="sidebarRef?.isCollapsed ? 'w-full' : 'max-w-7xl mx-auto'" class="overflow-visible">
          <slot />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
const sidebarRef = ref(null)
const headerRef = ref(null)

// Connect header and sidebar
onMounted(() => {
  if (headerRef.value && sidebarRef.value) {
    headerRef.value.sidebarRef = sidebarRef.value
  }
})
</script>

