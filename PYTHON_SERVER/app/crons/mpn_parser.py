import csv
import psycopg2
from datetime import datetime


def connect_to_db():
    """
    PostgreSQL veritabanına bağlantı oluşturur
    """
    # Bağlantı bilgileri düzeltildi - host ve port ayrı parametreler
    conn = psycopg2.connect(
        dbname="price_analysis",
        user="pa_liveuser",
        password="Z442XQ9ObVWs?.",
        host="10.20.50.13",
        port="5432"
    )
    return conn


def import_urls_to_db(csv_path):
    """
    CSV dosyasındaki URL'leri doğrudan product_url tablosuna ekler.

    Args:
        csv_path (str): CSV dosyasının yolu
    """
    # Şirket eşleştirmeleri - CSV başlığından veritabanı ID'sine
    company_mapping = {
        "pt.com.tr": 3,  # Apple
        "Gürgençler": 4,  # Gürgençler
        "Troy": 9,  # Troy
        "Aynet": 22,  # Aynet
        "TVT": 11,  # TVT
        "Trendyol": 10,  # Trendyol
        "Hepsiburada": 7,  # Hepsiburada
        "Amazon": 26,  # Amazon
        "Medimarkt": 6,  # Mediamarkt
        "Teknosa": 5,  # Teknosa
        "VATAN": 8,  # Vatan
        "Pazarama": 25  # Pazarama
    }

    conn = None
    cursor = None

    try:
        # Veritabanına bağlan
        conn = connect_to_db()
        cursor = conn.cursor()

        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file, delimiter=';')
            headers = next(csv_reader)  # Başlık satırını oku

            # Şimdiki zaman damgası
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # URL sayacı
            url_count = 0

            # Her satırı işle
            for row in csv_reader:
                mpn = row[0]  # MPN değeri

                # Her sütunu kontrol et
                for i, value in enumerate(row):
                    # İlk sütunu atla (MPN) ve boş URL'leri atla
                    if i > 0 and i < len(headers) and value and value != '-':
                        header = headers[i]

                        # Eğer başlık bilinen bir şirketse
                        if header in company_mapping:
                            company_id = company_mapping[header]
                            url = value

                            # Önce bu MPN ve şirket için bir kayıt var mı diye kontrol et
                            cursor.execute("""
                            SELECT id FROM product_url WHERE company_id = %s AND mpn = %s
                            """, (company_id, mpn))
                            existing_record = cursor.fetchone()

                            if existing_record:
                                # Kayıt varsa güncelle
                                cursor.execute("""
                                UPDATE product_url 
                                SET url = %s, updated_at = %s
                                WHERE company_id = %s AND mpn = %s
                                """, (url, now, company_id, mpn))
                            else:
                                # Kayıt yoksa yeni ekle
                                cursor.execute("""
                                INSERT INTO product_url (company_id, url, mpn, created_at, updated_at)
                                VALUES (%s, %s, %s, %s, %s)
                                """, (company_id, url, mpn, now, now))

                            url_count += 1

                            # Her 100 URL'de bir commit yap
                            if url_count % 100 == 0:
                                conn.commit()
                                print(f"{url_count} URL kaydedildi...")

            # Son değişiklikleri kaydet
            conn.commit()
            print(f"Toplam {url_count} URL başarıyla veritabanına eklendi.")

    except FileNotFoundError:
        print(f"Hata: '{csv_path}' dosyası bulunamadı.")
    except Exception as e:
        print(f"Veritabanı hatası: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    # Kullanım
    csv_path = 'testm4.csv'
    import_urls_to_db(csv_path)