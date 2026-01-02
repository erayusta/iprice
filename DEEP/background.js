// Background service worker

// Side panel'i aç
chrome.action.onClicked.addListener((tab) => {
  chrome.sidePanel.open({ windowId: tab.windowId });
});

// İlk yüklemede storage'ı başlat
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get(['selectors'], (result) => {
    if (!result.selectors) {
      chrome.storage.local.set({ selectors: {} });
    }
  });
});

// Mesaj yönlendirme (content script'ten panel'e)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'elementSelected') {
    // Mesajı tüm side panel'lere gönder
    chrome.runtime.sendMessage(message).catch(() => {
      // Panel açık değilse hata verme
    });
  } else if (message.action === 'processRabbitMQMessage') {
    // RabbitMQ mesajını işle
    processRabbitMQMessage(message.data).then(result => {
      sendResponse(result);
    }).catch(error => {
      sendResponse({ success: false, error: error.message });
    });
    return true; // Async response için
  }
  return true;
});

// RabbitMQ mesajını işle
// retryAttempt: 0 = ilk deneme, 1 = retry denemesi
async function processRabbitMQMessage(rabbitmqData, retryAttempt = 0) {
  let tab = null;
  try {
    // Mesaj formatını kontrol et
    if (!rabbitmqData.url) {
      throw new Error('Mesajda URL bulunamadı');
    }

    const url = rabbitmqData.url;
    const attributes = rabbitmqData.attributes || [];
    const jobId = rabbitmqData.job_id;
    const dataId = rabbitmqData.data_id;
    const companyId = rabbitmqData.company_id;
    const productId = rabbitmqData.product_id;
    const screenshotEnabled = rabbitmqData.screenshot || false;

    // Attributes'ları eklenti formatına çevir
    const selectors = attributes.map(attr => {
      let valueData = {};
      try {
        if (typeof attr.attributes_value === 'string') {
          valueData = JSON.parse(attr.attributes_value);
        } else {
          valueData = attr.attributes_value;
        }
      } catch (e) {
        console.warn('Attribute value parse hatası:', e);
      }

      return {
        label: attr.attributes_name,
        selector: valueData.selector || '',
        selector_type: attr.attributes_type || 'class',
        note: valueData.note || null,
        modules: valueData.modules || [],
        attributes_id: attr.attributes_id // attributes_id'yi ekle (stock kontrolü için)
      };
    }).filter(sel => sel.selector); // Boş selector'ları filtrele

    if (selectors.length === 0) {
      throw new Error('Geçerli selector bulunamadı');
    }

    // Eğer attributes_id: 23 (stock kontrolü) varsa, onu listenin başına al
    const stockIndex = selectors.findIndex(sel => sel.attributes_id === 23);
    if (stockIndex !== -1) {
      const stockSelector = selectors.splice(stockIndex, 1)[0];
      selectors.unshift(stockSelector);
      console.log('[processRabbitMQMessage] Stock kontrolü (attributes_id: 23) listenin başına alındı');
    }

    // URL'yi yeni sekmede aç
    tab = await chrome.tabs.create({ url, active: false });

    // Sayfanın yüklenmesini bekle
    await waitForTabLoad(tab.id);

    // Content script'e veri toplama mesajı gönder
    const response = await new Promise((resolve, reject) => {
      chrome.tabs.sendMessage(tab.id, {
        action: 'collectData',
        selectors: selectors
      }, (response) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
        } else if (response && response.error) {
          reject(new Error(response.error));
        } else {
          resolve(response);
        }
      });
    });

    // Yeni response formatını işle (data ve errors alanları)
    const collectedData = response?.data || response || {};
    const collectedErrors = response?.errors || [];

    // Screenshot al (eğer seçiliyse)
    let screenshot = null;
    if (screenshotEnabled) {
      try {
        await chrome.tabs.update(tab.id, { active: true });
        await new Promise(resolve => setTimeout(resolve, 1500));
        screenshot = await chrome.tabs.captureVisibleTab(null, {
          format: 'png',
          quality: 90
        });
        await chrome.tabs.update(tab.id, { active: false });
      } catch (error) {
        console.error('Screenshot hatası:', error);
      }
    }

    // Sonucu hazırla (orijinal mesaj + kazınan veri)
    const result = {
      ...rabbitmqData, // Orijinal mesaj verileri
      scraped_data: collectedData, // Kazınan veri
      errors: collectedErrors.length > 0 ? collectedErrors : undefined, // Hata detayları
      screenshot: screenshot,
      timestamp: new Date().toISOString(),
      success: true
    };

    console.log('RabbitMQ mesaj işlendi, sonuç hazırlandı:', {
      job_id: result.job_id,
      data_id: result.data_id,
      url: result.url,
      scraped_data_keys: Object.keys(result.scraped_data || {})
    });

    // Not: Artık storage'da veri tutmuyoruz, sadece API'ye gönderiyoruz
    console.log('Sonuç hazırlandı, API\'ye gönderiliyor...');

    // Sekmeyi kapat
    if (tab && tab.id) {
      await chrome.tabs.remove(tab.id);
    }

    // RabbitMQ'ya completed queue'suna gönder
    try {
      const sendResult = await sendToRabbitMQQueue('chrome.queue.completed', result);
      if (!sendResult.success) {
        console.error('Completed queue\'ya mesaj gönderilemedi:', sendResult.error);
      }
    } catch (error) {
      console.error('RabbitMQ completed queue gönderme hatası:', error);
    }

    // Panel'e sonuç bildirimi gönder
    chrome.runtime.sendMessage({
      action: 'rabbitmqScanComplete',
      result: result
    }).catch(() => {
      // Panel açık değilse hata verme
    });

    return {
      success: true,
      result: result
    };

  } catch (error) {
    console.error('RabbitMQ mesaj işleme hatası:', error);
    
    // Sekmeyi kapatmayı dene
    if (tab && tab.id) {
      try {
        await chrome.tabs.remove(tab.id);
      } catch (e) {}
    }

    // Eğer "Sayfa yükleme zaman aşımı" veya "Sayfa yüklenemedi" hatası ise ve henüz retry yapılmadıysa
    // retryAttempt 0 ise ilk deneme, mesajda _isRetry flag'i varsa retry denemesi
    const isRetryAttempt = rabbitmqData._isRetry === true || retryAttempt > 0;
    const isTimeoutError = error.message.includes('Sayfa yükleme zaman aşımı') || 
                           error.message.includes('Sayfa yüklenemedi');
    
    if (isTimeoutError && !isRetryAttempt) {
      console.log(`Sayfa yükleme hatası alındı (${error.message}). Mesaj tekrar işlenecek: ${rabbitmqData.url}`);
      
      // Retry mesajını işaretle
      const retryMessage = {
        ...rabbitmqData,
        _isRetry: true // Retry denemesi olduğunu işaretle
      };
      
      // Mesajı tekrar kuyruğa eklemek için rabbitmq-helper'a mesaj gönder
      // Side panel açıksa mesajı oraya gönder
      try {
        chrome.runtime.sendMessage({
          action: 'retryRabbitMQMessage',
          data: retryMessage
        }).catch(() => {
          // Panel açık değilse veya mesaj gönderilemezse, mesajı storage'a kaydet
          // rabbitmq-helper bunu kontrol edip kuyruğa ekleyecek
          chrome.storage.local.get(['retryQueue'], (result) => {
            const retryQueue = result.retryQueue || [];
            retryQueue.push(retryMessage);
            chrome.storage.local.set({ retryQueue });
            console.log('Retry mesajı storage\'a kaydedildi. Toplam retry kuyruğu:', retryQueue.length);
          });
        });
      } catch (sendError) {
        console.error('Retry mesajı gönderilemedi, storage\'a kaydediliyor:', sendError);
        // Storage'a kaydet
        chrome.storage.local.get(['retryQueue'], (result) => {
          const retryQueue = result.retryQueue || [];
          retryQueue.push(retryMessage);
          chrome.storage.local.set({ retryQueue });
          console.log('Retry mesajı storage\'a kaydedildi. Toplam retry kuyruğu:', retryQueue.length);
        });
      }

      return {
        success: false,
        error: error.message,
        retryScheduled: true,
        message: 'Mesaj tekrar işlenecek'
      };
    }

    // 2. denemede de başarısız olursa veya başka bir hata ise error queue'ya gönder
    const errorResult = {
      ...rabbitmqData, // Orijinal mesaj verileri
      error: error.message,
      retryAttempt: retryAttempt,
      timestamp: new Date().toISOString(),
      success: false
    };

    // RabbitMQ'ya error queue'suna gönder
    try {
      const sendResult = await sendToRabbitMQQueue('chrome.queue.error', errorResult);
      if (!sendResult.success) {
        console.error('Error queue\'ya mesaj gönderilemedi:', sendResult.error);
      } else {
        console.log(`Mesaj error queue'ya gönderildi (retryAttempt: ${retryAttempt}):`, rabbitmqData.url);
      }
    } catch (sendError) {
      console.error('RabbitMQ error queue gönderme hatası:', sendError);
    }

    return {
      success: false,
      error: error.message,
      result: errorResult
    };
  }
}

// RabbitMQ'ya mesaj gönder (API üzerinden - VPN uyumlu)
async function sendToRabbitMQQueue(queueName, messageData) {
  try {
    // API base URL ve token al
    const apiBaseURL = await getAPIBaseURL();
    const apiToken = await getAPIToken();
    
    if (!apiToken) {
      console.warn('API token bulunamadı, RabbitMQ mesajı gönderilemedi');
      return {
        success: false,
        error: 'API token bulunamadı'
      };
    }
    
    // URL birleştirme (çift slash sorununu önler)
    const cleanBase = apiBaseURL.replace(/\/+$/, '');
    const cleanEndpoint = '/chrome-extension/send-to-queue'.replace(/^\/+/, '');
    const url = `${cleanBase}/${cleanEndpoint}`;
    
    console.log('RabbitMQ mesaj gönderiliyor (API üzerinden):', {
      queueName,
      url,
      payloadLength: JSON.stringify(messageData).length
    });
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        token: apiToken,
        queue_name: queueName,
        message_data: messageData
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('API mesaj gönderme hatası:', {
        status: response.status,
        statusText: response.statusText,
        error: errorData
      });
      throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log('API mesaj gönderme yanıtı:', data);
    
    return {
      success: true,
      message: data.message || 'Mesaj başarıyla gönderildi'
    };
  } catch (error) {
    console.error('API mesaj gönderme hatası:', error);
    return {
      success: false,
      error: error.message || 'Mesaj gönderilemedi'
    };
  }
}

// API base URL al
async function getAPIBaseURL() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['testMode', 'apiBaseURL'], (result) => {
      // Önce storage'dan kayıtlı API Base URL'i kontrol et
      if (result.apiBaseURL && result.apiBaseURL.trim().length > 0) {
        resolve(result.apiBaseURL.trim());
        return;
      }
      
      // Eğer storage'da yoksa, test moduna göre varsayılan değerleri kullan
      const isTestMode = result.testMode === true;
      
      if (isTestMode) {
        // Test modu: localhost
        resolve('http://localhost:8082/api');
      } else {
        // Canlı mod: varsayılan URL
        resolve('http://10.20.50.16/iprice_backend/api/');
      }
    });
  });
}

// API token al
async function getAPIToken() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['apiToken'], (result) => {
      resolve(result.apiToken || null);
    });
  });
}

// Sekme yüklenmesini bekle (güncellenmiş - daha uzun bekleme ve akıllı kontrol)
function waitForTabLoad(tabId) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    const timeout = setTimeout(() => {
      chrome.tabs.onUpdated.removeListener(checkComplete);
      const elapsed = Math.round((Date.now() - startTime) / 1000);
      console.warn(`[waitForTabLoad] Zaman aşımı: ${elapsed} saniye geçti, tabId: ${tabId}`);
      reject(new Error('Sayfa yükleme zaman aşımı'));
    }, 45000); // 45 saniye timeout (10 saniyeden 45 saniyeye çıkarıldı)

    let hasResolved = false;
    let checkCount = 0;
    const maxChecks = 90; // 45 saniye / 0.5 saniye = 90 kontrol
    
    console.log(`[waitForTabLoad] Sayfa yüklenmesi bekleniyor, tabId: ${tabId}, timeout: 45 saniye`);
    
    const checkComplete = async (updatedTabId, changeInfo, updatedTab) => {
      if (hasResolved) return;
      checkCount++;
      
      if (updatedTabId === tabId) {
        // Hata sayfası kontrolü
        if (updatedTab && updatedTab.url) {
          if (updatedTab.url.startsWith('chrome-error://') || 
              updatedTab.url.startsWith('chrome://') ||
              updatedTab.url.startsWith('about:') ||
              updatedTab.url.includes('error') ||
              updatedTab.url.includes('blocked')) {
            clearTimeout(timeout);
            chrome.tabs.onUpdated.removeListener(checkComplete);
            hasResolved = true;
            const elapsed = Math.round((Date.now() - startTime) / 1000);
            console.error(`[waitForTabLoad] Hata sayfası tespit edildi, tabId: ${tabId}, süre: ${elapsed} saniye, URL: ${updatedTab.url}`);
            reject(new Error(`Sayfa yüklenemedi: ${updatedTab.url}`));
            return;
          }
        }
        
        // Sayfa başarıyla yüklendi
        if (changeInfo.status === 'complete') {
          // Ekstra kontrol: Sayfanın gerçekten yüklendiğinden emin ol
          try {
            const tab = await chrome.tabs.get(tabId);
            if (tab && tab.status === 'complete' && tab.url && 
                !tab.url.startsWith('chrome-error://') && 
                !tab.url.startsWith('chrome://')) {
              clearTimeout(timeout);
              chrome.tabs.onUpdated.removeListener(checkComplete);
              hasResolved = true;
              
              const elapsed = Math.round((Date.now() - startTime) / 1000);
              console.log(`[waitForTabLoad] Sayfa yüklendi, tabId: ${tabId}, süre: ${elapsed} saniye, URL: ${tab.url}`);
              
              // JavaScript ve dinamik içerik yüklenmesi için bekleme (2 saniye)
              // Ağır sayfalar için ekstra süre
              setTimeout(() => {
                resolve();
              }, 2000);
            }
          } catch (error) {
            // Tab bulunamadı veya hata oluştu, yine de devam et
            if (!hasResolved) {
              clearTimeout(timeout);
              chrome.tabs.onUpdated.removeListener(checkComplete);
              hasResolved = true;
              setTimeout(() => resolve(), 2000);
            }
          }
        }
      }
      
      // Maksimum kontrol sayısına ulaşıldıysa timeout
      if (checkCount >= maxChecks && !hasResolved) {
        clearTimeout(timeout);
        chrome.tabs.onUpdated.removeListener(checkComplete);
        hasResolved = true;
        reject(new Error('Sayfa yükleme zaman aşımı (maksimum kontrol sayısına ulaşıldı)'));
      }
    };

    chrome.tabs.onUpdated.addListener(checkComplete);

    // Eğer zaten yüklenmişse kontrol et
    chrome.tabs.get(tabId, async (tab) => {
      if (hasResolved) return;
      
      if (tab) {
        // Hata sayfası kontrolü
        if (tab.url && (tab.url.startsWith('chrome-error://') || 
                        tab.url.startsWith('chrome://') ||
                        tab.url.startsWith('about:') ||
                        tab.url.includes('error'))) {
          clearTimeout(timeout);
          chrome.tabs.onUpdated.removeListener(checkComplete);
          hasResolved = true;
          reject(new Error(`Sayfa yüklenemedi: ${tab.url}`));
          return;
        }
        
        if (tab.status === 'complete' && tab.url && 
            !tab.url.startsWith('chrome-error://') && 
            !tab.url.startsWith('chrome://')) {
          clearTimeout(timeout);
          chrome.tabs.onUpdated.removeListener(checkComplete);
          hasResolved = true;
          // JavaScript yüklenmesi için bekleme (2 saniye)
          setTimeout(() => {
            resolve();
          }, 2000);
        }
      }
    });
  });
}

