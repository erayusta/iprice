import asyncio
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from typing import Dict, Any, List

from app.helper.get_random_agents import get_random_user_agent


class SeleniumParsingServiceByCompany:
    """
    Selenium tabanlı parsing service
    """

    def __init__(self, product_service, screenshot_service):
        self.product_service = product_service
        self.screenshot_service = screenshot_service
        self.logger = logging.getLogger(__name__)

    def _get_chrome_options(self) -> Options:
        """Chrome seçeneklerini ayarla"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument(get_random_user_agent())
        chrome_options.binary_location = '/usr/bin/chromium'

        return chrome_options

    def _get_chrome_service(self) -> Service:
        """Chrome service'ini ayarla"""
        return Service(
            executable_path='/usr/bin/chromedriver',
            log_output='/dev/null'  # Log'ları sustur
        )

    async def process_company_selenium(self, company_id: int, company_name: str) -> Dict[str, Any]:
        """
        Selenium ile company processing
        """
        start_time = time.time()

        try:
            self.logger.info(f"🔍 Starting Selenium processing for: {company_name}")

            # Ürünleri çek
            products = self.product_service.get_products_with_urls_by_company_id(company_id)

            if not products:
                return {
                    'company_id': company_id,
                    'company_name': company_name,
                    'status': 'no_products',
                    'duration': time.time() - start_time
                }

            # Firma attribute'larını çek
            attributes = self.product_service.get_attributes_for_company(company_name)

            if not attributes:
                return {
                    'company_id': company_id,
                    'company_name': company_name,
                    'status': 'no_attributes',
                    'product_count': len(products),
                    'duration': time.time() - start_time
                }

            self.logger.info(f"📦 Processing {len(products)} products with {len(attributes)} attributes")

            # İlk 5 ürünü test et (tam implementasyon için tümünü yapabilirsin)
            results = []

            for i, product in enumerate(products):
                self.logger.info(f"🔄 Processing product {i + 1}/{len(products)}: {product.mpn}")

                result = await self._process_single_product(product, attributes, company_name)
                results.append(result)

                # Kısa bekleme (site yükünü azaltmak için)
                await asyncio.sleep(1)

            # İstatistikler
            successful = len([r for r in results if r.get('status') == 'success'])
            failed = len(results) - successful
            total_duration = time.time() - start_time

            self.logger.info(f"✅ Selenium processing completed: {successful}/{len(results)} successful")

            return {
                'company_id': company_id,
                'company_name': company_name,
                'status': 'completed',
                'total_products': len(products),
                'processed_products': len(results),
                'successful': successful,
                'failed': failed,
                'duration': total_duration,
                'results': results
            }

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"❌ Selenium processing error: {e}")

            return {
                'company_id': company_id,
                'company_name': company_name,
                'status': 'error',
                'error': str(e),
                'duration': duration
            }

    async def _process_single_product(self, product, attributes: List[Dict], company_name: str) -> Dict[str, Any]:
        """
        Tek ürünü işle
        """
        return await asyncio.get_event_loop().run_in_executor(
            None, self._scrape_product_sync, product, attributes, company_name
        )

    def _scrape_product_sync(self, product, attributes: List[Dict], company_name: str) -> Dict[str, Any]:
        driver = None
        start_time = time.time()

        try:
            print(f"🔍 Processing URL: {product.url}")
            print(f"📋 Attributes to extract: {len(attributes)}")

            # Chrome driver'ı başlat
            chrome_options = self._get_chrome_options()
            service = self._get_chrome_service()
            driver = webdriver.Chrome(service=service, options=chrome_options)

            # Sayfayı yükle
            driver.get(product.url)
            print(f"📄 Page loaded: {driver.current_url}")

            # Sayfa yüklenmesini bekle
            time.sleep(3)

            # Attribute'ları çıkar
            attribute_values = []

            for attr in attributes:
                try:
                    print(f"🎯 Processing attribute: {attr['attribute_name']}")
                    print(f"🎯 Selector type: {attr['selector_type']}")
                    print(f"🎯 XPath/CSS: {attr['xpath']}")

                    if attr['attribute_name'] == 'is_redirect':
                        value = driver.current_url != product.url
                        print(f"✅ Redirect check: {value}")
                    else:
                        # Selector type'a göre element bul
                        if attr['selector_type'] == 'xpath':
                            elements = driver.find_elements(By.XPATH, attr['xpath'])
                            print(f"🔍 Found {len(elements)} elements with XPath")
                            value = elements[0].text.strip() if elements else None
                        elif attr['selector_type'] == 'css':
                            elements = driver.find_elements(By.CSS_SELECTOR, attr['xpath'])
                            print(f"🔍 Found {len(elements)} elements with CSS")
                            value = elements[0].text.strip() if elements else None
                        else:
                            value = None
                            print(f"❌ Unknown selector type: {attr['selector_type']}")

                    print(f"📝 Extracted value: '{value}'")

                    attribute_data = {
                        'company_id': attr['company_id'],
                        'mpn': product.mpn,
                        'attribute_id': attr['attribute_id'],
                        'attribute_name': attr['attribute_name'],
                        'value': value
                    }

                    attribute_values.append(attribute_data)

                except Exception as e:
                    print(f"❌ Attribute extraction error for {attr['attribute_name']}: {e}")

            print(f"📊 Total attributes to save: {len(attribute_values)}")
            for av in attribute_values:
                print(f"   - {av['attribute_name']}: '{av['value']}'")

            # Veritabanına kaydet
            if attribute_values:
                self.product_service.create_attribute_values(attribute_values)
                self.logger.info(f"💾 Saved {len(attribute_values)} attributes for {product.mpn}")

            return {
                'status': 'success',
                'mpn': product.mpn,
                'url': product.url,
                'attributes_processed': len(attribute_values),
                'duration': time.time() - start_time
            }

        except Exception as e:
            return {
                'status': 'failed',
                'mpn': product.mpn,
                'url': product.url,
                'error': str(e),
                'duration': time.time() - start_time
            }

        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass