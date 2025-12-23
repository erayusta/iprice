#!/usr/bin/env python3
"""
🔧 Local Environment Test Script
===============================
.env dosyasını yükleyerek lokal test yapar
"""

import os
import sys
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv('/Users/serkanodaci/Projects/iPriceNew/price_analysis_service/env_file')

# Path'i ekle
sys.path.append('/Users/serkanodaci/Projects/iPriceNew/price_analysis_service')

def test_environment():
    """Environment ayarlarını test et"""
    
    print("🔧 Environment Test")
    print("=" * 40)
    
    # SERVER değerini kontrol et
    server = os.getenv('SERVER')
    print(f"SERVER: {server}")
    
    # RabbitMQ ayarlarını kontrol et
    if server == 'SERVER_AZURE':
        host = os.getenv('RABBITMQ_HOST_AZURE')
        vhost = os.getenv('RABBITMQ_VHOST_AZURE')
        print(f"Azure Host: {host}")
        print(f"Azure VHost: {vhost}")
    else:
        host = os.getenv('RABBITMQ_HOST_LOCAL')
        vhost = os.getenv('RABBITMQ_VHOST_LOCAL')
        print(f"Local Host: {host}")
        print(f"Local VHost: {vhost}")
    
    # RabbitMQ bağlantısını test et
    print("\n🔌 RabbitMQ Bağlantı Testi")
    print("-" * 30)
    
    from app.messaging.connection import RabbitMQConnection
    
    try:
        connection = RabbitMQConnection()
        success = connection.test_connection()
        
        if success:
            print("✅ RabbitMQ bağlantısı başarılı!")
        else:
            print("❌ RabbitMQ bağlantısı başarısız!")
            
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")

if __name__ == "__main__":
    test_environment()
