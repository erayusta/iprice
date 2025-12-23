<template>
  <div v-if="isLoading" class="preloader-overlay" :class="{ 'fade-out': !isLoading }">
    <div class="preloader-container">
      <!-- Logo/Brand -->
      <div class="brand-logo">
        <div class="logo-icon">
          <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
      </div>
      
      <!-- Apple-style spinner -->
      <div class="spinner">
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
      </div>
      
      <!-- Loading text -->
      <div class="loading-text">
        <h3 class="text-xl font-semibold text-gray-800 mb-2">{{ loadingText }}</h3>
        <p class="text-sm text-gray-600">{{ loadingSubtext }}</p>
      </div>
      
      <!-- Progress bar -->
      <div class="progress-container">
        <div class="progress-bar" :style="{ width: progress + '%' }"></div>
        <div class="progress-text">{{ Math.round(progress) }}%</div>
      </div>
    </div>
  </div>
</template>

<script setup>
const isLoading = ref(true)
const progress = ref(0)
const loadingText = ref('Yükleniyor...')
const loadingSubtext = ref('Lütfen bekleyin')

// Loading text variations
const loadingTexts = [
  { text: 'Yükleniyor...', subtext: 'Lütfen bekleyin' },
  { text: 'Hazırlanıyor...', subtext: 'Sistem başlatılıyor' },
  { text: 'Neredeyse hazır!', subtext: 'Son dokunuşlar yapılıyor' }
]

// CSS yükleme kontrolü
const checkCSSLoaded = () => {
  return new Promise((resolve) => {
    // Önce Tailwind CSS'in yüklenip yüklenmediğini kontrol et
    const checkTailwindCSS = () => {
      const testElement = document.createElement('div')
      testElement.className = 'card-elevated'
      testElement.style.visibility = 'hidden'
      testElement.style.position = 'absolute'
      testElement.style.top = '-9999px'
      testElement.style.left = '-9999px'
      testElement.style.width = '1px'
      testElement.style.height = '1px'
      document.body.appendChild(testElement)
      
      const computedStyle = window.getComputedStyle(testElement)
      const hasStyles = computedStyle.borderRadius !== '' || 
                       computedStyle.boxShadow !== '' || 
                       computedStyle.backgroundColor !== '' ||
                       computedStyle.padding !== '' ||
                       computedStyle.margin !== ''
      
      document.body.removeChild(testElement)
      return hasStyles
    }
    
    // İlk kontrol - hemen kontrol et
    if (checkTailwindCSS()) {
      resolve(true)
      return
    }
    
    const checkInterval = setInterval(() => {
      if (checkTailwindCSS()) {
        clearInterval(checkInterval)
        resolve(true)
      }
    }, 20) // Çok daha sık kontrol et
    
    // Timeout - maksimum 3 saniye bekle
    setTimeout(() => {
      clearInterval(checkInterval)
      resolve(true)
    }, 3000)
  })
}

// Progress simulation
const simulateProgress = () => {
  const interval = setInterval(() => {
    if (progress.value < 90) {
      progress.value += Math.random() * 15
      
      // Loading text değiştir
      if (progress.value > 30 && progress.value < 60) {
        loadingText.value = loadingTexts[1].text
        loadingSubtext.value = loadingTexts[1].subtext
      } else if (progress.value > 60) {
        loadingText.value = loadingTexts[2].text
        loadingSubtext.value = loadingTexts[2].subtext
      }
    }
  }, 100)
  
  return interval
}

// Daha erken başlat - hemen başlat
const startPreloader = async () => {
  // Progress simulation başlat
  const progressInterval = simulateProgress()
  
  try {
    // CSS yüklenmesini bekle
    await checkCSSLoaded()
    
    // Minimum loading time (UX için)
    await new Promise(resolve => setTimeout(resolve, 1200))
    
    // Progress'i tamamla
    progress.value = 100
    loadingText.value = 'Tamamlandı!'
    loadingSubtext.value = 'Yönlendiriliyor...'
    
    // Kısa bir bekleme sonrası preloader'ı kapat
    setTimeout(() => {
      isLoading.value = false
    }, 500)
    
  } catch (error) {
    console.error('Preloader error:', error)
    // Hata durumunda da preloader'ı kapat
    setTimeout(() => {
      isLoading.value = false
    }, 1000)
  } finally {
    clearInterval(progressInterval)
  }
}

// Hemen başlat
startPreloader()
</script>

<style scoped>
/* Inline styles for immediate loading */
.preloader-overlay {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 100% !important;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  z-index: 99999 !important;
  backdrop-filter: blur(10px) !important;
}

.preloader-container {
  text-align: center;
  max-width: 350px;
  width: 100%;
  padding: 2rem;
}

.brand-logo {
  margin-bottom: 2rem;
}

.logo-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
  animation: logoFloat 2s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.spinner {
  position: relative;
  width: 60px;
  height: 60px;
  margin: 0 auto 2rem;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 3px solid transparent;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
}

.spinner-ring:nth-child(1) {
  animation-delay: -0.45s;
  border-top-color: #3b82f6;
}

.spinner-ring:nth-child(2) {
  animation-delay: -0.3s;
  border-top-color: #8b5cf6;
  width: 80%;
  height: 80%;
  top: 10%;
  left: 10%;
}

.spinner-ring:nth-child(3) {
  animation-delay: -0.15s;
  border-top-color: #06b6d4;
  width: 60%;
  height: 60%;
  top: 20%;
  left: 20%;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-text h3 {
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #1f2937;
}

.loading-text p {
  color: #6b7280;
  font-size: 0.875rem;
}

.progress-container {
  width: 100%;
  height: 6px;
  background-color: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
  margin-top: 1.5rem;
  position: relative;
}

.progress-text {
  position: absolute;
  top: -25px;
  right: 0;
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);
  border-radius: 2px;
  transition: width 0.3s ease;
  position: relative;
}

.progress-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* Fade out animation */
.preloader-overlay {
  transition: opacity 0.3s ease-out;
}

.preloader-overlay.fade-out {
  opacity: 0;
}
</style>
