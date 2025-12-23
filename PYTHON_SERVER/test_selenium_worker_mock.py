#!/usr/bin/env python3
"""
SeleniumWorker Test - Mock Data ile Test
=========================================
RabbitMQ bağlantısı olmadan mock data ile SeleniumWorker'ı test eder.

Kullanım:
    python test_selenium_worker_mock.py
"""

import sys
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Tüm eksik modülleri mockla (import edilmeden önce)
sys.modules['pika'] = MagicMock()
sys.modules['requests'] = MagicMock()

sys.path.append('/app')
from app.workers.selenium_worker import SeleniumWorker


# Mock Data
MOCK_JOB_DATA = {
    "job_id": 195,
    "company_id": 64,
    "product_id": 741,
    "application_id": 2,
    "server_id": 2,
    "server_name": "azure",
    "screenshot": False,
    "marketplace": False,
    "use_proxy": False,
    "proxy_type": None,
    "url": "https://www.gurgencler.com.tr/macbook-air-13-inc-m2-cip-8-cekirdek-cpu-8-cekirdek-gpu-16-gb-ram-256-gb-gece-yarisi-mc7x4tu-a?__cf_chl_tk=Rs2U0pyzOjoj.t5rioDLEX3p9ipT1aN5PHiYJlH9wfM-1761316162-1.0.1.1-4BPFmfXscgcmyrLen0WQhlh1pK8gfkZWlPa6Ax7IxcE",
    "npm": "MC7X4TU/A",
    "attributes": [
        {
            "company_id": 64,
            "attributes_id": 1,
            "attributes_name": "price",
            "attributes_type": "meta",
            "attributes_value": "unit_sale_price"
        }
    ]
}


def test_selenium_worker_with_mock_data():
    """Mock data ile SeleniumWorker'ı test et"""
    
    print("=" * 80)
    print("🧪 SeleniumWorker Mock Data Test Başlatılıyor...")
    print("=" * 80)
    print()
    
    # Mock data'yı göster
    print("📋 Mock Job Data:")
    print(json.dumps(MOCK_JOB_DATA, indent=2, ensure_ascii=False))
    print()
    
    # RabbitMQ bağlantısını mockla
    with patch('app.workers.base_worker.RabbitMQConnection') as mock_rabbitmq:
        # Mock connection ve channel oluştur
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_rabbitmq_instance = MagicMock()
        mock_rabbitmq_instance.get_connection.return_value = mock_connection
        mock_rabbitmq.return_value = mock_rabbitmq_instance
        mock_connection.channel.return_value = mock_channel
        
        try:
            # SeleniumWorker'ı oluştur
            print("🔧 SeleniumWorker oluşturuluyor...")
            worker = SeleniumWorker()
            print("✅ SeleniumWorker oluşturuldu!")
            print()
            
            # Parser'ı da mockla (gerçek parsing yapmak yerine)
            print("🔧 Parser mock'lanıyor...")
            with patch('app.workers.selenium_worker.ParserFactory') as mock_factory:
                mock_parser = MagicMock()
                mock_factory.get_parser.return_value = mock_parser
                
                # Mock parse sonucu
                mock_parse_result = {
                    'status': 'success',
                    'url': MOCK_JOB_DATA['url'],
                    'job_id': MOCK_JOB_DATA['job_id'],
                    'product_id': MOCK_JOB_DATA['product_id'],
                    'price': 45999.99,
                    'title': 'MacBook Air 13" M2',
                    'parser_used': 'selenium'
                }
                mock_parser.parse.return_value = mock_parse_result
                
                print("✅ Parser mock'landı!")
                print()
                
                # process_job metodunu çağır
                print("🚀 process_job metodu çağrılıyor...")
                print("-" * 80)
                
                result = worker.process_job(MOCK_JOB_DATA)
                
                print("-" * 80)
                print()
                
                # Sonuçları göster
                print("=" * 80)
                print("📊 Test Sonuçları:")
                print("=" * 80)
                print()
                print("📤 Process Job Sonucu:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                print()
                
                # Sonuçları kontrol et
                print("🔍 Sonuç Kontrolleri:")
                print("-" * 80)
                
                if result.get('status') == 'success':
                    print("✅ Status: SUCCESS")
                else:
                    print(f"❌ Status: {result.get('status')}")
                    print(f"❌ Hata: {result.get('error')}")
                
                # Parser'ın doğru parametrelerle çağrıldığını kontrol et
                if mock_parser.parse.called:
                    print("✅ Parser.parse() çağrıldı")
                    call_args = mock_parser.parse.call_args
                    print(f"   - URL: {call_args[0][0]}")
                    print(f"   - Company ID: {call_args[0][1]}")
                    print(f"   - Application ID: {call_args[0][2]}")
                    print(f"   - Server ID: {call_args[0][3]}")
                    if 'job_data' in call_args[1]:
                        job_data_arg = call_args[1]['job_data']
                        print(f"   - Job Data gönderildi: ✅")
                        if 'attributes' in job_data_arg:
                            print(f"   - Attributes var: ✅ ({len(job_data_arg['attributes'])} adet)")
                        else:
                            print(f"   - Attributes YOK: ❌")
                else:
                    print("❌ Parser.parse() çağrılmadı!")
                
                # save.queue'ye gönderilip gönderilmediğini kontrol et
                if mock_channel.basic_publish.called:
                    publish_calls = [call for call in mock_channel.basic_publish.call_args_list 
                                   if len(call[1]) > 0 and call[1].get('routing_key') == 'save.queue']
                    if publish_calls:
                        print("✅ save.queue'ye mesaj gönderildi")
                    else:
                        print("⚠️ save.queue'ye mesaj gönderilmedi (status error olabilir)")
                else:
                    print("⚠️ Hiçbir queue'ya mesaj gönderilmedi")
                
                print()
                print("=" * 80)
                print("✅ Test Tamamlandı!")
                print("=" * 80)
                
                return result
                
        except Exception as e:
            print()
            print("=" * 80)
            print("❌ TEST HATASI!")
            print("=" * 80)
            print(f"Hata: {str(e)}")
            print()
            import traceback
            traceback.print_exc()
            print()
            raise


def test_with_real_parser():
    """Gerçek parser ile test et - GERÇEK VERİ ÇEKİLİR"""
    
    print("=" * 80)
    print("🧪 SeleniumWorker GERÇEK PARSER Test Başlatılıyor...")
    print("=" * 80)
    print()
    
    # Mock data'yı göster
    print("📋 Mock Job Data:")
    print(json.dumps(MOCK_JOB_DATA, indent=2, ensure_ascii=False))
    print()
    
    # RabbitMQ bağlantısını mockla
    with patch('app.workers.base_worker.RabbitMQConnection') as mock_rabbitmq:
        # Mock connection ve channel oluştur
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_rabbitmq_instance = MagicMock()
        mock_rabbitmq_instance.get_connection.return_value = mock_connection
        mock_rabbitmq.return_value = mock_rabbitmq_instance
        mock_connection.channel.return_value = mock_channel
        
        try:
            # SeleniumWorker'ı oluştur
            print("🔧 SeleniumWorker oluşturuluyor...")
            worker = SeleniumWorker()
            print("✅ SeleniumWorker oluşturuldu!")
            print()
            
            # process_job metodunu çağır (gerçek parser ile)
            print("🚀 process_job metodu çağrılıyor (GERÇEK PARSER)...")
            print("⚠️  Bu işlem uzun sürebilir (web scraping yapılacak)...")
            print("🌐 Gerçek URL'e gidilecek ve veri çekilecek!")
            print("-" * 80)
            
            result = worker.process_job(MOCK_JOB_DATA)
            
            print("-" * 80)
            print()
            
            # Sonuçları göster
            print("=" * 80)
            print("📊 GERÇEK PARSER TEST SONUÇLARI:")
            print("=" * 80)
            print()
            print("📤 Process Job Sonucu (GERÇEK VERİ):")
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
            print()
            
            # Sonuçları detaylı kontrol et
            print("🔍 Sonuç Detaylı Kontrolleri:")
            print("-" * 80)
            
            if result.get('status') == 'success':
                print("✅ Status: SUCCESS")
                print()
                
                # Results içindeki verileri göster
                if 'results' in result:
                    print("📊 Çekilen Veriler (results):")
                    results = result.get('results', {})
                    for key, value in results.items():
                        print(f"   - {key}: {value}")
                    print()
                
                # Eski format kontrolü (price direkt result'ta varsa)
                if 'price' in result:
                    print(f"💰 Fiyat: {result.get('price')}")
                
                # Job ID kontrolü
                if 'job_id' in result:
                    print(f"🆔 Job ID: {result.get('job_id')}")
                
                # Product ID kontrolü
                if 'product_id' in result:
                    print(f"📦 Product ID: {result.get('product_id')}")
                
                # Attributes kontrolü
                if 'attributes' in result:
                    attrs = result.get('attributes', [])
                    print(f"📋 Attributes: {len(attrs)} adet")
                    for attr in attrs:
                        print(f"   - {attr.get('attributes_name')} ({attr.get('attributes_type')})")
                
                # Parser kullanılanı kontrol et
                if 'parser_used' in result:
                    print(f"🔧 Parser: {result.get('parser_used')}")
                
            else:
                print(f"❌ Status: {result.get('status')}")
                print(f"❌ Hata: {result.get('error')}")
                if 'error_details' in result:
                    print(f"❌ Hata Detayları: {result.get('error_details')}")
            
            print()
            print("=" * 80)
            print("✅ Test Tamamlandı!")
            print("=" * 80)
            
            return result
                
        except Exception as e:
            print()
            print("=" * 80)
            print("❌ TEST HATASI!")
            print("=" * 80)
            print(f"Hata: {str(e)}")
            print()
            import traceback
            traceback.print_exc()
            print()
            raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='SeleniumWorker Test')
    parser.add_argument('--mock-parser', action='store_true', 
                       help='Mock parser ile test et (hızlı, gerçek veri çekmez)')
    
    args = parser.parse_args()
    
    # Varsayılan olarak gerçek parser ile test et
    if args.mock_parser:
        test_selenium_worker_with_mock_data()
    else:
        test_with_real_parser()

