#!/bin/bash
###############################################################################
# 🚀 Gürgençler Price Extraction Fix - Quick Deploy Script
###############################################################################

set -e  # Exit on error

echo "================================================================================"
echo "🚀 GÜRGENÇLER PRICE EXTRACTION FIX - DEPLOYMENT"
echo "================================================================================"
echo ""

# Production sunucu bilgileri
PROD_SERVER="root@68.219.209.108"
PROD_PATH="/root/PROJE_IPRICE/PYTHON_SERVER"  # Sunucudaki proje yolu (değiştir!)

echo "📋 Deployment Bilgileri:"
echo "   Server: $PROD_SERVER"
echo "   Path: $PROD_PATH"
echo ""

# Kullanıcıdan onay al
read -p "⚠️  Production'a deploy edilecek. Devam? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "❌ Deployment iptal edildi"
    exit 1
fi

echo ""
echo "📦 Adım 1/4: Güncel kodu production'a yükleme..."
echo "--------------------------------------------------------------------------------"

# selenium_parser.py dosyasını production'a kopyala
scp app/parsers/selenium_parser.py $PROD_SERVER:$PROD_PATH/app/parsers/

echo "✅ Dosya yüklendi"
echo ""

echo "🔄 Adım 2/4: Selenium worker'ı yeniden başlatma..."
echo "--------------------------------------------------------------------------------"

# SSH ile sunucuya bağlan ve container'ı restart et
ssh $PROD_SERVER << 'ENDSSH'
    cd /root/PROJE_IPRICE/PYTHON_SERVER  # Proje yolunu buraya da yaz
    
    echo "   🔍 Mevcut container durumu:"
    docker-compose ps | grep selenium-worker || echo "   ⚠️  Container çalışmıyor"
    
    echo ""
    echo "   🔄 Container restart ediliyor..."
    docker-compose restart selenium-worker
    
    echo ""
    echo "   ⏳ 5 saniye bekleniyor (startup için)..."
    sleep 5
    
    echo ""
    echo "   ✅ Yeni durum:"
    docker-compose ps | grep selenium-worker || echo "   ❌ Container başlatılamadı!"
ENDSSH

echo "✅ Worker yeniden başlatıldı"
echo ""

echo "📊 Adım 3/4: Log'ları kontrol etme..."
echo "--------------------------------------------------------------------------------"

# Son 30 satır log'u göster
ssh $PROD_SERVER << 'ENDSSH'
    cd /root/PROJE_IPRICE/PYTHON_SERVER
    
    echo "   📄 Son 30 satır log:"
    echo "   ............................................................................"
    docker-compose logs --tail=30 selenium-worker | tail -30
ENDSSH

echo ""
echo "✅ Log kontrol edildi"
echo ""

echo "🧪 Adım 4/4: Test job gönderme (opsiyonel)"
echo "--------------------------------------------------------------------------------"
echo ""
echo "   Test job göndermek ister misiniz? (RabbitMQ'ya manuel job)"
read -p "   Test job gönder? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo ""
    echo "   📤 Test job gönderiliyor..."
    
    # Python script ile test job gönder
    python3 << 'ENDPYTHON'
import pika
import json

try:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='68.219.209.108',
            port=5672,
            virtual_host='azure',
            credentials=pika.PlainCredentials('admin', '41jqJ526lOxP')
        )
    )
    channel = connection.channel()
    
    job_data = {
        "job_id": 999,
        "company_id": 64,
        "product_id": 0,
        "application_id": 2,
        "server_id": 2,
        "server_name": "azure",
        "screenshot": False,
        "marketplace": False,
        "use_proxy": True,
        "proxy_type": "BrightData",
        "url": "https://www.gurgencler.com.tr/airpods-4-aktif-gurultu-engelleme-ozellikli-mxp93tu-a",
        "npm": "TEST_DEPLOY",
        "attributes": [
            {
                "attributes_id": 1,
                "attributes_name": "price",
                "attributes_type": "meta",
                "attributes_value": "unit_sale_price"
            }
        ]
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='selenium.queue',
        body=json.dumps(job_data)
    )
    
    print("   ✅ Test job gönderildi (Job ID: 999)")
    connection.close()
    
except Exception as e:
    print(f"   ❌ Test job gönderilemedi: {e}")
ENDPYTHON

    echo ""
    echo "   ⏳ 10 saniye bekleniyor (processing için)..."
    sleep 10
    
    echo ""
    echo "   📊 Test job log'ları:"
    echo "   ............................................................................"
    
    # Test job log'larını göster
    ssh $PROD_SERVER << 'ENDSSH'
        cd /root/PROJE_IPRICE/PYTHON_SERVER
        docker-compose logs selenium-worker | grep -A 50 "Job ID: 999" | tail -50
ENDSSH
    
    echo ""
else
    echo "   ⏭️  Test job atlandı"
fi

echo ""
echo "================================================================================"
echo "✅ DEPLOYMENT TAMAMLANDI!"
echo "================================================================================"
echo ""
echo "📝 Sonraki Adımlar:"
echo ""
echo "1. Log'ları canlı izlemek için:"
echo "   ssh $PROD_SERVER"
echo "   cd $PROD_PATH"
echo "   docker-compose logs -f selenium-worker"
echo ""
echo "2. Gerçek job'ları izlemek için:"
echo "   docker-compose logs -f selenium-worker | grep -E 'Job ID|PROXY|META|price:'"
echo ""
echo "3. Aranacak başarı mesajları:"
echo "   - ✅ META attribute detected: price = unit_sale_price"
echo "   - 🔒 Undetected Selenium proxy kullanılıyor"
echo "   - 🔍 insider_object durumu: True"
echo "   - ✅ price: 9999"
echo ""
echo "4. Detaylı debug guide:"
echo "   cat GURGENCLER_DEBUG_GUIDE.md"
echo ""
echo "================================================================================"




