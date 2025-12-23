// Background Service Worker - Eklenti durumunu yönetir

// Eklenti yüklendiğinde varsayılan ayarları kontrol et
chrome.runtime.onInstalled.addListener(async () => {
  const result = await chrome.storage.local.get(['isEnabled']);
  if (result.isEnabled === undefined) {
    await chrome.storage.local.set({ isEnabled: true });
  }
  await updateRules();
});

// Storage değişikliklerini dinle
chrome.storage.onChanged.addListener((changes, areaName) => {
  if (areaName === 'local' && changes.isEnabled) {
    updateRules();
  }
});

// Kuralları güncelle
async function updateRules() {
  const result = await chrome.storage.local.get(['isEnabled']);
  const isEnabled = result.isEnabled !== false; // Varsayılan olarak true

  try {
    if (isEnabled) {
      // Kuralları etkinleştir
      await chrome.declarativeNetRequest.updateEnabledRulesets({
        enableRulesetIds: ['ruleset_1'],
        disableRulesetIds: []
      });
    } else {
      // Kuralları devre dışı bırak
      await chrome.declarativeNetRequest.updateEnabledRulesets({
        enableRulesetIds: [],
        disableRulesetIds: ['ruleset_1']
      });
    }
  } catch (error) {
    console.error('Kurallar güncellenirken hata:', error);
  }
}

// Tab güncellendiğinde content script'e mesaj gönder
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status === 'loading' && tab.url) {
    const result = await chrome.storage.local.get(['isEnabled']);
    const isEnabled = result.isEnabled !== false;
    
    if (isEnabled) {
      try {
        await chrome.tabs.sendMessage(tabId, { action: 'blockMedia' });
      } catch (error) {
        // Tab henüz hazır değilse veya mesaj gönderilemezse hata yok sayılır
      }
    }
  }
});

