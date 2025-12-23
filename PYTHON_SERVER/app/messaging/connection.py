import pika
import os


class RabbitMQConnection:
    def __init__(self):
        # SERVER değişkenine göre RabbitMQ ayarlarını belirle
        server_type = os.getenv('SERVER', 'SERVER_LOCAL')
        
        if server_type == 'SERVER_AZURE':
            host = os.getenv('RABBITMQ_HOST_AZURE', '68.219.209.108')
            port = int(os.getenv('RABBITMQ_PORT_AZURE', 5672))
            user = os.getenv('RABBITMQ_USER_AZURE', 'admin')
            password = os.getenv('RABBITMQ_PASS_AZURE', '41jqJ526lOxP')
            vhost = os.getenv('RABBITMQ_VHOST_AZURE', 'azure')
        else:  # SERVER_LOCAL
            host = os.getenv('RABBITMQ_HOST_LOCAL', 'localhost')
            port = int(os.getenv('RABBITMQ_PORT_LOCAL', 5672))
            user = os.getenv('RABBITMQ_USER_LOCAL', 'admin')
            password = os.getenv('RABBITMQ_PASS_LOCAL', 'password123')
            vhost = os.getenv('RABBITMQ_VHOST_LOCAL', 'local')
        
        # 🔥 Environment'tan connection pool ayarlarını al
        heartbeat = int(os.getenv('RABBITMQ_HEARTBEAT', 600))
        blocked_connection_timeout = int(os.getenv('RABBITMQ_BLOCKED_CONNECTION_TIMEOUT', 300))
        
        self.connection_params = pika.ConnectionParameters(
            host=host,
            port=port,
            virtual_host=vhost,
            credentials=pika.PlainCredentials(user, password),
            heartbeat=heartbeat,
            blocked_connection_timeout=blocked_connection_timeout
        )
        
        print(f"🔌 RabbitMQ Bağlantı: {server_type} -> {host}:{port}/{vhost}")

    def get_connection(self):
        return pika.BlockingConnection(self.connection_params)

    def test_connection(self):
        try:
            connection = self.get_connection()
            connection.close()
            print("✅ RabbitMQ bağlantısı başarılı!")
            return True
        except Exception as e:
            print(f"❌ RabbitMQ bağlantı hatası: {e}")
            return False