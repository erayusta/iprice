// Navigasyon sistemi - sayfa geçişleri için

// Ana menüden modüllere geçiş
document.addEventListener('DOMContentLoaded', () => {
  // Ana menü sayfası kontrolü
  const dataScraperBtn = document.getElementById('data-scraper-btn');
  if (dataScraperBtn) {
    dataScraperBtn.addEventListener('click', () => {
      window.location.href = 'data-scraper.html';
    });
  }
  
  // Data Scraper sayfasından ana menüye dönüş
  const backToHomeBtn = document.getElementById('back-to-home');
  if (backToHomeBtn) {
    backToHomeBtn.addEventListener('click', () => {
      window.location.href = 'index.html';
    });
  }
});

