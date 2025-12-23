# Web Öğe Seçici ve Veri Toplayıcı Chrome Eklentisi

Bu Chrome eklentisi, web sayfalarından öğe seçme ve otomatik veri toplama işlemlerini gerçekleştirmenizi sağlar.

## Özellikler

- ✅ **Öğe Seçme**: Web sayfalarındaki öğeleri görsel olarak seçip kaydetme
- ✅ **Seçici Yönetimi**: Domain bazlı seçici kaydetme ve yönetme
- ✅ **Otomatik Tarama**: URL listesi ile otomatik veri toplama
- ✅ **Sonuç Görüntüleme**: Toplanan verileri görüntüleme ve JSON olarak indirme

## Kurulum

1. Chrome'da `chrome://extensions/` adresine gidin
2. Sağ üstteki "Geliştirici modu"nu açın
3. "Paketlenmemiş uzantı yükle" butonuna tıklayın
4. Bu klasörü seçin

## Kullanım

### 1. Öğe Seçme

1. Bir web sitesine gidin
2. Side panel'i açın (eklenti ikonuna tıklayın)
3. "Öğe Seç" sekmesine gidin
4. "Öğe Seç Başlat" butonuna tıklayın
5. Sayfada istediğiniz öğeye tıklayın
6. Öğe bilgileri görünecek, bir "Label" (etiket) girin (örn: price, title)
7. "Seçiciyi Kaydet" butonuna tıklayın

### 2. URL Tarama

1. "URL Tarama" sekmesine gidin
2. Her satıra bir URL yazın
3. "Tarama Başlat" butonuna tıklayın
4. Eklenti her URL'yi sırayla açacak ve kayıtlı seçicilere göre veri toplayacak

### 3. Sonuçları Görüntüleme

1. "Sonuçlar" sekmesine gidin
2. Toplanan tüm verileri görüntüleyin
3. "JSON Olarak İndir" butonu ile verileri indirebilirsiniz

## Dosya Yapısı

```
chrome-extension/
├── manifest.json          # Eklenti manifest dosyası
├── background.js          # Background service worker
├── contentScript.js       # Sayfa içi script (öğe seçme ve veri toplama)
├── sidepanel/
│   ├── index.html         # Side panel arayüzü
│   ├── panel.js           # Panel JavaScript
│   └── style.css          # Panel stilleri
└── README.md              # Bu dosya
```

## Veri Formatı

### Kayıtlı Seçiciler
```json
{
  "vatanbilgisayar.com": [
    {
      "selector": ".product-list__price",
      "label": "price"
    },
    {
      "selector": ".product-list__title",
      "label": "title"
    }
  ]
}
```

### Tarama Sonuçları
```json
[
  {
    "url": "https://www.vatanbilgisayar.com/iphone.html",
    "domain": "vatanbilgisayar.com",
    "data": {
      "price": "43.999",
      "title": "iPhone 15 Pro"
    },
    "timestamp": "2025-01-06T10:45:00.000Z"
  }
]
```

## Notlar

- Eklenti, Chrome Storage API kullanarak verileri saklar
- Her domain için farklı seçiciler tanımlanabilir
- Tarama sırasında sayfalar arka planda açılır ve otomatik kapanır
- Rate limiting için URL'ler arasında 500ms bekleme süresi vardır

## Lisans

Bu proje özel kullanım içindir.

