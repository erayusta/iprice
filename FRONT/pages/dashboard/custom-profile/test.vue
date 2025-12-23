<template>
  <div class="p-6">
    <h1 class="text-3xl font-bold text-gray-900">Test Sayfası</h1>
    <p class="text-gray-600">Bu sayfa çalışıyor!</p>
  </div>
</template>

<script setup>
definePageMeta({
  layout: 'dashboard',
  middleware: 'auth'
})
</script>
