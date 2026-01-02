<?php

/**
 * JSON dosyasındaki null_value hatalarını analiz eder ve firma/URL bazında gruplar
 * 
 * Kullanım: php analyze_null_value_errors.php
 */

$inputFile = __DIR__ . '/../DATA/chrome_db_queue_error_messages.json';
$outputFile = __DIR__ . '/../DATA/null_value_errors_grouped.json';

echo "🔍 Null Value Hataları Analiz Ediliyor...\n";
echo "Input: {$inputFile}\n";
echo "Output: {$outputFile}\n\n";

if (!file_exists($inputFile)) {
    die("❌ HATA: Input dosyası bulunamadı: {$inputFile}\n");
}

// JSON dosyasını oku
echo "📖 JSON dosyası okunuyor...\n";
$jsonContent = file_get_contents($inputFile);
$data = json_decode($jsonContent, true);

if (!$data || !isset($data['messages'])) {
    die("❌ HATA: JSON dosyası geçersiz veya messages bulunamadı.\n");
}

$totalMessages = count($data['messages']);
echo "✅ {$totalMessages} mesaj yüklendi.\n\n";

// Null value hatalarını topla
echo "🔍 Null value hataları filtreleniyor...\n";

$nullValueErrors = [];
$companyUrlMap = []; // company_id -> domain -> URLs

foreach ($data['messages'] as $message) {
    $messageData = $message['data'] ?? null;
    if (!$messageData) {
        continue;
    }
    
    // Errors array'ini kontrol et
    $errors = $messageData['original_message']['errors'] ?? [];
    $hasNullValueError = false;
    
    // Null value hatası var mı kontrol et
    foreach ($errors as $error) {
        if (isset($error['error_type']) && $error['error_type'] === 'null_value') {
            $hasNullValueError = true;
            break;
        }
    }
    
    if (!$hasNullValueError) {
        continue;
    }
    
    // URL ve company bilgilerini al
    $url = $messageData['url'] ?? $messageData['original_message']['url'] ?? null;
    $companyId = $messageData['company_id'] ?? $messageData['original_message']['company_id'] ?? null;
    
    if (!$url) {
        continue;
    }
    
    // Domain'i çıkar
    $domain = extractDomain($url);
    $companyName = extractCompanyName($domain);
    
    // Company ID yoksa domain'den çıkar
    if (!$companyId) {
        $companyId = 'unknown_' . $companyName;
    }
    
    // İlk kez görülen company için array oluştur
    if (!isset($companyUrlMap[$companyId])) {
        $companyUrlMap[$companyId] = [
            'company_id' => $companyId,
            'company_name' => $companyName,
            'domain' => $domain,
            'urls' => []
        ];
    }
    
    // URL'i ekle (duplicate kontrolü)
    if (!in_array($url, $companyUrlMap[$companyId]['urls'])) {
        $companyUrlMap[$companyId]['urls'][] = $url;
    }
    
    $nullValueErrors[] = [
        'index' => $message['index'] ?? null,
        'url' => $url,
        'company_id' => $companyId,
        'company_name' => $companyName,
        'domain' => $domain,
        'job_id' => $messageData['job_id'] ?? null,
        'product_id' => $messageData['product_id'] ?? null,
        'errors' => array_filter($errors, function($e) {
            return isset($e['error_type']) && $e['error_type'] === 'null_value';
        })
    ];
}

echo "✅ {$totalMessages} mesajdan " . count($nullValueErrors) . " adet null_value hatası bulundu.\n\n";

// Firma bazında grupla ve örnek URL'leri hazırla
echo "📊 Firma bazında gruplanıyor...\n";

$groupedByCompany = [];

foreach ($companyUrlMap as $companyId => $companyData) {
    $urls = $companyData['urls'];
    $sampleUrls = array_slice($urls, 0, 5); // İlk 5 URL'i örnek olarak al
    
    $groupedByCompany[] = [
        'firma' => $companyData['company_name'],
        'company_id' => $companyId,
        'domain' => $companyData['domain'],
        'toplam_hata_sayisi' => count($urls),
        'ornek_url_sayisi' => min(5, count($urls)),
        'ornek_urls' => $sampleUrls,
        'tum_urls' => $urls // Tüm URL'leri de ekle (isteğe bağlı)
    ];
}

// Firma adına göre sırala
usort($groupedByCompany, function($a, $b) {
    return strcmp($a['firma'], $b['firma']);
});

// Sonuç JSON'u hazırla
$result = [
    'analiz_bilgileri' => [
        'analiz_tarihi' => date('Y-m-d H:i:s'),
        'toplam_mesaj_sayisi' => $totalMessages,
        'null_value_hata_sayisi' => count($nullValueErrors),
        'firma_sayisi' => count($groupedByCompany)
    ],
    'firmalar' => $groupedByCompany
];

// JSON dosyasına kaydet
echo "💾 Sonuçlar JSON dosyasına kaydediliyor...\n";

$jsonContent = json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);

if (file_put_contents($outputFile, $jsonContent) === false) {
    die("❌ HATA: Dosya yazılamadı: {$outputFile}\n");
}

$fileSize = filesize($outputFile);
$fileSizeKB = round($fileSize / 1024, 2);

echo "✅ Analiz tamamlandı!\n";
echo "   📄 Dosya: {$outputFile}\n";
echo "   📊 Toplam firma: " . count($groupedByCompany) . "\n";
echo "   📊 Toplam null_value hatası: " . count($nullValueErrors) . "\n";
echo "   💾 Dosya boyutu: {$fileSizeKB} KB\n\n";

// Özet bilgileri göster
echo "📋 Özet:\n";
foreach ($groupedByCompany as $company) {
    echo "   • {$company['firma']}: {$company['toplam_hata_sayisi']} hata\n";
}

echo "\n🎉 İşlem tamamlandı!\n";

/**
 * URL'den domain çıkarır
 */
function extractDomain($url) {
    try {
        $parsedUrl = parse_url($url);
        $host = $parsedUrl['host'] ?? '';
        
        // www. prefix'ini kaldır
        if (strpos($host, 'www.') === 0) {
            $host = substr($host, 4);
        }
        
        return $host;
    } catch (Exception $e) {
        return 'unknown';
    }
}

/**
 * Domain'den firma adını çıkarır
 */
function extractCompanyName($domain) {
    // Domain'den firma adını çıkar (örn: gurgencler.com.tr -> gurgencler)
    $parts = explode('.', $domain);
    
    if (count($parts) > 0) {
        return $parts[0];
    }
    
    return $domain;
}

