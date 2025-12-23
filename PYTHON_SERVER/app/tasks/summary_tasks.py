import psycopg2
from collections import defaultdict
import json
import os
import logging
from datetime import datetime, date, timedelta
from app.celery_worker import celery


@celery.task(name='app.tasks.summary_tasks.generate_summary', queue='summary', bind=True)
def generate_summary(self):
    logger = logging.getLogger(__name__)
    db_params = {
        "host": os.environ.get('POSTGRES_HOST', '10.20.50.16'),
        "port": os.environ.get('POSTGRES_PORT', 5432),
        "user": os.environ.get('SHARED_DB_USER', 'ipricetestuser'),
        "password": os.environ.get('SHARED_DB_PASS', 'YeniSifre123!'),
        "dbname": os.environ.get('SHARED_DB_NAME', 'ipricetest')
    }

    summary_data = defaultdict(lambda: {"attributes": {}, "created_at": datetime.now()})
    conn = None
    processed_select_count = 0

    try:
        conn = psycopg2.connect(**db_params)
        conn.autocommit = False  # Otomatik commit'i kapat, transaction'ı manuel yöneteceğiz

        with conn.cursor(name='summary_select_cursor') as cur:
            today_start = date.today()
            tomorrow_start = today_start + timedelta(days=1)

            logger.info(
                f"Bugün için (Başlangıç: {today_start}, Bitiş: {tomorrow_start}) özetlenecek kayıtlar sorgulanıyor.")
            cur.execute("""
                SELECT pav.mpn, pav.company_id, a.name AS attribute_name, pav.value, pu.url
                FROM product_attribute_value pav
                JOIN attribute a ON a.id = pav.attribute_id
                LEFT JOIN product_url pu ON pu.mpn = pav.mpn AND pu.company_id = pav.company_id
                WHERE pav.created_at >= %s AND pav.created_at < %s
            """, (today_start, tomorrow_start))

            for mpn, company_id, attribute_name, value, url in cur:
                key = (mpn, company_id)
                summary_data[key]["attributes"][attribute_name] = value
                if url:
                    summary_data[key]["attributes"]["url"] = url
                processed_select_count += 1

        logger.info(f"SELECT işlemi tamamlandı. Toplam {processed_select_count} kayıt okundu.")

        if processed_select_count == 0:
            logger.info("Bugün için işlenecek kayıt bulunamadı. Veritabanı işlemi commit ediliyor.")
            conn.commit()
            return "Bugün için işlenecek kayıt bulunamadı."

        with conn.cursor() as cur_delete:
            logger.info(f"Mevcut tarihin (Bugün: {today_start}) eski özet kayıtları siliniyor.")
            cur_delete.execute("""
                DELETE FROM product_attribute_summary
                WHERE created_at >= %s AND created_at < %s;
            """, (today_start, tomorrow_start))
            logger.info(f"{cur_delete.rowcount} adet eski özet kaydı silindi.")

        insert_values = []
        for (mpn, company_id), data in summary_data.items():
            insert_values.append((mpn, company_id, json.dumps(data["attributes"]), data["created_at"]))

        if insert_values:
            with conn.cursor() as cur_insert:
                logger.info(f"{len(insert_values)} adet yeni özet kaydı toplu olarak ekleniyor.")
                cur_insert.executemany("""
                    INSERT INTO product_attribute_summary (mpn, company_id, attributes, created_at)
                    VALUES (%s, %s, %s, %s)
                """, insert_values)
            logger.info(f"{len(insert_values)} özet kaydı başarıyla veritabanına eklendi.")
        else:
            logger.info("Eklenecek yeni özet kayıt bulunamadı.")

        conn.commit()  # Tüm işlemler başarılıysa transaction'ı commit et
        logger.info(
            f"Tüm özet kaydı işlemleri başarıyla tamamlandı ve commit edildi. Toplam {len(summary_data)} özet kaydı işlendi.")

    except psycopg2.Error as e:
        logger.error(f"Veritabanı hatası oluştu: {e}. İşlem geri alınıyor. 60 saniye sonra yeniden denenecek.")
        if conn:
            conn.rollback()
        raise self.retry(exc=e, countdown=60)
    except Exception as e:
        logger.error(f"Beklenmeyen bir hata oluştu: {e}. İşlem geri alınıyor. 60 saniye sonra yeniden denenecek.")
        if conn:
            conn.rollback()
        raise self.retry(exc=e, countdown=60)
    finally:
        if conn:
            conn.close()

    return f"{len(summary_data)} özet kaydı işlendi."