#!/usr/bin/env python3
"""
🔒 Proxy System Test Script
===========================
Yeni dinamik proxy sistemini test eder

Test Cases:
1. Queue'dan use_proxy=false → Proxy kullanılmaz
2. Queue'dan use_proxy=true, proxy_type=brightdata → BrightData proxy
3. Queue'dan use_proxy=true, proxy_type=free → Free proxy
4. Queue'dan use_proxy=true, proxy_type=smartproxy → SmartProxy
5. Job data yok → .env ayarlarına göre
"""

import sys
sys.path.append('/Users/serkanodaci/Projects/iPriceNew/price_analysis_service')

from app.services.ProxyManager import get_proxy_manager

def test_proxy_system():
    """Proxy sistemini test et"""
    
    print("🔒 Proxy System Test Başlıyor...")
    print("=" * 50)
    
    proxy_manager = get_proxy_manager()
    
    # Test Case 1: use_proxy=false
    print("\n📋 Test 1: use_proxy=false")
    job_data_1 = {
        'use_proxy': False,
        'proxy_type': 'brightdata'
    }
    proxy_1 = proxy_manager.get_proxy(job_data=job_data_1)
    print(f"   Result: {proxy_1}")
    print(f"   Expected: None")
    print(f"   Status: {'✅' if proxy_1 is None else '❌'}")
    
    # Test Case 2: use_proxy=true, proxy_type=brightdata
    print("\n📋 Test 2: use_proxy=true, proxy_type=brightdata")
    job_data_2 = {
        'use_proxy': True,
        'proxy_type': 'brightdata'
    }
    proxy_2 = proxy_manager.get_proxy(job_data=job_data_2)
    print(f"   Result: {proxy_2}")
    print(f"   Expected: BrightData proxy URL")
    print(f"   Status: {'✅' if proxy_2 and 'brd.superproxy.io' in proxy_2 else '❌'}")
    
    # Test Case 3: use_proxy=true, proxy_type=free
    print("\n📋 Test 3: use_proxy=true, proxy_type=free")
    job_data_3 = {
        'use_proxy': True,
        'proxy_type': 'free'
    }
    proxy_3 = proxy_manager.get_proxy(job_data=job_data_3)
    print(f"   Result: {proxy_3}")
    print(f"   Expected: Free proxy URL or None (if no proxies)")
    print(f"   Status: {'✅' if proxy_3 is None or proxy_3.startswith('http://') else '❌'}")
    
    # Test Case 4: use_proxy=true, proxy_type=smartproxy
    print("\n📋 Test 4: use_proxy=true, proxy_type=smartproxy")
    job_data_4 = {
        'use_proxy': True,
        'proxy_type': 'smartproxy'
    }
    proxy_4 = proxy_manager.get_proxy(job_data=job_data_4)
    print(f"   Result: {proxy_4}")
    print(f"   Expected: SmartProxy URL or None (if no credentials)")
    print(f"   Status: {'✅' if proxy_4 is None or 'gate.smartproxy.com' in proxy_4 else '❌'}")
    
    # Test Case 5: Job data yok
    print("\n📋 Test 5: Job data yok (.env ayarları)")
    proxy_5 = proxy_manager.get_proxy()
    print(f"   Result: {proxy_5}")
    print(f"   Expected: .env'deki PROXY_TYPE'a göre")
    print(f"   Status: {'✅' if proxy_5 is None or proxy_5.startswith('http://') else '❌'}")
    
    # Test Case 6: Selenium proxy format
    print("\n📋 Test 6: Selenium proxy format")
    selenium_proxy = proxy_manager.get_selenium_proxy(job_data=job_data_2)
    print(f"   Result: {selenium_proxy}")
    print(f"   Expected: host:port format")
    print(f"   Status: {'✅' if selenium_proxy is None or ':' in selenium_proxy else '❌'}")
    
    # Test Case 7: Proxy dict format
    print("\n📋 Test 7: Proxy dict format")
    proxy_dict = proxy_manager.get_proxy_dict(job_data=job_data_2)
    print(f"   Result: {proxy_dict}")
    print(f"   Expected: {{'http': '...', 'https': '...'}} or None")
    print(f"   Status: {'✅' if proxy_dict is None or ('http' in proxy_dict and 'https' in proxy_dict) else '❌'}")
    
    print("\n" + "=" * 50)
    print("🎉 Proxy System Test Tamamlandı!")
    
    # Proxy stats
    stats = proxy_manager.get_stats()
    print(f"\n📊 Proxy İstatistikleri:")
    print(f"   - Enabled: {stats['enabled']}")
    print(f"   - Type: {stats['type']}")
    print(f"   - Free Proxy Count: {stats['free_proxy_count']}")
    print(f"   - Tested Proxies: {stats['tested_proxy_count']}")
    print(f"   - Working Proxies: {stats['working_proxies']}")
    print(f"   - Failed Proxies: {stats['failed_proxies']}")

if __name__ == "__main__":
    test_proxy_system()
