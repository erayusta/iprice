-- ========================================
-- Proxy Management Fields Rollback
-- ========================================
-- Bu script, proxy management alanlarını GERİ ALIR.
--
-- Kullanım:
-- psql -h 68.219.209.108 -U postgres -d price_analysis -f rollback_proxy_management_fields.sql
--
-- ⚠️ DİKKAT: Bu işlem VERİ KAYBINA sebep olur!
-- is_active, failure_count, last_used_at alanlarındaki
-- tüm veriler silinecektir.
-- ========================================

-- Onay mesajı
DO $$ 
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE '⚠️ ROLLBACK BAŞLIYOR';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Aşağıdaki değişiklikler yapılacak:';
    RAISE NOTICE '  - is_active alanı SİLİNECEK';
    RAISE NOTICE '  - failure_count alanı SİLİNECEK';
    RAISE NOTICE '  - last_used_at alanı SİLİNECEK';
    RAISE NOTICE '  - ix_proxies_is_active index SİLİNECEK';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️ Bu işlem VERİ KAYBINA sebep olur!';
    RAISE NOTICE '';
END $$;

-- 1. Index'i sil
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'proxies' AND indexname = 'ix_proxies_is_active'
    ) THEN
        DROP INDEX ix_proxies_is_active;
        
        RAISE NOTICE '✅ ix_proxies_is_active index silindi';
    ELSE
        RAISE NOTICE '⚠️ ix_proxies_is_active index bulunamadı';
    END IF;
END $$;

-- 2. last_used_at alanını sil
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'proxies' AND column_name = 'last_used_at'
    ) THEN
        ALTER TABLE proxies DROP COLUMN last_used_at;
        
        RAISE NOTICE '✅ last_used_at alanı silindi';
    ELSE
        RAISE NOTICE '⚠️ last_used_at alanı bulunamadı';
    END IF;
END $$;

-- 3. failure_count alanını sil
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'proxies' AND column_name = 'failure_count'
    ) THEN
        ALTER TABLE proxies DROP COLUMN failure_count;
        
        RAISE NOTICE '✅ failure_count alanı silindi';
    ELSE
        RAISE NOTICE '⚠️ failure_count alanı bulunamadı';
    END IF;
END $$;

-- 4. is_active alanını sil
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'proxies' AND column_name = 'is_active'
    ) THEN
        ALTER TABLE proxies DROP COLUMN is_active;
        
        RAISE NOTICE '✅ is_active alanı silindi';
    ELSE
        RAISE NOTICE '⚠️ is_active alanı bulunamadı';
    END IF;
END $$;

-- 5. Onay mesajı
DO $$ 
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ ROLLBACK TAMAMLANDI';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Silinen alanlar:';
    RAISE NOTICE '  - is_active';
    RAISE NOTICE '  - failure_count';
    RAISE NOTICE '  - last_used_at';
    RAISE NOTICE '';
    RAISE NOTICE 'Silinen index:';
    RAISE NOTICE '  - ix_proxies_is_active';
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
END $$;

-- 6. Tablo yapısını göster (kontrol için)
\d proxies

