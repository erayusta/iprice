# test_worker.py
import pika
import json
from datetime import datetime


def send_test_job():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='shared-rabbitmq',
            port=5672,
            credentials=pika.PlainCredentials('admin', 'password123')
        )
    )
    channel = connection.channel()

    # Test job'ı
    test_job = {
        'url': 'https://www.beymen.com/tr/p_apple-ipad-11-nesil-a16-11-wi-fi-128gb-pembe-tablet-md4e4tua_1729787',
        'mpn': 'MD4E4TU/A',
        'company_id': 40,
        'application_id': 5,
        'server_id': 1,
        'timestamp': datetime.now().isoformat()
    }

    # scrapy_jobs queue'suna gönder
    channel.basic_publish(
        exchange='',
        routing_key='scrapy_jobs',
        body=json.dumps(test_job),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    print("✅ Test job'ı gönderildi!")
    connection.close()


if __name__ == "__main__":
    send_test_job()