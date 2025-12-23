#!/usr/bin/env python3
"""
Price Parser Test Script
========================
Yeni standardize_price fonksiyonunu test eder
"""

import sys
sys.path.append('/Users/serkanodaci/Projects/iPriceNew/price_analysis_service')

from app.helper.standardize_price import standardize_price

def test_price_parsing():
    """Test cases for price parsing"""
    
    test_cases = [
        # (input, expected_output, description)
        ("7,829.37 TL", "7829.37", "DepoBT format"),
        ("4,623.22 TL", "4623.22", "City Bilişim format"),
        ("7,829.37", "7829.37", "DepoBT without TL"),
        ("4,623.22", "4623.22", "City Bilişim without TL"),
        ("39.999 TL", "39999.00", "Binlik ayıracı format"),
        ("1.250,50 TL", "1250.50", "Karma format"),
        ("500 TL", "500.00", "Basit format"),
        ("1.000.000 TL", "1000000.00", "Çoklu binlik ayıracı"),
        ("99,99 TL", "99.99", "Virgül decimal"),
        ("1500", "1500.00", "Sadece sayı"),
    ]
    
    print("🧪 Price Parser Test Sonuçları:")
    print("=" * 50)
    
    all_passed = True
    
    for input_price, expected, description in test_cases:
        result = standardize_price(input_price)
        status = "✅" if result == expected else "❌"
        
        print(f"{status} {description}")
        print(f"   Input:    '{input_price}'")
        print(f"   Expected: '{expected}'")
        print(f"   Result:   '{result}'")
        
        if result != expected:
            all_passed = False
            print(f"   ❌ HATA!")
        
        print()
    
    print("=" * 50)
    if all_passed:
        print("🎉 TÜM TESTLER BAŞARILI!")
    else:
        print("❌ BAZI TESTLER BAŞARISIZ!")
    
    return all_passed

if __name__ == "__main__":
    test_price_parsing()
