# parsers/__init__.py
from .factory import ParserFactory, create_parser
from .base import ParserInterface

# Lazy loading - import etme, sadece factory üzerinden kullan

__all__ = [
    'ParserFactory',
    'create_parser',
    'ParserInterface'
]