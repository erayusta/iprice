import requests
import psycopg2
import json
from datetime import datetime
import logging
from psycopg2.extras import execute_values
import math
import time

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("proxy_fetcher.log"), logging.StreamHandler()]
)

# PostgreSQL bağlantı bilgileri
DB_CONFIG = dict(
    host='10.20.50.13',
    user='priceanalysis_dev',
    password='2u5XPL3mVJWA',
    database='price_analysis_dev',
    port=5432
)

# API URL
PROXY_API_BASE_URL = 'https://proxylist.geonode.com/api/proxy-list'
LIMIT_PER_PAGE = 500


def main():
    try:
        # 1. Veritabanı bağlantısı
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 2. Tablo oluştur (yoksa)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proxies (
                id SERIAL PRIMARY KEY,
                proxy_id VARCHAR(100),
                ip VARCHAR(45) NOT NULL,
                port INT NOT NULL,
                country VARCHAR(100),
                city VARCHAR(100),
                region VARCHAR(100),
                anonymity_level VARCHAR(50),
                isp VARCHAR(200),
                asn VARCHAR(100),
                organization VARCHAR(200),
                speed INT,
                latency FLOAT,
                response_time INT,
                last_checked TIMESTAMP,
                protocols JSONB,
                working_percent FLOAT,
                up_time FLOAT,
                up_time_success_count INT,
                up_time_try_count INT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                CONSTRAINT unique_proxy UNIQUE (ip, port)
            )
        ''')
        conn.commit()
        logging.info("Proxies tablosu kontrol edildi/oluşturuldu")

        # 3. Toplam proxy sayısını al
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(f"{PROXY_API_BASE_URL}?limit=1&page=1", headers=headers, timeout=30)
        total_count = response.json().get('total', 0)
        total_pages = math.ceil(total_count / LIMIT_PER_PAGE)
        logging.info(f"Toplam {total_count} proxy ({total_pages} sayfa) bulundu")

        # 4. Tüm sayfaları çek
        all_proxies = []
        for page in range(1, total_pages + 1):
            try:
                logging.info(f"Sayfa {page}/{total_pages} çekiliyor...")
                url = f"{PROXY_API_BASE_URL}?limit={LIMIT_PER_PAGE}&page={page}&sort_by=lastChecked&sort_type=desc"
                response = requests.get(url, headers=headers, timeout=30)
                proxies = response.json().get('data', [])
                all_proxies.extend(proxies)
                logging.info(f"Sayfa {page}: {len(proxies)} proxy alındı")

                # API'yi yüklememek için bekleme
                if page < total_pages:
                    time.sleep(1)
            except Exception as e:
                logging.error(f"Sayfa {page} çekilirken hata: {e}")

        # 5. Batch işleme ile veritabanına kaydet
        batch_size = 1000
        total_processed = 0

        insert_query = '''
            INSERT INTO proxies (
                proxy_id, ip, port, country, city, region, anonymity_level, 
                isp, asn, organization, speed, latency, response_time, 
                last_checked, protocols, working_percent, up_time, 
                up_time_success_count, up_time_try_count, created_at, updated_at
            ) VALUES %s
            ON CONFLICT (ip, port) DO UPDATE SET
                proxy_id = EXCLUDED.proxy_id,
                country = EXCLUDED.country,
                city = EXCLUDED.city,
                region = EXCLUDED.region,
                anonymity_level = EXCLUDED.anonymity_level,
                isp = EXCLUDED.isp,
                asn = EXCLUDED.asn,
                organization = EXCLUDED.organization,
                speed = EXCLUDED.speed,
                latency = EXCLUDED.latency,
                response_time = EXCLUDED.response_time,
                last_checked = EXCLUDED.last_checked,
                protocols = EXCLUDED.protocols,
                working_percent = EXCLUDED.working_percent,
                up_time = EXCLUDED.up_time,
                up_time_success_count = EXCLUDED.up_time_success_count,
                up_time_try_count = EXCLUDED.up_time_try_count,
                updated_at = EXCLUDED.updated_at
        '''

        for i in range(0, len(all_proxies), batch_size):
            batch = all_proxies[i:i + batch_size]
            values = []

            for proxy in batch:
                # Değerleri hazırla ve dönüştür
                values.append((
                    proxy.get('_id', ''),
                    proxy.get('ip', ''),
                    int(proxy.get('port', 0)),
                    proxy.get('country', ''),
                    proxy.get('city', ''),
                    proxy.get('region', ''),
                    proxy.get('anonymityLevel', ''),
                    proxy.get('isp', ''),
                    proxy.get('asn', ''),
                    proxy.get('org', ''),
                    int(proxy.get('speed', 0)) if proxy.get('speed') else 0,
                    float(proxy.get('latency', 0)) if proxy.get('latency') else 0,
                    int(proxy.get('responseTime', 0)) if proxy.get('responseTime') else 0,
                    datetime.fromtimestamp(int(proxy.get('lastChecked', 0))) if proxy.get('lastChecked') else None,
                    json.dumps(proxy.get('protocols', [])),
                    float(proxy.get('workingPercent', 0)) if proxy.get('workingPercent') else 0,
                    float(proxy.get('upTime', 0)) if proxy.get('upTime') else 0,
                    int(proxy.get('upTimeSuccessCount', 0)) if proxy.get('upTimeSuccessCount') else 0,
                    int(proxy.get('upTimeTryCount', 0)) if proxy.get('upTimeTryCount') else 0,
                    datetime.fromisoformat(proxy.get('created_at', '').replace('Z', '+00:00')) if proxy.get(
                        'created_at') else None,
                    datetime.fromisoformat(proxy.get('updated_at', '').replace('Z', '+00:00')) if proxy.get(
                        'updated_at') else None
                ))

            # Batch ekle
            execute_values(cursor, insert_query, values)
            conn.commit()

            total_processed += len(batch)
            logging.info(f"Batch işlendi: {total_processed}/{len(all_proxies)} proxy")

        # 6. Özet bilgileri göster
        cursor.execute("SELECT COUNT(*) FROM proxies")
        total_db_records = cursor.fetchone()[0]
        logging.info(f"İşlem tamamlandı. Toplam {len(all_proxies)} proxy işlendi.")
        logging.info(f"Veritabanında toplam {total_db_records} proxy kaydı var.")

    except Exception as e:
        logging.error(f"Hata: {e}", exc_info=True)
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()
            logging.info("Veritabanı bağlantısı kapatıldı")


if __name__ == "__main__":
    start_time = time.time()
    main()
    elapsed_time = time.time() - start_time
    logging.info(f"Toplam süre: {elapsed_time:.2f} saniye ({elapsed_time / 60:.2f} dakika)")