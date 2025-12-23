import json
from collections import Counter


def count_mpns(json_file_path):
    """
    JSON dosyasındaki toplam MPN sayısını, benzersiz MPN sayısını hesaplar
    ve tekrar eden tüm MPN'leri listeler

    Args:
        json_file_path (str): JSON dosyasının yolu
    """
    try:
        # JSON dosyasını okuma
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Tüm MPN değerlerini toplama
        mpn_values = [item.get('mpn') for item in data if 'mpn' in item]

        # Toplam MPN sayısı
        total_mpn_count = len(mpn_values)

        # Benzersiz MPN sayısını hesaplama
        unique_mpns = set(mpn_values)
        unique_mpn_count = len(unique_mpns)

        # MPN frekanslarını hesaplama
        mpn_counter = Counter(mpn_values)

        # Tekrar eden MPNleri bulma (en az 2 kez geçenler)
        repeated_mpns = {mpn: count for mpn, count in mpn_counter.items() if count > 1}
        repeated_mpns_sorted = sorted(repeated_mpns.items(), key=lambda x: x[1], reverse=True)

        # Sonuçları yazdır
        print(f"Toplam MPN sayısı: {total_mpn_count}")
        print(f"Benzersiz MPN sayısı: {unique_mpn_count}")
        print(f"Tekrar eden MPN sayısı: {len(repeated_mpns)}")

        print("\nTüm tekrar eden MPNler (sıklık sırasına göre):")
        for mpn, count in repeated_mpns_sorted:
            print(f"{mpn}: {count} kez")

    except Exception as e:
        print(f"Hata oluştu: {e}")


if __name__ == "__main__":
    # Dosya yolunu belirtin - kendi dosya yolunuzu buraya yazın
    json_file_path = 'all_marketplace_results.json'

    # MPN sayılarını hesapla ve sonuçları yazdır
    count_mpns(json_file_path)