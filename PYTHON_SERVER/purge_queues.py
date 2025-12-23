#!/usr/bin/env python3
"""
🗑️ RabbitMQ Queue Purge Script
===============================
Tüm RabbitMQ queue'lerini temizler (error ve completed dahil)

Kullanım:
    python purge_queues.py local
    python purge_queues.py azure
"""

import os
import sys
import requests
from typing import List, Dict
import json

# Renk kodları
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color


def load_env():
    """Load .env file"""
    env_vars = {}
    
    if not os.path.exists('.env'):
        print(f"{Colors.RED}❌ .env dosyası bulunamadı!{Colors.NC}")
        sys.exit(1)
    
    print(f"{Colors.BLUE}📄 .env dosyası yükleniyor...{Colors.NC}")
    
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Boş satırları ve yorum satırlarını atla
            if not line or line.startswith('#'):
                continue
            
            # Satırda = varsa ve geçerli variable name varsa
            if '=' in line:
                # Inline yorumları temizle
                if '#' in line:
                    # = den sonraki ilk # karakterini bul
                    key_val = line.split('=', 1)
                    if len(key_val) == 2:
                        key = key_val[0].strip()
                        val = key_val[1].split('#')[0].strip()
                        env_vars[key] = val
                else:
                    key, val = line.split('=', 1)
                    env_vars[key.strip()] = val.strip()
    
    print(f"{Colors.GREEN}✅ .env dosyası yüklendi ({len(env_vars)} variable){Colors.NC}")
    return env_vars


def get_rabbitmq_config(environment: str, env_vars: dict) -> dict:
    """Get RabbitMQ configuration based on environment"""
    
    if environment == 'local':
        config = {
            'host': env_vars.get('RABBITMQ_HOST_LOCAL'),
            'port': env_vars.get('RABBITMQ_PORT_LOCAL', '5672'),
            'user': env_vars.get('RABBITMQ_USER_LOCAL', env_vars.get('RABBITMQ_USER')),
            'pass': env_vars.get('RABBITMQ_PASS_LOCAL', env_vars.get('RABBITMQ_PASS')),
            'vhost': env_vars.get('RABBITMQ_VHOST_LOCAL', '/'),
            'api_port': '15672'
        }
        print(f"{Colors.GREEN}📍 Local RabbitMQ: {config['host']}:{config['port']} (vhost: {config['vhost']}){Colors.NC}")
    else:  # azure
        config = {
            'host': env_vars.get('RABBITMQ_HOST_AZURE'),
            'port': env_vars.get('RABBITMQ_PORT_AZURE', '5672'),
            'user': env_vars.get('RABBITMQ_USER_AZURE', env_vars.get('RABBITMQ_USER')),
            'pass': env_vars.get('RABBITMQ_PASS_AZURE', env_vars.get('RABBITMQ_PASS')),
            'vhost': env_vars.get('RABBITMQ_VHOST_AZURE', '/'),
            'api_port': '15672'
        }
        print(f"{Colors.BLUE}☁️  Azure RabbitMQ: {config['host']}:{config['port']} (vhost: {config['vhost']}){Colors.NC}")
    
    return config


def get_queues() -> List[str]:
    """Get all queue names"""
    return [
        # Scrapy queues
        'scrapy.queue',
        'scrapy.queue.completed',
        'scrapy.queue.error',
        
        # Selenium queues
        'selenium.queue',
        'selenium.queue.completed',
        'selenium.queue.error',
        
        # Playwright queues
        'playwright.queue',
        'playwright.queue.completed',
        'playwright.queue.error',
        
        # Save queues
        'save.queue',
        'save.queue.completed',
        'save.queue.error',
        
        # Test queues (optional)
        'test.queue',
        'test.queue.completed',
        'test.queue.error',
    ]


def purge_queue(queue_name: str, config: dict) -> Dict[str, any]:
    """Purge a single queue"""
    
    # URL encode vhost
    vhost = config['vhost'].replace('/', '%2F')
    
    api_url = f"http://{config['host']}:{config['api_port']}/api"
    auth = (config['user'], config['pass'])
    
    try:
        # Queue bilgisini al
        queue_info_url = f"{api_url}/queues/{vhost}/{queue_name}"
        response = requests.get(queue_info_url, auth=auth, timeout=10)
        
        if response.status_code == 404:
            return {'status': 'skip', 'message': 'Queue bulunamadı', 'count': 0}
        
        if response.status_code != 200:
            return {'status': 'error', 'message': f'HTTP {response.status_code}', 'count': 0}
        
        # Mesaj sayısını al
        queue_info = response.json()
        message_count = queue_info.get('messages', 0)
        
        # Queue'yu purge et
        purge_url = f"{api_url}/queues/{vhost}/{queue_name}/contents"
        purge_response = requests.delete(purge_url, auth=auth, timeout=10)
        
        if purge_response.status_code in [200, 204]:
            return {'status': 'success', 'message': 'Temizlendi', 'count': message_count}
        else:
            return {'status': 'error', 'message': f'Purge HTTP {purge_response.status_code}', 'count': message_count}
            
    except requests.exceptions.Timeout:
        return {'status': 'error', 'message': 'Timeout', 'count': 0}
    except requests.exceptions.ConnectionError:
        return {'status': 'error', 'message': 'Connection failed', 'count': 0}
    except Exception as e:
        return {'status': 'error', 'message': str(e), 'count': 0}


def main():
    # Banner
    print(f"{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         🗑️  RabbitMQ Queue Purge Script                  ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.NC}")
    
    # Environment seçimi
    if len(sys.argv) < 2:
        environment = 'local'
        print(f"{Colors.YELLOW}⚠️  Environment belirtilmedi, varsayılan: local{Colors.NC}")
    else:
        environment = sys.argv[1].lower()
    
    if environment not in ['local', 'azure']:
        print(f"{Colors.RED}❌ Hatalı environment! Kullanım: {sys.argv[0]} [local|azure]{Colors.NC}")
        sys.exit(1)
    
    print(f"{Colors.YELLOW}🌍 Environment: {environment}{Colors.NC}")
    print()
    
    # .env dosyasını yükle
    env_vars = load_env()
    print()
    
    # RabbitMQ config al
    config = get_rabbitmq_config(environment, env_vars)
    print()
    
    # Queue listesi
    queues = get_queues()
    
    # Onay iste
    print(f"{Colors.YELLOW}⚠️  DİKKAT: Aşağıdaki {len(queues)} queue temizlenecek:{Colors.NC}")
    print()
    for queue in queues:
        print(f"   {Colors.RED}🗑️{Colors.NC}  {queue}")
    print()
    
    # Onay
    response = input("Devam etmek istiyor musunuz? (yes/no): ")
    if response.lower() not in ['yes', 'y', 'evet', 'e']:
        print(f"{Colors.YELLOW}❌ İşlem iptal edildi{Colors.NC}")
        sys.exit(0)
    
    print()
    print(f"{Colors.GREEN}🚀 Queue purge işlemi başlatılıyor...{Colors.NC}")
    print()
    
    # Queue'ları temizle
    stats = {
        'success': 0,
        'skip': 0,
        'error': 0,
        'total_messages': 0
    }
    
    for queue in queues:
        print(f"🗑️  Purging: {queue:30s} ... ", end='', flush=True)
        
        result = purge_queue(queue, config)
        
        if result['status'] == 'success':
            stats['success'] += 1
            stats['total_messages'] += result['count']
            print(f"{Colors.GREEN}✅ Temizlendi ({result['count']} mesaj){Colors.NC}")
        elif result['status'] == 'skip':
            stats['skip'] += 1
            print(f"{Colors.YELLOW}⚠️  {result['message']}{Colors.NC}")
        else:
            stats['error'] += 1
            print(f"{Colors.RED}❌ {result['message']}{Colors.NC}")
    
    # Özet
    print()
    print(f"{Colors.BLUE}{'═' * 60}{Colors.NC}")
    print(f"{Colors.GREEN}✅ Purge işlemi tamamlandı!{Colors.NC}")
    print()
    print(f"   {Colors.GREEN}Başarılı:{Colors.NC} {stats['success']} queue")
    print(f"   {Colors.YELLOW}Atlandı:{Colors.NC} {stats['skip']} queue")
    print(f"   {Colors.RED}Hata:{Colors.NC} {stats['error']} queue")
    print(f"   {Colors.CYAN}Silinen Mesaj:{Colors.NC} {stats['total_messages']} adet")
    print(f"{Colors.BLUE}{'═' * 60}{Colors.NC}")
    print()
    
    # Alternatif yöntem
    if stats['error'] > 0:
        print(f"{Colors.YELLOW}💡 Alternatif Yöntem (Docker ile):{Colors.NC}")
        if environment == 'local':
            print(f"{Colors.BLUE}   docker exec rabbitmq rabbitmqadmin purge queue name=scrapy.queue{Colors.NC}")
            print(f"{Colors.BLUE}   docker exec rabbitmq rabbitmqadmin purge queue name=selenium.queue{Colors.NC}")
            print(f"{Colors.BLUE}   docker exec rabbitmq rabbitmqadmin purge queue name=playwright.queue{Colors.NC}")
            print(f"{Colors.BLUE}   docker exec rabbitmq rabbitmqadmin purge queue name=save.queue{Colors.NC}")
        print()
    
    print(f"{Colors.GREEN}🎉 Tamamlandı!{Colors.NC}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}❌ İşlem iptal edildi (Ctrl+C){Colors.NC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Beklenmeyen hata: {e}{Colors.NC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

