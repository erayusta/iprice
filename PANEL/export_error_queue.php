<?php

/**
 * RabbitMQ chrome.db.queue.error kuyruğundaki tüm mesajları JSON dosyasına aktarır
 * 
 * Kullanım: php export_error_queue.php
 */

require __DIR__ . '/vendor/autoload.php';

use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

// RabbitMQ bağlantı bilgileri
$rabbitmqHost = '10.20.50.16';
$rabbitmqPort = 5672;
$rabbitmqUser = 'admin';
$rabbitmqPass = 'admin123';
$vhost = 'chrome';
$queueName = 'chrome.db.queue.error';

// Çıktı dosyası
$outputFile = __DIR__ . '/../DATA/chrome_db_queue_error_messages.json';

echo "🚀 RabbitMQ Error Queue Export Başlatılıyor...\n";
echo "Queue: {$queueName}\n";
echo "Output: {$outputFile}\n\n";

try {
    // RabbitMQ'ya bağlan
    echo "📡 RabbitMQ'ya bağlanılıyor...\n";
    $connection = new AMQPStreamConnection(
        $rabbitmqHost,
        $rabbitmqPort,
        $rabbitmqUser,
        $rabbitmqPass,
        $vhost,
        false,
        'AMQPLAIN',
        null,
        'en_US',
        3.0, // connection_timeout
        3.0, // read_write_timeout
        null,
        false,
        60   // heartbeat
    );

    $channel = $connection->channel();
    
    // Queue'yu declare et
    $channel->queue_declare($queueName, false, true, false, false);
    
    // Queue bilgilerini al
    $queueInfo = $channel->queue_declare($queueName, false, true, false, false);
    $messageCount = $queueInfo[1]; // Ready mesaj sayısı
    
    echo "✅ Bağlantı başarılı!\n";
    echo "📊 Kuyruktaki mesaj sayısı: {$messageCount}\n\n";
    
    if ($messageCount == 0) {
        echo "⚠️  Kuyrukta mesaj bulunamadı.\n";
        $channel->close();
        $connection->close();
        exit(0);
    }
    
    // Mesajları topla
    $messages = [];
    $processedCount = 0;
    $maxMessages = 100000; // Maksimum mesaj limiti (güvenlik için)
    
    echo "📥 Mesajlar okunuyor...\n";
    echo "⚠️  NOT: Mesajlar kuyruktan silinmeyecek, sadece okunacak ve JSON'a kaydedilecek.\n\n";
    
    // Tüm mesajları oku (basic_get ile)
    while ($processedCount < $messageCount && $processedCount < $maxMessages) {
        // Mesaj al (no_ack=false, böylece nack ile requeue yapabiliriz)
        $msg = $channel->basic_get($queueName, false);
        
        if ($msg === null) {
            // Daha fazla mesaj yok
            break;
        }
        
        // Mesaj içeriğini parse et
        $messageBody = $msg->body;
        $messageData = json_decode($messageBody, true);
        
        // Eğer JSON parse edilemezse, ham string olarak kaydet
        if (json_last_error() !== JSON_ERROR_NONE) {
            $messageData = [
                'raw_body' => $messageBody,
                'parse_error' => json_last_error_msg()
            ];
        }
        
        // Mesaj bilgilerini ekle
        $messages[] = [
            'index' => $processedCount + 1,
            'timestamp' => date('Y-m-d H:i:s'),
            'delivery_tag' => $msg->delivery_info['delivery_tag'] ?? null,
            'exchange' => $msg->delivery_info['exchange'] ?? '',
            'routing_key' => $msg->delivery_info['routing_key'] ?? '',
            'data' => $messageData
        ];
        
        $processedCount++;
        
        // Her 100 mesajda bir ilerleme göster
        if ($processedCount % 100 == 0) {
            echo "   ✅ {$processedCount} mesaj okundu...\n";
        }
        
        // Mesajı requeue yap (kuyrukta kalsın) - nack ile requeue=true
        $msg->nack(false, true); // false = multiple, true = requeue
    }
    
    echo "\n✅ Toplam {$processedCount} mesaj okundu.\n";
    
    // Mesajları JSON dosyasına kaydet
    echo "💾 JSON dosyasına kaydediliyor...\n";
    
    // DATA klasörünü oluştur (yoksa)
    $dataDir = dirname($outputFile);
    if (!is_dir($dataDir)) {
        mkdir($dataDir, 0755, true);
        echo "📁 DATA klasörü oluşturuldu: {$dataDir}\n";
    }
    
    // JSON formatında kaydet (güzel formatlanmış)
    $jsonData = [
        'export_info' => [
            'export_date' => date('Y-m-d H:i:s'),
            'queue_name' => $queueName,
            'total_messages' => count($messages),
            'rabbitmq_host' => $rabbitmqHost,
            'rabbitmq_port' => $rabbitmqPort,
            'vhost' => $vhost
        ],
        'messages' => $messages
    ];
    
    $jsonContent = json_encode($jsonData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    
    if (file_put_contents($outputFile, $jsonContent) === false) {
        throw new Exception("Dosya yazılamadı: {$outputFile}");
    }
    
    $fileSize = filesize($outputFile);
    $fileSizeMB = round($fileSize / 1024 / 1024, 2);
    
    echo "✅ JSON dosyası başarıyla kaydedildi!\n";
    echo "   📄 Dosya: {$outputFile}\n";
    echo "   📊 Toplam mesaj: " . count($messages) . "\n";
    echo "   💾 Dosya boyutu: {$fileSizeMB} MB\n";
    
    // Bağlantıları kapat
    $channel->close();
    $connection->close();
    
    echo "\n🎉 İşlem tamamlandı!\n";
    
} catch (Exception $e) {
    echo "\n❌ HATA: " . $e->getMessage() . "\n";
    echo "📍 Dosya: " . $e->getFile() . "\n";
    echo "📍 Satır: " . $e->getLine() . "\n";
    echo "\nStack Trace:\n" . $e->getTraceAsString() . "\n";
    exit(1);
}

