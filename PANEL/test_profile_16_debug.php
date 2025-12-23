<?php

require __DIR__ . '/vendor/autoload.php';

$app = require_once __DIR__ . '/bootstrap/app.php';
$app->make('Illuminate\Contracts\Console\Kernel')->bootstrap();

use Illuminate\Support\Facades\DB;

$profileId = 16;
$productId = 737;

echo "=== Profile 16 Debug ===\n\n";

// 1. Product'ı kontrol et
echo "1. Product 737 kontrolü:\n";
$product = DB::table('user_products')->where('id', $productId)->first();
if (!$product) {
    echo "   ❌ Product bulunamadı!\n";
    exit;
}
echo "   ✓ Product bulundu: {$product->name}\n";
echo "   is_active: {$product->is_active}\n\n";

// 2. Company products URLs kontrolü
echo "2. Company Products URLs kontrolü:\n";
$cpuRecords = DB::table('company_products_urls')
    ->where('product_id', $productId)
    ->get();

echo "   ✓ " . count($cpuRecords) . " kayıt bulundu\n";
foreach ($cpuRecords as $cpu) {
    echo "   - Company ID: {$cpu->company_id}, URL: {$cpu->url}\n";
    
    // Company kontrolü
    $company = DB::table('companies')->where('id', $cpu->company_id)->first();
    if ($company) {
        echo "     Company: {$company->name}, deleted: " . ($company->deleted ? 'true' : 'false') . "\n";
    } else {
        echo "     ❌ Company bulunamadı!\n";
    }
}
echo "\n";

// 3. SQL sorgusunu test et
echo "3. SQL sorgusu testi:\n";
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
    AND up.id = {$productId}
";

echo "   SQL: " . str_replace("\n", " ", $query) . "\n\n";

$urls = DB::select($query);
echo "   ✓ " . count($urls) . " sonuç bulundu\n\n";

// 4. Product ID tipini kontrol et
echo "4. Product ID tip kontrolü:\n";
$cpuSample = DB::table('company_products_urls')->where('product_id', $productId)->first();
if ($cpuSample) {
    echo "   cpu.product_id değeri: {$cpuSample->product_id}\n";
    echo "   cpu.product_id tipi: " . gettype($cpuSample->product_id) . "\n";
    
    // Cast testi
    $castTest = DB::select("SELECT cpu.product_id::bigint as casted_id FROM company_products_urls cpu WHERE cpu.product_id = ? LIMIT 1", [$cpuSample->product_id]);
    if ($castTest) {
        echo "   Cast edilmiş değer: {$castTest[0]->casted_id}\n";
    }
}
echo "\n";

// 5. Alternatif sorgu (cast olmadan)
echo "5. Alternatif sorgu (cast olmadan):\n";
$query2 = "
    SELECT 
        c.id as company_id,
        cpu.product_id,
        cpu.url
    FROM companies c
    INNER JOIN company_products_urls cpu ON c.id = cpu.company_id
    INNER JOIN user_products up ON cpu.product_id = up.id::text
    WHERE c.deleted = false
    AND up.is_active = 1
    AND up.id = {$productId}
";

$urls2 = DB::select($query2);
echo "   ✓ " . count($urls2) . " sonuç bulundu (alternatif sorgu)\n\n";

// 6. En basit sorgu
echo "6. En basit sorgu:\n";
$query3 = "
    SELECT 
        c.id as company_id,
        cpu.product_id,
        cpu.url
    FROM companies c
    INNER JOIN company_products_urls cpu ON c.id = cpu.company_id
    WHERE c.deleted = false
    AND cpu.product_id::text = '{$productId}'
";

$urls3 = DB::select($query3);
echo "   ✓ " . count($urls3) . " sonuç bulundu (basit sorgu)\n";









