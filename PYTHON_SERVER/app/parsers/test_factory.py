# parsers/test_factory.py (test için)
from .factory import ParserFactory, create_parser


def test_factory():
    """Factory'yi test et"""
    try:
        # Mevcut parser'ları listele
        print("📋 Mevcut parser'lar:", ParserFactory.get_available_parsers())

        # Scrapy parser oluştur
        scrapy_parser = ParserFactory.get_parser('scrapy')
        print(f"✅ Scrapy parser oluşturuldu: {scrapy_parser.get_parser_name()}")

        # Convenience function test
        parser2 = create_parser('SCRAPY')  # Case insensitive
        print(f"✅ Convenience function çalışıyor: {parser2.get_parser_name()}")

        # Hatalı parser type test
        try:
            ParserFactory.get_parser('nonexistent')
        except ValueError as e:
            print(f"✅ Hata yakalama çalışıyor: {e}")

        print("🎉 Factory testi başarılı!")

    except Exception as e:
        print(f" Factory test hatası: {e}")


if __name__ == "__main__":
    test_factory()