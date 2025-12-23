<template>
  <div class="price-comparison-chart">
    <!-- İstatistik Özeti -->
    <div class="mb-3 p-2 bg-gray-50 rounded-lg">
      <div class="grid grid-cols-2 gap-2 text-xs">
        <div class="text-center">
          <div class="text-gray-500">Ortalama Fiyat</div>
          <div class="font-semibold text-gray-800">{{ averagePrice.toLocaleString() }} ₺</div>
        </div>
        <div class="text-center">
          <div class="text-gray-500">Fiyat Farkı</div>
          <div class="font-semibold" :class="priceDifferenceClass">{{ priceDifferenceText }}</div>
        </div>
        <div class="text-center">
          <div class="text-gray-500">En Düşük</div>
          <div class="font-semibold text-green-600">{{ minPrice.toLocaleString() }} ₺</div>
        </div>
        <div class="text-center">
          <div class="text-gray-500">En Yüksek</div>
          <div class="font-semibold text-red-600">{{ maxPrice.toLocaleString() }} ₺</div>
        </div>
      </div>
    </div>

    <!-- Grafik -->
    <div class="relative">
      <canvas ref="chartCanvas" class="w-full h-32"></canvas>
    </div>

    <!-- Grafik Açıklaması -->
    <div class="mt-2 flex items-center justify-center space-x-4 text-xs">
      <div class="flex items-center space-x-1">
        <div class="w-3 h-0.5 bg-blue-500"></div>
        <span class="text-gray-600">Rakip Fiyat Geçmişi</span>
      </div>
      <div v-if="myPrice > 0" class="flex items-center space-x-1">
        <div class="w-3 h-0.5 bg-green-500"></div>
        <span class="text-gray-600">Benim Fiyatım</span>
      </div>
      <div class="flex items-center space-x-1">
        <div class="w-3 h-0.5 bg-orange-500"></div>
        <span class="text-gray-600">Güncel Rakip Fiyatı</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'

// Chart.js bileşenlerini kaydet
Chart.register(...registerables)

const props = defineProps({
  priceHistory: {
    type: Array,
    default: () => []
  },
  myPrice: {
    type: Number,
    default: 0
  },
  competitorPrice: {
    type: Number,
    default: 0
  }
})

const chartCanvas = ref(null)
let chartInstance = null

// İstatistik hesaplamaları
const averagePrice = computed(() => {
  if (props.priceHistory.length === 0) return 0
  const sum = props.priceHistory.reduce((acc, item) => acc + item.price, 0)
  return Math.round(sum / props.priceHistory.length)
})

const minPrice = computed(() => {
  if (props.priceHistory.length === 0) return 0
  return Math.min(...props.priceHistory.map(item => item.price))
})

const maxPrice = computed(() => {
  if (props.priceHistory.length === 0) return 0
  return Math.max(...props.priceHistory.map(item => item.price))
})

const priceDifference = computed(() => {
  if (!props.competitorPrice || !props.myPrice) return 0
  return ((props.competitorPrice - props.myPrice) / props.myPrice) * 100
})

const priceDifferenceText = computed(() => {
  const diff = priceDifference.value
  if (diff > 0) {
    return `+${diff.toFixed(1)}%`
  } else if (diff < 0) {
    return `${diff.toFixed(1)}%`
  } else {
    return '0%'
  }
})

const priceDifferenceClass = computed(() => {
  const diff = priceDifference.value
  if (diff > 0) {
    return 'text-green-600' // Rakip daha pahalı (benim lehime)
  } else if (diff < 0) {
    return 'text-red-600' // Rakip daha ucuz (benim aleyhime)
  } else {
    return 'text-gray-600'
  }
})

// Grafik oluşturma
const createChart = () => {
  if (!chartCanvas.value || props.priceHistory.length === 0) return

  // Debug logları
  console.log('📊 PriceComparisonChart props:', {
    myPrice: props.myPrice,
    competitorPrice: props.competitorPrice,
    priceHistoryLength: props.priceHistory.length
  })

  // Mevcut grafiği temizle
  if (chartInstance) {
    chartInstance.destroy()
  }

  // Veri hazırlama
  const sortedHistory = [...props.priceHistory].sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt))
  
  const labels = sortedHistory.map(item => {
    const date = new Date(item.createdAt)
    return date.toLocaleDateString('tr-TR', { day: '2-digit', month: '2-digit' })
  })
  
  const prices = sortedHistory.map(item => item.price)
  
  // Tüm fiyatları içeren aralık hesapla (0 olanları hariç tut)
  const allPrices = [...prices, props.competitorPrice]
  if (props.myPrice > 0) {
    allPrices.push(props.myPrice)
  }
  const minValue = Math.min(...allPrices)
  const maxValue = Math.max(...allPrices)
  const padding = (maxValue - minValue) * 0.1

  const ctx = chartCanvas.value.getContext('2d')
  
  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Rakip Fiyat Geçmişi',
          data: prices,
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderWidth: 2,
          fill: false,
          tension: 0.4,
          pointRadius: 3,
          pointHoverRadius: 5
        },
        ...(props.myPrice > 0 ? [{
          label: 'Benim Fiyatım',
          data: Array(labels.length).fill(props.myPrice),
          borderColor: '#10B981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          borderWidth: 2,
          borderDash: [5, 5],
          fill: false,
          pointRadius: 0
        }] : []),
        {
          label: 'Güncel Rakip Fiyatı',
          data: Array(labels.length).fill(props.competitorPrice),
          borderColor: '#F59E0B',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          borderWidth: 2,
          borderDash: [3, 3],
          fill: false,
          pointRadius: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false // Açıklama alt kısımda gösteriliyor
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          callbacks: {
            label: function(context) {
              return `${context.dataset.label}: ${context.parsed.y.toLocaleString()} ₺`
            }
          }
        }
      },
      scales: {
        x: {
          display: true,
          grid: {
            display: false
          },
          ticks: {
            maxTicksLimit: 6,
            font: {
              size: 10
            }
          }
        },
        y: {
          display: true,
          min: Math.max(0, minValue - padding),
          max: maxValue + padding,
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            font: {
              size: 10
            },
            callback: function(value) {
              return value.toLocaleString() + ' ₺'
            }
          }
        }
      },
      interaction: {
        intersect: false,
        mode: 'index'
      }
    }
  })
}

// Props değiştiğinde grafiği güncelle
watch([() => props.priceHistory, () => props.myPrice, () => props.competitorPrice], () => {
  nextTick(() => {
    createChart()
  })
}, { deep: true })

onMounted(() => {
  nextTick(() => {
    createChart()
  })
})
</script>

<style scoped>
.price-comparison-chart {
  @apply w-full;
}
</style>
