import json
import psycopg2
from collections import defaultdict
from datetime import datetime

print("Veritabanına bağlanılıyor...")
try:
    # DB bağlantısı
    conn = psycopg2.connect(
        host='10.20.50.13',
        user='pa_liveuser',
        password='Z442XQ9ObVWs?.',
        database='price_analysis',
        port=5432
    )
    cur = conn.cursor()
    print("Veritabanı bağlantısı başarılı")

    # 1. Normalize attribute verilerini çek
    print("Attribute verileri çekiliyor...")
    cur.execute("""
    SELECT pav.mpn, pav.company_id, a.name AS attribute, pav.value
    FROM product_attribute_value pav
    JOIN attribute a ON a.id = pav.attribute_id
    WHERE pav.created_at >= NOW() - INTERVAL '1 day'
    """)

    records = cur.fetchall()
    print(f"Toplam {len(records)} kayıt bulundu")

    # 2. Özet tablo verisini oluştur
    print("Özet veriler oluşturuluyor...")
    summary = defaultdict(lambda: {"attributes": {}, "created_at": datetime.now()})

    for mpn, company_id, attribute, value in records:
        key = (mpn, company_id)
        summary[key]["attributes"][attribute] = value

    print(f"Toplam {len(summary)} ürün için özet oluşturuldu")

    # 3. Eski verileri temizle
    print("Eski veriler temizleniyor...")
    cur.execute("DELETE FROM product_attribute_summary WHERE created_at::date = CURRENT_DATE")
    print(f"{cur.rowcount} eski kayıt silindi")

    # 4. Yeni özet verileri ekle
    print("Yeni veriler ekleniyor...")
    for (mpn, company_id), data in summary.items():
        cur.execute("""
            INSERT INTO product_attribute_summary (mpn, company_id, attributes, created_at)
            VALUES (%s, %s, %s, %s)
        """, (mpn, company_id, json.dumps(data["attributes"]), data["created_at"]))

    print(f"{len(summary)} yeni kayıt eklendi")

    conn.commit()
    print("İşlem başarıyla tamamlandı")

except Exception as e:
    print(f"HATA: {e}")
    conn.rollback()
finally:
    if conn:
        cur.close()
        conn.close()
        print("Veritabanı bağlantısı kapatıldı")