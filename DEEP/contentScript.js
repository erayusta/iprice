// Öğe seçme modu durumu
let pickerMode = false;
let highlightedElement = null;

// Mesaj dinleyicisi
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'startPicker') {
    startPickerMode();
    sendResponse({ success: true });
  } else if (message.action === 'stopPicker') {
    stopPickerMode();
    sendResponse({ success: true });
  } else if (message.action === 'collectData') {
    collectData(message.selectors).then(data => {
      sendResponse(data);
    }).catch(error => {
      sendResponse({ error: error.message });
    });
    return true; // Async response için
  } else if (message.action === 'testSelector') {
    testSelector(message.selector, message.selectorType, message.modules).then(result => {
      sendResponse(result);
    }).catch(error => {
      sendResponse({ success: false, error: error.message });
    });
    return true; // Async response için
  }
});

// Öğe seçme modunu başlat
function startPickerMode() {
  pickerMode = true;
  
  // Sayfa üzerine overlay ekle
  document.body.style.cursor = 'crosshair';
  
  // Tüm öğelerin pointer-events'ini etkinleştir (disabled öğeler için)
  const style = document.createElement('style');
  style.id = 'picker-mode-style';
  style.textContent = `
    * {
      pointer-events: auto !important;
      cursor: crosshair !important;
    }
  `;
  document.head.appendChild(style);
  
  // Tüm öğelere hover ve click event listener ekle
  document.addEventListener('mouseover', handleMouseOver, true);
  document.addEventListener('mouseout', handleMouseOut, true);
  document.addEventListener('click', handleClick, true);
  
  // Scroll'u engelle (seçim sırasında)
  document.body.style.overflow = 'hidden';
}

// Öğe seçme modunu durdur
function stopPickerMode() {
  pickerMode = false;
  document.body.style.cursor = '';
  document.body.style.overflow = '';
  
  // Eklenen style'ı kaldır
  const style = document.getElementById('picker-mode-style');
  if (style) {
    style.remove();
  }
  
  document.removeEventListener('mouseover', handleMouseOver, true);
  document.removeEventListener('mouseout', handleMouseOut, true);
  document.removeEventListener('click', handleClick, true);
  
  if (highlightedElement) {
    highlightedElement.style.outline = '';
    highlightedElement.style.boxShadow = '';
    highlightedElement.style.border = '';
    highlightedElement = null;
  }
}

// Mouse over event handler
function handleMouseOver(e) {
  if (!pickerMode) return;
  
  e.stopPropagation();
  
  // Disabled öğeleri de seçilebilir yap
  const target = e.target;
  if (target.disabled) {
    target.style.pointerEvents = 'auto';
  }
  
  // Önceki highlight'ı kaldır
  if (highlightedElement && highlightedElement !== target) {
    highlightedElement.style.outline = '';
    highlightedElement.style.boxShadow = '';
    highlightedElement.style.border = '';
  }
  
  // Yeni öğeyi highlight et - daha görünür yap
  highlightedElement = target;
  highlightedElement.style.outline = '3px solid #667eea';
  highlightedElement.style.outlineOffset = '2px';
  highlightedElement.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.3)';
  
  // Eğer öğenin zaten border'ı varsa, onu koru ama highlight ekle
  const originalBorder = highlightedElement.style.border;
  if (!originalBorder || originalBorder === 'none') {
    highlightedElement.style.border = '2px solid #667eea';
  }
}

// Mouse out event handler
function handleMouseOut(e) {
  if (!pickerMode) return;
  
  // Highlight'ı kaldırma (click için hazır tut)
  // Sadece başka bir öğeye geçildiğinde kaldırılacak
}

// Parent'ları kullanarak spesifik class selector oluştur
function generateClassSelectorWithParents(element, includeParents = []) {
  // ID varsa kullan
  if (element.id) {
    return `#${element.id}`;
  }
  
  // Öğenin kendi selector'ını oluştur
  let elementSelector = '';
  
  // Class varsa kullan - tüm class'ları birleştir (daha spesifik olması için)
  if (element.className && typeof element.className === 'string') {
    const classes = element.className.trim().split(/\s+/).filter(c => c && c.length > 0);
    if (classes.length > 0) {
      // Birden fazla class varsa hepsini kullan (daha spesifik)
      if (classes.length > 1) {
        elementSelector = '.' + classes.join('.');
      } else {
        elementSelector = `.${classes[0]}`;
      }
    }
  }
  
  // Class yoksa tag name kullan
  if (!elementSelector) {
    elementSelector = element.tagName.toLowerCase();
  }
  
  // Disabled attribute'u varsa ekle (:disabled pseudo-class daha güvenilir)
  if (element.disabled || element.hasAttribute('disabled')) {
    // Hem [disabled] hem de :disabled kullan (daha güvenilir)
    elementSelector += ':disabled';
  }
  
  // Parent'ları ekle (en dıştan içe doğru)
  if (includeParents.length > 0) {
    const parentSelectors = includeParents.map(parent => {
      if (parent.id) {
        return `#${parent.id}`;
      }
      if (parent.className && typeof parent.className === 'string') {
        const classes = parent.className.trim().split(/\s+/).filter(c => c);
        if (classes.length > 0) {
          const mainClass = classes.find(c => c.length > 3) || classes[0];
          return `.${mainClass}`;
        }
      }
      return null;
    }).filter(s => s !== null);
    
    if (parentSelectors.length > 0) {
      return parentSelectors.join(' ') + ' ' + elementSelector;
    }
  }
  
  return elementSelector;
}

// Class selector oluştur (basit versiyon - geriye dönük uyumluluk için)
function generateClassSelector(element) {
  return generateClassSelectorWithParents(element, []);
}

// Disabled öğeler için selector'ı düzelt (test için)
function fixSelectorForDisabled(selector) {
  // Eğer selector'da [disabled] yoksa ve sayfada disabled öğeler varsa, ekle
  // Ancak bu otomatik yapılmasın, sadece test sırasında yardımcı olsun
  return selector;
}

// En içteki text içeren öğeyi bul
function findDeepestTextElement(element) {
  // Öğenin child node'larını al
  const children = Array.from(element.childNodes);
  const elementChildren = children.filter(node => node.nodeType === Node.ELEMENT_NODE);
  const textNodes = children.filter(node => node.nodeType === Node.TEXT_NODE && node.textContent?.trim());
  
  // Eğer hiç element child yoksa, bu öğeyi döndür (içinde sadece text var)
  if (elementChildren.length === 0) {
    return element;
  }
  
  // Eğer sadece bir element child varsa
  if (elementChildren.length === 1) {
    const child = elementChildren[0];
    const childText = child.textContent?.trim();
    const parentText = element.textContent?.trim();
    
    // Eğer parent'ın direkt text node'u yoksa, child'a git
    if (textNodes.length === 0) {
      return findDeepestTextElement(child);
    }
    
    // Eğer parent'ın text'i child'ın text'ini içeriyorsa (örn: "Ürün Kodu: MDYK4TU/A" içinde "MDYK4TU/A" var)
    // ve child'ın içinde element yoksa, child'ı seç
    if (childText && parentText.includes(childText)) {
      const childElementChildren = Array.from(child.childNodes).filter(node => node.nodeType === Node.ELEMENT_NODE);
      if (childElementChildren.length === 0) {
        return child;
      }
      // Eğer child'ın içinde element varsa, recursive devam et
      return findDeepestTextElement(child);
    }
  }
  
  // Birden fazla child varsa, en içteki text içeren öğeyi bul
  // Önce child'ların içinde sadece text içeren (child element olmayan) öğeyi bul
  for (const child of elementChildren) {
    const childElementChildren = Array.from(child.childNodes).filter(node => node.nodeType === Node.ELEMENT_NODE);
    
    // Eğer child'ın içinde element yoksa, bu child'ı seç
    if (childElementChildren.length === 0) {
      const childText = child.textContent?.trim();
      if (childText) {
        return child;
      }
    }
  }
  
  // Eğer hiçbir child sadece text içermiyorsa, ilk child'ı recursive olarak kontrol et
  if (elementChildren.length > 0) {
    return findDeepestTextElement(elementChildren[0]);
  }
  
  // Hiçbir şey bulunamadıysa, orijinal öğeyi döndür
  return element;
}

// Tüm parent öğeleri topla
function getAllParents(element) {
  const parents = [];
  let current = element;
  
  while (current && current !== document.body && current !== document.documentElement) {
    parents.push(current);
    current = current.parentElement;
    if (!current) break;
  }
  
  return parents;
}

// Click event handler
function handleClick(e) {
  if (!pickerMode) return;
  
  e.stopPropagation();
  e.preventDefault();
  
  let element = e.target;
  
  // Disabled öğeleri de seçilebilir yap
  if (element.disabled) {
    element.style.pointerEvents = 'auto';
  }
  
  // En içteki text içeren öğeyi seç
  element = findDeepestTextElement(element);
  
  // Tüm parent öğeleri topla
  const parents = getAllParents(element);
  
  // Her parent seviyesi için selector oluştur (parent'ları kullanarak)
  const elementsData = [];
  
  // En içteki öğe (parent olmadan)
  elementsData.push({
    classSelector: generateClassSelector(element),
    xpathSelector: generateXPath(element),
    tagName: element.tagName,
    className: element.className,
    id: element.id,
    content: getElementContent(element),
    textContent: element.textContent?.trim().substring(0, 50),
    parentCount: 0
  });
  
  // Parent'ları kullanarak daha spesifik selector'lar oluştur
  for (let i = 0; i < parents.length; i++) {
    const parentSubset = parents.slice(0, i + 1).reverse(); // En yakın parent'tan en uzağa
    const classSelector = generateClassSelectorWithParents(element, parentSubset);
    const xpathSelector = generateXPath(element);
    
    elementsData.push({
      classSelector: classSelector,
      xpathSelector: xpathSelector,
      tagName: element.tagName,
      className: element.className,
      id: element.id,
      content: getElementContent(element),
      textContent: element.textContent?.trim().substring(0, 50),
      parentCount: parentSubset.length,
      parents: parentSubset.map(p => {
        if (p.className && typeof p.className === 'string') {
          const classes = p.className.trim().split(/\s+/).filter(c => c);
          if (classes.length > 0) {
            return classes[0];
          }
        }
        return p.tagName.toLowerCase();
      })
    });
  }
  
  // Helper function for element content
  function getElementContent(el) {
    let elementContent = '';
    const textNodes = Array.from(el.childNodes).filter(node => node.nodeType === Node.TEXT_NODE);
    const directText = textNodes.map(node => node.textContent?.trim()).filter(t => t).join(' ').trim();
    
    if (directText) {
      elementContent = directText;
    } else {
      elementContent = el.textContent?.trim() || '';
    }
    
    if (!elementContent) {
      elementContent = el.innerHTML?.trim() || el.value || el.getAttribute('value') || '';
    }
    if (!elementContent) {
      elementContent = el.innerText?.trim() || '';
    }
    
    return elementContent.substring(0, 100);
  }
  
  // Domain'i al
  const domain = window.location.hostname.replace('www.', '');
  
  // Öğe bilgilerini panel'e gönder
  chrome.runtime.sendMessage({
    action: 'elementSelected',
    element: {
      elements: elementsData,
      domain: domain,
      selectedIndex: 0 // Varsayılan olarak en içteki öğe seçili
    }
  });
  
  // Picker modunu durdur
  stopPickerMode();
}

// XPath oluştur
function generateXPath(element) {
  // En yakın ID'li parent'ı bul (Chrome'un mantığı)
  let idParent = null;
  let current = element;
  
  // Önce element'in kendisini kontrol et
  if (current.id) {
    idParent = current;
  } else {
    // Sonra parent'ları kontrol et
    current = current.parentElement;
    while (current && current !== document.body && current !== document.documentElement) {
      if (current.id) {
        idParent = current;
        break;
      }
      current = current.parentElement;
    }
  }
  
  // ID'li parent bulunduysa, ondan başla
  if (idParent) {
    const idPath = `//*[@id="${idParent.id}"]`;
    
    // Eğer element, ID'li parent'ın kendisiyse, sadece ID path'ini döndür
    if (element === idParent) {
      return idPath;
    }
    
    // ID'li parent'tan element'e kadar olan path'i oluştur
    let path = '';
    current = element;
    
    // ID'li parent'a kadar olan tüm parent'ları topla
    const pathElements = [];
    while (current && current !== idParent && current !== document.body && current !== document.documentElement) {
      pathElements.unshift(current); // Başa ekle (en yakın parent'tan en uzağa)
      current = current.parentElement;
    }
    
    // Her path element için selector oluştur
    for (const pathElement of pathElements) {
      let selector = pathElement.nodeName.toLowerCase();
      
      // Aynı tag name'e sahip kardeşlerin sayısını bul
      let sibling = pathElement;
      let nth = 1;
      let sameTagSiblings = 1; // Aynı tag name'e sahip toplam kardeş sayısı
      
      // Önceki kardeşleri say
      while (sibling.previousElementSibling) {
        sibling = sibling.previousElementSibling;
        if (sibling.nodeName.toLowerCase() === selector) {
          nth++;
          sameTagSiblings++;
        }
      }
      
      // Sonraki kardeşleri say
      sibling = pathElement;
      while (sibling.nextElementSibling) {
        sibling = sibling.nextElementSibling;
        if (sibling.nodeName.toLowerCase() === selector) {
          sameTagSiblings++;
        }
      }
      
      // Sadece aynı tag name'e sahip birden fazla kardeş varsa index ekle (Chrome gibi)
      if (sameTagSiblings > 1) {
        selector += `[${nth}]`;
      }
      
      path += '/' + selector;
    }
    
    return idPath + path;
  }
  
  // ID yoksa, Chrome gibi // ile başlayan relative path oluştur
  if (element === document.body) {
    return '//body';
  }
  
  if (element === document.documentElement) {
    return '//html';
  }
  
  let path = '';
  current = element;
  
  while (current && current.nodeType === Node.ELEMENT_NODE) {
    let selector = current.nodeName.toLowerCase();
    
    // Aynı tag name'e sahip kardeşlerin sayısını bul
    let sibling = current;
    let nth = 1;
    let sameTagSiblings = 1; // Aynı tag name'e sahip toplam kardeş sayısı
    
    // Önceki kardeşleri say
    while (sibling.previousElementSibling) {
      sibling = sibling.previousElementSibling;
      if (sibling.nodeName.toLowerCase() === selector) {
        nth++;
        sameTagSiblings++;
      }
    }
    
    // Sonraki kardeşleri say
    sibling = current;
    while (sibling.nextElementSibling) {
      sibling = sibling.nextElementSibling;
      if (sibling.nodeName.toLowerCase() === selector) {
        sameTagSiblings++;
      }
    }
    
    // Sadece aynı tag name'e sahip birden fazla kardeş varsa index ekle (Chrome gibi)
    if (sameTagSiblings > 1) {
      selector += `[${nth}]`;
    }
    
    path = '/' + selector + path;
    
    current = current.parentElement;
    
    // ID'li bir parent bulursak, //*[@id="..."] formatında başla
    if (current && current.id) {
      path = `//*[@id="${current.id}"]` + path;
      break;
    }
    
    // Body veya html'e ulaşırsak dur
    if (!current || current === document.body) {
      path = '//body' + path;
      break;
    }
    
    if (current === document.documentElement) {
      path = '//html' + path;
      break;
    }
  }
  
  // Eğer path // ile başlamıyorsa ekle
  if (!path.startsWith('//')) {
    path = '//body' + path;
  }
  
  return path;
}


// XPath ile element bul
function findElementByXPath(xpath) {
  try {
    // XPath'i temizle ve normalize et
    xpath = xpath.trim();
    
    // Escape edilmiş slash'ları düzelt (\\/ -> /)
    xpath = xpath.replace(/\\\//g, '/');
    
    // Context node belirleme
    let contextNode = document;
    
    // // ile başlayan XPath'ler için document'i context olarak kullan
    if (xpath.startsWith('//')) {
      contextNode = document;
    } 
    // / ile başlayan absolute XPath'ler için documentElement'i context olarak kullan
    else if (xpath.startsWith('/')) {
      contextNode = document.documentElement;
      
      // Eğer /html ile başlamıyorsa, /html/body ekle (eski format için)
      if (!xpath.startsWith('/html')) {
        xpath = '/html/body' + xpath;
      }
    }
    
    console.log(`[XPath] Aranıyor: ${xpath}, Context: ${contextNode === document ? 'document' : 'documentElement'}`);
    
    const result = document.evaluate(
      xpath,
      contextNode,
      null,
      XPathResult.FIRST_ORDERED_NODE_TYPE,
      null
    );
    
    let node = result.singleNodeValue;
    
    // Eğer bulunamadıysa ve // ile başlamıyorsa, // ile tekrar dene
    if (!node && !xpath.startsWith('//')) {
      const altXPath = xpath.replace(/^\/html\/body/, '//body').replace(/^\/html/, '//html');
      if (altXPath !== xpath) {
        console.log(`[XPath] Alternatif deneme: ${altXPath}`);
        const altResult = document.evaluate(
          altXPath,
          document,
          null,
          XPathResult.FIRST_ORDERED_NODE_TYPE,
          null
        );
        node = altResult.singleNodeValue;
      }
    }
    
    if (!node) {
      console.warn(`[XPath] Sonuç bulunamadı: ${xpath}`);
    } else {
      console.log(`[XPath] Element bulundu:`, node, `Text: ${node.textContent?.trim()}`);
    }
    
    return node;
  } catch (error) {
    console.error(`[XPath] Hata (${xpath}):`, error);
    return null;
  }
}

// Selector test fonksiyonu
async function testSelector(selector, selectorType, modules = []) {
  try {
    let element = null;
    let count = 0;
    
    if (selectorType === 'xpath' || isXPath(selector)) {
      // XPath kullan (findElementByXPath fonksiyonu otomatik düzeltme yapıyor)
      element = findElementByXPath(selector);
      if (element) {
        // Count için snapshot al
        let testXpath = selector.trim();
        if (testXpath.startsWith('/') && !testXpath.startsWith('//') && !testXpath.startsWith('/html')) {
          testXpath = '/html/body' + testXpath;
        }
        const contextNode = testXpath.startsWith('/html') || (testXpath.startsWith('/') && !testXpath.startsWith('//')) 
          ? document.documentElement 
          : document;
        const countResult = document.evaluate(
          testXpath,
          contextNode,
          null,
          XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
          null
        );
        count = countResult.snapshotLength;
      } else {
        count = 0;
      }
    } else {
      // CSS selector kullan
      try {
        const elements = document.querySelectorAll(selector);
        count = elements.length;
        if (count > 0) {
          element = elements[0];
        }
      } catch (selectorError) {
        console.error('Selector hatası:', selectorError, 'Selector:', selector);
        // Eğer selector hatalıysa, alternatif denemeler yap
        // Örneğin :disabled eklenmişse kaldırmayı dene
        if (selector.includes(':disabled') || selector.includes('[disabled]')) {
          const altSelector = selector.replace(/:disabled/g, '').replace(/\[disabled\]/g, '');
          try {
            const altElements = document.querySelectorAll(altSelector);
            if (altElements.length > 0) {
              // Disabled olanları filtrele
              const disabledElements = Array.from(altElements).filter(el => el.disabled || el.hasAttribute('disabled'));
              if (disabledElements.length > 0) {
                element = disabledElements[0];
                count = disabledElements.length;
              }
            }
          } catch (e) {
            // Alternatif de çalışmadı
          }
        }
      }
    }
    
    if (!element) {
      // Daha detaylı hata mesajı için console'a yaz
      console.warn('Öğe bulunamadı. Selector:', selector, 'Type:', selectorType);
      
      // Eğer ifTrue veya ifFalse modülü varsa, uygun değeri döndür
      if (modules && Array.isArray(modules)) {
        if (modules.includes('ifTrue')) {
          return { success: true, count: 0, value: false, error: null };
        }
        if (modules.includes('ifFalse')) {
          return { success: true, count: 0, value: true, error: null };
        }
      }
      
      return { success: false, count: 0, error: 'Öğe bulunamadı' };
    }
    
    let rawValue = element.textContent?.trim() || '';
    if (!rawValue) {
      rawValue = element.innerHTML?.trim() || element.value || element.getAttribute('value') || '';
    }
    if (!rawValue) {
      rawValue = element.innerText?.trim() || '';
    }
    
    // Modülleri uygula (eğer varsa)
    let processedValue = rawValue;
    if (modules && Array.isArray(modules) && modules.length > 0) {
      processedValue = applyModules(rawValue, modules, selector, element);
      console.log(`[testSelector] Modül sonrası değer:`, processedValue);
    }
    
    // Element'in style.display değerini al (checkDisplayNone modülü için)
    // Boş string veya undefined ise boş string olarak geç (style="" durumu için)
    const elementStyleDisplay = element.style.display !== undefined ? element.style.display : '';
    
    // Element'in disabled durumunu al (disabled modülü için)
    const elementDisabled = element.disabled || element.hasAttribute('disabled');
    
    return {
      success: true,
      count: count,
      value: processedValue,
      rawValue: rawValue, // Ham değeri de döndür (UI'da göstermek için)
      elementStyleDisplay: elementStyleDisplay, // checkDisplayNone modülü için
      elementDisabled: elementDisabled // disabled modülü için
    };
  } catch (error) {
    console.error('Test hatası:', error);
    return { success: false, error: error.message };
  }
}

// XPath mi kontrol et
function isXPath(selector) {
  if (!selector || typeof selector !== 'string') return false;
  // XPath belirteçleri: / ile başlayan, // ile başlayan, veya XPath fonksiyonları içeren
  return selector.startsWith('/') || 
         selector.startsWith('//') || 
         selector.includes('[@') ||
         selector.includes('/@') ||
         selector.includes('::');
}

// Modül fonksiyonları (contentScript için)
const moduleFunctions = {
  parseTL: function(value) {
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
  },
  
  ifTrue: function(value) {
    if (!value || value === null || value === undefined || value === '') {
      return false;
    }
    const str = String(value).trim();
    return str.length > 0;
  },
  
  ifFalse: function(value) {
    if (!value || value === null || value === undefined || value === '') {
      return true;
    }
    const str = String(value).trim();
    return str.length === 0;
  },
  
  trim: function(value) {
    return String(value || '').trim();
  },
  
  removeHTML: function(value) {
    const div = document.createElement('div');
    div.innerHTML = String(value || '');
    return div.textContent || div.innerText || '';
  },
  
  normalizeWhitespace: function(value) {
    return String(value || '').replace(/\s+/g, ' ').trim();
  },
  
  extractNumber: function(value) {
    const numbers = String(value || '').match(/\d+\.?\d*/g);
    return numbers ? numbers.join('') : '';
  },
  
  parseUSD: function(value) {
    if (!value || typeof value !== 'string') return value;
    const parsed = parseFloat(value.replace(/[$,\s]/g, '').replace(',', '.'));
    return isNaN(parsed) ? value : parsed.toFixed(2);
  },
  
  parseEUR: function(value) {
    if (!value || typeof value !== 'string') return value;
    const parsed = parseFloat(value.replace(/[€,\s.]/g, '').replace(',', '.'));
    return isNaN(parsed) ? value : parsed.toFixed(2);
  },
  
  parseInternationalPrice: function(value) {
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
  },
  
  toLowerCase: function(value) {
    return String(value || '').toLowerCase();
  },
  
  toUpperCase: function(value) {
    return String(value || '').toUpperCase();
  },
  
  removeSpecialChars: function(value) {
    return String(value || '').replace(/[^a-zA-Z0-9\s]/g, '');
  },
  
  extractURL: function(value) {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const matches = String(value || '').match(urlRegex);
    return matches ? matches[0] : '';
  },
  
  extractEmail: function(value) {
    const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
    const matches = String(value || '').match(emailRegex);
    return matches ? matches[0] : '';
  },
  
  extractFirstWord: function(value) {
    const words = String(value || '').trim().split(/\s+/);
    return words[0] || '';
  },
  
  extractLastWord: function(value) {
    const words = String(value || '').trim().split(/\s+/);
    return words.length > 0 ? words[words.length - 1] : '';
  },
  
  defaultValue: function(value, defaultValue = 'N/A') {
    if (!value || value === null || value === undefined || String(value).trim() === '') {
      return defaultValue;
    }
    return value;
  },
  
  formatDate: function(value) {
    if (!value) return '';
    const date = new Date(value);
    if (isNaN(date.getTime())) return value;
    return date.toISOString().split('T')[0];
  },
  
  split: function(value, separator = ',', index = 0) {
    const parts = String(value || '').split(separator);
    return parts[index] ? parts[index].trim() : '';
  },
  
  slice: function(value, start = 0, end = null) {
    const str = String(value || '');
    return end !== null ? str.slice(start, end) : str.slice(start);
  },
  
  checkDisplayNone: function(value, selector = null, element = null) {
    try {
      let el = null;
      
      // Eğer element direkt geçilmişse kullan
      if (element && element.nodeType) {
        el = element;
      }
      // Eğer selector geçilmişse element'i bul
      else if (selector) {
        el = document.querySelector(selector);
      }
      
      // Element bulunamazsa null döndür (scraped_data'ya eklenmeyecek)
      if (!el) {
        console.warn('checkDisplayNone: Element bulunamadı', { selector, element: !!element });
        return null;
      }
      
      // Sadece inline style'ı kontrol et (style="display: none;")
      // Boş string ('') geçerli bir değerdir (style="" durumu)
      const display = el.style.display !== undefined ? el.style.display : '';
      
      // style="display: none;" varsa false, yoksa true döndür
      // Boş string ('') veya undefined ise true döndür (style="" veya style yok)
      const result = display !== 'none';
      console.log('checkDisplayNone sonucu:', { display, result, selector });
      return result;
    } catch (error) {
      console.error('checkDisplayNone hatası:', error);
      return null; // Hata durumunda null döndür (scraped_data'ya eklenmeyecek)
    }
  },
  
  disabled: function(value, selector = null, element = null) {
    try {
      let el = null;
      
      // Eğer element direkt geçilmişse kullan
      if (element && element.nodeType) {
        el = element;
      }
      // Eğer selector geçilmişse element'i bul
      else if (selector) {
        el = document.querySelector(selector);
      }
      
      // Element bulunamazsa null döndür (scraped_data'ya eklenmeyecek)
      if (!el) {
        console.warn('disabled: Element bulunamadı', { selector, element: !!element });
        return null;
      }
      
      // disabled attribute'unu kontrol et
      const isDisabled = el.disabled || el.hasAttribute('disabled');
      
      // disabled attribute'u varsa false, yoksa true döndür
      const result = !isDisabled;
      console.log('disabled sonucu:', { isDisabled, result, selector });
      return result;
    } catch (error) {
      console.error('disabled hatası:', error);
      return null; // Hata durumunda null döndür (scraped_data'ya eklenmeyecek)
    }
  },
  
  checkStockOut: function(value) {
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
        'out of stock',
        'unavailable',
        'not available',
        'sold out',
        'stokta yok',
        'stok bitti',
        'stokta bulunmuyor'
      ];
      
      // Metinde stok bitti kelimelerinden biri var mı kontrol et
      const hasStockOutKeyword = stockOutKeywords.some(keyword => lowerValue.includes(keyword));
      
      // Eğer stok bitti kelimesi varsa false, yoksa true döndür
      const result = !hasStockOutKeyword;
      console.log('checkStockOut sonucu:', { value, hasStockOutKeyword, result });
      return result;
    } catch (error) {
      console.error('checkStockOut hatası:', error);
      // Hata durumunda true döndür (stok var gibi davran)
      return true;
    }
  },
  
  checkURLMatch: function(value) {
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
  },
  
  checkAddToCart: function(value) {
    try {
      if (!value || typeof value !== 'string') {
        // Değer yoksa veya string değilse null döndür
        return null;
      }
      
      // Metni normalize et (küçük harfe çevir, boşlukları temizle)
      const normalizedValue = String(value).toLowerCase().trim();
      
      // "Sepete Ekle" kontrolü
      const addToCartKeywords = [
        'sepete ekle',
        'sepeteekle',
        'sepet ekle',
        'add to cart',
        'addtocart',
        'add to basket',
        'sepet'
      ];
      
      // "Stoktaki Mağazalar" kontrolü
      const stockStoresKeywords = [
        'stoktaki mağazalar',
        'stoktakimağazalar',
        'stoktaki mağaza',
        'stoktakimağaza',
        'stok mağazalar',
        'stokmağazalar',
        'stoktaki',
        'mağazalar'
      ];
      
      // "Benzer Ürünleri Gör" kontrolü
      const similarProductsKeywords = [
        'benzer ürünleri gör',
        'benzerürünlerigör',
        'benzer ürünleri',
        'benzerürünleri',
        'benzer ürünler',
        'benzerürünler',
        'benzer ürün',
        'benzerürün',
        'similar products',
        'similarproducts',
        'view similar',
        'viewsimilar'
      ];
      
      // "Sepete Ekle" içeriyor mu kontrol et
      const hasAddToCart = addToCartKeywords.some(keyword => normalizedValue.includes(keyword.toLowerCase()));
      
      // "Stoktaki Mağazalar" içeriyor mu kontrol et
      const hasStockStores = stockStoresKeywords.some(keyword => normalizedValue.includes(keyword.toLowerCase()));
      
      // "Benzer Ürünleri Gör" içeriyor mu kontrol et
      const hasSimilarProducts = similarProductsKeywords.some(keyword => normalizedValue.includes(keyword.toLowerCase()));
      
      // "Sepete Ekle" varsa true döndür
      if (hasAddToCart) {
        console.log('checkAddToCart sonucu:', { value, result: true, reason: 'Sepete Ekle bulundu' });
        return true;
      }
      
      // "Stoktaki Mağazalar" varsa false döndür
      if (hasStockStores) {
        console.log('checkAddToCart sonucu:', { value, result: false, reason: 'Stoktaki Mağazalar bulundu' });
        return false;
      }
      
      // "Benzer Ürünleri Gör" varsa false döndür
      if (hasSimilarProducts) {
        console.log('checkAddToCart sonucu:', { value, result: false, reason: 'Benzer Ürünleri Gör bulundu' });
        return false;
      }
      
      // Hiçbiri yoksa null döndür (belirsiz durum)
      console.log('checkAddToCart sonucu:', { value, result: null, reason: 'Ne Sepete Ekle ne de Stoktaki Mağazalar/Benzer Ürünleri Gör bulunamadı' });
      return null;
    } catch (error) {
      console.error('checkAddToCart hatası:', error);
      // Hata durumunda null döndür
      return null;
    }
  }
};

// Modül uygulama fonksiyonu (pipeline)
function applyModules(value, moduleNames, selector = null, element = null) {
  if (!moduleNames || !Array.isArray(moduleNames) || moduleNames.length === 0) {
    return value;
  }
  
  let processedValue = value;
  
  for (const moduleName of moduleNames) {
    if (moduleFunctions[moduleName] && typeof moduleFunctions[moduleName] === 'function') {
      try {
        // checkDisplayNone modülü için selector ve element bilgisini geç
        if (moduleName === 'checkDisplayNone') {
          console.log('checkDisplayNone modülü çağrılıyor:', { value, selector, element: !!element });
          processedValue = moduleFunctions[moduleName](processedValue, selector, element);
          console.log('checkDisplayNone modülü sonucu:', processedValue);
        }
        // disabled modülü için selector ve element bilgisini geç
        else if (moduleName === 'disabled') {
          console.log('disabled modülü çağrılıyor:', { value, selector, element: !!element });
          processedValue = moduleFunctions[moduleName](processedValue, selector, element);
          console.log('disabled modülü sonucu:', processedValue);
        } else {
          processedValue = moduleFunctions[moduleName](processedValue);
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

// Element görünür mü kontrol et
function isElementVisible(element) {
  if (!element) return false;
  
  const style = window.getComputedStyle(element);
  if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
    return false;
  }
  
  const rect = element.getBoundingClientRect();
  if (rect.width === 0 && rect.height === 0) {
    return false;
  }
  
  return true;
}

// Element görünür olana kadar bekle (dinamik içerik için)
function waitForElement(selector, selectorType, maxWait = 3000, retryInterval = 500) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    let observer = null;
    
    const checkElement = () => {
      let element = null;
      
      if (selectorType === 'xpath' || isXPath(selector)) {
        element = findElementByXPath(selector);
      } else {
        const elements = document.querySelectorAll(selector);
        if (elements.length > 0) {
          element = elements[0];
        }
      }
      
      // Element bulundu mu kontrol et (görünürlük kontrolünü kaldırdık - bazı elementler görünür olmayabilir ama veri içerebilir)
      if (element) {
        // Element DOM'da varsa, başarılı say (içerik kontrolü yapmıyoruz - boş elementler de geçerli olabilir)
        if (observer) {
          observer.disconnect();
        }
        const hasContent = element.textContent?.trim() || element.innerHTML?.trim() || element.value || element.getAttribute('value');
        console.log(`[waitForElement] Element bulundu: ${selector}, İçerik: ${hasContent ? 'Var' : 'Yok'}`);
        resolve(element);
        return;
      }
      
      // Zaman aşımı kontrolü
      if (Date.now() - startTime >= maxWait) {
        if (observer) {
          observer.disconnect();
        }
        console.warn(`[waitForElement] Zaman aşımı: ${selector} (${selectorType})`);
        reject(new Error(`Element bulunamadı: ${selector}`));
        return;
      }
      
      // Tekrar dene
      setTimeout(checkElement, retryInterval);
    };
    
    // İlk kontrol
    checkElement();
    
    // MutationObserver ile DOM değişikliklerini izle (daha hızlı tepki için)
    if (document.body) {
      observer = new MutationObserver(() => {
        checkElement();
      });
      
      observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class', 'style', 'id']
      });
      
      // Zaman aşımında observer'ı temizle
      setTimeout(() => {
        if (observer) {
          observer.disconnect();
        }
      }, maxWait);
    }
  });
}

// Veri toplama fonksiyonu (güncellenmiş - retry ve bekleme ile)
async function collectData(selectors) {
  const data = {};
  const errors = []; // Hata detaylarını topla
  
  // Gurgencler.com.tr için modüller uygulanmadan önce 5 saniye ekstra bekleme
  const currentUrl = window.location.href;
  if (currentUrl.includes('gurgencler.com.tr')) {
    console.log(`[collectData] Gurgencler.com.tr tespit edildi. Modüller uygulanmadan önce 5 saniye bekleniyor...`);
    await new Promise(resolve => setTimeout(resolve, 5000));
    console.log(`[collectData] 5 saniyelik bekleme tamamlandı, veri toplama başlıyor.`);
  }
  
  console.log(`[collectData] Toplam ${selectors.length} selector işlenecek`);
  
  for (const item of selectors) {
    try {
      console.log(`[collectData] İşleniyor: ${item.label} - Selector: ${item.selector} - Type: ${item.selector_type || 'class'}`);
      
      let element = null;
      
      // Element'i bulana kadar bekle (maksimum 3 saniye, 500ms aralıklarla)
      // ifTrue/ifFalse modülü varsa, element bulunamadığında hemen false/true döndür
      const hasIfTrueModule = item.modules && Array.isArray(item.modules) && item.modules.includes('ifTrue');
      const hasIfFalseModule = item.modules && Array.isArray(item.modules) && item.modules.includes('ifFalse');
      
      // Stock kontrolü kontrolü (attributes_id: 23)
      const isStockCheck = item.attributes_id === 23;
      
      try {
        element = await waitForElement(item.selector, item.selector_type || 'class', 3000, 500);
        console.log(`[collectData] Element bulundu: ${item.label}`, element);
      } catch (error) {
        const errorMessage = error.message || 'Bilinmeyen hata';
        const selectorType = item.selector_type || 'class';
        const isXPathSelector = selectorType === 'xpath' || isXPath(item.selector);
        
        // Detaylı hata mesajı oluştur
        let detailedError = '';
        if (errorMessage.includes('timeout') || errorMessage.includes('Zaman aşımı')) {
          detailedError = `[waitForElement] Zaman aşımı: ${item.selector} (${selectorType})`;
        } else if (isXPathSelector) {
          detailedError = `[XPath] Sonuç bulunamadı: ${item.selector}`;
        } else {
          detailedError = `[collectData] Öğe bulunamadı (timeout): ${item.label} - Selector: ${item.selector}`;
        }
        
        console.warn(detailedError);
        
        // Hata detayını ekle
        errors.push({
          label: item.label,
          selector: item.selector,
          selector_type: selectorType,
          error: detailedError,
          error_type: 'timeout'
        });
        
        // Eğer ifTrue modülü varsa, false döndür (boolean olarak)
        if (hasIfTrueModule) {
          data[item.label] = false; // Boolean false
          console.log(`[collectData] ifTrue modülü için false döndürüldü (timeout/XPath): ${item.label}`, data[item.label]);
          
          // Eğer stock kontrolü ise ve false döndüyse, diğer selector'ları işleme
          if (isStockCheck && data[item.label] === false) {
            console.log(`[collectData] Stock kontrolü false döndü (${item.label}). Diğer selector'lar atlanıyor.`);
            break; // Döngüyü kır, diğer selector'ları işleme
          }
          
          continue; // ifTrue için false kaydedildi, devam et
        }
        // Eğer ifFalse modülü varsa, true döndür (boolean olarak)
        if (hasIfFalseModule) {
          data[item.label] = true; // Boolean true
          console.log(`[collectData] ifFalse modülü için true döndürüldü (timeout/XPath): ${item.label}`, data[item.label]);
          continue; // ifFalse için true kaydedildi, devam et
        }
        // checkDisplayNone modülü varsa, null döndür (eklenmeyecek)
        // Diğer durumlarda da null ekleme (scraped_data'ya eklenmeyecek)
        // Eğer stock kontrolü ise ve yanıt alınamadıysa, devam et (diğer kontroller yapılmalı)
        if (isStockCheck) {
          console.log(`[collectData] Stock kontrolü yanıt alınamadı (${item.label}). Diğer kontroller yapılacak.`);
        }
        continue;
      }
      
      if (!element) {
        const selectorType = item.selector_type || 'class';
        const isXPathSelector = selectorType === 'xpath' || isXPath(item.selector);
        
        let detailedError = '';
        if (isXPathSelector) {
          detailedError = `[XPath] Sonuç bulunamadı: ${item.selector}`;
        } else {
          detailedError = `[collectData] Öğe bulunamadı: ${item.label} - Selector: ${item.selector}`;
        }
        
        console.warn(detailedError);
        
        // Hata detayını ekle
        errors.push({
          label: item.label,
          selector: item.selector,
          selector_type: selectorType,
          error: detailedError,
          error_type: 'element_not_found'
        });
        
        // Eğer ifTrue modülü varsa, false döndür (boolean olarak)
        if (hasIfTrueModule) {
          data[item.label] = false; // Boolean false
          console.log(`[collectData] ifTrue modülü için false döndürüldü (element_not_found): ${item.label}`, data[item.label]);
          
          // Eğer stock kontrolü ise ve false döndüyse, diğer selector'ları işleme
          if (isStockCheck && data[item.label] === false) {
            console.log(`[collectData] Stock kontrolü false döndü (${item.label}). Diğer selector'lar atlanıyor.`);
            break; // Döngüyü kır, diğer selector'ları işleme
          }
          
          continue; // ifTrue için false kaydedildi, devam et
        }
        // Eğer ifFalse modülü varsa, true döndür (boolean olarak)
        if (hasIfFalseModule) {
          data[item.label] = true; // Boolean true
          console.log(`[collectData] ifFalse modülü için true döndürüldü (element_not_found): ${item.label}`, data[item.label]);
          continue; // ifFalse için true kaydedildi, devam et
        }
        // checkDisplayNone modülü varsa, null döndür (eklenmeyecek)
        // Diğer durumlarda da null ekleme (scraped_data'ya eklenmeyecek)
        // Eğer stock kontrolü ise ve yanıt alınamadıysa, devam et (diğer kontroller yapılmalı)
        if (isStockCheck) {
          console.log(`[collectData] Stock kontrolü yanıt alınamadı (${item.label}). Diğer kontroller yapılacak.`);
        }
        continue;
      }
      
      // Element'in içeriğinin yüklenmesini bekle (eğer boşsa)
      let value = element.textContent?.trim() || '';
      
      console.log(`[collectData] İlk textContent değeri (${item.label}):`, value);
      
      // Eğer value boşsa, biraz bekle ve tekrar dene (dinamik içerik için)
      if (!value) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        value = element.textContent?.trim() || '';
        console.log(`[collectData] İkinci textContent değeri (${item.label}):`, value);
      }
      
      // Eğer hala boşsa, innerHTML veya value attribute'unu dene
      if (!value) {
        value = element.innerHTML?.trim() || element.value || element.getAttribute('value') || '';
        console.log(`[collectData] innerHTML/value değeri (${item.label}):`, value);
      }
      
      // Eğer hala boşsa, innerText'i dene
      if (!value) {
        value = element.innerText?.trim() || '';
        console.log(`[collectData] innerText değeri (${item.label}):`, value);
      }
      
      console.log(`[collectData] Modül öncesi değer (${item.label}):`, value, `Type: ${typeof value}`);
      
      // Modülleri uygula (eğer varsa)
      if (item.modules && Array.isArray(item.modules) && item.modules.length > 0) {
        value = applyModules(value, item.modules, item.selector, element);
        console.log(`[collectData] Modül sonrası değer (${item.label}):`, value, `Type: ${typeof value}`);
        
        // ifTrue veya ifFalse modülü boolean döndürüyor, bu değerleri koru
        if (item.modules.includes('ifTrue') || item.modules.includes('ifFalse')) {
          // Boolean değeri koru (string'e çevirme)
          if (typeof value === 'boolean') {
            data[item.label] = value;
            console.log(`[collectData] Boolean değer eklendi (${item.label}):`, value);
            
            // Eğer stock kontrolü ise ve false döndüyse, diğer selector'ları işleme
            if (isStockCheck && value === false) {
              console.log(`[collectData] Stock kontrolü false döndü (${item.label}). Diğer selector'lar atlanıyor.`);
              break; // Döngüyü kır, diğer selector'ları işleme
            }
            
            continue; // Bu değer kaydedildi, devam et
          }
        }
      }
      
      // Null değerleri ekleme (scraped_data'ya eklenmeyecek)
      if (value !== null && value !== undefined) {
        data[item.label] = value;
        console.log(`[collectData] Veri eklendi (${item.label}):`, value, `Type: ${typeof value}`);
        
        // Eğer stock kontrolü ise ve false döndüyse, diğer selector'ları işleme
        // (ifTrue modülü olmadan da false değeri dönebilir)
        if (isStockCheck && value === false) {
          console.log(`[collectData] Stock kontrolü false döndü (${item.label}). Diğer selector'lar atlanıyor.`);
          break; // Döngüyü kır, diğer selector'ları işleme
        }
      } else {
        console.warn(`[collectData] Veri null/undefined, eklenmedi (${item.label})`);
        // Null/undefined değerler için de hata kaydı ekle
        errors.push({
          label: item.label,
          selector: item.selector,
          selector_type: item.selector_type || 'class',
          error: `[collectData] Veri null/undefined, eklenmedi (${item.label})`,
          error_type: 'null_value'
        });
        
        // Eğer stock kontrolü ise ve null/undefined döndüyse, devam et (yanıt alınamadı, diğer kontroller yapılmalı)
        if (isStockCheck) {
          console.log(`[collectData] Stock kontrolü yanıt alınamadı (${item.label}). Diğer kontroller yapılacak.`);
          // Devam et, diğer selector'ları işle
        }
      }
    } catch (error) {
      const errorMessage = error.message || 'Bilinmeyen hata';
      console.error(`Selector hatası (${item.label} - ${item.selector}):`, error);
      
      // Hata detayını ekle
      errors.push({
        label: item.label,
        selector: item.selector,
        selector_type: item.selector_type || 'class',
        error: `[collectData] Selector hatası: ${errorMessage}`,
        error_type: 'selector_error'
      });
      
      // Eğer ifTrue modülü varsa, false döndür (element bulunamadığı için - boolean olarak)
      if (hasIfTrueModule) {
        data[item.label] = false; // Boolean false
        console.log(`[collectData] ifTrue modülü için false döndürüldü (hata durumu): ${item.label}`, data[item.label]);
        
        // Eğer stock kontrolü ise ve false döndüyse, diğer selector'ları işleme
        if (isStockCheck && data[item.label] === false) {
          console.log(`[collectData] Stock kontrolü false döndü (${item.label}). Diğer selector'lar atlanıyor.`);
          break; // Döngüyü kır, diğer selector'ları işleme
        }
      }
      // Eğer ifFalse modülü varsa, true döndür (veri yoksa true - boolean olarak)
      if (hasIfFalseModule) {
        data[item.label] = true; // Boolean true
        console.log(`[collectData] ifFalse modülü için true döndürüldü (hata durumu): ${item.label}`, data[item.label]);
      }
    }
  }
  
  // Hata detaylarını response'a ekle
  const response = { data };
  if (errors.length > 0) {
    response.errors = errors;
  }
  
  return response;
}


