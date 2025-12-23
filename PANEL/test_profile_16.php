<?php

require __DIR__ . '/vendor/autoload.php';

$app = require_once __DIR__ . '/bootstrap/app.php';
$app->make('Illuminate\Contracts\Console\Kernel')->bootstrap();

use Illuminate\Support\Facades\DB;

$profileId = 16;

echo "=== Profile 16 Test ===\n\n";

// 1. Profile'ı kontrol et
echo "1. Profile kontrolü:\n";
$profile = DB::table('custom_profiles')->where('id', $profileId)->first();
if (!$profile) {
    echo "   ❌ Profile bulunamadı!\n";
    exit;
}
echo "   ✓ Profile bulundu: {$profile->name}\n\n";

// 2. Profile ürünlerini bul
echo "2. Profile ürünleri:\n";
$profileProductIds = DB::table('custom_profile_products')
    ->where('custom_profile_id', $profileId)
    ->pluck('user_product_id')
    ->toArray();

if (empty($profileProductIds)) {
    echo "   ❌ Profile'da ürün bulunamadı!\n";
    exit;
}

echo "   ✓ " . count($profileProductIds) . " ürün bulundu\n";
echo "   Ürün ID'leri: " . implode(', ', array_slice($profileProductIds, 0, 10)) . (count($profileProductIds) > 10 ? '...' : '') . "\n\n";

// 3. URL'leri bul
echo "3. URL'leri bulma:\n";
$query = "
    SELECT 
        c.id as company_id,
        c.crawler_id,
        c.server_id,
        c.screenshot,
        c.marketplace,
        c.use_proxy,
        c.proxy_id,
        cpu.product_id,
        cpu.url,
        up.mpn,
        cl.name as crawler_name,
        sl.name as server_name
    FROM companies c
    LEFT JOIN crawler_list cl ON c.crawler_id = cl.id
    LEFT JOIN server_list sl ON c.server_id = sl.id
    INNER JOIN company_products_urls cpu ON c.id = cpu.company_id
    INNER JOIN user_products up ON cpu.product_id::bigint = up.id
    WHERE c.deleted = false
    AND up.is_active = 1
    AND up.id IN (" . implode(',', array_map('intval', $profileProductIds)) . ")
";

$urls = DB::select($query);

if (empty($urls)) {
    echo "   ❌ URL bulunamadı!\n";
    exit;
}

echo "   ✓ " . count($urls) . " URL bulundu\n\n";

// 4. Company ID'leri topla
echo "4. Company ID'leri:\n";
$companyIds = [];
foreach ($urls as $url) {
    $companyIds[] = $url->company_id;
}
$companyIds = array_unique($companyIds);
echo "   ✓ " . count($companyIds) . " benzersiz company bulundu\n";
echo "   Company ID'leri: " . implode(', ', array_slice($companyIds, 0, 10)) . (count($companyIds) > 10 ? '...' : '') . "\n\n";

// 5. Attributes'ları bul
echo "5. Attributes kontrolü:\n";
$attributes = DB::table('company_attributes as ca')
    ->join('attributes as a', 'ca.attribute_id', '=', 'a.id')
    ->whereIn('ca.company_id', $companyIds)
    ->where('ca.value', '!=', '-1')
    ->select('ca.company_id', 'a.id as attributes_id', 'a.name as attributes_name', 'ca.type as attributes_type', 'ca.value as attributes_value')
    ->get()
    ->groupBy('company_id');

echo "   ✓ " . $attributes->count() . " company için attributes bulundu\n\n";

// 6. Her URL için attributes kontrolü
echo "6. URL başına attributes kontrolü:\n";
$urlsWithAttributes = 0;
$urlsWithoutAttributes = 0;
$urlsWithoutAttributesDetails = [];

foreach ($urls as $url) {
    $companyAttributes = $attributes->get($url->company_id, collect());
    
    if ($companyAttributes->isEmpty()) {
        $urlsWithoutAttributes++;
        $urlsWithoutAttributesDetails[] = [
            'company_id' => $url->company_id,
            'url' => $url->url,
            'company_name' => DB::table('companies')->where('id', $url->company_id)->value('name') ?? 'Bilinmiyor'
        ];
    } else {
        $urlsWithAttributes++;
    }
}

echo "   ✓ Attributes'lı URL sayısı: $urlsWithAttributes\n";
echo "   ❌ Attributes'sız URL sayısı: $urlsWithoutAttributes\n\n";

if ($urlsWithoutAttributes > 0) {
    echo "7. Attributes'sız URL detayları (ilk 10):\n";
    foreach (array_slice($urlsWithoutAttributesDetails, 0, 10) as $detail) {
        echo "   - Company ID: {$detail['company_id']} ({$detail['company_name']})\n";
        echo "     URL: {$detail['url']}\n";
        
        // Bu company için gerçekten attributes var mı kontrol et
        $checkAttributes = DB::table('company_attributes')
            ->where('company_id', $detail['company_id'])
            ->where('value', '!=', '-1')
            ->count();
        echo "     DB'de attributes sayısı: $checkAttributes\n";
        
        // Company'nin deleted durumunu kontrol et
        $company = DB::table('companies')->where('id', $detail['company_id'])->first();
        if ($company) {
            echo "     Company deleted: " . ($company->deleted ? 'true' : 'false') . "\n";
        }
        echo "\n";
    }
}

// 8. Sonuç
echo "=== SONUÇ ===\n";
if ($urlsWithoutAttributes > 0) {
    echo "❌ SORUN BULUNDU: $urlsWithoutAttributes URL için attributes bulunamadı!\n";
    echo "   Bu URL'ler job'a eklenmiyor (kod 672-675 satırlarında continue ediliyor).\n";
    echo "   Eğer tüm URL'ler attributes'sızsa, job boş kalıyor ve hata veriyor.\n";
} else {
    echo "✓ Tüm URL'ler için attributes mevcut.\n";
    echo "   Sorun başka bir yerde olabilir.\n";
}









