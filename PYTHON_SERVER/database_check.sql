-- ==========================================
-- VERİTABANI KONTROL SQL SCRİPTLERİ
-- ==========================================

-- 1️⃣ SON PARSE EDİLEN ATTRIBUTE DEĞERLERİ (Son 50 kayıt)
-- Bu tablo, Scrapy ve Selenium worker'larının parse ettiği değerleri tutar
SELECT 
    pav.id,
    pav.company_id,
    pav.attribute_id,
    pav.mpn,
    pav.value,
    pav.created_at,
    pav.updated_at,
    c.name as company_name,
    a.name as attribute_name
FROM product_attribute_value pav
LEFT JOIN company c ON c.id = pav.company_id
LEFT JOIN attribute a ON a.id = pav.attribute_id
ORDER BY pav.created_at DESC
LIMIT 50;

-- 2️⃣ BELİRLİ BİR MPN İÇİN PARSE EDİLEN TÜM ATTRIBUTE'LAR
-- Örnek: npm = 'MW123TU/A'
SELECT 
    pav.*,
    c.name as company_name,
    a.name as attribute_name,
    a.type as attribute_type
FROM product_attribute_value pav
LEFT JOIN company c ON c.id = pav.company_id
LEFT JOIN attribute a ON a.id = pav.attribute_id
WHERE pav.mpn = 'MW123TU/A'  -- <-- Buraya MPN yazın
ORDER BY pav.created_at DESC;

-- 3️⃣ BELİRLİ BİR COMPANY İÇİN SON PARSE EDİLEN KAYITLAR
SELECT 
    pav.mpn,
    COUNT(*) as toplam_attribute,
    MAX(pav.created_at) as son_parse_tarihi,
    c.name as company_name
FROM product_attribute_value pav
LEFT JOIN company c ON c.id = pav.company_id
WHERE pav.company_id = 2  -- <-- Buraya company_id yazın
GROUP BY pav.mpn, c.name
ORDER BY son_parse_tarihi DESC
LIMIT 20;

-- 4️⃣ BUGÜN PARSE EDİLEN KAYITLAR (Günlük özet)
SELECT 
    pav.company_id,
    c.name as company_name,
    COUNT(*) as toplam_kayit,
    COUNT(DISTINCT pav.mpn) as toplam_urun,
    MIN(pav.created_at) as ilk_kayit,
    MAX(pav.created_at) as son_kayit
FROM product_attribute_value pav
LEFT JOIN company c ON c.id = pav.company_id
WHERE DATE(pav.created_at) = CURRENT_DATE
GROUP BY pav.company_id, c.name
ORDER BY toplam_kayit DESC;

-- 5️⃣ CRAWLER LOGLARI (Son 20 çalıştırma)
SELECT 
    id,
    crawler_name,
    status,
    started_at,
    completed_at,
    total_products_processed as islenen,
    total_products_updated as guncellenen,
    total_products_created as olusturulan,
    execution_time_seconds as sure_saniye,
    error_message
FROM crawler_logs
ORDER BY started_at DESC
LIMIT 20;

-- 6️⃣ SON 24 SAAT İÇİNDE İŞLENEN JOB'LAR
SELECT 
    id,
    company_id,
    status,
    total_urls,
    message,
    started_at,
    finished_at,
    EXTRACT(EPOCH FROM (finished_at - started_at)) as sure_saniye
FROM job_logs
WHERE started_at > NOW() - INTERVAL '24 hours'
ORDER BY started_at DESC;

-- 7️⃣ ÜRÜN GEÇMİŞİ - FİYAT DEĞİŞİKLİKLERİ (Belirli bir MPN için)
SELECT 
    id,
    mpn,
    title,
    price,
    sale_price,
    availability,
    cron_source,
    created_at
FROM products_history
WHERE mpn = 'MW123TU/A'  -- <-- Buraya MPN yazın
ORDER BY created_at DESC
LIMIT 30;

-- 8️⃣ BUGÜN İŞLENEN ÜRÜNLER (Özet)
SELECT 
    COUNT(*) as toplam_kayit,
    COUNT(DISTINCT mpn) as farkli_urun,
    cron_source as kaynak
FROM products_history
WHERE DATE(created_at) = CURRENT_DATE
GROUP BY cron_source;

-- 9️⃣ SON PARSE EDİLEN ÜRÜNLER VE MEVCUT FİYATLARI
SELECT 
    p.mpn,
    p.title,
    p.price,
    p.availability,
    p.product_status,
    p.updated_at
FROM products p
ORDER BY p.updated_at DESC
LIMIT 50;

-- 🔟 ATTRIBUTE BAŞINA GÜNLÜK İSTATİSTİK
SELECT 
    a.id as attribute_id,
    a.name as attribute_name,
    COUNT(*) as toplam_parse,
    COUNT(DISTINCT pav.mpn) as farkli_urun,
    COUNT(DISTINCT pav.company_id) as farkli_company
FROM product_attribute_value pav
LEFT JOIN attribute a ON a.id = pav.attribute_id
WHERE DATE(pav.created_at) = CURRENT_DATE
GROUP BY a.id, a.name
ORDER BY toplam_parse DESC;

-- 1️⃣1️⃣ SON 1 SAAT İÇİNDE PARSE EDİLEN KAYITLAR (Canlı izleme için)
SELECT 
    pav.id,
    pav.mpn,
    pav.company_id,
    c.name as company_name,
    a.name as attribute_name,
    pav.value,
    pav.created_at,
    NOW() - pav.created_at as gecen_sure
FROM product_attribute_value pav
LEFT JOIN company c ON c.id = pav.company_id
LEFT JOIN attribute a ON a.id = pav.attribute_id
WHERE pav.created_at > NOW() - INTERVAL '1 hour'
ORDER BY pav.created_at DESC;

-- 1️⃣2️⃣ BAŞARISIZ CRAWLER ÇALIŞTIRMALARI
SELECT 
    id,
    crawler_name,
    status,
    error_message,
    started_at,
    completed_at
FROM crawler_logs
WHERE status = 'failed'
ORDER BY started_at DESC
LIMIT 10;

-- 1️⃣3️⃣ EN ÇOK PARSE EDİLEN MPN'LER (Popüler ürünler)
SELECT 
    mpn,
    COUNT(*) as toplam_parse,
    COUNT(DISTINCT company_id) as farkli_company,
    MAX(created_at) as son_parse
FROM product_attribute_value
GROUP BY mpn
ORDER BY toplam_parse DESC
LIMIT 20;

-- 1️⃣4️⃣ COMPANY BAZINDA PARSE İSTATİSTİKLERİ
SELECT 
    c.id,
    c.name as company_name,
    COUNT(pav.id) as toplam_parse,
    COUNT(DISTINCT pav.mpn) as farkli_urun,
    MAX(pav.created_at) as son_parse
FROM company c
LEFT JOIN product_attribute_value pav ON pav.company_id = c.id
GROUP BY c.id, c.name
ORDER BY toplam_parse DESC;

