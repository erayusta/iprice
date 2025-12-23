# Görsel ve Video Engelleme Chrome Eklentisi

Bu Chrome eklentisi, ziyaret ettiğiniz web sitelerinde fotoğraf ve videoların yüklenmesini engeller. Bu sayede:
- İnternet veri kullanımınızı azaltır
- Sayfa yükleme hızını artırır
- Görsel içerik olmadan daha hızlı gezinme sağlar

## Kurulum

1. Chrome'da `chrome://extensions/` adresine gidin
2. Sağ üst köşede "Geliştirici modu"nu açın
3. "Paketlenmemiş uzantı yükle" butonuna tıklayın
4. `image-block` klasörünü seçin

## Kullanım

1. Eklenti yüklendikten sonra, tarayıcı araç çubuğunda eklenti ikonunu göreceksiniz
2. İkona tıklayarak popup penceresini açın
3. Açma/kapama butonunu kullanarak eklentiyi aktif veya pasif hale getirebilirsiniz
4. Eklenti varsayılan olarak aktif durumdadır

## Özellikler

- **Ağ seviyesinde engelleme**: `declarativeNetRequest` API'si ile görsel ve video istekleri ağ seviyesinde engellenir
- **DOM seviyesinde engelleme**: Content script ile sayfadaki img ve video etiketleri engellenir
- **Dinamik içerik desteği**: Sayfaya sonradan eklenen görsel ve videolar da otomatik olarak engellenir
- **Kolay açma/kapama**: Popup üzerinden tek tıkla açıp kapatabilirsiniz

## İkon Dosyaları

Eklentiyi yüklemeden önce `icons` klasörüne aşağıdaki boyutlarda PNG ikonlar eklemeniz gerekmektedir:
- `icon16.png` (16x16 piksel)
- `icon48.png` (48x48 piksel)
- `icon128.png` (128x128 piksel)

İkonlar olmadan da eklenti çalışır, ancak tarayıcı araç çubuğunda varsayılan ikon görünecektir.

## Teknik Detaylar

- **Manifest Version**: 3
- **Engelleme Yöntemi**: 
  - `declarativeNetRequest` ile ağ seviyesinde engelleme
  - Content script ile DOM manipülasyonu
- **Storage**: Chrome Storage API ile durum saklama

## Lisans

Bu proje özgür yazılımdır.

