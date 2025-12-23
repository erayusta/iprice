import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
import pandas as pd

class UrlImporter:
    def __init__(self):
        # Veritabanı bağlantı bilgileriniz
        self.conn = psycopg2.connect(
            host=os.getenv('SHARED_DB_HOST', '10.20.50.16'),
            user=os.getenv('SHARED_DB_USER', 'ipricetestuser'),
            password=os.getenv('SHARED_DB_PASS', 'YeniSifre123!'),
            database=os.getenv('SHARED_DB_NAME', 'ipricetest'),
            port=os.getenv('SHARED_DB_PORT', '5432')
        )
        self.cursor = self.conn.cursor(cursor_factory=DictCursor)
        self.companies = self.get_companies()

    def get_companies(self):
        self.cursor.execute("SELECT id, name FROM company where marketplace_id = id")
        companies = {}
        for row in self.cursor:
            company_name = row['name'].lower().replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ı', 'i').replace('ö', 'o').replace('ç', 'c')
            companies[company_name] = row['id']
        return companies

    def get_company_id(self, store_name):
        normalized_name = store_name.lower().replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ı', 'i').replace('ö', 'o').replace('ç', 'c')
        return self.companies.get(normalized_name)

    # --- DEĞİŞİKLİK BURADA ---
    # Bu fonksiyonu orijinal, veritabanına yazan haline geri döndürüyoruz.
    def insert_or_update_url(self, company_id, mpn, url):
        """URL'yi veritabanında kontrol edip ekler veya günceller."""
        try:
            current_time = datetime.now()

            # Kaydın var olup olmadığını kontrol et
            self.cursor.execute("""
                SELECT id FROM product_url 
                WHERE company_id = %s AND mpn = %s
            """, (company_id, mpn))
            existing_record = self.cursor.fetchone()

            if existing_record:
                # Kayıt varsa GÜNCELLE
                self.cursor.execute("""
                    UPDATE product_url 
                    SET url = %s, updated_at = %s
                    WHERE company_id = %s AND mpn = %s
                """, (url, current_time, company_id, mpn))
            else:
                # Kayıt yoksa EKLE
                self.cursor.execute("""
                    INSERT INTO product_url (company_id, mpn, url, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (company_id, mpn, url, current_time, current_time))

            self.conn.commit() # Değişiklikleri onayla ve kaydet
            return True
        except Exception as e:
            self.conn.rollback() # Hata durumunda değişiklikleri geri al
            print(f"Hata: {str(e)}")
            return False
    # --- DEĞİŞİKLİK SONA ERDİ ---


    def import_data(self):
        stores = [
            'Gürgençler', 'Teknosa', 'Mediamarkt', 'Hepsiburada', 'Vatan',
            'Troy', 'Trendyol', 'TVT', 'Amazon', 'İtopya',
            'GamingGen', 'İncehesap', 'D&R', 'İdefix', 'Nethouse',
            'N11', 'PttAvm', 'Pazarama', 'Aynet', 'Pasaj', 'BEYMEN', 'Apple EDU', 'Apple'
        ]
        success_count = 0
        error_count = 0
        skip_count = 0
        print("=== URL İMPORT İŞLEMİ BAŞLADI (DB KAYIT MODU) ===\n")
        try:
            df = pd.read_csv('../crons/test.csv', delimiter=';')
            print(f"CSV Headers: {df.columns.tolist()}\n")
            for index, row in df.iterrows():
                mpn = str(row.iloc[0])
                if not mpn or pd.isna(row.iloc[0]):
                    continue
                print(f"İşleniyor - MPN: {mpn}")
                for store in stores:
                    if store in df.columns and pd.notna(row[store]) and str(row[store]).strip() != '-':
                        company_id = self.get_company_id(store)
                        url = str(row[store]).strip()
                        if company_id:
                            if self.insert_or_update_url(company_id, mpn, url):
                                success_count += 1
                                print(f"  ✓ Başarılı: {store}")
                            else:
                                error_count += 1
                                print(f"  ✗ Hata (DB): {store}")
                        else:
                            skip_count += 1
                            print(f"  ⚠  Atlandı (ID Yok): {store}")
        except FileNotFoundError:
            print(f"HATA: 'test.csv' dosyası bulunamadı.")
            return
        except Exception as e:
            print(f"Beklenmedik bir hata oluştu: {e}")
            return
        print("\n" + "=" * 60)
        print("ÖZET:")
        print(f"Başarılı kayıt (Ekleme/Güncelleme): {success_count}")
        print(f"Hatalı kayıt: {error_count}")
        print(f"Atlanan kayıt (ID bulunamadı): {skip_count}")
        print("=" * 60)
        print("\nTüm veriler başarıyla DB'ye kaydedildi!")

    def close(self):
        self.cursor.close()
        self.conn.close()

if __name__ == "__main__":
    importer = UrlImporter()
    try:
        importer.import_data()
    finally:
        importer.close()