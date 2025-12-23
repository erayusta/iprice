# Product URL İşleme Komutu

Bu komut, product URL JSON dosyasındaki verileri işleyerek `company_products_urls` tablosuna ekler.

## Kullanım

```bash
php artisan process:product-urls /path/to/product_url_202510091504.json
```

## Nasıl Çalışır

1. **JSON Dosyasını Okur**: Product URL verilerini JSON dosyasından okur
2. **Domain Eşleştirmesi**: Her URL'den domain çıkarır (örn: `hepsiburada.com`)
3. **Company Bulma**: Companies tablosundaki URL'lerden domain eşleştirmesi yapar
4. **Product Bulma**: MPN ile `user_products` tablosundan `product_id` bulur
5. **Kayıt Ekleme**: `company_products_urls` tablosuna yeni kayıt ekler

## Örnek Veri Yapısı

### Product URL JSON:
```json
{
  "product_url": [
    {
      "id": 1353,
      "company_id": 7,
      "url": "https://www.hepsiburada.com/apple-macbook-air-m3...",
      "mpn": "MRXR3TU/A",
      "created_at": "2024-12-31T15:58:14.000Z",
      "updated_at": "2024-12-31T15:58:44.000Z"
    }
  ]
}
```

### Companies Tablosu:
- `url` kolonu: `https://www.hepsiburada.com`
- Domain çıkarımı: `hepsiburada.com`

### User Products Tablosu:
- `mpn` kolonu ile eşleştirme yapılır

### Sonuç:
`company_products_urls` tablosuna:
- `company_id`: Eşleşen company'nin ID'si
- `product_id`: MPN ile bulunan user product'ın ID'si  
- `url`: Orijinal product URL'i

## İstatistikler

Komut çalıştıktan sonra şu istatistikleri gösterir:
- İşlenen toplam kayıt sayısı
- Başarılı eklenen kayıt sayısı
- Atlanan kayıt sayısı (zaten mevcut)
- Başarısız kayıt sayısı

## Hata Durumları

- Geçersiz URL formatı
- Domain için company bulunamama
- MPN için user product bulunamama
- Veritabanı hataları
