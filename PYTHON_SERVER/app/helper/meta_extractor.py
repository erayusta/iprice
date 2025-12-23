"""
Meta/JSON Değer Çıkarıcı
Sayfa kaynağından meta tag veya JavaScript object'lerinden değer çıkarır
"""
import re
from typing import Any, Optional


def extract_from_html(html_content: str, meta_key: str) -> Optional[str]:
    """
    HTML içeriğinden meta key'e göre değer çıkar
    
    Args:
        html_content: Sayfa HTML içeriği
        meta_key: Aranacak key (örn: unit_sale_price)
    
    Returns:
        Bulunan değer veya None
    """
    # 1. Meta tag ara (product:price:amount)
    if meta_key == 'unit_sale_price':
        meta_pattern = r'<meta\s+property="product:price:amount"\s+content="([0-9.]+)"'
        match = re.search(meta_pattern, html_content, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # 2. Genel meta tag
    meta_pattern = f'<meta\\s+(?:property|name)="{meta_key}"\\s+content="([^"]+)"'
    match = re.search(meta_pattern, html_content, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # 3. JSON object'te ara (örn: "unit_sale_price":45999)
    json_pattern = f'"{meta_key}"\\s*:\\s*([0-9.]+)'
    match = re.search(json_pattern, html_content, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # 4. Tek tırnak ile
    json_pattern2 = f"'{meta_key}'\\s*:\\s*([0-9.]+)"
    match = re.search(json_pattern2, html_content, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # 5. insider_object içinde ara (string içinde) - ÖNCE BUNU DENESİN
    if meta_key == 'unit_sale_price':
        # Önce insider_object.product.unit_sale_price pattern'i (önce en spesifik)
        insider_patterns = [
            # window.insider_object.product = {"unit_sale_price":9999,...} (ASSIGNMENT FORMAT)
            r'window\.insider_object\.product\s*=\s*\{[^}]*?"unit_sale_price"\s*:\s*([0-9.]+)',
            # insider_object.product = {"unit_sale_price":9999,...}
            r'insider_object\.product\s*=\s*\{[^}]*?"unit_sale_price"\s*:\s*([0-9.]+)',
            # window.insider_object = {product: {"unit_sale_price":9999,...}}
            r'window\.insider_object\s*=\s*\{[^}]*?product\s*:\s*\{[^}]*?"unit_sale_price"\s*:\s*([0-9.]+)',
            # insider_object = {product: {"unit_sale_price":9999,...}}
            r'insider_object\s*=\s*\{[^}]*?product\s*:\s*\{[^}]*?"unit_sale_price"\s*:\s*([0-9.]+)',
            # Genel pattern (JSON içinde)
            r'insider_object["\']?\s*:\s*\{[^}]*?product["\']?\s*:\s*\{[^}]*?"unit_sale_price"\s*:\s*([0-9.]+)',
            # window.insider_object.product unit_sale_price (genel)
            r'window\.insider_object.*?product.*?"unit_sale_price"\s*:\s*([0-9.]+)',
            # Genel
            r'insider_object.*?product.*?"unit_sale_price"\s*:\s*([0-9.]+)',
        ]
        for pattern in insider_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if match:
                found_value = match.group(1)
                try:
                    num_value = float(found_value)
                    if 100 <= num_value <= 1000000:  # Makul fiyat aralığı
                        print(f"   ✅ insider_object pattern ile değer bulundu: {found_value}")
                        return str(int(num_value))
                except:
                    pass
    else:
        insider_pattern = f'insider_object.*?product.*?{meta_key}\\s*[:=]\\s*([0-9.]+)'
        match = re.search(insider_pattern, html_content, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
    
    # 6. Daha spesifik unit_sale_price pattern'leri (sadece güvenilir kaynaklardan)
    if meta_key == 'unit_sale_price':
        # Sadece güvenilir JSON structure'lardan ara (genel sayı araması kaldırıldı)
        specific_patterns = [
            # JSON içinde unit_sale_price ile bağlantılı pattern'ler
            r'product["\']?\s*:\s*\{[^}]*?unit_sale_price["\']?\s*:\s*([0-9.]+)',
            r'insider_object["\']?\s*:\s*\{[^}]*?product["\']?\s*:\s*\{[^}]*?unit_sale_price["\']?\s*:\s*([0-9.]+)',
            # Script tag içinde JSON
            r'<script[^>]*>.*?unit_sale_price["\']?\s*:\s*([0-9.]+).*?</script>',
        ]
        
        for pattern in specific_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if match:
                found_value = match.group(1)
                # Değeri doğrula (makul fiyat aralığında mı?)
                try:
                    num_value = float(found_value)
                    if 100 <= num_value <= 1000000:  # Makul fiyat aralığı
                        print(f"   ✅ Spesifik pattern ile değer bulundu: {found_value}")
                        return str(int(num_value))
                except:
                    pass
    
    return None


def extract_with_selenium(driver, meta_key: str) -> Optional[str]:
    """
    Selenium driver ile meta değer çıkar
    JavaScript execution ile de dener
    """
    try:
        # Önce JavaScript ile dene (daha güvenilir)
        print(f"🔍 Meta extraction başlıyor: {meta_key}")
        
        # Debug: insider_object'in var olup olmadığını kontrol et
        try:
            insider_check = driver.execute_script("""
                var result = {
                    has_insider: false,
                    has_product: false,
                    has_unit_sale_price: false,
                    value: null,
                    keys: []
                };
                
                if (window.insider_object) {
                    result.has_insider = true;
                    if (window.insider_object.product) {
                        result.has_product = true;
                        result.keys = Object.keys(window.insider_object.product);
                        if (window.insider_object.product.unit_sale_price !== undefined) {
                            result.has_unit_sale_price = true;
                            result.value = window.insider_object.product.unit_sale_price;
                        }
                    }
                }
                return result;
            """)
            print(f"   🔍 Debug insider_object kontrolü: {insider_check}")
            if insider_check.get('has_unit_sale_price') and insider_check.get('value'):
                print(f"   ✅ insider_object.product.unit_sale_price bulundu: {insider_check.get('value')}")
                return str(insider_check.get('value'))
        except Exception as debug_e:
            print(f"   ⚠️ Debug kontrolü hatası: {str(debug_e)[:100]}")
        
        js_result = driver.execute_script(f"""
            var debug_info = [];
            
            // 1. Meta tag ile dene
            if ('{meta_key}' === 'unit_sale_price') {{
                var metaPrice = document.querySelector('meta[property="product:price:amount"]');
                if (metaPrice) {{
                    debug_info.push('Meta tag bulundu');
                    return {{found: true, value: metaPrice.getAttribute('content'), source: 'meta_tag'}};
                }}
            }}
            
            // 2. window.insider_object'ten dene (Gürgençler için)
            if (window.insider_object) {{
                debug_info.push('insider_object var');
                if (window.insider_object.product) {{
                    debug_info.push('insider_object.product var');
                    var keys = Object.keys(window.insider_object.product);
                    debug_info.push('Product keys: ' + keys.join(', '));
                    
                    var value = window.insider_object.product['{meta_key}'];
                    if (value !== undefined && value !== null) {{
                        debug_info.push('Value found in product object');
                        return {{found: true, value: String(value), source: 'insider_object.product', debug: debug_info}};
                    }}
                    
                    // unit_sale_price için özel kontrol
                    if ('{meta_key}' === 'unit_sale_price' && window.insider_object.product.unit_sale_price) {{
                        debug_info.push('unit_sale_price found directly');
                        return {{found: true, value: String(window.insider_object.product.unit_sale_price), source: 'insider_object.product.unit_sale_price', debug: debug_info}};
                    }}
                }} else {{
                    debug_info.push('insider_object.product YOK');
                }}
            }} else {{
                debug_info.push('insider_object YOK');
            }}
            
            // 3. dataLayer'dan dene
            if (window.dataLayer) {{
                debug_info.push('dataLayer var, length: ' + window.dataLayer.length);
                for (var i = 0; i < window.dataLayer.length; i++) {{
                    if (window.dataLayer[i].product) {{
                        var value = window.dataLayer[i].product['{meta_key}'];
                        if (value !== undefined && value !== null) {{
                            debug_info.push('Value found in dataLayer');
                            return {{found: true, value: String(value), source: 'dataLayer', debug: debug_info}};
                        }}
                    }}
                }}
            }} else {{
                debug_info.push('dataLayer YOK');
            }}
            
            // 4. Genel meta tag araması
            var metaByProperty = document.querySelector('meta[property="{meta_key}"]');
            if (metaByProperty) {{
                debug_info.push('Meta property bulundu');
                return {{found: true, value: metaByProperty.getAttribute('content'), source: 'meta_property', debug: debug_info}};
            }}
            
            var metaByName = document.querySelector('meta[name="{meta_key}"]');
            if (metaByName) {{
                debug_info.push('Meta name bulundu');
                return {{found: true, value: metaByName.getAttribute('content'), source: 'meta_name', debug: debug_info}};
            }}
            
            return {{found: false, debug: debug_info}};
        """)
        
        # Debug bilgisini göster
        if isinstance(js_result, dict):
            if js_result.get('found'):
                print(f"✅ Meta değer bulundu: {js_result.get('value')} (source: {js_result.get('source')})")
                if js_result.get('debug'):
                    print(f"   Debug: {', '.join(js_result.get('debug', []))}")
                return str(js_result.get('value'))
            else:
                print(f"❌ Meta değer bulunamadı")
                if js_result.get('debug'):
                    print(f"   Debug: {', '.join(js_result.get('debug', []))}")
        elif js_result:
            print(f"✅ Meta değer bulundu (basit format): {js_result}")
            return str(js_result)
            
    except Exception as js_e:
        print(f"⚠️ JavaScript meta extraction hatası: {str(js_e)[:100]}")
        import traceback
        traceback.print_exc()
    
    # Fallback: HTML'den regex ile ara
    try:
        print(f"📄 HTML fallback deneniyor...")
        page_source = driver.page_source
        
        # Debug: insider_object.product geçiyor mu?
        if meta_key == 'unit_sale_price':
            if 'insider_object' in page_source and 'product' in page_source:
                # Önce window.insider_object.product = {...} pattern'ini ara
                # Nested JSON için daha geniş context kullan
                insider_match = re.search(r'window\.insider_object\.product\s*=\s*\{([^}]+?"unit_sale_price"[^}]+)', page_source, re.IGNORECASE | re.DOTALL)
                if insider_match:
                    product_json = insider_match.group(1)
                    print(f"   🔍 insider_object.product JSON bulundu: {product_json[:300]}...")
                    # unit_sale_price'ı ara
                    unit_price_match = re.search(r'"unit_sale_price"\s*:\s*([0-9.]+)', product_json)
                    if unit_price_match:
                        found_value = unit_price_match.group(1)
                        print(f"   ✅ HTML fallback'te insider_object.product içinde unit_sale_price bulundu: {found_value}")
                        try:
                            num_value = float(found_value)
                            if 100 <= num_value <= 1000000:
                                return str(int(num_value))
                        except:
                            pass
                else:
                    # Alternatif: sadece unit_sale_price pattern'ini ara (insider_object context'i içinde)
                    context_match = re.search(r'window\.insider_object[^}]*?"unit_sale_price"\s*:\s*([0-9.]+)', page_source, re.IGNORECASE | re.DOTALL)
                    if context_match:
                        found_value = context_match.group(1)
                        print(f"   ✅ HTML fallback'te insider_object context'inde unit_sale_price bulundu: {found_value}")
                        try:
                            num_value = float(found_value)
                            if 100 <= num_value <= 1000000:
                                return str(int(num_value))
                        except:
                            pass
        
        result = extract_from_html(page_source, meta_key)
        if result:
            print(f"✅ HTML'den değer bulundu: {result}")
        else:
            print(f"❌ HTML'den değer bulunamadı")
            # Debug: Sayfa kaynağında unit_sale_price geçiyor mu?
            if 'unit_sale_price' in page_source.lower():
                print(f"   ⚠️ 'unit_sale_price' string'i sayfa kaynağında var ama parse edilemedi")
                # İlk 500 karakteri göster
                index = page_source.lower().find('unit_sale_price')
                if index != -1:
                    start = max(0, index - 200)
                    end = min(len(page_source), index + 300)
                    print(f"   📄 Context: ...{page_source[start:end]}...")
        return result
    except Exception as html_e:
        print(f"⚠️ HTML meta extraction hatası: {str(html_e)[:100]}")
        import traceback
        traceback.print_exc()
        return None

