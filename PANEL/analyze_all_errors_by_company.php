<?php

/**
 * JSON dosyasındaki TÜM hataları firma/domain bazında gruplar
 * 
 * Kullanım: php analyze_all_errors_by_company.php
 */

$inputFile = __DIR__ . '/../DATA/chrome_db_queue_error_messages.json';
$outputFile = __DIR__ . '/../DATA/all_errors_grouped_by_company.json';

echo "🔍 Tüm Hatalar Firma Bazında Gruplanıyor...\n";
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

// Tüm hataları firma bazında topla
echo "🔍 Hatalar firma bazında gruplanıyor...\n";

$companyUrlMap = []; // company_id -> domain -> URLs

foreach ($data['messages'] as $message) {
    $messageData = $message['data'] ?? null;
    if (!$messageData) {
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
}

echo "✅ Toplam " . count($companyUrlMap) . " firma bulundu.\n\n";

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
        'tum_urls' => $urls // Tüm URL'leri de ekle
    ];
}

// Hata sayısına göre sırala (en çok hatadan en aza)
usort($groupedByCompany, function($a, $b) {
    return $b['toplam_hata_sayisi'] - $a['toplam_hata_sayisi'];
});

// Sonuç JSON'u hazırla
$result = [
    'analiz_bilgileri' => [
        'analiz_tarihi' => date('Y-m-d H:i:s'),
        'toplam_mesaj_sayisi' => $totalMessages,
        'toplam_hata_sayisi' => array_sum(array_column($groupedByCompany, 'toplam_hata_sayisi')),
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
echo "   📊 Toplam hata: " . $result['analiz_bilgileri']['toplam_hata_sayisi'] . "\n";
echo "   💾 Dosya boyutu: {$fileSizeKB} KB\n\n";

// Özet bilgileri göster
echo "📋 Özet (Hata Sayısına Göre Sıralı):\n";
foreach ($groupedByCompany as $company) {
    echo "   • {$company['firma']} ({$company['domain']}): {$company['toplam_hata_sayisi']} hata\n";
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

