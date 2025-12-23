// Popup JavaScript - UI kontrolü

const toggleSwitch = document.getElementById('toggleSwitch');
const statusText = document.getElementById('statusText');

// Mevcut durumu yükle
chrome.storage.local.get(['isEnabled'], (result) => {
  const isEnabled = result.isEnabled !== false; // Varsayılan true
  toggleSwitch.checked = isEnabled;
  updateStatusText(isEnabled);
});

// Toggle değişikliğini dinle
toggleSwitch.addEventListener('change', (e) => {
  const isEnabled = e.target.checked;
  chrome.storage.local.set({ isEnabled: isEnabled }, () => {
    updateStatusText(isEnabled);
    
    // Tüm sekmelere mesaj gönder
    chrome.tabs.query({}, (tabs) => {
      tabs.forEach(tab => {
        chrome.tabs.sendMessage(tab.id, {
          action: isEnabled ? 'blockMedia' : 'unblockMedia'
        }).catch(() => {
          // Tab hazır değilse hata yok sayılır
        });
      });
    });
  });
});

// Durum metnini güncelle
function updateStatusText(isEnabled) {
  statusText.textContent = isEnabled ? 'Aktif' : 'Pasif';
  statusText.className = isEnabled ? 'status-text active' : 'status-text inactive';
}

