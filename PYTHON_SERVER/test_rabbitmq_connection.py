#!/usr/bin/env python3
"""
RabbitMQ Bağlantı Test Scripti
Bu script RabbitMQ bağlantısını ve queue'ları test eder.
"""

import os
import sys

# Projeyi path'e ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.messaging.connection import RabbitMQConnection
from app.messaging.producer import JobProducer


def test_connection():
    """RabbitMQ bağlantısını test et"""
    print("=" * 60)
    print("🔌 RabbitMQ Bağlantı Testi")
    print("=" * 60)
    
    rabbitmq = RabbitMQConnection()
    
    if rabbitmq.test_connection():
        print("✅ RabbitMQ bağlantısı BAŞARILI!")
        return True
    else:
        print("❌ RabbitMQ bağlantısı BAŞARISIZ!")
        return False


def test_queues():
    """Queue'ları test et"""
    print("\n" + "=" * 60)
    print("📋 Queue'ları Kontrol Et")
    print("=" * 60)
    
    try:
        producer = JobProducer()
        print("✅ Queue'lar başarıyla oluşturuldu!")
        
        # Queue'ların durumunu kontrol et
        queues = [
            'scrapy.queue',
            'selenium.queue',
            'scrapy.queue.completed',
            'scrapy.queue.error',
            'selenium.queue.completed',
            'selenium.queue.error'
        ]
        
        print("\n📊 Queue Durumları:")
        for queue in queues:
            try:
                size = producer.get_queue_size(queue)
                print(f"  • {queue}: {size} mesaj")
            except Exception as e:
                print(f"  ⚠️ {queue}: Erişilemedi - {e}")
        
        return True
    except Exception as e:
        print(f"❌ Queue oluşturma hatası: {e}")
        return False


def test_send_job():
    """Test job'ı gönder"""
    print("\n" + "=" * 60)
    print("📤 Test Job'ı Gönder")
    print("=" * 60)
    
    try:
        producer = JobProducer()
        
        test_job = {
            'url': 'https://www.example.com/test-product',
            'company_id': 1,
            'application_id': 1,
            'server_id': 1,
            'parser_type': 'scrapy'
        }
        
        print(f"📦 Test job'ı gönderiliyor...")
        print(f"   URL: {test_job['url']}")
        print(f"   Parser: {test_job['parser_type']}")
        
        result = producer.send_parsing_job(**test_job)
        
        if result.get('success'):
            print(f"\n✅ Test job'ı BAŞARILI!")
            print(f"   Job ID: {result.get('job_id')}")
            print(f"   Queue: {result.get('queue')}")
            print(f"\n💡 Worker loglarını takip edin:")
            print(f"   docker-compose logs -f scrapy-worker")
            return True
        else:
            print(f"❌ Test job'ı BAŞARISIZ!")
            print(f"   Hata: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Job gönderme hatası: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ana test fonksiyonu"""
    print("\n")
    print("🚀 RabbitMQ Kurulum Test Paketi")
    print("=" * 60)
    
    server = os.getenv('SERVER', 'Bilinmiyor')
    print(f"🔧 Aktif Server: {server}")
    print("=" * 60)
    
    # Test adımları
    tests = [
        ("Bağlantı Testi", test_connection),
        ("Queue Testi", test_queues),
        ("Test Job Gönderimi", test_send_job)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} sırasında beklenmeyen hata: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Özet
    print("\n" + "=" * 60)
    print("📊 TEST SONUÇLARI")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{status} - {test_name}")
    
    all_passed = all(result for _, result in results)
    
    print("=" * 60)
    if all_passed:
        print("🎉 TÜM TESTLER BAŞARILI!")
        print("\n💡 Sonraki adımlar:")
        print("   1. docker-compose logs -f scrapy-worker")
        print("   2. http://68.219.209.108:15672 - RabbitMQ Panel")
        print("   3. http://localhost:8000/docs - API Docs")
    else:
        print("⚠️ BAZI TESTLER BAŞARISIZ!")
        print("\n🔧 Kontrol edilecekler:")
        print("   1. .env dosyası doğru mu?")
        print("   2. RabbitMQ erişilebilir mi?")
        print("   3. Virtual host ayarları doğru mu?")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

