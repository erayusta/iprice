// DOM yüklendiğinde çalış
document.addEventListener('DOMContentLoaded', () => {
  // Tab yönetimi
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tabName = btn.dataset.tab;
      
      // Tüm tab butonlarını ve içeriklerini deaktif et
      document.querySelectorAll('.tab-btn').forEach(b => {
        b.classList.remove('active', 'border-gray-900', 'text-gray-900');
        b.classList.add('text-gray-600');
      });
      document.querySelectorAll('.tab-content').forEach(c => {
        c.classList.add('hidden');
        c.classList.remove('active');
      });
      
      // Seçilen tab'ı aktif et
      btn.classList.add('active', 'border-gray-900', 'text-gray-900');
      btn.classList.remove('text-gray-600');
      document.getElementById(`${tabName}-tab`).classList.remove('hidden');
      document.getElementById(`${tabName}-tab`).classList.add('active');
      
      // Tab'a göre verileri yükle
      if (tabName === 'selectors') {
        loadSelectors();
      } else if (tabName === 'results') {
        loadResults();
      } else if (tabName === 'labels') {
        loadLabels();
      } else if (tabName === 'settings') {
        loadSettings();
      }
    });
  });

  // Öğe Seçme Modu
  let pickerActive = false;
  const startPickerBtn = document.getElementById('start-picker');
  const stopPickerBtn = document.getElementById('stop-picker');
  const pickerStatus = document.getElementById('picker-status');
  const selectedElementInfo = document.getElementById('selected-element-info');

  startPickerBtn.addEventListener('click', async () => {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (!tab) {
        showStatus(pickerStatus, 'Aktif bir sekme bulunamadı.', 'error');
        return;
      }

      // Content script'e öğe seçme modunu başlat mesajı gönder
      chrome.tabs.sendMessage(tab.id, { action: 'startPicker' }, (response) => {
        if (chrome.runtime.lastError) {
          showStatus(pickerStatus, 'Sayfa yüklenene kadar bekleyin veya sayfayı yenileyin.', 'error');
          return;
        }
        
        pickerActive = true;
        startPickerBtn.classList.add('hidden');
        stopPickerBtn.classList.remove('hidden');
        showStatus(pickerStatus, 'Öğe seçme modu aktif. Sayfada bir öğeye tıklayın.', 'info');
      });
    } catch (error) {
      showStatus(pickerStatus, 'Hata: ' + error.message, 'error');
    }
  });

  stopPickerBtn.addEventListener('click', async () => {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab) {
        chrome.tabs.sendMessage(tab.id, { action: 'stopPicker' });
      }
      
      pickerActive = false;
      startPickerBtn.classList.remove('hidden');
      stopPickerBtn.classList.add('hidden');
      selectedElementInfo.classList.add('hidden');
      pickerStatus.textContent = '';
      pickerStatus.className = 'status-message hidden';
    } catch (error) {
      console.error('Picker durdurma hatası:', error);
    }
  });

  // Seçilen öğe bilgileri
  let currentElementsData = null;
  let currentSelectedIndex = 0;
  let selectedModules = []; // Seçilen modüller listesi

  // Öğe seviyesi seçildiğinde güncelle
  function updateElementDisplay(index) {
    if (!currentElementsData || !currentElementsData.elements || !currentElementsData.elements[index]) {
      return;
    }
    
    const element = currentElementsData.elements[index];
    currentSelectedIndex = index;
    
    // Selector'ı güncelle
    const selectorType = document.querySelector('input[name="selector-type"]:checked').value;
    document.getElementById('element-selector').value = selectorType === 'xpath' 
      ? element.xpathSelector 
      : element.classSelector;
    
    // Öğe içeriğini göster
    const previewElement = document.getElementById('element-preview');
    if (element.content) {
      previewElement.textContent = element.content;
      previewElement.classList.remove('empty');
    } else {
      previewElement.textContent = '(İçerik bulunamadı)';
      previewElement.classList.add('empty');
    }
  }

  // Content script'ten gelen öğe seçim mesajlarını dinle
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'elementSelected') {
      const data = message.element;
      currentElementsData = data;
      currentSelectedIndex = data.selectedIndex || 0;
      
      // Domain'i göster
      document.getElementById('element-domain').value = data.domain;
      document.getElementById('element-label').value = '';
      document.getElementById('element-note').value = '';
      document.getElementById('selector-type-class').checked = true;
      document.getElementById('selector-type-xpath').checked = false;
      updateSelectorTypeUI('class');
      
      // Modülleri temizle
      selectedModules = [];
      updateSelectedModulesList();
      
      // Etiket dropdown'unu doldur
      loadLabelsIntoSelect();
      
      // Modül dropdown'unu doldur
      loadModulesIntoSelect();
      
      // Öğe seviyesi dropdown'unu doldur
      const levelSelect = document.getElementById('element-level-select');
      levelSelect.innerHTML = '';
      
      if (data.elements && data.elements.length > 0) {
        data.elements.forEach((el, index) => {
          const option = document.createElement('option');
          option.value = index;
          
          // Selector'ı göster
          let label = el.classSelector || el.xpathSelector || 'selector';
          
          // Parent sayısını göster
          if (el.parentCount > 0) {
            label = `[${el.parentCount} parent] ${label}`;
          } else {
            label = `[direkt] ${label}`;
          }
          
          // İçerik önizlemesi ekle
          const contentPreview = el.content ? ` - ${el.content.substring(0, 25)}` : '';
          option.textContent = label + contentPreview;
          option.value = index;
          
          if (index === currentSelectedIndex) {
            option.selected = true;
          }
          
          levelSelect.appendChild(option);
        });
      }
      
      // İlk öğeyi göster
      updateElementDisplay(currentSelectedIndex);
      
      selectedElementInfo.classList.remove('hidden');
      
      // Test sonucunu temizle
      const testResult = document.getElementById('test-result');
      testResult.classList.add('hidden');
      testResult.className = 'test-result';
      
      // Öğe seçme modunu durdur
      pickerActive = false;
      startPickerBtn.classList.remove('hidden');
      stopPickerBtn.classList.add('hidden');
    }
  });

  // Öğe seviyesi değiştiğinde
  document.getElementById('element-level-select').addEventListener('change', (e) => {
    const index = parseInt(e.target.value);
    if (!isNaN(index) && currentElementsData && currentElementsData.elements) {
      updateElementDisplay(index);
    }
  });

  // Selector tipi değiştiğinde selector'ı güncelle
  document.getElementById('selector-type-class').addEventListener('change', () => {
    if (currentElementsData && currentElementsData.elements && currentElementsData.elements[currentSelectedIndex]) {
      const element = currentElementsData.elements[currentSelectedIndex];
      document.getElementById('element-selector').value = element.classSelector || '';
      updateSelectorTypeUI('class');
    }
  });

  document.getElementById('selector-type-xpath').addEventListener('change', () => {
    if (currentElementsData && currentElementsData.elements && currentElementsData.elements[currentSelectedIndex]) {
      const element = currentElementsData.elements[currentSelectedIndex];
      document.getElementById('element-selector').value = element.xpathSelector || '';
      updateSelectorTypeUI('xpath');
    }
  });

  // Selector type UI güncelleme
  function updateSelectorTypeUI(type) {
    document.querySelectorAll('.selector-type-option').forEach(opt => {
      opt.classList.remove('bg-white', 'border-gray-900');
      opt.classList.add('border-transparent');
    });
    const selectedOption = document.querySelector(`.selector-type-option[data-type="${type}"]`);
    if (selectedOption) {
      selectedOption.classList.add('bg-white', 'border-gray-900');
      selectedOption.classList.remove('border-transparent');
    }
  }

  // Copy selector button
  document.getElementById('copy-selector').addEventListener('click', () => {
    const selector = document.getElementById('element-selector');
    selector.select();
    document.execCommand('copy');
    
    const btn = document.getElementById('copy-selector');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg><span>Kopyalandı!</span>';
    btn.classList.add('text-green-600');
    
    setTimeout(() => {
      btn.innerHTML = originalText;
      btn.classList.remove('text-green-600');
    }, 2000);
  });

  // Test butonu
  document.getElementById('test-selector').addEventListener('click', async () => {
    const selector = document.getElementById('element-selector').value.trim();
    const selectorType = document.querySelector('input[name="selector-type"]:checked').value;
    const testResult = document.getElementById('test-result');
    
    if (!selector) {
        testResult.classList.remove('hidden');
        testResult.className = 'test-result';
        testResult.innerHTML = `
          <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); border-radius: 12px; padding: 20px; color: white; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <div style="display: flex; align-items: center; gap: 12px;">
              <div style="width: 48px; height: 48px; background: rgba(255, 255, 255, 0.2); border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                <svg style="width: 24px; height: 24px; color: white;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
              </div>
              <div style="flex: 1;">
                <h4 style="font-size: 18px; font-weight: 700; margin: 0 0 4px 0; color: white;">Uyarı</h4>
                <p style="font-size: 13px; margin: 0; color: rgba(255, 255, 255, 0.9);">Lütfen önce bir öğe seçin.</p>
              </div>
            </div>
          </div>
        `;
      return;
    }
    
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (!tab) {
        testResult.classList.remove('hidden');
        testResult.className = 'test-result';
        testResult.innerHTML = `
          <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); border-radius: 12px; padding: 20px; color: white; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <div style="display: flex; align-items: center; gap: 12px;">
              <div style="width: 48px; height: 48px; background: rgba(255, 255, 255, 0.2); border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                <svg style="width: 24px; height: 24px; color: white;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </div>
              <div style="flex: 1;">
                <h4 style="font-size: 18px; font-weight: 700; margin: 0 0 4px 0; color: white;">Hata</h4>
                <p style="font-size: 13px; margin: 0; color: rgba(255, 255, 255, 0.9);">Aktif bir sekme bulunamadı.</p>
              </div>
            </div>
          </div>
        `;
        return;
      }
      
      // Content script'e test mesajı gönder
      chrome.tabs.sendMessage(tab.id, {
        action: 'testSelector',
        selector: selector,
        selectorType: selectorType
      }, (response) => {
        if (chrome.runtime.lastError) {
          testResult.classList.remove('hidden');
          testResult.className = 'test-result';
          testResult.innerHTML = `
            <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); border-radius: 12px; padding: 20px; color: white; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
              <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 48px; height: 48px; background: rgba(255, 255, 255, 0.2); border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                  <svg style="width: 24px; height: 24px; color: white;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </div>
                <div style="flex: 1;">
                  <h4 style="font-size: 18px; font-weight: 700; margin: 0 0 4px 0; color: white;">Hata</h4>
                  <p style="font-size: 13px; margin: 0; color: rgba(255, 255, 255, 0.9);">${chrome.runtime.lastError.message}</p>
                </div>
              </div>
            </div>
          `;
          return;
        }
        
        if (response && response.success) {
          const rawValue = response.value || '(boş)';
          const count = response.count || 0;
          
          // Modülleri uygula
          let processedValue = rawValue;
          let hasModules = selectedModules.length > 0;
          
          if (hasModules && typeof applyModules === 'function') {
            try {
              // checkDisplayNone modülü için selector ve elementStyleDisplay bilgisini geç
              // Boş string ('') geçerli bir değerdir (style="" durumu), undefined ise null geç
              const elementStyleDisplay = response.elementStyleDisplay !== undefined ? response.elementStyleDisplay : null;
              // disabled modülü için elementDisabled bilgisini geç
              const elementDisabled = response.elementDisabled !== undefined ? response.elementDisabled : null;
              processedValue = applyModules(rawValue, selectedModules, selector, null, elementStyleDisplay, elementDisabled);
            } catch (error) {
              console.error('Modül uygulama hatası:', error);
              processedValue = rawValue; // Hata durumunda ham değeri kullan
            }
          }
          
          // Escape HTML
          const escapeHtml = (text) => {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
          };
          
          const rawValueEscaped = escapeHtml(rawValue);
          const processedValueEscaped = escapeHtml(String(processedValue));
          
          testResult.classList.remove('hidden');
          testResult.className = 'test-result';
          testResult.innerHTML = `
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 12px; padding: 20px; color: white; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
              <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                <div style="width: 48px; height: 48px; background: rgba(255, 255, 255, 0.2); border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                  <svg style="width: 24px; height: 24px; color: white;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <div style="flex: 1;">
                  <h4 style="font-size: 18px; font-weight: 700; margin: 0 0 4px 0; color: white;">Test Başarılı!</h4>
                  <p style="font-size: 13px; margin: 0; color: rgba(255, 255, 255, 0.9);">Selector doğru çalışıyor</p>
                </div>
              </div>
              <div style="background: rgba(255, 255, 255, 0.15); border-radius: 8px; padding: 16px; margin-top: 16px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                  <div>
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: rgba(255, 255, 255, 0.8); margin-bottom: 6px; font-weight: 600;">Bulunan Öğe</div>
                    <div style="font-size: 24px; font-weight: 700; color: white;">${count}</div>
                  </div>
                  ${hasModules ? `
                  <div>
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: rgba(255, 255, 255, 0.8); margin-bottom: 6px; font-weight: 600;">Modül Sayısı</div>
                    <div style="font-size: 24px; font-weight: 700; color: white;">${selectedModules.length}</div>
                  </div>
                  ` : ''}
                </div>
                <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(255, 255, 255, 0.2);">
                  <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: rgba(255, 255, 255, 0.8); margin-bottom: 8px; font-weight: 600;">Ham Değer</div>
                  <div style="font-size: 12px; color: white; font-family: monospace; background: rgba(0, 0, 0, 0.2); padding: 8px; border-radius: 6px; word-break: break-all; max-height: 100px; overflow-y: auto;">${rawValueEscaped}</div>
                </div>
                ${hasModules ? `
                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255, 255, 255, 0.2);">
                  <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: rgba(255, 255, 255, 0.8); margin-bottom: 8px; font-weight: 600;">İşlenmiş Değer</div>
                  <div style="font-size: 12px; color: white; font-family: monospace; background: rgba(0, 0, 0, 0.3); padding: 8px; border-radius: 6px; word-break: break-all; max-height: 100px; overflow-y: auto; border: 1px solid rgba(255, 255, 255, 0.3);">${processedValueEscaped}</div>
                </div>
                ` : ''}
              </div>
            </div>
          `;
        } else {
          // Eğer ifTrue modülü seçiliyse, false döndür ve başarılı göster
          const hasIfTrueModule = selectedModules.includes('ifTrue');
          
          if (hasIfTrueModule && typeof applyModules === 'function') {
            // ifTrue modülünü uygula (null/undefined değerini false'a çevirir)
            let processedValue = false;
            try {
              processedValue = applyModules(null, selectedModules);
            } catch (error) {
              console.error('Modül uygulama hatası:', error);
              processedValue = false;
            }
            
            // Escape HTML
            const escapeHtml = (text) => {
              const div = document.createElement('div');
              div.textContent = text;
              return div.innerHTML;
            };
            
            const processedValueEscaped = escapeHtml(String(processedValue));
            
            testResult.classList.remove('hidden');
            testResult.className = 'test-result';
            testResult.innerHTML = `
              <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 12px; padding: 20px; color: white; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                  <div style="width: 48px; height: 48px; background: rgba(255, 255, 255, 0.2); border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                    <svg style="width: 24px; height: 24px; color: white;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                  </div>
                  <div style="flex: 1;">
                    <h4 style="font-size: 18px; font-weight: 700; margin: 0 0 4px 0; color: white;">Test Başarılı!</h4>
                    <p style="font-size: 13px; margin: 0; color: rgba(255, 255, 255, 0.9);">ifTrue modülü uygulandı: Öğe bulunamadığı için false döndürüldü</p>
                  </div>
                </div>
                <div style="background: rgba(255, 255, 255, 0.15); border-radius: 8px; padding: 16px; margin-top: 16px;">
                  <div style="margin-top: 12px;">
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: rgba(255, 255, 255, 0.8); margin-bottom: 8px; font-weight: 600;">İşlenmiş Değer</div>
                    <div style="font-size: 12px; color: white; font-family: monospace; background: rgba(0, 0, 0, 0.3); padding: 8px; border-radius: 6px; word-break: break-all; max-height: 100px; overflow-y: auto; border: 1px solid rgba(255, 255, 255, 0.3);">${processedValueEscaped}</div>
                  </div>
                </div>
              </div>
            `;
          } else {
            // ifTrue modülü yoksa, normal hata mesajını göster
            testResult.classList.remove('hidden');
            testResult.className = 'test-result';
            testResult.innerHTML = `
              <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); border-radius: 12px; padding: 20px; color: white; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <div style="display: flex; align-items: center; gap: 12px;">
                  <div style="width: 48px; height: 48px; background: rgba(255, 255, 255, 0.2); border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                    <svg style="width: 24px; height: 24px; color: white;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                  </div>
                  <div style="flex: 1;">
                    <h4 style="font-size: 18px; font-weight: 700; margin: 0 0 4px 0; color: white;">Test Başarısız</h4>
                    <p style="font-size: 13px; margin: 0; color: rgba(255, 255, 255, 0.9);">Öğe bulunamadı. Selector'ı kontrol edin.</p>
                  </div>
                </div>
              </div>
            `;
          }
        }
      });
    } catch (error) {
      testResult.classList.remove('hidden');
      testResult.className = 'test-result';
      testResult.innerHTML = `
        <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); border-radius: 12px; padding: 20px; color: white; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
          <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 48px; height: 48px; background: rgba(255, 255, 255, 0.2); border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
              <svg style="width: 24px; height: 24px; color: white;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </div>
            <div style="flex: 1;">
              <h4 style="font-size: 18px; font-weight: 700; margin: 0 0 4px 0; color: white;">Hata</h4>
              <p style="font-size: 13px; margin: 0; color: rgba(255, 255, 255, 0.9);">${error.message}</p>
            </div>
          </div>
        </div>
      `;
    }
  });

  // Seçiciyi kaydet (API'ye kaydet)
  document.getElementById('save-selector').addEventListener('click', async () => {
    const selector = document.getElementById('element-selector').value;
    const labelSelect = document.getElementById('element-label');
    const label = labelSelect.value.trim();
    const labelOption = labelSelect.options[labelSelect.selectedIndex];
    const labelId = labelOption ? labelOption.getAttribute('data-attribute-id') : null;
    const domain = document.getElementById('element-domain').value;
    const note = document.getElementById('element-note').value.trim();
    const modules = [...selectedModules]; // Seçilen modüllerin kopyasını al
    const selectorType = document.querySelector('input[name="selector-type"]:checked').value; // class veya xpath
    const saveBtn = document.getElementById('save-selector');
    
    if (!selector || !label) {
      showStatus(pickerStatus, 'Lütfen selector ve etiket seçin.', 'error');
      return;
    }

    // Loading state
    const originalText = saveBtn.innerHTML;
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg><span>Kaydediliyor...</span>';
    saveBtn.style.backgroundColor = '#6b7280';

    try {
      // API'ye kaydet
      if (typeof window.apiHelper !== 'undefined' && window.apiHelper.syncSelectors) {
        // Mevcut domain için selectors'ı al
        const currentSelectorsResult = await window.apiHelper.getSelectors(domain);
        let currentItems = [];
        
        if (currentSelectorsResult.success && currentSelectorsResult.data && currentSelectorsResult.data.length > 0) {
          const domainData = currentSelectorsResult.data.find(d => d.domain === domain);
          if (domainData) {
            currentItems = domainData.items || [];
          }
        }
        
        // Aynı selector'ın zaten var olup olmadığını kontrol et
        const exists = currentItems.some(item => item.selector === selector && item.label === label);
        if (exists) {
          saveBtn.innerHTML = originalText;
          saveBtn.style.backgroundColor = '';
          saveBtn.disabled = false;
          showStatus(pickerStatus, 'Bu seçici zaten kayıtlı.', 'error');
          return;
        }
        
        // Yeni seçiciyi ekle (note, modules ve label_id ile birlikte)
        const newItem = {
          label: label,
          selector: selector,
          selector_type: selectorType,
          note: note || null,
          modules: modules.length > 0 ? modules : []
        };
        
        // Eğer label_id varsa ekle (backend'de attribute_id olarak kullanılacak)
        if (labelId) {
          newItem.label_id = parseInt(labelId);
          newItem.attribute_id = parseInt(labelId); // Alias
        }
        
        currentItems.push(newItem);
        
        // API'ye gönder
        const apiResult = await window.apiHelper.syncSelectors([{
          domain: domain,
          items: currentItems
        }]);
        
        if (apiResult.success) {
          // Başarı mesajı - daha görünür
          saveBtn.innerHTML = '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg><span>Başarıyla Kaydedildi!</span>';
          saveBtn.style.backgroundColor = '#10b981';
          
          const moduleInfo = modules.length > 0 ? ` (${modules.length} modül)` : '';
          showStatus(pickerStatus, `✅ Seçici başarıyla API'ye kaydedildi!${moduleInfo}\nLabel: ${label}\nSelector: ${selector.substring(0, 50)}${selector.length > 50 ? '...' : ''}`, 'success');
          
          selectedElementInfo.classList.add('hidden');
          document.getElementById('element-label').value = '';
          document.getElementById('element-note').value = '';
          selectedModules = [];
          updateSelectedModulesList();
          
          // Kayıtlı seçiciler sekmesindeyse listeyi güncelle
          if (document.getElementById('selectors-tab') && !document.getElementById('selectors-tab').classList.contains('hidden')) {
            await loadSelectors();
          }
          
          setTimeout(() => {
            saveBtn.innerHTML = originalText;
            saveBtn.style.backgroundColor = '';
            saveBtn.disabled = false;
          }, 3000);
        } else {
          saveBtn.innerHTML = originalText;
          saveBtn.style.backgroundColor = '';
          saveBtn.disabled = false;
          showStatus(pickerStatus, '❌ Kayıt hatası: ' + (apiResult.message || 'Bilinmeyen hata'), 'error');
        }
      } else {
        saveBtn.innerHTML = originalText;
        saveBtn.style.backgroundColor = '';
        saveBtn.disabled = false;
        showStatus(pickerStatus, '❌ API helper yüklenemedi. Lütfen API ayarlarını kontrol edin.', 'error');
      }
    } catch (error) {
      saveBtn.innerHTML = originalText;
      saveBtn.style.backgroundColor = '';
      saveBtn.disabled = false;
      showStatus(pickerStatus, '❌ Kayıt hatası: ' + error.message, 'error');
    }
  });

  // Tüm seçicileri sakla (filtreleme için)
  let allSelectorsData = [];
  
  // Kayıtlı seçicileri yükle (API'den)
  async function loadSelectors() {
    const selectorsList = document.getElementById('selectors-list');
    
    try {
      // Loading state
      selectorsList.innerHTML = `
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <p class="text-sm text-blue-800">Seçiciler API'den yükleniyor...</p>
        </div>
      `;

      // API'den seçicileri çek
      if (typeof window.apiHelper !== 'undefined' && window.apiHelper.getSelectors) {
        const apiResult = await window.apiHelper.getSelectors();
        
        if (apiResult.success && apiResult.data) {
          allSelectorsData = apiResult.data; // Tüm verileri sakla
          
          if (allSelectorsData.length === 0) {
            selectorsList.innerHTML = `
              <div class="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
                <svg class="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
                </svg>
                <p class="text-sm text-gray-500 mb-1">Henüz seçici kaydedilmemiş.</p>
                <p class="text-xs text-gray-400">Öğe Seç sekmesinden yeni seçici ekleyebilirsiniz.</p>
              </div>
            `;
            return;
          }
          
          // İlk yüklemede tüm firmaları göster
          renderSelectors(allSelectorsData);
        } else {
          throw new Error(apiResult.message || 'Seçiciler yüklenemedi');
        }
      } else {
        throw new Error('API helper yüklenemedi. Lütfen API ayarlarını kontrol edin.');
      }
    } catch (error) {
      selectorsList.innerHTML = `
        <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p class="text-sm text-red-800">Veriler yüklenirken hata oluştu: ${error.message}</p>
          <p class="text-xs text-red-600 mt-2">API ayarlarını kontrol edin veya sayfayı yenileyin.</p>
        </div>
      `;
      console.error('Seçiciler yüklenirken hata:', error);
    }
  }
  
  // Seçicileri render et (filtrelenmiş veri ile) - MODERN TASARIM
  function renderSelectors(selectorsData) {
    const selectorsList = document.getElementById('selectors-list');
    
    if (selectorsData.length === 0) {
      selectorsList.innerHTML = `
        <div class="bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-yellow-200 rounded-2xl p-8 text-center shadow-sm">
          <div class="w-16 h-16 bg-gradient-to-br from-yellow-400 to-orange-400 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900 mb-2">Firma Bulunamadı</h3>
          <p class="text-sm text-gray-600">Seçilen kriterlere uygun firma bulunamadı.</p>
          <p class="text-xs text-gray-500 mt-1">Farklı bir firma adı deneyin.</p>
        </div>
      `;
      return;
    }
    
    let html = '';
    for (const domainData of selectorsData) {
      const domain = domainData.domain;
      const items = domainData.items || [];
      
      html += `
        <div class="bg-gradient-to-br from-white to-gray-50 border-2 border-gray-200 rounded-2xl p-6 mb-6 shadow-lg hover:shadow-xl transition-all duration-300 hover:border-gray-300">
          <div class="flex items-center justify-between mb-6 pb-4 border-b-2 border-gray-200">
            <div class="flex items-center space-x-4">
              <div class="w-14 h-14 bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl flex items-center justify-center shadow-lg">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path>
                </svg>
              </div>
              <div>
                <h3 class="text-xl font-bold text-gray-900 mb-1">${domain}</h3>
                <span class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-800 text-xs font-bold rounded-full border border-blue-200">
                  <svg class="w-3 h-3 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                  ${items.length} Seçici
                </span>
              </div>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      `;
            
            items.forEach((item, index) => {
              const safeDomain = domain.replace(/'/g, "\\'");
              const safeNote = (item.note || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
              const selectorId = `selector-${domain}-${index}`;
              const testResultId = `test-result-${domain}-${index}`;
              const buttonId = `test-btn-${domain}-${index}`;
              
              // Modül bilgilerini hazırla
              let modulesHtml = '';
              if (item.modules && Array.isArray(item.modules) && item.modules.length > 0) {
                modulesHtml = `
                  <div class="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-3">
                    <div class="flex items-center space-x-2 mb-2">
                      <div class="w-6 h-6 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center">
                        <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                        </svg>
                      </div>
                      <span class="text-xs font-bold text-gray-700 uppercase tracking-wide">Modüller</span>
                    </div>
                    <div class="flex flex-wrap gap-2">
                `;
                item.modules.forEach((moduleId, modIndex) => {
                  let moduleName = moduleId;
                  if (typeof getModuleInfo === 'function') {
                    const moduleInfo = getModuleInfo(moduleId);
                    if (moduleInfo) {
                      moduleName = moduleInfo.displayName;
                    }
                  }
                  modulesHtml += `
                    <span class="inline-flex items-center px-3 py-1.5 bg-white border-2 border-blue-300 text-blue-800 text-xs font-bold rounded-lg shadow-sm">
                      <span class="w-5 h-5 bg-gradient-to-br from-blue-500 to-indigo-500 text-white rounded-full flex items-center justify-center text-xs font-bold mr-1.5">${modIndex + 1}</span>
                      ${moduleName}
                    </span>
                  `;
                });
                modulesHtml += '</div></div>';
              }
              
              // Selector ve modülleri base64 encode et (güvenli geçiş için)
              const encodedSelector = btoa(unescape(encodeURIComponent(item.selector || '')));
              const encodedModules = btoa(unescape(encodeURIComponent(JSON.stringify(item.modules || []))));
              
              html += `
                <div class="group bg-white border-2 border-gray-200 rounded-2xl p-5 hover:border-blue-400 transition-all duration-300 shadow-md hover:shadow-xl" id="${selectorId}">
                  <div class="space-y-4 mb-5">
                    <!-- Selector -->
                    <div class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 border border-gray-200">
                      <div class="flex items-center space-x-2 mb-2">
                        <div class="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center shadow-md">
                          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"></path>
                          </svg>
                        </div>
                        <span class="text-xs font-bold text-gray-600 uppercase tracking-wider">Selector</span>
                      </div>
                      <div class="text-sm text-gray-900 font-mono break-all bg-white border border-gray-300 rounded-lg p-3 shadow-inner">${item.selector}</div>
                    </div>
                    
                    <!-- Label -->
                    <div class="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl p-4 border border-emerald-200">
                      <div class="flex items-center space-x-2 mb-2">
                        <div class="w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-lg flex items-center justify-center shadow-md">
                          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                          </svg>
                        </div>
                        <span class="text-xs font-bold text-gray-600 uppercase tracking-wider">Label</span>
                      </div>
                      <div class="text-base font-bold text-gray-900 bg-white border border-emerald-300 rounded-lg p-3 shadow-inner">${item.label}</div>
                    </div>
                    
                    ${modulesHtml}
                    
                    ${item.note ? `
                    <div class="bg-gradient-to-br from-amber-50 to-yellow-50 rounded-xl p-4 border border-amber-200">
                      <div class="flex items-center space-x-2 mb-2">
                        <div class="w-8 h-8 bg-gradient-to-br from-amber-500 to-yellow-500 rounded-lg flex items-center justify-center shadow-md">
                          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                          </svg>
                        </div>
                        <span class="text-xs font-bold text-gray-600 uppercase tracking-wider">Not</span>
                      </div>
                      <div class="text-sm text-gray-700 bg-white border border-amber-300 rounded-lg p-3 whitespace-pre-wrap shadow-inner">${safeNote}</div>
                    </div>
                    ` : ''}
                  </div>
                  
                  <!-- Test Butonu -->
                  <div class="pt-4 border-t-2 border-gray-200">
                    <button 
                      id="${buttonId}"
                      data-selector="${encodedSelector}"
                      data-selector-type="${item.selector_type || 'class'}"
                      data-result-id="${testResultId}"
                      data-modules="${encodedModules}"
                      class="w-full group relative overflow-hidden inline-flex items-center justify-center px-5 py-3.5 bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 hover:from-blue-700 hover:via-blue-800 hover:to-indigo-800 text-white font-bold rounded-xl text-sm transition-all duration-300 shadow-lg hover:shadow-xl active:scale-[0.97] transform">
                      <div class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
                      <svg class="w-5 h-5 mr-2.5 relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                      <span class="relative z-10">Aktif Sekmede Test Et</span>
                    </button>
                    <div id="${testResultId}" class="mt-4 hidden"></div>
                  </div>
                </div>
              `;
            });
            
            html += `
          </div>
        </div>
      `;
    }
    
    selectorsList.innerHTML = html;
    
    // Event listener'ları ekle (onclick yerine)
    for (const domainData of selectorsData) {
      const domain = domainData.domain;
      const items = domainData.items || [];
      
      items.forEach((item, index) => {
        const buttonId = `test-btn-${domain}-${index}`;
        const button = document.getElementById(buttonId);
        
        if (button) {
          button.addEventListener('click', function() {
            window.testSelectorInActiveTabFromButton(this);
          });
        }
      });
    }
  }
  
  // Firma arama fonksiyonu
  const companySearchInput = document.getElementById('company-search');
  if (companySearchInput) {
    companySearchInput.addEventListener('input', (e) => {
      const searchTerm = e.target.value.trim().toLowerCase();
      
      if (searchTerm === '') {
        // Boşsa tüm firmaları göster
        renderSelectors(allSelectorsData);
      } else {
        // Filtrele
        const filtered = allSelectorsData.filter(domainData => {
          const domain = domainData.domain.toLowerCase();
          return domain.includes(searchTerm);
        });
        renderSelectors(filtered);
      }
    });
  }

  // Etiket Yönetimi
  // Etiketleri yükle ve listele (API'den)
  async function loadLabels() {
    const labelsList = document.getElementById('labels-list');
    
    try {
      // Loading state
      labelsList.innerHTML = `
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <p class="text-sm text-blue-800">Etiketler API'den yükleniyor...</p>
        </div>
      `;

      // API'den etiketleri çek
      if (typeof window.apiHelper !== 'undefined' && window.apiHelper.getLabels) {
        const apiResult = await window.apiHelper.getLabels();
        
        if (apiResult.success && apiResult.data) {
          const labels = apiResult.data;
          
          if (labels.length === 0) {
            labelsList.innerHTML = `
              <div class="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
                <svg class="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                </svg>
                <p class="text-sm text-gray-500 mb-1">Henüz etiket eklenmemiş.</p>
                <p class="text-xs text-gray-400">Yukarıdaki formdan yeni etiket ekleyebilirsiniz.</p>
              </div>
            `;
            return;
          }
          
          let html = '';
          labels.forEach((label, index) => {
            html += `
              <div class="bg-white border border-gray-200 rounded-lg p-5">
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="flex items-center space-x-3 mb-2">
                      <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                        </svg>
                      </div>
                      <div class="flex-1">
                        <h4 class="text-base font-semibold text-gray-900">${label.name}</h4>
                        ${label.description ? `<p class="text-sm text-gray-600 mt-1">${label.description}</p>` : ''}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            `;
          });
          
          labelsList.innerHTML = html;
        } else {
          throw new Error(apiResult.message || 'Etiketler yüklenemedi');
        }
      } else {
        throw new Error('API helper yüklenemedi. Lütfen API ayarlarını kontrol edin.');
      }
    } catch (error) {
      labelsList.innerHTML = `
        <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p class="text-sm text-red-800">Etiketler yüklenirken hata oluştu: ${error.message}</p>
          <p class="text-xs text-red-600 mt-2">API ayarlarını kontrol edin veya sayfayı yenileyin.</p>
        </div>
      `;
      console.error('Etiketler yüklenirken hata:', error);
    }
  }

  // Etiketleri dropdown'a yükle (API'den)
  async function loadLabelsIntoSelect() {
    const labelSelect = document.getElementById('element-label');
    
    try {
      // Mevcut seçili değeri sakla
      const currentValue = labelSelect.value;
      
      // Dropdown'u temizle ve varsayılan seçeneği ekle
      labelSelect.innerHTML = '<option value="">Etiket seçin...</option>';
      
      // API'den etiketleri çek
      if (typeof window.apiHelper !== 'undefined' && window.apiHelper.getLabels) {
        const apiResult = await window.apiHelper.getLabels();
        
        if (apiResult.success && apiResult.data) {
          const labels = apiResult.data;
          
          // Etiketleri ekle (attribute_id'yi data attribute olarak sakla)
          labels.forEach((label) => {
            const option = document.createElement('option');
            option.value = label.name;
            option.textContent = label.description ? `${label.name} - ${label.description}` : label.name;
            if (label.id) {
              option.setAttribute('data-attribute-id', label.id);
            }
            labelSelect.appendChild(option);
          });
          
          // Önceki seçimi geri yükle (varsa)
          if (currentValue) {
            labelSelect.value = currentValue;
          }
        }
      } else {
        console.warn('API helper yüklenemedi. Etiketler yüklenemedi.');
      }
    } catch (error) {
      console.error('Etiketler dropdown\'a yüklenirken hata:', error);
    }
  }

  // Yeni etiket ekle (API'ye kaydet)
  document.getElementById('add-label-btn').addEventListener('click', async () => {
    const nameInput = document.getElementById('new-label-name');
    const descInput = document.getElementById('new-label-description');
    const name = nameInput.value.trim();
    const description = descInput.value.trim();
    const btn = document.getElementById('add-label-btn');
    
    if (!name) {
      alert('Lütfen etiket adı girin.');
      return;
    }
    
    // Loading state
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg><span>Ekleniyor...</span>';
    btn.style.backgroundColor = '#6b7280';
    
    try {
      // API'ye kaydet
      if (typeof window.apiHelper !== 'undefined' && window.apiHelper.syncLabels) {
        const apiResult = await window.apiHelper.syncLabels([{ name, description }]);
        
        if (apiResult.success) {
          // Formu temizle
          nameInput.value = '';
          descInput.value = '';
          
          // Listeyi güncelle
          await loadLabels();
          await loadLabelsIntoSelect();
          
          // Başarı mesajı - daha görünür
          btn.innerHTML = '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg><span>Başarıyla Eklendi!</span>';
          btn.style.backgroundColor = '#10b981';
          
          // Başarı bildirimi göster
          const labelsList = document.getElementById('labels-list');
          if (labelsList) {
            const successDiv = document.createElement('div');
            successDiv.className = 'bg-green-50 border border-green-200 rounded-lg p-4 mb-4';
            successDiv.innerHTML = `
              <div class="flex items-center space-x-2">
                <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <p class="text-sm font-medium text-green-800">✅ Etiket "${name}" başarıyla API'ye kaydedildi!</p>
              </div>
            `;
            labelsList.insertBefore(successDiv, labelsList.firstChild);
            
            setTimeout(() => {
              successDiv.remove();
            }, 5000);
          }
          
          setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.backgroundColor = '';
            btn.disabled = false;
          }, 3000);
        } else {
          btn.innerHTML = originalText;
          btn.style.backgroundColor = '';
          btn.disabled = false;
          alert('❌ Etiket eklenirken hata oluştu: ' + (apiResult.message || 'Bilinmeyen hata'));
        }
      } else {
        btn.innerHTML = originalText;
        btn.style.backgroundColor = '';
        btn.disabled = false;
        alert('❌ API helper yüklenemedi. Lütfen API ayarlarını kontrol edin.');
      }
    } catch (error) {
      btn.innerHTML = originalText;
      btn.style.backgroundColor = '';
      btn.disabled = false;
      alert('❌ Etiket eklenirken hata oluştu: ' + error.message);
    }
  });

  // Etiket silme kaldırıldı

  // Sayfa yüklendiğinde etiketleri yükle (API'den)
  // Not: loadLabelsIntoSelect() artık API'den veri çekiyor, bu yüzden sayfa yüklendiğinde otomatik çalışacak
  // Ancak element-label elementi varsa yükle
  if (document.getElementById('element-label')) {
    loadLabelsIntoSelect();
  }
  
  // Modül Yönetimi
  // Modülleri dropdown'a yükle
  function loadModulesIntoSelect() {
    const moduleSelect = document.getElementById('module-select');
    
    try {
      // Mevcut seçili değeri sakla
      const currentValue = moduleSelect.value;
      
      // Dropdown'u temizle ve varsayılan seçeneği ekle
      moduleSelect.innerHTML = '<option value="">Modül seçin...</option>';
      
      // Modülleri ekle
      if (typeof getAllModules === 'function') {
        const modules = getAllModules();
        modules.forEach((module) => {
          const option = document.createElement('option');
          option.value = module.id;
          option.textContent = `${module.displayName} - ${module.description}`;
          moduleSelect.appendChild(option);
        });
      }
      
      // Önceki seçimi geri yükle (varsa)
      if (currentValue) {
        moduleSelect.value = currentValue;
      }
    } catch (error) {
      console.error('Modüller dropdown\'a yüklenirken hata:', error);
    }
  }
  
  // Seçilen modüller listesini güncelle
  function updateSelectedModulesList() {
    const modulesList = document.getElementById('selected-modules-list');
    modulesList.innerHTML = '';
    
    if (selectedModules.length === 0) {
      return;
    }
    
    selectedModules.forEach((moduleId, index) => {
      if (typeof getModuleInfo === 'function') {
        const moduleInfo = getModuleInfo(moduleId);
        if (moduleInfo) {
          const moduleItem = document.createElement('div');
          moduleItem.className = 'bg-gray-50 border-2 border-gray-200 rounded-lg p-3 flex items-center justify-between';
          moduleItem.innerHTML = `
            <div class="flex items-center space-x-3 flex-1">
              <div class="w-8 h-8 bg-gray-900 rounded-lg flex items-center justify-center flex-shrink-0">
                <span class="text-white text-xs font-bold">${index + 1}</span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-semibold text-gray-900">${moduleInfo.displayName}</div>
                <div class="text-xs text-gray-600 truncate">${moduleInfo.description}</div>
              </div>
            </div>
            <button onclick="removeModule(${index})" class="ml-3 inline-flex items-center justify-center w-8 h-8 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg transition-colors flex-shrink-0">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          `;
          modulesList.appendChild(moduleItem);
        }
      }
    });
  }
  
  // Modül ekle
  document.getElementById('add-module-btn').addEventListener('click', () => {
    const moduleSelect = document.getElementById('module-select');
    const moduleId = moduleSelect.value;
    
    if (!moduleId) {
      return;
    }
    
    // Zaten ekli mi kontrol et
    if (selectedModules.includes(moduleId)) {
      return;
    }
    
    // Modülü ekle
    selectedModules.push(moduleId);
    updateSelectedModulesList();
    
    // Dropdown'u sıfırla
    moduleSelect.value = '';
  });
  
  // Modül çıkar (global fonksiyon - HTML'den çağrılacak)
  window.removeModule = function(index) {
    if (index >= 0 && index < selectedModules.length) {
      selectedModules.splice(index, 1);
      updateSelectedModulesList();
    }
  };
  
  // Sayfa yüklendiğinde modülleri yükle
  loadModulesIntoSelect();

  // Global fonksiyonlar (HTML'den çağrılacak)
  // Domain silme kaldırıldı

  window.deleteSelector = async function(domain, labelName) {
    alert('Seçici silme özelliği şu anda kullanılamıyor. Lütfen backend üzerinden silin.');
    // TODO: Backend'e silme endpoint'i eklendiğinde bu fonksiyonu güncelle
  };

  // URL Tarama
  let scanning = false;
  const startScanBtn = document.getElementById('start-scan');
  const stopScanBtn = document.getElementById('stop-scan');
  const scanStatus = document.getElementById('scan-status');
  const scanProgress = document.getElementById('scan-progress');
  const progressFill = document.getElementById('progress-fill');

  startScanBtn.addEventListener('click', async () => {
    const urlListText = document.getElementById('url-list').value.trim();
    
    if (!urlListText) {
      showStatus(scanStatus, 'Lütfen en az bir URL girin.', 'error');
      return;
    }
    
    const urls = urlListText.split('\n').map(url => url.trim()).filter(url => url);
    
    if (urls.length === 0) {
      showStatus(scanStatus, 'Geçerli URL bulunamadı.', 'error');
      return;
    }
    
    scanning = true;
    startScanBtn.classList.add('hidden');
    stopScanBtn.classList.remove('hidden');
    scanProgress.classList.remove('hidden');
    
    try {
      await scanUrls(urls);
    } catch (error) {
      showStatus(scanStatus, 'Tarama hatası: ' + error.message, 'error');
      scanning = false;
      startScanBtn.classList.remove('hidden');
      stopScanBtn.classList.add('hidden');
    }
  });

  stopScanBtn.addEventListener('click', () => {
    scanning = false;
    startScanBtn.classList.remove('hidden');
    stopScanBtn.classList.add('hidden');
    showStatus(scanStatus, 'Tarama durduruldu.', 'info');
  });

  async function scanUrls(urls) {
    const results = [];
    const failedUrls = [];
    const total = urls.length;
    let processed = 0;
    let successCount = 0;
    let failedCount = 0;
    
    // Paralel işlem sayısı
    const parallelCount = parseInt(document.getElementById('parallel-count').value) || 5;
    
    // Rapor alanını göster
    const scanReport = document.getElementById('scan-report');
    scanReport.classList.remove('hidden');
    document.getElementById('report-total').textContent = total;
    document.getElementById('report-success').textContent = '0';
    document.getElementById('report-failed').textContent = '0';
    document.getElementById('report-processed').textContent = '0';
    
    // Screenshot alma fonksiyonu
    const captureScreenshot = async (tabId) => {
      try {
        // Sekmeyi aktif hale getir (screenshot için gerekli)
        await chrome.tabs.update(tabId, { active: true });
        
        // Kısa bir bekleme (sayfa tamamen render olsun)
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Screenshot al
        const dataUrl = await chrome.tabs.captureVisibleTab(null, {
          format: 'png',
          quality: 90
        });
        
        // Sekmeyi tekrar arka plana al
        await chrome.tabs.update(tabId, { active: false });
        
        return dataUrl;
      } catch (error) {
        console.error('Screenshot hatası:', error);
        // Sekmeyi arka plana almayı dene
        try {
          await chrome.tabs.update(tabId, { active: false });
        } catch (e) {}
        return null;
      }
    };
    
    // Not: Artık storage'da veri tutmuyoruz, sadece API'ye gönderiyoruz
    // Bu fonksiyon sadece log için kullanılıyor
    const saveResultToStorage = async (resultItem) => {
      // Artık storage'a kaydetmiyoruz, sadece log basıyoruz
      console.log(`[saveResultToStorage] Sonuç hazırlandı (storage'a kaydedilmedi): ${resultItem.url}`);
    };
    
    // URL'leri paralel işlemek için batch'lere böl
    const processUrl = async (url) => {
      if (!scanning) return { success: false, url, error: 'Tarama durduruldu' };
      
      let tab = null;
      try {
        // URL'yi yeni sekmede aç
        tab = await chrome.tabs.create({ url, active: false });
        
        // Sayfanın yüklenmesini bekle
        await waitForTabLoad(tab.id);
        
        // Domain'i çıkar
        const urlObj = new URL(url);
        const domain = urlObj.hostname.replace('www.', '');
        
        // Bu domain için kayıtlı seçicileri API'den al
        let domainSelectors = [];
        
        if (typeof window.apiHelper !== 'undefined' && window.apiHelper.getSelectors) {
          const apiResult = await window.apiHelper.getSelectors(domain);
          
          if (apiResult.success && apiResult.data && apiResult.data.length > 0) {
            const domainData = apiResult.data.find(d => d.domain === domain);
            if (domainData && domainData.items) {
              // API formatından eklenti formatına çevir
              domainSelectors = domainData.items.map(item => ({
                label: item.label,
                selector: item.selector,
                selector_type: item.selector_type || 'class',
                note: item.note || null,
                modules: item.modules || []
              }));
            }
          }
        }
        
        if (domainSelectors.length === 0) {
          // Selector bulunamadığında da sonucu kaydet
          const noSelectorResult = {
            url,
            domain,
            data: {},
            errors: [{
              label: 'Selector Bulunamadı',
              selector: domain,
              selector_type: 'domain',
              error: `${domain} için kayıtlı seçici bulunamadı`,
              error_type: 'no_selector'
            }],
            timestamp: new Date().toISOString(),
            screenshot: null,
            success: false,
            error: `${domain} için kayıtlı seçici bulunamadı`
          };
          
          // Storage'a kaydet - helper fonksiyon kullan
          await saveResultToStorage(noSelectorResult);
          
          await chrome.tabs.remove(tab.id);
          return { success: false, url, error: `${domain} için kayıtlı seçici bulunamadı`, result: noSelectorResult };
        }
        
        // Content script'e veri toplama mesajı gönder
        const response = await new Promise((resolve, reject) => {
          chrome.tabs.sendMessage(tab.id, {
            action: 'collectData',
            selectors: domainSelectors
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
        const captureScreenshotEnabled = document.getElementById('capture-screenshot').checked;
        if (captureScreenshotEnabled) {
          screenshot = await captureScreenshot(tab.id);
        }
        
        // Sonucu kaydet
        const resultItem = {
          url,
          domain,
          data: collectedData,
          errors: collectedErrors.length > 0 ? collectedErrors : undefined,
          timestamp: new Date().toISOString(),
          screenshot: screenshot,
          success: true
        };
        
        // Storage'a kaydet - helper fonksiyon kullan
        await saveResultToStorage(resultItem);
        
        // Sekmeyi kapat
        await chrome.tabs.remove(tab.id);
        
        return { success: true, url, result: resultItem };
        
      } catch (error) {
        console.error(`URL tarama hatası (${url}):`, error);
        
        // Hata durumunda da sonucu kaydet
        const urlObj = new URL(url);
        const domain = urlObj.hostname.replace('www.', '');
        
        const errorResult = {
          url,
          domain,
          data: {},
          errors: [{
            label: 'URL Tarama Hatası',
            selector: url,
            selector_type: 'url',
            error: error.message || 'Bilinmeyen hata',
            error_type: 'url_scan_error'
          }],
          timestamp: new Date().toISOString(),
          screenshot: null,
          success: false,
          error: error.message
        };
        
        // Storage'a kaydet - helper fonksiyon kullan
        await saveResultToStorage(errorResult);
        
        // Sekmeyi kapatmayı dene
        if (tab && tab.id) {
          try {
            await chrome.tabs.remove(tab.id);
          } catch (e) {}
        }
        
        return { success: false, url, error: error.message, result: errorResult };
      }
    };
    
    // Worker pool pattern: Sürekli paralelCount kadar aktif worker olsun
    let urlIndex = 0;
    const activeWorkers = new Set();
    
    // Worker başlatma fonksiyonu (recursive)
    const startWorker = async () => {
      if (!scanning || urlIndex >= urls.length) {
        return;
      }
      
      const url = urls[urlIndex++];
      const workerPromise = processUrl(url).then(async (result) => {
        // Worker bitti, sonucu işle
        processed++;
        
        if (result.success) {
          results.push(result.result);
          successCount++;
        } else {
          failedUrls.push({ url: result.url, error: result.error });
          failedCount++;
        }
        
        // Progress güncelle
        const progress = (processed / total) * 100;
        progressFill.style.width = `${progress}%`;
        progressFill.textContent = `${processed} / ${total}`;
        
        // Rapor güncelle
        document.getElementById('report-processed').textContent = processed;
        document.getElementById('report-success').textContent = successCount;
        document.getElementById('report-failed').textContent = failedCount;
        
        showStatus(scanStatus, `İşleniyor: ${processed}/${total} - Başarılı: ${successCount}, Başarısız: ${failedCount}`, 'info');
        
        // Worker'dan çıkar
        activeWorkers.delete(workerPromise);
        
        // Eğer daha fazla URL varsa, hemen yeni bir worker başlat
        if (scanning && urlIndex < urls.length) {
          await startWorker();
        }
        
        return result;
      }).catch(async (error) => {
        // Hata durumunda da worker'dan çıkar ve yeni worker başlat
        activeWorkers.delete(workerPromise);
        
        if (scanning && urlIndex < urls.length) {
          await startWorker();
        }
        
        throw error;
      });
      
      activeWorkers.add(workerPromise);
      return workerPromise;
    };
    
    // İlk paralelCount kadar worker'ı başlat
    for (let i = 0; i < Math.min(parallelCount, urls.length); i++) {
      if (!scanning || urlIndex >= urls.length) break;
      startWorker();
    }
    
    // Tüm worker'ların bitmesini bekle (her biri bitince yeni worker başlatılıyor)
    // activeWorkers set'i boşalana kadar bekle
    while (activeWorkers.size > 0 && scanning) {
      await Promise.race(Array.from(activeWorkers));
    }
    
    // Son kalan worker'ları da bekle (scanning durdurulmuş olsa bile)
    if (activeWorkers.size > 0) {
      await Promise.all(Array.from(activeWorkers));
    }
    
    scanning = false;
    
    // Queue'da kalan kayıtları işle (maksimum 10 saniye bekle)
    console.log(`[scanUrls] Queue'da kalan kayıt sayısı: ${storageQueue.length}`);
    let queueWaitTime = 0;
    const maxQueueWaitTime = 10000; // 10 saniye
    
    while (storageQueue.length > 0 && queueWaitTime < maxQueueWaitTime) {
      await new Promise(resolve => setTimeout(resolve, 100));
      queueWaitTime += 100;
    }
    
    // Son bir kez queue'yu işle
    if (storageQueue.length > 0) {
      console.log(`[scanUrls] Queue'da hala ${storageQueue.length} kayıt var, işleniyor...`);
      await processStorageQueue();
    }
    
    // Queue'nun tamamen işlendiğinden emin ol (ekstra 1 saniye bekle)
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    startScanBtn.classList.remove('hidden');
    stopScanBtn.classList.add('hidden');
    scanProgress.classList.add('hidden');
    
    // Tarama sonunda özet bilgileri logla
    try {
      console.log(`[scanUrls] Tarama tamamlandı. İşlenen URL sayısı: ${processed}, Başarılı: ${successCount}, Başarısız: ${failedCount}`);
      // Not: Artık storage'da veri tutmuyoruz, sadece API'ye gönderiyoruz
      
      // Tarama sonuç özeti
      showStatus(scanStatus, `Tarama tamamlandı! Toplam: ${total}, Başarılı: ${successCount}, Başarısız: ${failedCount}.`, 'success');
    } catch (error) {
      console.error('[scanUrls] Final check hatası:', error);
      showStatus(scanStatus, `Tarama tamamlandı! Toplam: ${total}, Başarılı: ${successCount}, Başarısız: ${failedCount}`, 'success');
    }
    
    // Başarısız URL'leri göster
    if (failedUrls.length > 0) {
      const failedUrlsDiv = document.getElementById('failed-urls');
      const failedUrlsList = document.getElementById('failed-urls-list');
      failedUrlsDiv.classList.remove('hidden');
      failedUrlsList.innerHTML = '';
      
      failedUrls.forEach(item => {
        const li = document.createElement('li');
        li.className = 'bg-red-100 border border-red-300 rounded p-2 text-xs text-red-900 mb-2';
        li.innerHTML = `<strong>${item.url}</strong><br><small class="text-red-700">${item.error}</small>`;
        failedUrlsList.appendChild(li);
      });
    } else {
      document.getElementById('failed-urls').classList.add('hidden');
    }
    
    // Sonuçlar sekmesine geç
    if (results.length > 0 || failedUrls.length > 0) {
      document.querySelector('[data-tab="results"]').click();
      // Sonuçları yeniden yükle
      setTimeout(() => {
        loadResults();
      }, 500);
    }
  }

  function waitForTabLoad(tabId) {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        chrome.tabs.onUpdated.removeListener(listener);
        reject(new Error('Sayfa yükleme zaman aşımı'));
      }, 45000); // 45 saniye timeout

      let hasResolved = false;
      
      const listener = async (updatedTabId, changeInfo, updatedTab) => {
        if (hasResolved) return;
        
        if (updatedTabId === tabId) {
          // Hata sayfası kontrolü
          if (updatedTab && updatedTab.url) {
            if (updatedTab.url.startsWith('chrome-error://') || 
                updatedTab.url.startsWith('chrome://') ||
                updatedTab.url.startsWith('about:') ||
                updatedTab.url.includes('error') ||
                updatedTab.url.includes('blocked')) {
              clearTimeout(timeout);
              chrome.tabs.onUpdated.removeListener(listener);
              hasResolved = true;
              reject(new Error(`Sayfa yüklenemedi: ${updatedTab.url}`));
              return;
            }
          }
          
          // Sayfa başarıyla yüklendi
          if (changeInfo.status === 'complete') {
            try {
              const tab = await chrome.tabs.get(tabId);
              if (tab && tab.status === 'complete' && tab.url && 
                  !tab.url.startsWith('chrome-error://') && 
                  !tab.url.startsWith('chrome://')) {
                clearTimeout(timeout);
                chrome.tabs.onUpdated.removeListener(listener);
                hasResolved = true;
                // JavaScript ve dinamik içerik yüklenmesi için bekleme (2 saniye)
                setTimeout(() => {
                  resolve();
                }, 2000);
              }
            } catch (error) {
              // Tab bulunamadı veya hata oluştu, yine de devam et
              if (!hasResolved) {
                clearTimeout(timeout);
                chrome.tabs.onUpdated.removeListener(listener);
                hasResolved = true;
                setTimeout(() => resolve(), 2000);
              }
            }
          }
        }
      };
      
      chrome.tabs.onUpdated.addListener(listener);
      
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
            chrome.tabs.onUpdated.removeListener(listener);
            hasResolved = true;
            reject(new Error(`Sayfa yüklenemedi: ${tab.url}`));
            return;
          }
          
          if (tab.status === 'complete' && tab.url && 
              !tab.url.startsWith('chrome-error://') && 
              !tab.url.startsWith('chrome://')) {
            clearTimeout(timeout);
            chrome.tabs.onUpdated.removeListener(listener);
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

  // Sonuçları yükle
  async function loadResults() {
    const resultsList = document.getElementById('results-list');
    
    try {
      // Not: Artık storage'da veri tutmuyoruz, sadece API'ye gönderiyoruz
      // Sonuçlar artık burada gösterilmiyor
      resultsList.innerHTML = `
        <div class="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
          <svg class="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <p class="text-sm text-gray-500 mb-1">Sonuçlar artık burada gösterilmiyor.</p>
          <p class="text-xs text-gray-400">Veriler API'ye gönderiliyor ve backend'de saklanıyor.</p>
        </div>
      `;
    } catch (error) {
      resultsList.innerHTML = `
        <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p class="text-sm text-red-800">Sonuçlar yüklenirken hata oluştu.</p>
        </div>
      `;
      console.error('Sonuçlar yüklenirken hata:', error);
    }
  }

  // Hata detaylarını aç/kapat fonksiyonu (global scope'a ekle)
  window.toggleErrorDetails = function(errorDetailsId) {
    const detailsDiv = document.getElementById(errorDetailsId);
    const iconSvg = document.getElementById(`${errorDetailsId}-icon`);
    
    if (detailsDiv && iconSvg) {
      if (detailsDiv.classList.contains('hidden')) {
        // Aç
        detailsDiv.classList.remove('hidden');
        iconSvg.classList.add('rotate-180');
      } else {
        // Kapat
        detailsDiv.classList.add('hidden');
        iconSvg.classList.remove('rotate-180');
      }
    }
  };

  // JSON export
  document.getElementById('export-json').addEventListener('click', async () => {
    // Not: Artık storage'da veri tutmuyoruz, sadece API'ye gönderiyoruz
    alert('Sonuçlar artık storage\'da tutulmuyor. Veriler API\'ye gönderiliyor ve backend\'de saklanıyor. Verileri backend üzerinden alabilirsiniz.');
  });

  // Sonuçları temizle
  document.getElementById('clear-results').addEventListener('click', async () => {
    // Not: Artık storage'da veri tutmuyoruz, sadece API'ye gönderiyoruz
    alert('Sonuçlar artık storage\'da tutulmuyor. Veriler API\'ye gönderiliyor ve backend\'de saklanıyor. Verileri backend üzerinden yönetebilirsiniz.');
    loadResults(); // UI'ı güncelle
  });

  // Yardımcı fonksiyonlar
  function showStatus(element, message, type) {
    element.classList.remove('hidden');
    const typeClasses = {
      success: 'bg-green-50 border border-green-200 rounded-lg p-4 text-sm text-green-800',
      error: 'bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-800',
      info: 'bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800'
    };
    element.className = `status-message ${typeClasses[type] || typeClasses.info}`;
    element.textContent = message;
  }

  // Ayarlar Yönetimi
  // Ayarlar sekmesini yükle
  async function loadSettings() {
    await updateDataStats();
  }

  // Veri istatistiklerini güncelle (API'den)
  async function updateDataStats() {
    try {
      // Etiket sayısı - API'den
      let labelsCount = 0;
      if (typeof window.apiHelper !== 'undefined' && window.apiHelper.getLabels) {
        try {
          const labelsResult = await window.apiHelper.getLabels();
          if (labelsResult.success && labelsResult.data) {
            labelsCount = labelsResult.data.length;
          }
        } catch (error) {
          console.error('Etiket istatistikleri yüklenirken hata:', error);
        }
      }
      document.getElementById('stats-labels').textContent = labelsCount;
      
      // Seçici sayısı - API'den
      let selectorsCount = 0;
      if (typeof window.apiHelper !== 'undefined' && window.apiHelper.getSelectors) {
        try {
          const selectorsResult = await window.apiHelper.getSelectors();
          if (selectorsResult.success && selectorsResult.data) {
            selectorsResult.data.forEach(domainData => {
              selectorsCount += (domainData.items || []).length;
            });
          }
        } catch (error) {
          console.error('Seçici istatistikleri yüklenirken hata:', error);
        }
      }
      document.getElementById('stats-selectors').textContent = selectorsCount;
      
      // Tarama sonuçları sayısı - Artık storage'da tutulmuyor
      document.getElementById('stats-results').textContent = '0';
      // Not: Sonuçlar artık storage'da tutulmuyor, sadece API'ye gönderiliyor
    } catch (error) {
      console.error('İstatistikler yüklenirken hata:', error);
    }
  }

  // Tüm verileri yedekle (API'den)
  document.getElementById('export-all-data').addEventListener('click', async () => {
    try {
      // API'den labels ve selectors çek
      let labels = [];
      let selectors = {};
      
      if (typeof window.apiHelper !== 'undefined') {
        // Labels
        if (window.apiHelper.getLabels) {
          const labelsResult = await window.apiHelper.getLabels();
          if (labelsResult.success && labelsResult.data) {
            labels = labelsResult.data;
          }
        }
        
        // Selectors
        if (window.apiHelper.getSelectors) {
          const selectorsResult = await window.apiHelper.getSelectors();
          if (selectorsResult.success && selectorsResult.data) {
            // API formatından storage formatına çevir
            for (const domainData of selectorsResult.data) {
              selectors[domainData.domain] = domainData.items || [];
            }
          }
        }
      }
      
      // Not: Artık scanResults storage'da tutulmuyor
      const backupData = {
        version: '1.0',
        exportDate: new Date().toISOString(),
        labels: labels,
        selectors: selectors,
        scanResults: [] // Artık storage'da tutulmuyor
      };
      
      const dataStr = JSON.stringify(backupData, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `deep-extension-backup-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      // Başarı mesajı
      const btn = document.getElementById('export-all-data');
      const originalText = btn.innerHTML;
      btn.innerHTML = '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg><span>Yedeklendi!</span>';
      btn.style.backgroundColor = '#10b981';
      
      setTimeout(() => {
        btn.innerHTML = originalText;
        btn.style.backgroundColor = '';
      }, 2000);
    } catch (error) {
      alert('Yedekleme hatası: ' + error.message);
      console.error('Yedekleme hatası:', error);
    }
  });

  // Yedekten geri yükle
  document.getElementById('import-all-data').addEventListener('click', () => {
    document.getElementById('import-file-input').click();
  });

  document.getElementById('import-file-input').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    if (!confirm('Mevcut tüm veriler silinip yedekten geri yüklenecek. Devam etmek istediğinize emin misiniz?')) {
      e.target.value = '';
      return;
    }
    
    try {
      const text = await file.text();
      const backupData = JSON.parse(text);
      
      // Veri formatını kontrol et (scanResults artık opsiyonel)
      if (!backupData.labels || !backupData.selectors) {
        throw new Error('Geçersiz yedek dosyası formatı.');
      }
      
      // Labels'ı API'ye kaydet
      if (typeof window.apiHelper !== 'undefined' && window.apiHelper.syncLabels) {
        await window.apiHelper.syncLabels(backupData.labels || []);
      }
      
      // Selectors'ı API'ye kaydet
      if (typeof window.apiHelper !== 'undefined' && window.apiHelper.syncSelectors) {
        // Storage formatından API formatına çevir
        const selectorsArray = [];
        for (const [domain, items] of Object.entries(backupData.selectors || {})) {
          selectorsArray.push({
            domain: domain,
            items: items.map(item => ({
              label: item.label,
              selector: item.selector,
              selector_type: item.selector_type || 'class',
              note: item.note || null,
              modules: item.modules || []
            }))
          });
        }
        await window.apiHelper.syncSelectors(selectorsArray);
      }
      
      // Not: Artık scanResults storage'da tutulmuyor, sadece API'ye gönderiliyor
      // scanResults'ı restore etmiyoruz
      
      // Tüm sekmeleri güncelle
      await loadLabels();
      await loadSelectors();
      await loadResults();
      await updateDataStats();
      
      // Başarı mesajı
      alert('Veriler başarıyla geri yüklendi ve API\'ye kaydedildi!');
      
      // Dosya input'unu temizle
      e.target.value = '';
    } catch (error) {
      alert('Geri yükleme hatası: ' + error.message);
      console.error('Geri yükleme hatası:', error);
      e.target.value = '';
    }
  });

  // Tüm verileri temizle
  document.getElementById('clear-all-data').addEventListener('click', async () => {
    if (!confirm('TÜM VERİLERİ SİLMEK İSTEDİĞİNİZE EMİN MİSİNİZ?\n\n⚠️ DİKKAT: Etiketler ve seçiciler backend\'de saklanıyor. Bu işlem sadece tarama sonuçlarını temizleyecektir.\n\nEtiketler ve seçicileri silmek için backend üzerinden silmeniz gerekiyor.')) {
      return;
    }
    
    try {
      // Not: Artık scanResults storage'da tutulmuyor, sadece API'ye gönderiliyor
      // Storage temizleme işlemi gerekmiyor
      
      // Tüm sekmeleri güncelle
      await loadLabels();
      await loadSelectors();
      await loadResults();
      await updateDataStats();
      
      alert('Tarama sonuçları artık storage\'da tutulmuyor.\n\nNot: Veriler API\'ye gönderiliyor ve backend\'de saklanıyor. Etiketler ve seçiciler backend\'de saklanıyor ve buradan silinemez.');
    } catch (error) {
      alert('Temizleme hatası: ' + error.message);
      console.error('Temizleme hatası:', error);
    }
  });

  // Varsayılan token kontrolü ve ayarlama (ayrı fonksiyon)
  async function checkAndSetDefaultToken() {
    try {
      const defaultToken = 'iprice_Wi9vtsk56PO4QJAEgBXWROkHjimflqyE';
      const result = await chrome.storage.local.get(['apiToken']);
      
      // Token kontrolü: null, undefined, boş string veya sadece boşluk kontrolü
      const existingToken = result.apiToken;
      const hasValidToken = existingToken && typeof existingToken === 'string' && existingToken.trim().length > 0;
      
      if (!hasValidToken) {
        // Varsayılan token'ı kaydet
        await chrome.storage.local.set({ apiToken: defaultToken });
        console.log('Varsayılan API token storage\'a kaydedildi:', defaultToken);
        
        // Eğer input elementi varsa, onu da güncelle
        const apiTokenInput = document.getElementById('api-token');
        if (apiTokenInput) {
          apiTokenInput.value = defaultToken;
        }
      }
    } catch (error) {
      console.error('Varsayılan token kontrolü hatası:', error);
    }
  }
  
  // Sayfa yüklendiğinde verileri yükle
  if (document.getElementById('selectors-tab') && document.getElementById('selectors-tab').classList.contains('active')) {
    loadSelectors();
  }
  if (document.getElementById('labels-tab') && document.getElementById('labels-tab').classList.contains('active')) {
    loadLabels();
  }
  if (document.getElementById('settings-tab') && document.getElementById('settings-tab').classList.contains('active')) {
    loadSettings();
    loadAPISettings();
  }
  
  // Sayfa yüklendiğinde varsayılan token kontrolü yap (her durumda)
  checkAndSetDefaultToken();

  // API Ayarları Yönetimi
  // API ayarlarını yükle
  async function loadAPISettings() {
    try {
      const result = await chrome.storage.local.get(['apiToken', 'testMode', 'apiBaseURL']);
      
      // Test modu checkbox'ını ayarla (varsayılan: false - canlı mod)
      const testMode = result.testMode === true;
      const testModeCheckbox = document.getElementById('test-mode');
      if (testModeCheckbox) {
        testModeCheckbox.checked = testMode;
      }
      
      // API Base URL'i yükle
      const apiBaseUrlInput = document.getElementById('api-base-url');
      if (apiBaseUrlInput) {
        // Eğer storage'da kayıtlı bir URL varsa onu kullan
        if (result.apiBaseURL && result.apiBaseURL.trim().length > 0) {
          apiBaseUrlInput.value = result.apiBaseURL;
        } else {
          // Yoksa test moduna göre otomatik ayarla
          await updateAPIBaseURL();
        }
      }
      
      // Token'ı input'a yükle
      const defaultToken = 'iprice_Wi9vtsk56PO4QJAEgBXWROkHjimflqyE';
      const apiTokenInput = document.getElementById('api-token');
      
      if (apiTokenInput) {
        // Token kontrolü: null, undefined, boş string veya sadece boşluk kontrolü
        const existingToken = result.apiToken;
        const hasValidToken = existingToken && typeof existingToken === 'string' && existingToken.trim().length > 0;
        
        if (hasValidToken) {
          apiTokenInput.value = existingToken;
        } else {
          // Varsayılan token'ı ayarla (storage'a zaten kaydedilmiş olmalı)
          apiTokenInput.value = defaultToken;
        }
      }
    } catch (error) {
      console.error('API ayarları yüklenirken hata:', error);
    }
  }

  // API Base URL'i güncelle (test moduna göre)
  async function updateAPIBaseURL() {
    const testMode = document.getElementById('test-mode').checked;
    const apiBaseUrlInput = document.getElementById('api-base-url');
    
    if (!apiBaseUrlInput) return;
    
    // Eğer kullanıcı manuel bir URL girmişse, test modu değiştiğinde sadece boşsa veya varsayılan değerlerden biri ise güncelle
    const currentValue = apiBaseUrlInput.value.trim();
    const testModeURL = 'http://localhost:8082/api';
    const liveModeURL = 'http://10.20.50.16/iprice_backend/api/';
    
    // Eğer input boşsa veya mevcut değer varsayılan değerlerden biri ise güncelle
    if (!currentValue || currentValue === testModeURL || currentValue === liveModeURL) {
      if (testMode) {
        apiBaseUrlInput.value = testModeURL;
      } else {
        apiBaseUrlInput.value = liveModeURL;
      }
    }
  }

  // Test modu değiştiğinde
  document.getElementById('test-mode').addEventListener('change', async () => {
    const testMode = document.getElementById('test-mode').checked;
    
    // Storage'a kaydet
    await chrome.storage.local.set({ testMode: testMode });
    
    // Base URL'i güncelle (sadece boşsa veya varsayılan değerlerden biri ise)
    await updateAPIBaseURL();
    
    // Güncellenen URL'i storage'a kaydet
    const apiBaseUrlInput = document.getElementById('api-base-url');
    if (apiBaseUrlInput && apiBaseUrlInput.value.trim()) {
      await chrome.storage.local.set({ apiBaseURL: apiBaseUrlInput.value.trim() });
    }
  });

  // API Base URL değiştiğinde otomatik kaydet (debounce ile)
  let apiBaseUrlTimeout = null;
  const apiBaseUrlInput = document.getElementById('api-base-url');
  if (apiBaseUrlInput) {
    apiBaseUrlInput.addEventListener('input', () => {
      // Önceki timeout'u temizle
      if (apiBaseUrlTimeout) {
        clearTimeout(apiBaseUrlTimeout);
      }
      
      // 1 saniye sonra kaydet (kullanıcı yazmayı bitirdikten sonra)
      apiBaseUrlTimeout = setTimeout(async () => {
        const baseURL = apiBaseUrlInput.value.trim();
        if (baseURL) {
          await chrome.storage.local.set({ apiBaseURL: baseURL });
        }
      }, 1000);
    });
    
    // Blur olduğunda hemen kaydet
    apiBaseUrlInput.addEventListener('blur', async () => {
      if (apiBaseUrlTimeout) {
        clearTimeout(apiBaseUrlTimeout);
      }
      const baseURL = apiBaseUrlInput.value.trim();
      if (baseURL) {
        await chrome.storage.local.set({ apiBaseURL: baseURL });
      }
    });
  }

  // API ayarlarını kaydet
  document.getElementById('save-api-settings').addEventListener('click', async () => {
    const tokenInput = document.getElementById('api-token');
    const apiBaseUrlInput = document.getElementById('api-base-url');
    const token = tokenInput.value.trim();
    const baseURL = apiBaseUrlInput.value.trim();
    const testMode = document.getElementById('test-mode').checked;
    const apiStatus = document.getElementById('api-status');
    const defaultToken = 'iprice_Wi9vtsk56PO4QJAEgBXWROkHjimflqyE';

    // Eğer token boşsa, varsayılan token'ı kullan
    const finalToken = token || defaultToken;
    
    // Base URL kontrolü
    if (!baseURL) {
      showStatus(apiStatus, 'Lütfen API Base URL girin!', 'error');
      return;
    }

    try {
      await chrome.storage.local.set({
        apiToken: finalToken,
        testMode: testMode,
        apiBaseURL: baseURL
      });

      // Eğer token boşsa, input'a da varsayılan token'ı yaz
      if (!token) {
        tokenInput.value = defaultToken;
      }

      showStatus(apiStatus, 'API ayarları başarıyla kaydedildi!', 'success');
    } catch (error) {
      showStatus(apiStatus, 'Ayarlar kaydedilirken hata: ' + error.message, 'error');
    }
  });

  // API bağlantısını test et
  document.getElementById('test-api-connection').addEventListener('click', async () => {
    const apiStatus = document.getElementById('api-status');
    const tokenInput = document.getElementById('api-token');
    let token = tokenInput.value.trim();
    const testMode = document.getElementById('test-mode').checked;
    const defaultToken = 'iprice_Wi9vtsk56PO4QJAEgBXWROkHjimflqyE';

    // Eğer token boşsa, varsayılan token'ı kullan
    if (!token) {
      token = defaultToken;
      tokenInput.value = defaultToken;
    }

    try {
      showStatus(apiStatus, 'Bağlantı test ediliyor...', 'info');

      // Base URL'i al (input'tan veya storage'dan)
      const apiBaseUrlInput = document.getElementById('api-base-url');
      let baseURL = apiBaseUrlInput.value.trim();
      
      // Eğer input boşsa, storage'dan yükle veya test moduna göre ayarla
      if (!baseURL) {
        const stored = await chrome.storage.local.get(['apiBaseURL']);
        if (stored.apiBaseURL && stored.apiBaseURL.trim()) {
          baseURL = stored.apiBaseURL;
          apiBaseUrlInput.value = baseURL;
        } else {
          await updateAPIBaseURL();
          baseURL = apiBaseUrlInput.value.trim();
        }
      }
      
      // Token ve test modunu kaydet
      await chrome.storage.local.set({
        apiToken: token,
        testMode: testMode,
        apiBaseURL: baseURL
      });

      // Test connection
      if (typeof window.apiHelper !== 'undefined' && window.apiHelper.testConnection) {
        const result = await window.apiHelper.testConnection();
        if (result.success) {
          showStatus(apiStatus, `Bağlantı başarılı! Kullanıcı: ${result.user?.name || 'Bilinmiyor'}`, 'success');
        } else {
          showStatus(apiStatus, 'Bağlantı başarısız: ' + (result.message || 'Bilinmeyen hata'), 'error');
        }
      } else {
        // Fallback: Direct API call
        // URL birleştirme (çift slash sorununu önler)
        const cleanBase = baseURL.replace(/\/+$/, '');
        const cleanEndpoint = '/chrome-extension/test-connection'.replace(/^\/+/, '');
        const testURL = `${cleanBase}/${cleanEndpoint}`;
        const response = await fetch(testURL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({ token })
        });

        const result = await response.json();
        if (result.success) {
          showStatus(apiStatus, `Bağlantı başarılı! Kullanıcı: ${result.user?.name || 'Bilinmiyor'}`, 'success');
        } else {
          showStatus(apiStatus, 'Bağlantı başarısız: ' + (result.message || 'Bilinmeyen hata'), 'error');
        }
      }
    } catch (error) {
      showStatus(apiStatus, 'Bağlantı hatası: ' + error.message, 'error');
    }
  });

  // Etiketleri yenile (API'den)
  document.getElementById('sync-labels-to-api').addEventListener('click', async () => {
    const syncStatus = document.getElementById('sync-status');
    
    try {
      showStatus(syncStatus, 'Etiketler yenileniyor...', 'info');
      await loadLabels();
      await loadLabelsIntoSelect();
      showStatus(syncStatus, 'Etiketler başarıyla yenilendi!', 'success');
    } catch (error) {
      showStatus(syncStatus, 'Hata: ' + error.message, 'error');
    }
  });

  // Seçicileri yenile (API'den)
  document.getElementById('sync-selectors-to-api').addEventListener('click', async () => {
    const syncStatus = document.getElementById('sync-status');
    
    try {
      showStatus(syncStatus, 'Seçiciler yenileniyor...', 'info');
      await loadSelectors();
      showStatus(syncStatus, 'Seçiciler başarıyla yenilendi!', 'success');
    } catch (error) {
      showStatus(syncStatus, 'Hata: ' + error.message, 'error');
    }
  });

  // Etiketleri yenile (API'den)
  document.getElementById('fetch-labels-from-api').addEventListener('click', async () => {
    const syncStatus = document.getElementById('sync-status');
    
    try {
      showStatus(syncStatus, 'Etiketler yenileniyor...', 'info');
      await loadLabels();
      await loadLabelsIntoSelect();
      showStatus(syncStatus, 'Etiketler başarıyla yenilendi!', 'success');
    } catch (error) {
      showStatus(syncStatus, 'Hata: ' + error.message, 'error');
    }
  });

  // Seçicileri yenile (API'den)
  document.getElementById('fetch-selectors-from-api').addEventListener('click', async () => {
    const syncStatus = document.getElementById('sync-status');
    
    try {
      showStatus(syncStatus, 'Seçiciler yenileniyor...', 'info');
      await loadSelectors();
      showStatus(syncStatus, 'Seçiciler başarıyla yenilendi!', 'success');
    } catch (error) {
      showStatus(syncStatus, 'Hata: ' + error.message, 'error');
    }
  });

  // RabbitMQ Listener
  let rabbitmqProcessedCount = 0;
  let rabbitmqQueueInfoInterval = null;

  // RabbitMQ durumunu güncelle (artık API'ye istek atmıyor, sadece local state'ten bilgi alıyor)
  function updateRabbitMQStatus() {
    if (typeof window.rabbitmqHelper === 'undefined') {
      return;
    }

    try {
      // Local state'ten bilgi al (API'ye gereksiz istek atmıyor)
      const queueInfo = window.rabbitmqHelper.getQueueInfo();
      if (queueInfo.success) {
        document.getElementById('rabbitmq-queue-count').textContent = queueInfo.data.messages || 0;
      }
    } catch (error) {
      console.error('Queue bilgisi güncellenemedi:', error);
    }
  }

  // RabbitMQ listener başlat
  document.getElementById('rabbitmq-start').addEventListener('click', async () => {
    if (typeof window.rabbitmqHelper === 'undefined') {
      showStatus(document.getElementById('rabbitmq-message'), 'RabbitMQ helper yüklenemedi. Sayfayı yenileyin.', 'error');
      return;
    }

    try {
      // Bağlantı testi
      const testResult = await window.rabbitmqHelper.testConnection();
      if (!testResult.success) {
        showStatus(document.getElementById('rabbitmq-message'), 'RabbitMQ bağlantı hatası: ' + (testResult.error || 'Bilinmeyen hata'), 'error');
        return;
      }

      // Paralel işlem sayısını al
      const parallelCount = parseInt(document.getElementById('rabbitmq-parallel-count').value) || 3;
      
      // Aktif işlem sayacı (paralel işlem kontrolü için)
      let activeProcesses = 0;
      const maxParallel = parallelCount;
      
      // Listener'ı başlat
      window.rabbitmqHelper.startListening(async (message, result) => {
        if (message) {
          // Paralel işlem limitini kontrol et
          if (activeProcesses >= maxParallel) {
            console.log('Paralel işlem limiti doldu, bekleniyor...');
            return;
          }
          
          activeProcesses++;
          console.log('RabbitMQ mesajı alındı:', message, `(Aktif işlem: ${activeProcesses}/${maxParallel})`);
          
          // Mesajı background.js'e gönder ve işlet
          try {
            showStatus(document.getElementById('rabbitmq-message'), `Mesaj işleniyor: ${message.url || 'Bilinmeyen URL'}... (${activeProcesses}/${maxParallel})`, 'info');
            
            const processResult = await new Promise((resolve, reject) => {
              chrome.runtime.sendMessage({
                action: 'processRabbitMQMessage',
                data: message
              }, (response) => {
                if (chrome.runtime.lastError) {
                  reject(new Error(chrome.runtime.lastError.message));
                } else {
                  resolve(response);
                }
              });
            });

            if (processResult && processResult.success) {
              // Mesaj başarıyla işlendi
              rabbitmqProcessedCount++;
              document.getElementById('rabbitmq-processed-count').textContent = rabbitmqProcessedCount;
              
              // Queue bilgisini güncelle
              await updateRabbitMQStatus();
              
              // Sonuçları yükle
              await loadResults();
              
              showStatus(document.getElementById('rabbitmq-message'), `Mesaj başarıyla işlendi: ${message.url || 'Bilinmeyen URL'}`, 'success');
              
              // 3 saniye sonra mesajı gizle
              setTimeout(() => {
                const msgEl = document.getElementById('rabbitmq-message');
                if (msgEl) {
                  msgEl.classList.add('hidden');
                }
              }, 3000);
              
              // ÖNEMLİ: processResult'ı döndür ki rabbitmq-helper job takibini yapabilsin
              return processResult;
            } else {
              // İşleme hatası
              const errorMsg = processResult?.error || 'Bilinmeyen hata';
              showStatus(document.getElementById('rabbitmq-message'), `Hata: ${errorMsg}`, 'error');
              console.error('Mesaj işleme hatası:', processResult);
              
              // Hata durumunda da result'ı döndür
              return processResult || { success: false, error: errorMsg };
            }
          } catch (error) {
            console.error('RabbitMQ mesaj işleme hatası:', error);
            showStatus(document.getElementById('rabbitmq-message'), `Hata: ${error.message}`, 'error');
            
            // Hata durumunda da result'ı döndür
            return { success: false, error: error.message };
          } finally {
            activeProcesses--;
            console.log(`İşlem tamamlandı. Aktif işlem: ${activeProcesses}/${maxParallel}`);
          }
        } else if (result && !result.success) {
          // Hata durumu
          showStatus(document.getElementById('rabbitmq-message'), 'Hata: ' + (result.error || 'Bilinmeyen hata'), 'error');
        }
      }, parallelCount);

      // UI güncelle
      document.getElementById('rabbitmq-start').classList.add('hidden');
      document.getElementById('rabbitmq-stop').classList.remove('hidden');
      document.getElementById('rabbitmq-status-indicator').classList.remove('bg-gray-400');
      document.getElementById('rabbitmq-status-indicator').classList.add('bg-green-500');
      document.getElementById('rabbitmq-status-text').textContent = 'Dinleniyor';
      document.getElementById('rabbitmq-status-text').classList.remove('text-gray-600');
      document.getElementById('rabbitmq-status-text').classList.add('text-green-600');

      // Queue bilgisini periyodik güncelle (artık API'ye istek atmıyor, sadece local state gösteriyor)
      rabbitmqQueueInfoInterval = setInterval(updateRabbitMQStatus, 5000);
      updateRabbitMQStatus();

      showStatus(document.getElementById('rabbitmq-message'), 'RabbitMQ dinleme başlatıldı!', 'success');
    } catch (error) {
      showStatus(document.getElementById('rabbitmq-message'), 'Hata: ' + error.message, 'error');
    }
  });

  // RabbitMQ listener durdur
  document.getElementById('rabbitmq-stop').addEventListener('click', () => {
    if (typeof window.rabbitmqHelper !== 'undefined') {
      window.rabbitmqHelper.stopListening();
    }

    // UI güncelle
    document.getElementById('rabbitmq-start').classList.remove('hidden');
    document.getElementById('rabbitmq-stop').classList.add('hidden');
    document.getElementById('rabbitmq-status-indicator').classList.remove('bg-green-500');
    document.getElementById('rabbitmq-status-indicator').classList.add('bg-gray-400');
    document.getElementById('rabbitmq-status-text').textContent = 'Durduruldu';
    document.getElementById('rabbitmq-status-text').classList.remove('text-green-600');
    document.getElementById('rabbitmq-status-text').classList.add('text-gray-600');

    // Queue bilgisi güncellemesini durdur
    if (rabbitmqQueueInfoInterval) {
      clearInterval(rabbitmqQueueInfoInterval);
      rabbitmqQueueInfoInterval = null;
    }

    showStatus(document.getElementById('rabbitmq-message'), 'RabbitMQ dinleme durduruldu.', 'info');
  });

  // RabbitMQ scan complete mesajını dinle
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'rabbitmqScanComplete') {
      // Sonuçları yükle
      loadResults();
      
      // İşlenen mesaj sayısını güncelle
      rabbitmqProcessedCount++;
      document.getElementById('rabbitmq-processed-count').textContent = rabbitmqProcessedCount;
      
      // Queue bilgisini güncelle
      updateRabbitMQStatus();
    }
  });

  // İlk yüklemede queue bilgisini al
  if (typeof window.rabbitmqHelper !== 'undefined') {
    updateRabbitMQStatus();
  }
});

// Screenshot modal fonksiyonları (global olmalı - HTML'den çağrılacak)
window.openScreenshotModal = function(screenshotUrl, url) {
  const modal = document.getElementById('screenshot-modal');
  const img = document.getElementById('modal-screenshot-img');
  img.src = screenshotUrl;
  img.alt = `Screenshot: ${url}`;
  modal.classList.remove('hidden');
};

window.closeScreenshotModal = function() {
  const modal = document.getElementById('screenshot-modal');
  modal.classList.add('hidden');
};

// Modal event listeners
document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('screenshot-modal');
  const closeBtn = document.getElementById('screenshot-modal-close');
  
  if (modal) {
    // Modal dışına tıklanınca kapat
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeScreenshotModal();
      }
    });
  }
  
  if (closeBtn) {
    closeBtn.addEventListener('click', closeScreenshotModal);
  }
  
  // ESC tuşu ile kapat
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal && !modal.classList.contains('hidden')) {
      closeScreenshotModal();
    }
  });
});

window.downloadScreenshot = function(screenshotUrl, url) {
  try {
    // URL'den dosya adı oluştur
    const urlObj = new URL(url);
    const filename = urlObj.hostname.replace('www.', '') + '_' + 
                     urlObj.pathname.replace(/\//g, '_').replace(/\./g, '_') + 
                     '_' + new Date().getTime() + '.png';
    
    // Data URL'yi blob'a çevir
    fetch(screenshotUrl)
      .then(res => res.blob())
      .then(blob => {
        const blobUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(blobUrl);
      })
      .catch(error => {
        console.error('Screenshot indirme hatası:', error);
        alert('Screenshot indirilemedi: ' + error.message);
      });
  } catch (error) {
    console.error('Screenshot indirme hatası:', error);
    alert('Screenshot indirilemedi: ' + error.message);
  }
};

// Butondan data attribute'ları oku ve test et
window.testSelectorInActiveTabFromButton = function(button) {
  try {
    const encodedSelector = button.getAttribute('data-selector');
    const selectorType = button.getAttribute('data-selector-type') || 'class';
    const resultElementId = button.getAttribute('data-result-id');
    const encodedModules = button.getAttribute('data-modules');
    
    // Decode
    const selector = decodeURIComponent(escape(atob(encodedSelector)));
    const modules = encodedModules ? JSON.parse(decodeURIComponent(escape(atob(encodedModules)))) : [];
    
    // Test fonksiyonunu çağır
    window.testSelectorInActiveTab(selector, selectorType, resultElementId, modules);
  } catch (error) {
    console.error('Test butonu hatası:', error);
    const resultElementId = button.getAttribute('data-result-id');
    if (resultElementId) {
      const testResult = document.getElementById(resultElementId);
      if (testResult) {
        testResult.classList.remove('hidden');
        testResult.innerHTML = `
          <div class="bg-gradient-to-br from-red-50 to-pink-50 border-2 border-red-300 rounded-2xl p-5 shadow-lg">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-gradient-to-br from-red-500 to-pink-500 rounded-xl flex items-center justify-center shadow-md">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </div>
              <div>
                <span class="text-sm font-bold text-red-900 block">Hata</span>
                <span class="text-xs text-red-700">${error.message}</span>
              </div>
            </div>
          </div>
        `;
      }
    }
  }
};

  // Aktif sekmede selector test et (Kayıtlı Seçiciler listesinden)
  window.testSelectorInActiveTab = async function(selector, selectorType, resultElementId, modules = []) {
    const testResult = document.getElementById(resultElementId);
    
    if (!testResult) {
      console.error('Test sonuç elementi bulunamadı:', resultElementId);
      return;
    }
    
    // Loading state - Modern tasarım
    testResult.classList.remove('hidden');
    testResult.innerHTML = `
      <div class="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-2xl p-5 shadow-lg">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center shadow-md">
            <svg class="w-5 h-5 text-white animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
          </div>
          <div>
            <span class="text-sm font-bold text-blue-900 block">Test ediliyor...</span>
            <span class="text-xs text-blue-700">Aktif sekmede selector kontrol ediliyor</span>
          </div>
        </div>
      </div>
    `;
  
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab) {
      testResult.innerHTML = `
        <div class="bg-gradient-to-br from-red-50 to-pink-50 border-2 border-red-300 rounded-2xl p-5 shadow-lg">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-to-br from-red-500 to-pink-500 rounded-xl flex items-center justify-center shadow-md">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </div>
            <span class="text-sm font-bold text-red-900">Aktif bir sekme bulunamadı.</span>
          </div>
        </div>
      `;
      return;
    }
    
    // Content script'e test mesajı gönder
    chrome.tabs.sendMessage(tab.id, {
      action: 'testSelector',
      selector: selector,
      selectorType: selectorType,
      modules: modules || []
    }, (response) => {
      if (chrome.runtime.lastError) {
        testResult.innerHTML = `
          <div class="bg-gradient-to-br from-red-50 to-pink-50 border-2 border-red-300 rounded-2xl p-5 shadow-lg">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-gradient-to-br from-red-500 to-pink-500 rounded-xl flex items-center justify-center shadow-md">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </div>
              <div>
                <span class="text-sm font-bold text-red-900 block">Hata</span>
                <span class="text-xs text-red-700">${chrome.runtime.lastError.message}</span>
              </div>
            </div>
          </div>
        `;
        return;
      }
      
      if (response && response.success) {
        // Modüller artık content script'te uygulanıyor, burada sadece gösteriyoruz
        const processedValue = response.value !== undefined ? response.value : '(boş)';
        const rawValue = response.rawValue !== undefined ? response.rawValue : processedValue; // Eğer rawValue yoksa processedValue kullan
        const count = response.count || 0;
        let hasModules = modules && Array.isArray(modules) && modules.length > 0;
        
        // Escape HTML
        const escapeHtml = (text) => {
          const div = document.createElement('div');
          div.textContent = text;
          return div.innerHTML;
        };
        
        const rawValueEscaped = escapeHtml(rawValue);
        const processedValueEscaped = escapeHtml(String(processedValue));
        
        testResult.innerHTML = `
          <div class="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-300 rounded-2xl p-5 shadow-lg">
            <div class="flex items-center space-x-3 mb-4">
              <div class="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center shadow-lg">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div>
                <h4 class="text-base font-bold text-green-900">Test Başarılı!</h4>
                <p class="text-xs text-green-700">Selector doğru çalışıyor</p>
              </div>
            </div>
            <div class="space-y-4">
              <div class="grid grid-cols-2 gap-3">
                <div class="bg-white border-2 border-green-200 rounded-xl p-3 text-center">
                  <div class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Bulunan Öğe</div>
                  <div class="text-2xl font-bold text-green-700">${count}</div>
                </div>
                ${hasModules ? `
                <div class="bg-white border-2 border-blue-200 rounded-xl p-3 text-center">
                  <div class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Modül Sayısı</div>
                  <div class="text-2xl font-bold text-blue-700">${modules.length}</div>
                </div>
                ` : '<div></div>'}
              </div>
              <div class="bg-white border-2 border-gray-200 rounded-xl p-4">
                <div class="flex items-center space-x-2 mb-2">
                  <div class="w-6 h-6 bg-gradient-to-br from-gray-500 to-gray-600 rounded-lg flex items-center justify-center">
                    <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                  </div>
                  <span class="text-xs font-bold text-gray-600 uppercase tracking-wide">Ham Değer</span>
                </div>
                <div class="text-sm text-gray-900 font-mono bg-gray-50 border border-gray-300 rounded-lg p-3 break-all max-h-24 overflow-y-auto shadow-inner">${rawValueEscaped}</div>
              </div>
              ${hasModules ? `
              <div class="bg-white border-2 border-blue-200 rounded-xl p-4">
                <div class="flex items-center space-x-2 mb-2">
                  <div class="w-6 h-6 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center">
                    <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                    </svg>
                  </div>
                  <span class="text-xs font-bold text-gray-600 uppercase tracking-wide">İşlenmiş Değer</span>
                </div>
                <div class="text-sm text-gray-900 font-mono bg-blue-50 border border-blue-300 rounded-lg p-3 break-all max-h-24 overflow-y-auto shadow-inner font-semibold">${processedValueEscaped}</div>
              </div>
              ` : ''}
            </div>
          </div>
        `;
      } else {
        // Escape HTML fonksiyonu (ifTrue için de gerekli)
        const escapeHtml = (text) => {
          const div = document.createElement('div');
          div.textContent = text;
          return div.innerHTML;
        };
        
        // Eğer ifTrue modülü varsa
        const hasIfTrueModule = modules && Array.isArray(modules) && modules.includes('ifTrue');
        
        if (hasIfTrueModule && typeof applyModules === 'function') {
          let processedValue = false;
          try {
            processedValue = applyModules(null, modules);
          } catch (error) {
            console.error('Modül uygulama hatası:', error);
            processedValue = false;
          }
          
          const processedValueEscaped = escapeHtml(String(processedValue));
          
          testResult.innerHTML = `
            <div class="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-300 rounded-2xl p-5 shadow-lg">
              <div class="flex items-center space-x-3 mb-4">
                <div class="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center shadow-lg">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <div>
                  <h4 class="text-base font-bold text-green-900">Test Başarılı! (ifTrue)</h4>
                  <p class="text-xs text-green-700">Modül uygulandı</p>
                </div>
              </div>
              <div class="bg-white border-2 border-green-200 rounded-xl p-4">
                <div class="text-xs font-bold text-gray-600 uppercase tracking-wide mb-2">İşlenmiş Değer</div>
                <div class="text-lg font-bold text-gray-900 bg-gray-50 border border-gray-300 rounded-lg p-3 text-center">${processedValueEscaped}</div>
                <div class="text-xs text-gray-500 mt-2 text-center">Öğe bulunamadığı için false döndürüldü</div>
              </div>
            </div>
          `;
        } else {
          testResult.innerHTML = `
            <div class="bg-gradient-to-br from-red-50 to-pink-50 border-2 border-red-300 rounded-2xl p-5 shadow-lg">
              <div class="flex items-center space-x-3 mb-3">
                <div class="w-12 h-12 bg-gradient-to-br from-red-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </div>
                <div>
                  <h4 class="text-base font-bold text-red-900">Test Başarısız</h4>
                  <p class="text-xs text-red-700">Öğe bulunamadı</p>
                </div>
              </div>
              <div class="bg-white border-2 border-red-200 rounded-xl p-3">
                <p class="text-sm text-red-800 font-medium">Selector'ı kontrol edin. Öğe sayfada bulunamadı.</p>
              </div>
            </div>
          `;
        }
      }
    });
  } catch (error) {
    testResult.innerHTML = `
      <div class="bg-gradient-to-br from-red-50 to-pink-50 border-2 border-red-300 rounded-2xl p-5 shadow-lg">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-gradient-to-br from-red-500 to-pink-500 rounded-xl flex items-center justify-center shadow-md">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </div>
          <div>
            <span class="text-sm font-bold text-red-900 block">Hata</span>
            <span class="text-xs text-red-700">${error.message}</span>
          </div>
        </div>
      </div>
    `;
  }
};

