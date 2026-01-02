// RabbitMQ Helper - Chrome Extension için Yeni API (RabbitMQ yerine)
// Artık RabbitMQ yerine backend API'den pending job'ları alıyoruz

class RabbitMQHelper {
  constructor() {
    // Eski RabbitMQ ayarları (artık kullanılmıyor ama geriye dönük uyumluluk için)
    this.host = '10.20.50.16';
    this.port = 15672;
    this.user = 'admin';
    this.pass = 'admin123';
    this.vhost = encodeURIComponent('chrome');
    this.queue = 'chrome.queue';
    this.isListening = false;
    this.pollInterval = null;
    this.pollIntervalMs = 3000; // 3 saniyede bir kontrol et (başlangıç değeri)
    
    // Exponential backoff ayarları
    this.currentPollInterval = 10000; // Mevcut polling aralığı (ms) - 10 saniye
    this.minPollInterval = 10000; // Minimum polling aralığı (10 saniye)
    this.maxPollInterval = 60000; // Maximum polling aralığı (60 saniye)
    this.backoffMultiplier = 2; // Her başarısız denemede çarpan
    this.consecutiveEmptyCount = 0; // Ardışık boş sonuç sayısı
    
    // Paralel işlem yönetimi
    this.activeProcesses = 0; // Aktif işlem sayısı
    this.isProcessingMessages = false; // Mesaj işleme döngüsü çalışıyor mu?
    this.processingCallback = null; // Callback fonksiyonu
    this.processingParallelCount = 1; // Paralel işlem sayısı
    
    // Mesaj kuyruğu (API'den alınan mesajlar burada bekler)
    this.messageQueue = []; // Bekleyen mesajlar kuyruğu
    this.isFetchingFromAPI = false; // Şu anda API'den veri çekiliyor mu?
    this.lastAPICallTime = 0; // Son API çağrısının zamanı (ms)
    
    // Yeni API ayarları
    this.apiBaseURL = null;
    this.apiToken = null;
    
    // Job takibi
    this.currentJobId = null; // Şu anda işlenen job'ın ID'si
    this.currentJobTotalCount = 0; // Job'daki toplam mesaj sayısı
    this.currentJobProcessedCount = 0; // İşlenen mesaj sayısı
    this.currentJobMessages = new Set(); // İşlenen mesaj ID'lerini takip et (duplicate kontrolü için)
    this.isFinishingJob = false; // Job finish işlemi devam ediyor mu? (race condition önleme)
  }
  
  // API base URL al
  async getAPIBaseURL() {
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
  async getAPIToken() {
    if (this.apiToken) {
      return this.apiToken;
    }
    
    return new Promise((resolve) => {
      chrome.storage.local.get(['apiToken'], (result) => {
        this.apiToken = result.apiToken || null;
        resolve(this.apiToken);
      });
    });
  }

  // Base64 encode for Basic Auth
  getAuthHeader() {
    const credentials = btoa(`${this.user}:${this.pass}`);
    return `Basic ${credentials}`;
  }

  // RabbitMQ Management API base URL
  getBaseURL() {
    return `http://${this.host}:${this.port}/api`;
  }

  // URL birleştirme yardımcı fonksiyonu (çift slash sorununu önler)
  joinURL(baseURL, endpoint) {
    // Base URL'in sonundaki slash'ı temizle
    const cleanBase = baseURL.replace(/\/+$/, '');
    // Endpoint'in başındaki slash'ı temizle
    const cleanEndpoint = endpoint.replace(/^\/+/, '');
    // Birleştir
    return `${cleanBase}/${cleanEndpoint}`;
  }

  // Yeni API'den pending job al (RabbitMQ yerine)
  // Tüm job item'larını döndürür (count parametresi artık kullanılmıyor)
  async peekMessage(count = 1) {
    try {
      const baseURL = await this.getAPIBaseURL();
      const token = await this.getAPIToken();
      
      // API endpoint
      let url = this.joinURL(baseURL, '/chrome-extension/next-pending-job');
      if (token) {
        url += `?token=${encodeURIComponent(token)}`;
      }
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          return { success: false, message: 'Pending durumunda job bulunamadı' };
        }
        if (response.status === 401) {
          return { success: false, message: 'Yetkilendirme hatası' };
        }
        const errorData = await response.json().catch(() => ({}));
        return { 
          success: false, 
          message: errorData.message || `HTTP ${response.status}: ${response.statusText}` 
        };
      }

      const data = await response.json();
      
      if (data.success && data.data && Array.isArray(data.data) && data.data.length > 0) {
        // API'den gelen job verisini RabbitMQ formatına çevir
        // data.data bir array, her eleman bir job item
        // TÜM item'ları döndür (count parametresini görmezden gel)
        const messages = data.data.map(item => ({
          message: item, // Job item'ı direkt mesaj olarak kullan
          deliveryTag: item.data_id, // data_id'yi deliveryTag olarak kullan
          exchange: '',
          routingKey: 'chrome.queue'
        }));
        
        console.log(`API'den ${messages.length} adet job item alındı (job_id: ${data.job_id})`);
        
        // Job takibini başlat (yeni job alındığında)
        if (data.job_id && this.currentJobId !== data.job_id) {
          console.log(`Yeni job başlatıldı: ${data.job_id}, Toplam mesaj: ${data.count || messages.length}`);
          this.currentJobId = data.job_id;
          this.currentJobTotalCount = data.count || messages.length;
          this.currentJobProcessedCount = 0;
          this.currentJobMessages.clear();
        }
        
        // Tek mesaj için eski formatı koru (geriye dönük uyumluluk)
        if (messages.length === 1) {
          return {
            success: true,
            message: messages[0].message,
            messages: messages, // Tüm mesajları döndür
            deliveryTag: messages[0].deliveryTag,
            exchange: messages[0].exchange,
            routingKey: messages[0].routingKey,
            job_id: data.job_id,
            job_name: data.job_name,
            count: data.count
          };
        }
        
        // Birden fazla mesaj varsa
        return {
          success: true,
          messages: messages, // TÜM mesajları döndür
          message: messages[0].message, // İlk mesajı da döndür (geriye dönük uyumluluk)
          job_id: data.job_id,
          job_name: data.job_name,
          count: data.count
        };
      }
      
      return { success: false, message: 'Pending durumunda job bulunamadı' };
    } catch (error) {
      console.error('API mesaj çekme hatası:', error);
      return {
        success: false,
        message: error.message || 'Mesaj çekilemedi'
      };
    }
  }

  // Mesajı işle ve sonucu backend'e gönder
  async processMessage(rabbitmqMessage) {
    try {
      // Mesaj formatını kontrol et
      if (!rabbitmqMessage.url) {
        throw new Error('Mesajda URL bulunamadı');
      }

      // URL'yi taramak için background script'e mesaj gönder
      const result = await new Promise((resolve, reject) => {
        chrome.runtime.sendMessage({
          action: 'processRabbitMQMessage',
          data: rabbitmqMessage
        }, (response) => {
          if (chrome.runtime.lastError) {
            reject(new Error(chrome.runtime.lastError.message));
          } else {
            resolve(response);
          }
        });
      });

      return result;
    } catch (error) {
      console.error('Mesaj işleme hatası:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // RabbitMQ'yu dinlemeye başla
  startListening(callback, parallelCount = 1) {
    if (this.isListening) {
      console.log('RabbitMQ zaten dinleniyor');
      return;
    }

    this.isListening = true;
    this.parallelCount = parallelCount;
    // Backoff değerlerini sıfırla
    this.currentPollInterval = this.minPollInterval;
    this.consecutiveEmptyCount = 0;
    // Paralel işlem değişkenlerini sıfırla
    this.activeProcesses = 0;
    this.isProcessingMessages = false;
    this.processingCallback = callback;
    this.processingParallelCount = parallelCount;
    // Kuyruğu temizle
    this.messageQueue = [];
    this.isFetchingFromAPI = false;
    this.lastAPICallTime = 0;
    // Job takibini sıfırla
    this.currentJobId = null;
    this.currentJobTotalCount = 0;
    this.currentJobProcessedCount = 0;
    this.currentJobMessages.clear();
    this.isFinishingJob = false;
    
    console.log('RabbitMQ dinleme başlatıldı, paralel işlem sayısı:', parallelCount);

    // Retry mesajlarını dinle
    this.setupRetryMessageListener();

    // Storage'dan retry queue'yu kontrol et ve kuyruğa ekle
    this.loadRetryQueueFromStorage();

    // Sürekli mesaj işleme döngüsünü başlat
    this.startMessageProcessingLoop();
  }
  
  // Retry mesajlarını dinle (background.js'den gelen mesajlar)
  setupRetryMessageListener() {
    // Chrome runtime mesajlarını dinle
    if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.onMessage) {
      chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.action === 'retryRabbitMQMessage' && message.data) {
          console.log('Retry mesajı alındı, kuyruğa ekleniyor:', message.data.url);
          // Mesajı kuyruğun sonuna ekle (tekrar işlenecek)
          this.messageQueue.push(message.data);
          console.log(`Retry mesajı kuyruğa eklendi. Toplam kuyruk: ${this.messageQueue.length}`);
          sendResponse({ success: true });
        }
        return true;
      });
    }
  }
  
  // Storage'dan retry queue'yu yükle ve kuyruğa ekle
  async loadRetryQueueFromStorage() {
    try {
      if (typeof chrome !== 'undefined' && chrome.storage) {
        return new Promise((resolve) => {
          chrome.storage.local.get(['retryQueue'], (result) => {
            const retryQueue = result.retryQueue || [];
            if (retryQueue.length > 0) {
              console.log(`Storage'dan ${retryQueue.length} adet retry mesajı bulundu, kuyruğa ekleniyor...`);
              // Tüm retry mesajlarını kuyruğun sonuna ekle
              for (const msg of retryQueue) {
                this.messageQueue.push(msg);
              }
              console.log(`Retry mesajları kuyruğa eklendi. Toplam kuyruk: ${this.messageQueue.length}`);
              // Storage'dan temizle
              chrome.storage.local.set({ retryQueue: [] }, () => {
                console.log('Retry queue storage\'dan temizlendi');
                resolve(true);
              });
            } else {
              resolve(false);
            }
          });
        });
      }
      return false;
    } catch (error) {
      console.error('Retry queue yükleme hatası:', error);
      return false;
    }
  }
  
  // Sürekli mesaj işleme döngüsü (paralel slotlar için)
  async startMessageProcessingLoop() {
    if (!this.isListening) {
      return;
    }

    this.isProcessingMessages = true;
    
    while (this.isListening) {
      try {
        // Aktif işlem sayısı paralel limitin altındaysa yeni mesaj al
        if (this.activeProcesses < this.processingParallelCount) {
          const availableSlots = this.processingParallelCount - this.activeProcesses;
          const queueLength = this.messageQueue.length;
          console.log(`Boş slot var: ${availableSlots}/${this.processingParallelCount} (Aktif: ${this.activeProcesses}, Kuyruk: ${queueLength})`);
          
          // ÖNEMLİ: Kuyrukta mesaj varsa, kesinlikle API'ye istek atma!
          if (queueLength > 0) {
            // Kuyruktan mesaj al ve işle
            const messageFromQueue = this.messageQueue.shift();
            if (messageFromQueue) {
              console.log(`Kuyruktan mesaj alındı: ${messageFromQueue.url || 'Bilinmeyen URL'} (Kalan: ${this.messageQueue.length})`);
              await this.processMessage(messageFromQueue);
              // Kısa bir süre bekle (diğer slotlar için)
              await new Promise(resolve => setTimeout(resolve, 100));
            }
          } else {
            // Kuyruk boş, önce storage'dan retry queue'yu kontrol et
            const retryLoaded = await this.loadRetryQueueFromStorage();
            
            // Kuyruk hala boşsa ve API'den veri çekilmiyorsa, API'den yeni mesaj al
            // Ayrıca son API çağrısından en az 10 saniye geçmiş olmalı
            const timeSinceLastAPICall = Date.now() - this.lastAPICallTime;
            const minAPICallInterval = 10000; // 10 saniye
            
            // ÖNEMLİ: API'den yeni mesaj almadan önce, mevcut job'ın tamamlanıp tamamlanmadığını kontrol et
            if (this.messageQueue.length === 0 && !this.isFetchingFromAPI && timeSinceLastAPICall >= minAPICallInterval) {
              // Önce finish kontrolü yap
              await this.checkAndFinishJob();
              
              // Eğer finish işlemi devam ediyorsa, bekle
              if (this.isFinishingJob) {
                console.log('Job finish işlemi devam ediyor, yeni job alınmadan önce bekleniyor...');
                await new Promise(resolve => setTimeout(resolve, 1000));
                continue; // Döngünün başına dön
              }
              
              // Eğer job tamamlandıysa ve yeni job yoksa, finish işlemi tamamlanana kadar bekle
              if (this.currentJobId && this.currentJobProcessedCount >= this.currentJobTotalCount) {
                console.log('Job tamamlandı, finish işlemi tamamlanana kadar bekleniyor...');
                await new Promise(resolve => setTimeout(resolve, 1000));
                continue; // Döngünün başına dön
              }
              
              console.log(`Kuyruk tamamen boş, API'den yeni mesajlar alınıyor... (Son çağrıdan ${Math.round(timeSinceLastAPICall/1000)} saniye geçti)`);
              const jobFound = await this.fetchMessagesFromAPI();
              
              if (jobFound) {
                // API'den mesajlar alındı ve kuyruğa eklendi, backoff'u sıfırla
                this.resetPollInterval();
                console.log(`API'den ${this.messageQueue.length} adet mesaj alındı, kuyruğa eklendi. İşlem başlıyor...`);
                // Kuyruktan bir mesaj al ve işle
                const messageFromQueue = this.messageQueue.shift();
                if (messageFromQueue) {
                  await this.processMessage(messageFromQueue);
                }
              } else {
                // Job bulunamadı (404 veya boş sonuç)
                // lastAPICallTime zaten fetchMessagesFromAPI içinde set edildi
                // Minimum 10 saniye bekle (zaten lastAPICallTime set edildi, döngü tekrar kontrol edecek)
                this.increasePollInterval();
                const waitTime = Math.min(this.currentPollInterval, 10000);
                console.log(`Job bulunamadı. Sonraki API isteği en az 10 saniye sonra atılacak. Şimdilik ${waitTime}ms bekleniyor (ardışık boş: ${this.consecutiveEmptyCount})`);
                await new Promise(resolve => setTimeout(resolve, waitTime));
              }
            } else if (this.messageQueue.length > 0) {
              // Retry queue'dan mesaj geldi, kuyruktan devam et
              const messageFromQueue = this.messageQueue.shift();
              if (messageFromQueue) {
                console.log(`Retry queue'dan mesaj alındı: ${messageFromQueue.url || 'Bilinmeyen URL'} (Kalan: ${this.messageQueue.length})`);
                await this.processMessage(messageFromQueue);
              }
            } else {
              // API'den veri çekiliyor veya minimum bekleme süresi dolmamış
              const timeSinceLastAPICall = Date.now() - this.lastAPICallTime;
              const minAPICallInterval = 10000; // 10 saniye
              
              if (this.isFetchingFromAPI) {
                console.log('API\'den veri çekiliyor, bekleniyor...');
                await new Promise(resolve => setTimeout(resolve, 1000));
              } else if (timeSinceLastAPICall < minAPICallInterval) {
                const remainingTime = minAPICallInterval - timeSinceLastAPICall;
                console.log(`Son API çağrısından ${Math.round(remainingTime/1000)} saniye geçmedi. ${Math.round(remainingTime/1000)} saniye daha bekleniyor...`);
                // Kalan sürenin tamamını bekle (maksimum 10 saniye)
                await new Promise(resolve => setTimeout(resolve, Math.min(remainingTime, 10000)));
              } else {
                // Minimum süre geçti ama başka bir durum var, kısa bekle
                // Kuyruk boş ve aktif işlem yoksa job kontrolü yap
                if (this.messageQueue.length === 0 && this.activeProcesses === 0) {
                  await this.checkAndFinishJob();
                  
                  // Eğer finish işlemi devam ediyorsa, bekle
                  if (this.isFinishingJob) {
                    console.log('Job finish işlemi devam ediyor, bekleniyor...');
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    continue; // Döngünün başına dön
                  }
                }
                await new Promise(resolve => setTimeout(resolve, 1000));
              }
            }
          }
        } else {
          // Tüm slotlar dolu, kısa bir süre bekle
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      } catch (error) {
        console.error('Mesaj işleme döngüsü hatası:', error);
        // Hata durumunda kısa bir süre bekle
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    this.isProcessingMessages = false;
  }
  
  // API'den mesajları al ve kuyruğa ekle
  async fetchMessagesFromAPI() {
    if (this.isFetchingFromAPI) {
      console.log('API\'ye zaten istek atılıyor, bekleniyor...');
      return false; // Zaten API'den veri çekiliyor
    }
    
    // API çağrısı zamanını kaydet (başarılı veya başarısız olsun)
    this.lastAPICallTime = Date.now();
    this.isFetchingFromAPI = true;
    
    try {
      // API'den pending job al
      const result = await this.peekMessage(1);
      
      if (result.success && result.messages && result.messages.length > 0) {
        // Tüm mesajları kuyruğa ekle
        console.log(`API'den ${result.messages.length} adet mesaj alındı, kuyruğa ekleniyor...`);
        
        for (const msg of result.messages) {
          this.messageQueue.push(msg.message);
        }
        
        console.log(`Kuyruğa ${result.messages.length} mesaj eklendi. Toplam kuyruk: ${this.messageQueue.length}`);
        this.isFetchingFromAPI = false;
        return true; // Mesajlar alındı
      } else if (result.success && result.message) {
        // Tek mesaj varsa (eski format - geriye dönük uyumluluk)
        this.messageQueue.push(result.message);
        console.log(`Tek mesaj kuyruğa eklendi. Toplam kuyruk: ${this.messageQueue.length}`);
        this.isFetchingFromAPI = false;
        return true; // Mesaj alındı
      } else {
        // Job bulunamadı (404 veya boş sonuç)
        console.log('API\'den job bulunamadı (404 veya boş sonuç). Sonraki istek 10 saniye sonra atılacak.');
        this.isFetchingFromAPI = false;
        return false; // Job bulunamadı
      }
    } catch (error) {
      console.error('API mesaj alma hatası:', error);
      this.isFetchingFromAPI = false;
      return false; // Hata durumunda
    }
  }
  
  // Mesajı işle (paralel olarak)
  async processMessage(message) {
    if (!this.isListening || this.activeProcesses >= this.processingParallelCount) {
      // Eğer limit dolduysa mesajı tekrar kuyruğa ekle
      this.messageQueue.unshift(message);
      return;
    }
    
    console.log(`Mesaj işleniyor: ${message.url || 'Bilinmeyen URL'} (Aktif: ${this.activeProcesses + 1}/${this.processingParallelCount})`);
    
    // Mesaj ID'sini al (data_id veya url)
    const messageId = message.data_id || message.url || JSON.stringify(message);
    
    // Mesajı paralel olarak işle
    this.activeProcesses++;
    const processPromise = Promise.resolve(
      this.processingCallback(message, { message: message })
    )
    .then(async result => {
      console.log(`Mesaj işlendi: ${message.url || 'Bilinmeyen URL'} (Aktif: ${this.activeProcesses - 1}/${this.processingParallelCount})`, result);
      
      // Job takibi: Mesaj başarıyla işlendiyse sayacı artır
      // result.success kontrolü yap (callback'den dönen processResult'ın success field'ı)
      if (result && result.success && this.currentJobId && !this.currentJobMessages.has(messageId)) {
        this.currentJobMessages.add(messageId);
        this.currentJobProcessedCount++;
        console.log(`✅ Job takibi: ${this.currentJobId} - İşlenen: ${this.currentJobProcessedCount}/${this.currentJobTotalCount}`);
      } else {
        // Debug: Neden sayılmadı?
        if (!result) {
          console.warn(`⚠️ Mesaj sayılmadı: result undefined - ${message.url || 'Bilinmeyen URL'}`);
        } else if (!result.success) {
          console.warn(`⚠️ Mesaj sayılmadı: result.success = ${result.success} - ${message.url || 'Bilinmeyen URL'}`);
        } else if (!this.currentJobId) {
          console.warn(`⚠️ Mesaj sayılmadı: currentJobId yok - ${message.url || 'Bilinmeyen URL'}`);
        } else if (this.currentJobMessages.has(messageId)) {
          console.warn(`⚠️ Mesaj sayılmadı: zaten işlenmiş (duplicate) - ${message.url || 'Bilinmeyen URL'}`);
        }
      }
      
      return result;
    })
    .catch(error => {
      console.error('Mesaj işleme hatası:', error);
      return { success: false, error: error.message };
    })
    .finally(async () => {
      // İşlem bitince aktif sayacı azalt
      this.activeProcesses = Math.max(0, this.activeProcesses - 1);
      console.log(`İşlem tamamlandı. Aktif işlem: ${this.activeProcesses}/${this.processingParallelCount}`);
      
      // Aktif işlem kalmadıysa ve kuyruk boşsa, job kontrolü yap
      if (this.activeProcesses === 0 && this.messageQueue.length === 0) {
        await this.checkAndFinishJob();
      }
    });
    
    // Promise'i beklemeyelim, arka planda çalışsın
    processPromise.catch(err => console.error('Promise hatası:', err));
  }
  
  // Job'ın tamamlanıp tamamlanmadığını kontrol et ve finish endpoint'ine istek at
  async checkAndFinishJob() {
    console.log(`🔍 checkAndFinishJob çağrıldı - Job: ${this.currentJobId}, İşlenen: ${this.currentJobProcessedCount}/${this.currentJobTotalCount}, Aktif: ${this.activeProcesses}, Kuyruk: ${this.messageQueue.length}, isFinishingJob: ${this.isFinishingJob}`);
    
    // Zaten finish işlemi devam ediyorsa bekle
    if (this.isFinishingJob) {
      console.log('⏳ Finish işlemi zaten devam ediyor, bekleniyor...');
      return;
    }
    
    // Job takibi aktif değilse
    if (!this.currentJobId) {
      console.log('⚠️ Job takibi aktif değil (currentJobId yok)');
      return;
    }
    
    // Hala aktif işlemler varsa veya kuyrukta mesaj varsa bekle
    if (this.activeProcesses > 0 || this.messageQueue.length > 0) {
      console.log(`⏳ Job kontrolü: Aktif işlem: ${this.activeProcesses}, Kuyruk: ${this.messageQueue.length}, İşlenen: ${this.currentJobProcessedCount}/${this.currentJobTotalCount} - Bekleniyor...`);
      return;
    }
    
    // ✅ YENİ MANTIK: Kuyruk boş ve aktif işlem yoksa finish-job at
    // currentJobProcessedCount kontrolü kaldırıldı çünkü başarısız mesajlar sayılmıyordu
    console.log(`✅ Job tamamlandı: ${this.currentJobId} - Kuyruk boş ve aktif işlem yok (İşlenen: ${this.currentJobProcessedCount}/${this.currentJobTotalCount})`);
    
    // Race condition önleme: flag'i set et
    this.isFinishingJob = true;
    
    // Finish endpoint'ine istek at
    try {
      const baseURL = await this.getAPIBaseURL();
      const token = await this.getAPIToken();
      
      if (!token) {
        console.warn('API token bulunamadı, finish job isteği gönderilemedi');
        this.isFinishingJob = false; // ✅ Flag'i sıfırla!
        return;
      }
      
      const url = this.joinURL(baseURL, '/chrome-extension/finish-job');
      
      console.log(`Job finish isteği gönderiliyor: ${this.currentJobId}`);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          token: token,
          job_id: this.currentJobId
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('Finish job hatası:', {
          status: response.status,
          statusText: response.statusText,
          error: errorData
        });
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log(`Job başarıyla tamamlandı olarak işaretlendi: ${this.currentJobId}`, data);
      
      // Job takibini sıfırla
      this.currentJobId = null;
      this.currentJobTotalCount = 0;
      this.currentJobProcessedCount = 0;
      this.currentJobMessages.clear();
      this.isFinishingJob = false;
      
    } catch (error) {
      console.error('Finish job isteği hatası:', error);
      // Hata durumunda flag'i sıfırla (tekrar deneme için)
      this.isFinishingJob = false;
      // Hata olsa bile job takibini sıfırla (tekrar deneme için)
      // this.currentJobId = null;
    }
  }
  
  
  // Bir sonraki kontrolü zamanla (exponential backoff ile)
  scheduleNextCheck(callback, parallelCount) {
    if (!this.isListening) {
      return;
    }
    
    // Mevcut interval'i temizle
    if (this.pollInterval) {
      clearTimeout(this.pollInterval);
    }
    
    // Yeni interval ayarla
    this.pollInterval = setTimeout(() => {
      if (this.isListening) {
        this.checkForMessages(callback, parallelCount);
      }
    }, this.currentPollInterval);
    
    console.log(`Sonraki kontrol ${this.currentPollInterval}ms sonra (ardışık boş: ${this.consecutiveEmptyCount})`);
  }
  
  // Polling interval'ini sıfırla (job bulunduğunda)
  resetPollInterval() {
    this.currentPollInterval = this.minPollInterval;
    this.consecutiveEmptyCount = 0;
  }
  
  // Polling interval'ini artır (job bulunamadığında - exponential backoff)
  increasePollInterval() {
    this.consecutiveEmptyCount++;
    // Exponential backoff: her boş sonuçta interval'i 2 katına çıkar
    this.currentPollInterval = Math.min(
      this.minPollInterval * Math.pow(this.backoffMultiplier, this.consecutiveEmptyCount),
      this.maxPollInterval
    );
  }

  // RabbitMQ'yu dinlemeyi durdur
  stopListening() {
    if (!this.isListening) {
      return;
    }

    this.isListening = false;
    if (this.pollInterval) {
      clearTimeout(this.pollInterval);
      this.pollInterval = null;
    }
    // Backoff değerlerini sıfırla
    this.currentPollInterval = this.minPollInterval;
    this.consecutiveEmptyCount = 0;
    // Paralel işlem değişkenlerini sıfırla
    this.isProcessingMessages = false;
    this.processingCallback = null;
    this.processingParallelCount = 1;
    // Kuyruğu temizle
    this.messageQueue = [];
    this.isFetchingFromAPI = false;
    this.lastAPICallTime = 0;
    // Job takibini sıfırla
    this.currentJobId = null;
    this.currentJobTotalCount = 0;
    this.currentJobProcessedCount = 0;
    this.currentJobMessages.clear();
    this.isFinishingJob = false;
    console.log('RabbitMQ dinleme durduruldu');
  }

  // Mesaj kontrolü - API'den job al ve tüm item'ları işle (ESKİ YÖNTEM - artık kullanılmıyor)
  // Bu fonksiyon artık kullanılmıyor, startMessageProcessingLoop kullanılıyor
  async checkForMessages(callback, parallelCount = 1) {
    // Eski yöntem artık kullanılmıyor, sadece geriye dönük uyumluluk için bırakıldı
    console.warn('checkForMessages artık kullanılmıyor, startMessageProcessingLoop kullanılıyor');
  }

  // Queue bilgilerini al (local state'ten - gereksiz API çağrısı yapmıyor)
  getQueueInfo() {
    // Local kuyruktan bilgi döndür (API'ye gereksiz istek atmıyor)
    return {
      success: true,
      data: {
        name: 'chrome.queue',
        messages: this.messageQueue.length, // Local kuyruktaki mesaj sayısı
        consumers: this.activeProcesses, // Aktif işlem sayısı
        state: this.messageQueue.length > 0 ? 'ready' : 'idle'
      }
    };
  }

  // Bağlantıyı test et (artık API'yi test ediyoruz)
  async testConnection() {
    try {
      const baseURL = await this.getAPIBaseURL();
      const token = await this.getAPIToken();
      
      let url = this.joinURL(baseURL, '/chrome-extension/next-pending-job');
      if (token) {
        url += `?token=${encodeURIComponent(token)}`;
      }
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });

      // 404 de başarılı sayılır (pending job yok demektir, API çalışıyor)
      if (response.status === 404 || response.ok) {
        return {
          success: true,
          message: 'API bağlantısı başarılı'
        };
      }
      
      if (response.status === 401) {
        return {
          success: false,
          error: 'Yetkilendirme hatası. Token kontrol edin.'
        };
      }
      
      return {
        success: false,
        error: `HTTP ${response.status}: ${response.statusText}`
      };
    } catch (error) {
      return {
        success: false,
        error: error.message || 'API bağlantı hatası'
      };
    }
  }

  // Mesajı queue'ya gönder (API üzerinden - VPN uyumlu)
  async sendMessage(queueName, messageData) {
    try {
      const baseURL = await this.getAPIBaseURL();
      const token = await this.getAPIToken();
      
      if (!token) {
        console.warn('API token bulunamadı, RabbitMQ mesajı gönderilemedi');
        return {
          success: false,
          error: 'API token bulunamadı'
        };
      }
      
      const url = this.joinURL(baseURL, '/chrome-extension/send-to-queue');
      
      console.log('RabbitMQ mesaj gönderiliyor (API üzerinden - helper):', {
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
          token: token,
          queue_name: queueName,
          message_data: messageData
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('API mesaj gönderme hatası (helper):', {
          status: response.status,
          statusText: response.statusText,
          error: errorData
        });
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('API mesaj gönderme yanıtı (helper):', data);
      
      return {
        success: true,
        message: data.message || 'Mesaj başarıyla gönderildi'
      };
    } catch (error) {
      console.error('API mesaj gönderme hatası (helper):', error);
      return {
        success: false,
        error: error.message || 'Mesaj gönderilemedi'
      };
    }
  }

  // Başarılı mesajı completed queue'suna gönder
  async sendToCompleted(messageData) {
    return await this.sendMessage('chrome.queue.completed', messageData);
  }

  // Hatalı mesajı error queue'suna gönder
  async sendToError(messageData) {
    return await this.sendMessage('chrome.queue.error', messageData);
  }
}

// Global olarak erişilebilir yap
if (typeof window !== 'undefined') {
  window.rabbitmqHelper = new RabbitMQHelper();
}

