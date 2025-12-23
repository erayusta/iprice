import requests
import os
from typing import Dict, Any

class CallbackService:
    def __init__(self):
        # Environment'dan Laravel URL'ini al, yoksa localhost kullan
        self.laravel_base_url = os.getenv('LARAVEL_API_URL', 'http://localhost:8000')

    def send_parsing_result(self, result: Dict[str, Any]) -> bool:
        try:
            callback_data = {
                'job_id': result.get('job_id'),
                'status': result.get('status'),
                'error': result.get('error'),
                'parser_used': result.get('parser_used'),
                'http_status_code': result.get('http_status_code', 0),
                'parsed_data': {  # ← BU KISMI EKLE
                    'url': result.get('url'),
                    'price': result.get('price'),
                    'stock': result.get('stock'),
                    'timestamp': result.get('timestamp'),
                }
            }

            print(f"📤 Laravel'e callback gönderiliyor: {callback_data}")

            response = requests.post(
                f"{self.laravel_base_url}/api/parsing-callback",
                json=callback_data,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )

            print(f"📤 Laravel yanıtı: {response.status_code} - {response.text}")
            return response.status_code == 200

        except Exception as e:
            print(f" Laravel callback hatası: {e}")
            return False