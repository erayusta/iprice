import os
from dotenv import load_dotenv

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(parent_dir, '.env')

# .env dosyası varsa yükle (local development için)
if os.path.exists(env_path):
    load_dotenv(env_path)

# DATABASE_URL'i önce environment'tan, sonra DB_DATABASE'den, sonra .env'den al
DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('DB_DATABASE')