docker network create shared_network
docker-compose build --no-cache
docker-compose up -d
docker-compose logs -f
python3 test_rabbitmq_connection.py

./monitor.sh watch
sudo ./purge_queues.sh azure  

docker-compose logs -f selenium-worker
docker-compose logs -f scrapy-worker
docker-compose logs -f playwright-worker
docker-compose logs -f save-worker

docker-compose logs --tail=30 scrapy-worker
docker-compose logs --tail=30 selenium-worker
docker-compose logs --tail=30 playwright-worker
docker-compose logs --tail=30 save-worker

docker-compose restart scrapy-worker selenium-worker playwright-worker save-worker


docker-compose build playwright-worker
docker-compose build scrapy-worker
docker-compose build selenium-worker
docker-compose build save-worker


docker-compose up -d --scale playwright-worker=10
docker-compose up -d --scale scrapy-worker=10
docker-compose up -d --scale selenium-worker=10
docker-compose up -d --scale save-worker=5

docker-compose up -d --scale selenium-worker=10 --scale save-worker=5 --scale scrapy-worker=3  --scale playwright-worker=1




# SQL dosyasını çalıştır
docker exec -i price_analysis_service-db-1 psql -U admin -d price_analysis < database_check.sql




# Worker loglarını izle
docker-compose logs -f selenium-worker

# Son kayıtları göster
docker exec -it price_analysis_service-db-1 psql -U admin -d price_analysis -c "SELECT COUNT(*) FROM product_attribute_value WHERE created_at > NOW() - INTERVAL '1 hour';"

✅ Bugün Kaç Kayıt İşlendi?
SELECT COUNT(*) FROM product_attribute_value 
WHERE DATE(created_at) = CURRENT_DATE;
✅ Worker'lar Çalışıyor mu?
SELECT 
    COUNT(*) as son_5dk,
    MAX(created_at) as son_kayit
FROM product_attribute_value
WHERE created_at > NOW() - INTERVAL '5 minutes';


# Docker üzerinden son kayıtları göster
docker exec -it price_analysis_service-db-1 psql -U admin -d price_analysis -c "
SELECT 
    pav.id,
    pav.mpn,
    c.name as company,
    a.name as attribute,
    pav.value,
    pav.created_at
FROM product_attribute_value pav
LEFT JOIN company c ON c.id = pav.company_id
LEFT JOIN attribute a ON a.id = pav.attribute_id
WHERE pav.created_at > NOW() - INTERVAL '10 minutes'
ORDER BY pav.created_at DESC
LIMIT 20;
"




Ana Tablolar
Tablo	Ne İçerir	Ne Zaman Dolar
product_attribute_value	Parse edilen her değer (price, stock, title)	Her Scrapy/Selenium parsing sonrası
products_history	Ürün fiyat/stok geçmişi	Scheduled crawler çalıştığında
crawler_logs	Crawler performans metrikleri	Her crawler başlangıç/bitiş
job_logs	Job durumları	Job başlangıç/bitiş


