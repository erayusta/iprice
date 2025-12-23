from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import time

def get_amazon_product_info(url: str) -> dict:
    """
    Belirtilen Amazon URL'sinden ürün fiyatını ve ana satıcı adını çeker.
    """
    product_data = {"main_seller": {}, "other_sellers": []}

    # Tarayıcı ayarları
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Görünmez modda çalıştır
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    chrome_options.binary_location = '/usr/bin/chromium'


    driver = None
    try:
        service = Service(executable_path='/usr/bin/chromedriver', log_output='chromedriver.log')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        print(">>> Tarayıcı başlatıldı ve sayfa yükleniyor...")

        driver.get(url)
        time.sleep(3)

        try:
            CSS_PRICE = '.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay .a-price-whole'
            price_element = driver.find_element(By.CSS_SELECTOR, CSS_PRICE)
            product_data["price"] = price_element.text.strip()
            print(f"✅ Fiyat bulundu: {product_data['price']}")
        except NoSuchElementException:
            print("❌ Fiyat elementi bulunamadı.")
            product_data["price"] = "Bulunamadı"

        # Satıcı bilgisini çek
        try:
            XPATH_SELLER = '//*[@id="bylineInfo"]'
            seller_element = driver.find_element(By.XPATH, XPATH_SELLER)
            product_data["seller_name"] = seller_element.text.strip()
            print(f"✅ Satıcı bulundu: {product_data['seller_name']}")
        except NoSuchElementException:
            print("❌ Satıcı elementi bulunamadı.")
            product_data["seller_name"] = "Bulunamadı"

        XPATH_OTHER_SELLERS_BUTTON = '//*[@id="aod-ingress-link"]'

        #diğer satıcılar
        try:
            XPATH_SEE_ALL_PRODUCTS = '//*[@id="aod-offer-list"]/div'

            see_all_button = driver.find_element(By.XPATH, XPATH_SEE_ALL_PRODUCTS)

            driver.execute_script("arguments[0].click();", see_all_button)

            print("✅ 'Tüm Ürünleri Gör' butonuna tıklandı.")
            time.sleep(1)

        except NoSuchElementException:
            print("ℹ️ 'Tüm Ürünleri Gör' butonu bulunamadı.")
        except Exception as e:
            print(f"❌ Butona tıklanırken bir hata oluştu: {e}")

        other_sellers_buttons = driver.find_elements(By.XPATH, XPATH_OTHER_SELLERS_BUTTON)

        if other_sellers_buttons:
            print("✅ Diğer satıcılar butonu bulundu. Pop-up yöntemi kullanılıyor...")
            try:
                button = other_sellers_buttons[0]
                driver.execute_script("arguments[0].click();", button)
                time.sleep(4)

                XPATH_SELLER_BOXES_IN_POPUP = '//*[@id="aod-offer"]'
                seller_boxes = driver.find_elements(By.XPATH, XPATH_SELLER_BOXES_IN_POPUP)

                print(f"    -> Pop-up içinden {len(seller_boxes)} adet satıcı bulundu.")
                for i, seller_box in enumerate(seller_boxes, 1):
                    seller_info = {}
                    try:
                        seller_element = seller_box.find_element(By.XPATH, ".//div[@id='aod-offer-soldBy']//a")
                        seller_info["seller_name"] = seller_element.text.strip()
                    except Exception:
                        seller_info["seller_name"] = f"Satıcı {i}"
                    try:
                        price_xpath = f'//*[@id="aod-price-{i}"]/div/span[2]/span[2]/span[1]'
                        seller_info["price"] = driver.find_element(By.XPATH, price_xpath).text.strip()
                    except Exception:
                        seller_info["price"] = None

                    product_data["other_sellers"].append(seller_info)

            except Exception as e:
                print(f"❌ Pop-up açılırken veya işlenirken bir hata oluştu: {e}")
        return product_data


    except WebDriverException as e:
        print(f"HATA: WebDriver hatası oluştu: {e}")
    except Exception as e:
        print(f"Beklenmeyen bir hata oluştu: {e}")
    finally:
        if driver:
            driver.quit()  # Tarayıcıyı kapat
            print("\n>>> Tarayıcı kapatıldı.")
    return product_data

if __name__ == "__main__":
    amazon_url = "https://www.amazon.com.tr/KIOXIA-EXCERIA-PLUS-1TB-Ta%C5%9F%C4%B1nabilir/dp/B0DRDBT6RV/ref=sr_1_1?__mk_tr_TR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=2X55O8WBFRO88&dib=eyJ2IjoiMSJ9.73bUUrRUQIGRGEX4qnY3Xg.1QSnH5HBWfP9lf87uOM_mA30LZK3wJpKIVSosqIs8d8&dib_tag=se&keywords=LXD20K001TG8&qid=1752153442&sprefix=lxd20k001tg8%2Caps%2C85&sr=8-1"

    product_info = get_amazon_product_info(amazon_url)

    print("\n--- Çekilen Bilgiler ---")
    print(f"Fiyat: {product_info['price']}")
    print(f"Satıcı: {product_info['seller_name']}")
    print(f"Satıcı: {product_info['other_sellers']}")
