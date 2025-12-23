<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Preloader -->
    <Preloader />
    
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="text-center">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">
          Hoş Geldiniz! 👋
        </h1>
        <p class="text-xl text-gray-600 mb-8">
          Modern ve mobil uyumlu panel uygulaması
        </p>
        
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <NuxtLink to="/login" class="btn-primary">
            Giriş Yap
          </NuxtLink>
          <NuxtLink to="/register" class="btn-secondary">
            Kayıt Ol
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  layout: false
})
</script>

