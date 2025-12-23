# queue_setup.py - güncelle
import pika
import json


def setup_queues():
    # Docker içinden RabbitMQ container'a bağlan
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='shared-rabbitmq',  # localhost değil, container adı
            port=5672,
            credentials=pika.PlainCredentials('admin', 'password123')
        )
    )
    channel = connection.channel()

    # Queue'ları oluştur
    channel.queue_declare(queue='scrapy_jobs', durable=True)
    channel.queue_declare(queue='selenium_jobs', durable=True)
    channel.queue_declare(queue='playwright_jobs', durable=True)

    print("✅ Queue'lar oluşturuldu!")
    connection.close()


if __name__ == "__main__":
    setup_queues()