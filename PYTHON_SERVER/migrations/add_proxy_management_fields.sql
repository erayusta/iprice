-- ========================================
-- Proxy Management Fields Migration
-- ========================================
-- Bu script, proxies tablosuna akıllı proxy yönetimi için
-- gerekli yeni alanları ekler.
--
-- Kullanım:
-- psql -h 68.219.209.108 -U postgres -d price_analysis -f add_proxy_management_fields.sql
-- ========================================

-- 1. is_active alanı ekle (varsayılan: true)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'proxies' AND column_name = 'is_active'
    ) THEN
        ALTER TABLE proxies 
        ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;
        
        RAISE NOTICE '✅ is_active alanı eklendi';
    ELSE
        RAISE NOTICE '⚠️ is_active alanı zaten mevcut';
    END IF;
END $$;

-- 2. failure_count alanı ekle (varsayılan: 0)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'proxies' AND column_name = 'failure_count'
    ) THEN
        ALTER TABLE proxies 
        ADD COLUMN failure_count INTEGER NOT NULL DEFAULT 0;
        
        RAISE NOTICE '✅ failure_count alanı eklendi';
    ELSE
        RAISE NOTICE '⚠️ failure_count alanı zaten mevcut';
    END IF;
END $$;

-- 3. last_used_at alanı ekle (nullable)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'proxies' AND column_name = 'last_used_at'
    ) THEN
        ALTER TABLE proxies 
        ADD COLUMN last_used_at TIMESTAMP WITH TIME ZONE;
        
        RAISE NOTICE '✅ last_used_at alanı eklendi';
    ELSE
        RAISE NOTICE '⚠️ last_used_at alanı zaten mevcut';
    END IF;
END $$;

-- 4. is_active için index oluştur (hızlı filtreleme için)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'proxies' AND indexname = 'ix_proxies_is_active'
    ) THEN
        CREATE INDEX ix_proxies_is_active ON proxies(is_active);
        
        RAISE NOTICE '✅ ix_proxies_is_active index oluşturuldu';
    ELSE
        RAISE NOTICE '⚠️ ix_proxies_is_active index zaten mevcut';
    END IF;
END $$;

-- 5. Doğrulama (opsiyonel)
DO $$ 
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ PROXY MANAGEMENT FIELDS EKLENDI';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Eklenen alanlar:';
    RAISE NOTICE '  - is_active (boolean, default: true)';
    RAISE NOTICE '  - failure_count (integer, default: 0)';
    RAISE NOTICE '  - last_used_at (timestamp, nullable)';
    RAISE NOTICE '';
    RAISE NOTICE 'Eklenen index:';
    RAISE NOTICE '  - ix_proxies_is_active';
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
END $$;

-- 6. Tablo yapısını göster (kontrol için)
\d proxies

