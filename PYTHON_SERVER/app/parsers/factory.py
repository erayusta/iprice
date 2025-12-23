# parsers/factory.py
from typing import Dict, Any
from .base import ParserInterface


class ParserFactory:
    # Mevcut parser'ları kaydet (lazy loading için sadece string tutalım)
    _parsers = {
        'scrapy': 'scrapy_parser.ScrapyParser',
        'selenium': 'selenium_parser.SeleniumParser',
        'playwright': 'playwright_parser.PlaywrightParser',
    }
    
    # Cache için
    _parser_instances = {}

    @classmethod
    def get_parser(cls, parser_type: str) -> ParserInterface:
        """
        Parser type'ına göre parser instance döndür (lazy loading)

        Args:
            parser_type: 'scrapy', 'selenium', 'playwright'

        Returns:
            ParserInterface: Parser instance

        Raises:
            ValueError: Bilinmeyen parser type
        """
        parser_type_lower = parser_type.lower()
        
        if parser_type_lower not in cls._parsers:
            available_parsers = list(cls._parsers.keys())
            raise ValueError(
                f"Bilinmeyen parser type: '{parser_type}'. "
                f"Mevcut parser'lar: {available_parsers}"
            )
        
        # Lazy import - sadece kullanıldığında import et
        if parser_type_lower not in cls._parser_instances:
            module_class = cls._parsers[parser_type_lower]
            module_name, class_name = module_class.rsplit('.', 1)
            
            # Import et
            import importlib
            module = importlib.import_module(f'.{module_name}', package='app.parsers')
            parser_class = getattr(module, class_name)
            
            cls._parser_instances[parser_type_lower] = parser_class
        
        # Instance döndür
        return cls._parser_instances[parser_type_lower]()

    @classmethod
    def get_available_parsers(cls) -> list:
        """Mevcut parser type'larını döndür"""
        return list(cls._parsers.keys())

    @classmethod
    def is_parser_available(cls, parser_type: str) -> bool:
        """Parser type mevcut mu kontrol et"""
        return parser_type.lower() in cls._parsers

    @classmethod
    def register_parser(cls, parser_type: str, parser_class):
        """Yeni parser type kaydet (gelecekte kullanım için)"""
        if not issubclass(parser_class, ParserInterface):
            raise ValueError("Parser class ParserInterface'i implement etmeli")

        cls._parsers[parser_type.lower()] = parser_class
        print(f"✅ Parser kaydedildi: {parser_type}")


# Convenience function
def create_parser(parser_type: str) -> ParserInterface:
    """Hızlı parser oluşturma fonksiyonu"""
    return ParserFactory.get_parser(parser_type)