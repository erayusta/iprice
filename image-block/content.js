// Content Script - DOM seviyesinde görsel ve video engelleme

let isBlockingEnabled = true;

// Eklenti durumunu kontrol et
chrome.storage.local.get(['isEnabled'], (result) => {
  isBlockingEnabled = result.isEnabled !== false;
  if (isBlockingEnabled) {
    blockMedia();
  }
});

// Storage değişikliklerini dinle
chrome.storage.onChanged.addListener((changes, areaName) => {
  if (areaName === 'local' && changes.isEnabled) {
    isBlockingEnabled = changes.isEnabled.newValue !== false;
    if (isBlockingEnabled) {
      blockMedia();
    } else {
      unblockMedia();
    }
  }
});

// Background'dan gelen mesajları dinle
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'blockMedia') {
    blockMedia();
    sendResponse({ success: true });
  } else if (request.action === 'unblockMedia') {
    unblockMedia();
    sendResponse({ success: true });
  }
  return true;
});

// Görsel ve videoları engelle
function blockMedia() {
  // Mevcut img etiketlerini engelle
  const images = document.querySelectorAll('img');
  images.forEach(img => {
    // src'yi boşalt veya placeholder ile değiştir
    if (img.dataset.originalSrc === undefined) {
      img.dataset.originalSrc = img.src;
    }
    img.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
    img.style.display = 'none';
  });

  // Mevcut video etiketlerini engelle
  const videos = document.querySelectorAll('video');
  videos.forEach(video => {
    if (video.dataset.originalSrc === undefined) {
      video.dataset.originalSrc = video.src;
    }
    video.src = '';
    video.srcObject = null;
    video.style.display = 'none';
  });

  // Yeni eklenen img etiketlerini engelle (MutationObserver)
  if (!window.imageBlockObserver) {
    window.imageBlockObserver = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1) { // Element node
            // Yeni eklenen img etiketleri
            if (node.tagName === 'IMG') {
              if (node.dataset.originalSrc === undefined) {
                node.dataset.originalSrc = node.src;
              }
              node.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
              node.style.display = 'none';
            }
            // Yeni eklenen video etiketleri
            if (node.tagName === 'VIDEO') {
              if (node.dataset.originalSrc === undefined) {
                node.dataset.originalSrc = node.src;
              }
              node.src = '';
              node.srcObject = null;
              node.style.display = 'none';
            }
            // İçindeki img ve video etiketlerini de kontrol et
            const childImages = node.querySelectorAll && node.querySelectorAll('img');
            if (childImages) {
              childImages.forEach(img => {
                if (img.dataset.originalSrc === undefined) {
                  img.dataset.originalSrc = img.src;
                }
                img.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
                img.style.display = 'none';
              });
            }
            const childVideos = node.querySelectorAll && node.querySelectorAll('video');
            if (childVideos) {
              childVideos.forEach(video => {
                if (video.dataset.originalSrc === undefined) {
                  video.dataset.originalSrc = video.src;
                }
                video.src = '';
                video.srcObject = null;
                video.style.display = 'none';
              });
            }
          }
        });
      });
    });

    window.imageBlockObserver.observe(document.body || document.documentElement, {
      childList: true,
      subtree: true
    });
  }
}

// Engellemeyi kaldır
function unblockMedia() {
  // Observer'ı durdur
  if (window.imageBlockObserver) {
    window.imageBlockObserver.disconnect();
    window.imageBlockObserver = null;
  }

  // Orijinal src'leri geri yükle
  const images = document.querySelectorAll('img[data-original-src]');
  images.forEach(img => {
    if (img.dataset.originalSrc) {
      img.src = img.dataset.originalSrc;
      img.style.display = '';
    }
  });

  const videos = document.querySelectorAll('video[data-original-src]');
  videos.forEach(video => {
    if (video.dataset.originalSrc) {
      video.src = video.dataset.originalSrc;
      video.style.display = '';
    }
  });
}

// Sayfa yüklendiğinde engellemeyi başlat
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    if (isBlockingEnabled) {
      blockMedia();
    }
  });
} else {
  if (isBlockingEnabled) {
    blockMedia();
  }
}

