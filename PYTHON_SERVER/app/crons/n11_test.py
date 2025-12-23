from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def get_product_links():
    print("Chrome için opsiyonlar ayarlanıyor...")
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument('--disable-dev-tools')
    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    chrome_options.binary_location = '/usr/bin/chromium'

    service = Service(
        executable_path='/usr/bin/chromedriver',
        log_output='chromedriver.log'
    )

    print("Chrome başlatılıyor...")
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Chrome başlatma hatası: {e}")
        return

    try:
        url = 'https://www.n11.com/arama?q=MC8K4TU%2FA'
        print(f"Sayfa yükleniyor: {url}")
        driver.get(url)

        print(f"Şu anki URL: {driver.current_url}")
        is_ready = driver.execute_script("return document.readyState")
        print(f"Sayfa durumu: {is_ready}")

        print("\nÜrün container'ı aranıyor...")
        try:
            wait = WebDriverWait(driver, 15)
            container = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "prdct-cntnr-wrppr"))
            )

            # Ürün kartlarını bul
            product_cards = container.find_elements(By.CLASS_NAME, "p-card-wrppr")
            print(f"Bulunan ürün kartı sayısı: {len(product_cards)}")

            # Her karttan bir link al (tekrarları önle)
            unique_links = set()
            for card in product_cards:
                try:
                    link = card.find_element(By.TAG_NAME, "a")
                    href = link.get_attribute('href')
                    if href:
                        unique_links.add(href)
                except Exception as e:
                    print(f"Kart link hatası: {e}")
                    continue

            print(f"\nBenzersiz link sayısı: {len(unique_links)}")
            for href in unique_links:
                print(f"Ürün URL: {href}")

        except Exception as e:
            print(f"Container bulma hatası: {e}")
            print("\nAlternatif yöntem deneniyor...")

            try:
                product_cards = driver.find_elements(By.CLASS_NAME, "p-card-wrppr")
                unique_links = set()

                for card in product_cards:
                    try:
                        link = card.find_element(By.TAG_NAME, "a")
                        href = link.get_attribute('href')
                        if href:
                            unique_links.add(href)
                    except:
                        continue

                print(f"Alternatif yöntemle bulunan benzersiz link sayısı: {len(unique_links)}")
                for href in unique_links:
                    print(f"Ürün URL: {href}")

            except Exception as e2:
                print(f"Alternatif yöntemde de hata oluştu: {e2}")
                print("\nSayfa kaynağından bir parça:")
                print(driver.page_source[:1000])

    except Exception as e:
        print(f"Genel hata: {e}")

    finally:
        print("Tarayıcı kapatılıyor...")
        try:
            driver.quit()
        except Exception as e:
            print(f"Tarayıcı kapatma hatası: {e}")


if __name__ == "__main__":
    get_product_links()