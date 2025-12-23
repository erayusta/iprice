# test_consumer.py
import pika
import json
import time


def process_scrapy_job(ch, method, properties, body):
    try:
        job_data = json.loads(body)
        print(f"📥 İşleniyor: {job_data}")

        # Simüle et - gerçekte burada scraping yapılacak
        print(f"🔍 Scraping: {job_data['url']}")
        print(f"🏷️  MPN: {job_data['mpn']}")
        time.sleep(2)  # 2 saniye scraping simülasyonu

        print("✅ İş tamamlandı!")

        # Mesajı onayla (queue'dan sil)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"❌ Hata: {e}")
        # Mesajı reddet ama tekrar queue'ya koy
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_consumer():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='shared-rabbitmq',
            port=5672,
            credentials=pika.PlainCredentials('admin', 'password123')
        )
    )
    channel = connection.channel()

    # QoS: Aynı anda sadece 1 mesaj işle
    channel.basic_qos(prefetch_count=1)

    # Consumer'ı başlat
    channel.basic_consume(
        queue='scrapy_jobs',
        on_message_callback=process_scrapy_job
    )

    print("🚀 Scrapy worker başlatıldı. Mesaj bekleniyor...")
    channel.start_consuming()


if __name__ == "__main__":
    start_consumer()