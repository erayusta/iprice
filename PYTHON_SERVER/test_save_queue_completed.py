#!/usr/bin/env python3
"""
🔍 SAVE.QUEUE.COMPLETED TEST SCRIPT
==================================
save.queue.completed queue'sunun çalışıp çalışmadığını test eder

Test adımları:
1. save.queue'ye test mesajı gönder
2. save.queue.completed'da mesaj gelip gelmediğini kontrol et
3. save.queue.error'da hata var mı kontrol et

Kullanım:
    python test_save_queue_completed.py
"""

import json
import time
from datetime import datetime
from app.messaging.producer import JobProducer
from app.messaging.connection import RabbitMQConnection

def test_save_queue_completed():
    """Save queue completed test"""
    
    print("🔍 Save Queue Completed Test Başlıyor...")
    print("=" * 50)
    
    # Test data oluştur
    test_payload = {
        'job_id': 9999,
        'product_id': 8888,
        'company_id': 1,
        'application_id': 1,
        'server_id': 1,
        'url': 'https://test.com/product',
        'npm': 'TEST123',
        'parser_used': 'test',
        'http_status_code': 200,
        'status': 'success',
        'timestamp': datetime.now().isoformat(),
        'results': {
            'price': '1000.00 TL',
            'product_title': 'Test Ürün',
            'is_stock': 'Stokta Var'
        },
        'attributes': [
            {
                'attributes_id': 1,
                'attributes_name': 'price',
                'attributes_type': 'class',
                'attributes_value': '.price'
            }
        ]
    }
    
    print(f"📤 Test payload oluşturuldu:")
    print(f"   Job ID: {test_payload['job_id']}")
    print(f"   Product ID: {test_payload['product_id']}")
    print(f"   URL: {test_payload['url']}")
    print()
    
    try:
        # Producer ile save.queue'ye gönder
        print("📤 save.queue'ye test mesajı gönderiliyor...")
        producer = JobProducer()
        
        # Direkt save.queue'ye gönder (bypass parsing)
        connection = producer.rabbitmq.get_connection()
        channel = connection.channel()
        
        channel.basic_publish(
            exchange='',
            routing_key='save.queue',
            body=json.dumps(test_payload),
            properties=producer.rabbitmq.get_pika_properties()
        )
        
        connection.close()
        print("✅ Test mesajı save.queue'ye gönderildi")
        print()
        
        # Biraz bekle (save worker işlesin)
        print("⏳ Save worker'ın işlemesi için 5 saniye bekleniyor...")
        time.sleep(5)
        print()
        
        # save.queue.completed'ı kontrol et
        print("🔍 save.queue.completed kontrol ediliyor...")
        connection = RabbitMQConnection().get_connection()
        channel = connection.channel()
        
        # Queue declare et
        channel.queue_declare(queue='save.queue.completed', durable=True)
        
        # Mesaj sayısını al
        method, properties, body = channel.basic_get(queue='save.queue.completed', auto_ack=True)
        
        if method:
            completed_data = json.loads(body)
            print("✅ save.queue.completed'da mesaj bulundu!")
            print(f"   Job ID: {completed_data.get('job_id')}")
            print(f"   Product ID: {completed_data.get('product_id')}")
            print(f"   Save Status: {completed_data.get('save_status')}")
            print(f"   Save Timestamp: {completed_data.get('save_timestamp')}")
            print(f"   Results: {completed_data.get('results')}")
            print()
            print("🎉 TEST BAŞARILI! save.queue.completed çalışıyor!")
        else:
            print("❌ save.queue.completed'da mesaj bulunamadı!")
            print("   Save worker çalışmıyor olabilir")
        
        # save.queue.error'ı kontrol et
        print()
        print("🔍 save.queue.error kontrol ediliyor...")
        channel.queue_declare(queue='save.queue.error', durable=True)
        method, properties, body = channel.basic_get(queue='save.queue.error', auto_ack=True)
        
        if method:
            error_data = json.loads(body)
            print("⚠️ save.queue.error'da mesaj bulundu!")
            print(f"   Error: {error_data.get('error')}")
            print(f"   Save Error: {error_data.get('save_error')}")
            print(f"   Error Type: {error_data.get('error_type')}")
            print()
            print("❌ TEST BAŞARISIZ! Save worker hata veriyor!")
        else:
            print("✅ save.queue.error'da hata yok")
        
        connection.close()
        
        # save.queue'da kalan mesaj sayısını kontrol et
        print()
        print("🔍 save.queue durumu kontrol ediliyor...")
        connection = RabbitMQConnection().get_connection()
        channel = connection.channel()
        channel.queue_declare(queue='save.queue', durable=True)
        
        # Queue info al
        method = channel.queue_declare(queue='save.queue', durable=True, passive=True)
        message_count = method.method.message_count
        consumer_count = method.method.consumer_count
        
        print(f"   Kalan mesaj sayısı: {message_count}")
        print(f"   Consumer sayısı: {consumer_count}")
        
        if message_count == 0:
            print("✅ save.queue boş - mesaj işlenmiş!")
        else:
            print(f"⚠️ save.queue'da {message_count} mesaj bekliyor!")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        import traceback
        traceback.print_exc()

def check_queue_status():
    """Tüm save queue'larının durumunu kontrol et"""
    
    print()
    print("📊 SAVE QUEUE DURUM RAPORU")
    print("=" * 50)
    
    try:
        connection = RabbitMQConnection().get_connection()
        channel = connection.channel()
        
        queues = ['save.queue', 'save.queue.completed', 'save.queue.error']
        
        for queue_name in queues:
            try:
                method = channel.queue_declare(queue=queue_name, durable=True, passive=True)
                message_count = method.method.message_count
                consumer_count = method.method.consumer_count
                
                status = "🟢" if consumer_count > 0 else "🔴"
                print(f"{status} {queue_name}:")
                print(f"   Mesaj sayısı: {message_count}")
                print(f"   Consumer sayısı: {consumer_count}")
                print()
                
            except Exception as e:
                print(f"❌ {queue_name}: Queue bulunamadı - {e}")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Queue durumu kontrol hatası: {e}")

if __name__ == "__main__":
    print("🔍 SAVE.QUEUE.COMPLETED TEST BAŞLATILIYOR")
    print("=" * 60)
    print()
    
    # Önce queue durumunu kontrol et
    check_queue_status()
    
    # Test'i çalıştır
    test_save_queue_completed()
    
    print()
    print("=" * 60)
    print("🏁 TEST TAMAMLANDI")
    print()
    print("📝 SONUÇLAR:")
    print("   - save.queue.completed'da mesaj varsa: ✅ ÇALIŞIYOR")
    print("   - save.queue.completed'da mesaj yoksa: ❌ ÇALIŞMIYOR")
    print("   - save.queue.error'da mesaj varsa: ❌ HATA VAR")
    print()
    print("🔧 SORUN GİDERME:")
    print("   1. Save worker çalışıyor mu kontrol edin:")
    print("      docker-compose ps | grep save-worker")
    print()
    print("   2. Save worker log'larını kontrol edin:")
    print("      docker-compose logs -f save-worker")
    print()
    print("   3. RabbitMQ Management UI kontrol edin:")
    print("      http://68.219.209.108:15672 (admin/password)")
