// Modül Sistemi
// Tüm modüller burada tanımlanır ve yönetilir

// Modül tanımları
const modules = {
  parseTL: {
    name: 'parseTL',
    displayName: 'Türk Lirası Parse',
    description: 'Türk Lirası formatındaki değerleri parse eder. Nokta binlik, virgül ondalık ayırıcıdır. Sadece rakamlar, nokta ve virgül kalır. Sayı yoksa null döner.',
    function: function parseTL(value) {
      if (!value || typeof value !== 'string') {
        return null; // Veri yoksa null döndür
      }
      
      // Orijinal metni küçük harfe çevirip kontrol et
      const lowerValue = value.toLowerCase().trim();
      
      // Fiyatla ilgili olmayan kelimeler (yanlış pozitifleri engellemek için)
      // Not: lowerValue kullanıldığı için tüm kelimeler küçük harfle yazılmalı
      const nonPriceKeywords = [
        'gün', 'günün', 'en düşük', 'en yüksek', 'en ucuz',
        'hafta', 'ay', 'yıl', 'saat', 'dakika', 'saniye',
        'adet', 'tane', 'paket', 'kutu', 'şişe',
        'yüzde', '%', 'indirim', 'kampanya', 'son', 'ürün', 'son 2', 'son 3', 'son 4', 'son 5',
        'son ürün', 'son ürünler', 'ürün sayısı', 'toplam ürün'
      ];
      
      // Metinde fiyatla ilgili olmayan kelimeler var mı kontrol et
      const hasNonPriceKeyword = nonPriceKeywords.some(keyword => lowerValue.includes(keyword));
      
      // Sadece rakamlar, nokta ve virgülü al (diğer her şeyi sil)
      const cleaned = value.replace(/[^\d.,]/g, '');
      
      // Eğer hiç rakam yoksa null döndür
      if (!/\d/.test(cleaned)) {
        return null;
      }
      
      // Türk Lirası formatı: nokta binlik, virgül ondalık ayırıcı
      let normalized;
      const lastCommaIndex = cleaned.lastIndexOf(',');
      if (lastCommaIndex !== -1) {
        // Virgül varsa: son virgülden önceki tüm noktaları kaldır (binlik ayırıcılar), son virgülü noktaya çevir
        const integerPart = cleaned.substring(0, lastCommaIndex).replace(/\./g, ''); // Binlik ayırıcıları kaldır
        const decimalPart = cleaned.substring(lastCommaIndex + 1);
        normalized = integerPart + '.' + decimalPart;
      } else {
        // Virgül yoksa: tüm noktaları kaldır (binlik ayırıcılar)
        normalized = cleaned.replace(/\./g, '');
      }
      
      // Parse et
      const parsed = parseFloat(normalized);
      
      // NaN kontrolü - eğer parse edilemezse null döndür
      if (isNaN(parsed)) {
        return null;
      }
      
      // Güvenlik kontrolü: Eğer metinde fiyatla ilgili olmayan kelimeler varsa null döndür
      if (hasNonPriceKeyword) {
        return null;
      }
      
      return parsed.toFixed(2); // iki ondalık basamak ekle
    }
  },
  
  ifTrue: {
    name: 'ifTrue',
    displayName: 'Boolean (True/False)',
    description: 'Veri varsa true, yoksa false döner',
    function: function(value) {
      if (!value || value === null || value === undefined || value === '') {
        return false;
      }
      const str = String(value).trim();
      return str.length > 0;
    }
  },
  
  ifFalse: {
    name: 'ifFalse',
    displayName: 'Boolean (False/True)',
    description: 'Veri varsa false, yoksa true döner',
    function: function(value) {
      if (!value || value === null || value === undefined || value === '') {
        return true;
      }
      const str = String(value).trim();
      return str.length === 0;
    }
  },
  
  trim: {
    name: 'trim',
    displayName: 'Boşluk Temizle',
    description: 'Başındaki ve sonundaki boşlukları temizler',
    function: function(value) {
      return String(value || '').trim();
    }
  },
  
  removeHTML: {
    name: 'removeHTML',
    displayName: 'HTML Tag Temizle',
    description: 'HTML tag\'lerini temizler, sadece text kalır',
    function: function(value) {
      const div = document.createElement('div');
      div.innerHTML = String(value || '');
      return div.textContent || div.innerText || '';
    }
  },
  
  normalizeWhitespace: {
    name: 'normalizeWhitespace',
    displayName: 'Boşluk Normalize Et',
    description: 'Birden fazla boşluğu tek boşluğa çevirir',
    function: function(value) {
      return String(value || '').replace(/\s+/g, ' ').trim();
    }
  },
  
  extractNumber: {
    name: 'extractNumber',
    displayName: 'Sadece Sayı Çıkar',
    description: 'String\'den sadece sayıları çıkarır',
    function: function(value) {
      const numbers = String(value || '').match(/\d+\.?\d*/g);
      return numbers ? numbers.join('') : '';
    }
  },
  
  parseUSD: {
    name: 'parseUSD',
    displayName: 'USD Parse',
    description: 'USD formatındaki değerleri parse eder ($, boşluk, nokta işlemleri)',
    function: function(value) {
      if (!value || typeof value !== 'string') return value;
      const parsed = parseFloat(value.replace(/[$,\s]/g, '').replace(',', '.'));
      return isNaN(parsed) ? value : parsed.toFixed(2);
    }
  },
  
  parseEUR: {
    name: 'parseEUR',
    displayName: 'EUR Parse',
    description: 'EUR formatındaki değerleri parse eder (€, boşluk, nokta işlemleri)',
    function: function(value) {
      if (!value || typeof value !== 'string') return value;
      const parsed = parseFloat(value.replace(/[€,\s.]/g, '').replace(',', '.'));
      return isNaN(parsed) ? value : parsed.toFixed(2);
    }
  },
  
  parseInternationalPrice: {
    name: 'parseInternationalPrice',
    displayName: 'Uluslararası Fiyat Parse',
    description: 'Virgül binlik, nokta ondalık ayırıcı formatını parse eder (59,037.80 -> 59037.80)',
    function: function(value) {
      if (!value || typeof value !== 'string') {
        return value;
      }
      
      // Boşlukları ve özel karakterleri temizle (₺, $, € gibi)
      let cleaned = value.replace(/[₺$€\s]/g, '');
      
      // Virgülü kaldır (binlik ayırıcı)
      cleaned = cleaned.replace(/,/g, '');
      
      // Noktayı koru (ondalık ayırıcı)
      const parsed = parseFloat(cleaned);
      
      // NaN kontrolü
      if (isNaN(parsed)) {
        return value; // Parse edilemezse orijinal değeri döndür
      }
      
      // 2 ondalık basamakla döndür
      return parsed.toFixed(2);
    }
  },
  
  toLowerCase: {
    name: 'toLowerCase',
    displayName: 'Küçük Harfe Çevir',
    description: 'Tüm harfleri küçük harfe çevirir',
    function: function(value) {
      return String(value || '').toLowerCase();
    }
  },
  
  toUpperCase: {
    name: 'toUpperCase',
    displayName: 'Büyük Harfe Çevir',
    description: 'Tüm harfleri büyük harfe çevirir',
    function: function(value) {
      return String(value || '').toUpperCase();
    }
  },
  
  removeSpecialChars: {
    name: 'removeSpecialChars',
    displayName: 'Özel Karakter Temizle',
    description: 'Özel karakterleri temizler (sadece harf, sayı ve boşluk kalır)',
    function: function(value) {
      return String(value || '').replace(/[^a-zA-Z0-9\s]/g, '');
    }
  },
  
  extractURL: {
    name: 'extractURL',
    displayName: 'URL Çıkar',
    description: 'Text içinden URL çıkarır',
    function: function(value) {
      const urlRegex = /(https?:\/\/[^\s]+)/g;
      const matches = String(value || '').match(urlRegex);
      return matches ? matches[0] : '';
    }
  },
  
  extractEmail: {
    name: 'extractEmail',
    displayName: 'Email Çıkar',
    description: 'Text içinden email adresi çıkarır',
    function: function(value) {
      const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
      const matches = String(value || '').match(emailRegex);
      return matches ? matches[0] : '';
    }
  },
  
  extractFirstWord: {
    name: 'extractFirstWord',
    displayName: 'İlk Kelime',
    description: 'İlk kelimeyi çıkarır',
    function: function(value) {
      const words = String(value || '').trim().split(/\s+/);
      return words[0] || '';
    }
  },
  
  extractLastWord: {
    name: 'extractLastWord',
    displayName: 'Son Kelime',
    description: 'Son kelimeyi çıkarır',
    function: function(value) {
      const words = String(value || '').trim().split(/\s+/);
      return words.length > 0 ? words[words.length - 1] : '';
    }
  },
  
  defaultValue: {
    name: 'defaultValue',
    displayName: 'Varsayılan Değer',
    description: 'Veri yoksa varsayılan değer döner (parametre: varsayılan_değer)',
    function: function(value, defaultValue = 'N/A') {
      if (!value || value === null || value === undefined || String(value).trim() === '') {
        return defaultValue;
      }
      return value;
    }
  },
  
  formatDate: {
    name: 'formatDate',
    displayName: 'Tarih Formatla',
    description: 'Tarihi belirli formata çevirir (YYYY-MM-DD)',
    function: function(value) {
      if (!value) return '';
      const date = new Date(value);
      if (isNaN(date.getTime())) return value;
      return date.toISOString().split('T')[0];
    }
  },
  
  split: {
    name: 'split',
    displayName: 'Böl',
    description: 'String\'i belirli karaktere göre böler (parametre: ayırıcı, index)',
    function: function(value, separator = ',', index = 0) {
      const parts = String(value || '').split(separator);
      return parts[index] ? parts[index].trim() : '';
    }
  },
  
  slice: {
    name: 'slice',
    displayName: 'Kes',
    description: 'String\'in belirli kısmını alır (parametre: başlangıç, bitiş)',
    function: function(value, start = 0, end = null) {
      const str = String(value || '');
      return end !== null ? str.slice(start, end) : str.slice(start);
    }
  },
  
  checkDisplayNone: {
    name: 'checkDisplayNone',
    displayName: 'Display None Kontrolü',
    description: 'Seçilen öğenin inline style\'ında (style="display: none;") varsa false, yoksa true döner. Element bulunamazsa null döner (scraped_data\'ya eklenmez)',
    function: function(value, selector = null, element = null, elementStyleDisplay = null) {
      try {
        let el = null;
        let display = null;
        
        // Eğer element direkt geçilmişse kullan
        if (element && element.nodeType) {
          el = element;
          display = el.style.display;
        }
        // Eğer elementStyleDisplay geçilmişse (test için content script'ten gelen değer)
        else if (elementStyleDisplay !== null && elementStyleDisplay !== undefined) {
          display = elementStyleDisplay;
        }
        // Eğer selector geçilmişse element'i bul
        else if (selector) {
          el = document.querySelector(selector);
          if (el) {
            display = el.style.display;
          }
        }
        // Eğer value bir element referansı ise direkt kullan
        else if (value && typeof value === 'object' && value.nodeType) {
          el = value;
          display = el.style.display;
        }
        // Eğer value bir CSS selector string'i ise
        else if (typeof value === 'string' && (value.trim().startsWith('.') || value.trim().startsWith('#'))) {
          el = document.querySelector(value);
          if (el) {
            display = el.style.display;
          }
        }
        
        // Element bulunamazsa veya display değeri alınamazsa null döndür
        // Ama boş string ('') geçerli bir değerdir (style="" durumu)
        if (display === null || (display === undefined && elementStyleDisplay === null)) {
          return null;
        }
        
        // style="display: none;" varsa false, yoksa true döndür
        // Boş string ('') veya undefined ise true döndür (style="" veya style yok)
        return display !== 'none';
      } catch (error) {
        console.error('checkDisplayNone hatası:', error);
        return null; // Hata durumunda null döndür (scraped_data'ya eklenmeyecek)
      }
    }
  },
  
  disabled: {
    name: 'disabled',
    displayName: 'Disabled Kontrolü',
    description: 'Seçilen öğenin disabled attribute\'u varsa false, yoksa true döner. Element bulunamazsa null döner (scraped_data\'ya eklenmez)',
    function: function(value, selector = null, element = null, elementDisabled = null) {
      try {
        let el = null;
        let isDisabled = null;
        
        // Eğer element direkt geçilmişse kullan
        if (element && element.nodeType) {
          el = element;
          isDisabled = el.disabled || el.hasAttribute('disabled');
        }
        // Eğer elementDisabled geçilmişse (test için content script'ten gelen değer)
        else if (elementDisabled !== null && elementDisabled !== undefined) {
          isDisabled = elementDisabled;
        }
        // Eğer selector geçilmişse element'i bul
        else if (selector) {
          el = document.querySelector(selector);
          if (el) {
            isDisabled = el.disabled || el.hasAttribute('disabled');
          }
        }
        // Eğer value bir element referansı ise direkt kullan
        else if (value && typeof value === 'object' && value.nodeType) {
          el = value;
          isDisabled = el.disabled || el.hasAttribute('disabled');
        }
        // Eğer value bir CSS selector string'i ise
        else if (typeof value === 'string' && (value.trim().startsWith('.') || value.trim().startsWith('#'))) {
          el = document.querySelector(value);
          if (el) {
            isDisabled = el.disabled || el.hasAttribute('disabled');
          }
        }
        
        // Element bulunamazsa null döndür
        if (isDisabled === null || (isDisabled === undefined && elementDisabled === null)) {
          return null;
        }
        
        // disabled attribute'u varsa false, yoksa true döndür
        return !isDisabled;
      } catch (error) {
        console.error('disabled hatası:', error);
        return null; // Hata durumunda null döndür (scraped_data'ya eklenmeyecek)
      }
    }
  },
  
  checkStockOut: {
    name: 'checkStockOut',
    displayName: 'Stok Bitti Kontrolü',
    description: 'Seçilen öğedeki metinde "tükendi", "stok bitti" gibi kelimeler varsa false, yoksa true döner. Stok yoksa false, stok varsa true döner.',
    function: function(value) {
      try {
        if (!value || typeof value !== 'string') {
          // Değer yoksa veya string değilse true döndür (stok var gibi davran)
          return true;
        }
        
        // Metni küçük harfe çevir ve normalize et
        const lowerValue = String(value).toLowerCase().trim();
        
        // Stok bitti/tükendi gibi kelimeleri içeren array
        const stockOutKeywords = [
          'tükendi',
          'Tükendi',
          'stok bitti',
          'stokta yok',
          'stok yok',
          'stokta bulunmuyor',
          'bulunmuyor',
          'mevcut değil',
          'stokta mevcut değil',
          'tükenmiş',
          'stok tükenmiş',
          'stokta tükenmiş',
          'yok',
          'stok yok',
          'out of stock',
          'unavailable',
          'not available',
          'sold out',
          'stokta yok',
          'stok bitti',
          'stokta bulunmuyor'
        ];
        
        // Metinde stok bitti kelimelerinden biri var mı kontrol et
        const hasStockOutKeyword = stockOutKeywords.some(keyword => lowerValue.includes(keyword.toLowerCase()));
        
        // Eğer stok bitti kelimesi varsa false, yoksa true döndür
        const result = !hasStockOutKeyword;
        console.log('checkStockOut sonucu:', { value, hasStockOutKeyword, result });
        return result;
      } catch (error) {
        console.error('checkStockOut hatası:', error);
        // Hata durumunda true döndür (stok var gibi davran)
        return true;
      }
    }
  },
  
  checkURLMatch: {
    name: 'checkURLMatch',
    displayName: 'URL Eşleşme Kontrolü',
    description: 'Sayfanın mevcut URL\'si ile data\'daki link aynı mı kontrol eder. Aynıysa true, farklıysa false döner.',
    function: function(value) {
      try {
        if (!value || typeof value !== 'string') {
          // Değer yoksa veya string değilse false döndür
          return false;
        }
        
        // Data'dan gelen URL'i normalize et
        let dataURL = String(value).trim();
        
        // Eğer relative URL ise (http/https ile başlamıyorsa), mevcut origin ile birleştir
        if (!dataURL.startsWith('http://') && !dataURL.startsWith('https://')) {
          // Relative URL ise, mevcut origin ile birleştir
          if (dataURL.startsWith('/')) {
            dataURL = window.location.origin + dataURL;
          } else {
            // Relative path ise, mevcut URL'nin base path'i ile birleştir
            const baseURL = window.location.href.substring(0, window.location.href.lastIndexOf('/') + 1);
            dataURL = baseURL + dataURL;
          }
        }
        
        // Sayfanın mevcut URL'sini al
        const currentURL = window.location.href;
        
        // URL'leri normalize et (karşılaştırma için)
        function normalizeURL(url) {
          try {
            const urlObj = new URL(url);
            // Protocol'ü normalize et (http/https)
            let normalized = urlObj.protocol + '//';
            // Hostname'i normalize et (www'yi kaldır veya ekle - mevcut sayfanın hostname'ine göre)
            let hostname = urlObj.hostname.toLowerCase();
            // www'yi normalize et - mevcut sayfanın www durumuna göre
            const currentHostname = window.location.hostname.toLowerCase();
            const currentHasWWW = currentHostname.startsWith('www.');
            const dataHasWWW = hostname.startsWith('www.');
            
            // Eğer mevcut sayfa www ile başlıyorsa ve data URL'i www ile başlamıyorsa, www ekle
            // Veya tam tersi - basit yaklaşım: www'yi kaldır ve karşılaştır
            if (hostname.startsWith('www.')) {
              hostname = hostname.substring(4);
            }
            normalized += hostname;
            
            // Pathname'i normalize et (trailing slash'i kaldır)
            let pathname = urlObj.pathname;
            if (pathname.endsWith('/') && pathname.length > 1) {
              pathname = pathname.slice(0, -1);
            }
            normalized += pathname;
            
            // Query string ve hash'i ekle
            if (urlObj.search) {
              normalized += urlObj.search;
            }
            if (urlObj.hash) {
              normalized += urlObj.hash;
            }
            
            return normalized.toLowerCase();
          } catch (e) {
            // URL parse edilemezse, orijinal URL'i normalize et
            return url.toLowerCase().trim();
          }
        }
        
        // URL'leri normalize et ve karşılaştır
        const normalizedDataURL = normalizeURL(dataURL);
        const normalizedCurrentURL = normalizeURL(currentURL);
        
        const isMatch = normalizedDataURL === normalizedCurrentURL;
        console.log('checkURLMatch sonucu:', { 
          dataURL, 
          currentURL, 
          normalizedDataURL, 
          normalizedCurrentURL, 
          isMatch 
        });
        
        return isMatch;
      } catch (error) {
        console.error('checkURLMatch hatası:', error);
        // Hata durumunda false döndür
        return false;
      }
    }
  }
};

// Modül uygulama fonksiyonu (pipeline)
function applyModules(value, moduleNames, selector = null, element = null, elementStyleDisplay = null, elementDisabled = null) {
  if (!moduleNames || !Array.isArray(moduleNames) || moduleNames.length === 0) {
    return value;
  }
  
  let processedValue = value;
  
  for (const moduleName of moduleNames) {
    if (modules[moduleName] && typeof modules[moduleName].function === 'function') {
      try {
        // checkDisplayNone modülü için selector, element ve elementStyleDisplay bilgisini geç
        if (moduleName === 'checkDisplayNone') {
          processedValue = modules[moduleName].function(processedValue, selector, element, elementStyleDisplay);
        }
        // disabled modülü için selector, element ve elementDisabled bilgisini geç
        else if (moduleName === 'disabled') {
          processedValue = modules[moduleName].function(processedValue, selector, element, elementDisabled);
        } else {
          processedValue = modules[moduleName].function(processedValue);
        }
      } catch (error) {
        console.error(`Modül hatası (${moduleName}):`, error);
        // Hata durumunda orijinal değeri döndür
        return value;
      }
    } else {
      console.warn(`Modül bulunamadı: ${moduleName}`);
    }
  }
  
  return processedValue;
}

// Tüm modülleri listele
function getAllModules() {
  return Object.keys(modules).map(key => ({
    id: key,
    name: modules[key].name,
    displayName: modules[key].displayName,
    description: modules[key].description
  }));
}

// Modül bilgisini al
function getModuleInfo(moduleName) {
  return modules[moduleName] || null;
}

// Export (eğer module system kullanılıyorsa)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    modules,
    applyModules,
    getAllModules,
    getModuleInfo
  };
}

