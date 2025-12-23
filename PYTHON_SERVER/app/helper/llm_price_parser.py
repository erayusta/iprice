"""
🤖 LLM Price Parser
===================
LLM kullanarak fiyat formatlarını parse eder
"""

import requests
import json
import re
from typing import Optional

class LLMPriceParser:
    """LLM ile fiyat parsing"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3.2:3b"  # Küçük, hızlı model
    
    def parse_price_with_llm(self, price_text: str) -> Optional[float]:
        """
        LLM ile fiyat parse et
        
        Args:
            price_text: "61.750,00 TL", "39.999 TL", vb.
            
        Returns:
            Float değer veya None
        """
        try:
            # LLM prompt
            prompt = f"""
            Aşağıdaki Türkçe fiyat metnini sadece sayısal değere çevir.
            Binlik ayıracı nokta (.), ondalık ayıracı virgül (,) kullanılır.
            
            Örnekler:
            - "61.750,00 TL" → 61750.00
            - "39.999 TL" → 39999.00  
            - "1.250,50 TL" → 1250.50
            - "500 TL" → 500.00
            
            Fiyat: "{price_text}"
            
            Sadece sayısal değeri döndür (nokta ile):
            """
            
            # Ollama API çağrısı
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Düşük temperature (tutarlılık için)
                        "top_p": 0.9
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                llm_output = result.get('response', '').strip()
                
                # Sayısal değeri ayıkla
                price_match = re.search(r'(\d+\.?\d*)', llm_output)
                if price_match:
                    price_value = float(price_match.group(1))
                    print(f"🤖 LLM Price Parse: '{price_text}' → {price_value}")
                    return price_value
            
            print(f"⚠️ LLM parse başarısız: {price_text}")
            return None
            
        except Exception as e:
            print(f"❌ LLM parse hatası: {e}")
            return None
    
    def is_ollama_running(self) -> bool:
        """Ollama çalışıyor mu kontrol et"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

# Global instance
_llm_parser = None

def get_llm_price_parser() -> LLMPriceParser:
    """LLM parser instance'ını al"""
    global _llm_parser
    if _llm_parser is None:
        _llm_parser = LLMPriceParser()
    return _llm_parser

def parse_price_with_llm(price_text: str) -> Optional[float]:
    """LLM ile fiyat parse et (kolay kullanım)"""
    parser = get_llm_price_parser()
    return parser.parse_price_with_llm(price_text)
