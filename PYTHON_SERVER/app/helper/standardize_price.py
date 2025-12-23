def standardize_price(price):
    """
    Türkçe fiyat formatını standart hale getirir
    
    Örnekler:
    - "7,829.37 TL" → "7829.37"
    - "4,623.22 TL" → "4623.22" 
    - "39.999 TL" → "39999.00"
    - "1.250,50 TL" → "1250.50"
    """
    if price is None or price == '':
        return None

    try:
        price_str = str(price).strip()
        price_str = price_str.replace('\r', '').replace('\n', '').replace(' ', '')
        price_str = price_str.replace('TL', '').replace('₺', '').replace('TRY', '')

        # Türkçe format: binlik ayıracı nokta (.), decimal ayıracı virgül (,)
        # Örnek: 7.829,37 → 7829.37
        
        if ',' in price_str and '.' in price_str:
            # Format: 7.829,37 → 7829.37
            parts = price_str.split(',')
            if len(parts) == 2:
                integer_part = parts[0].replace('.', '')  # Noktaları kaldır (binlik ayıracı)
                decimal_part = parts[1]
                
                # Decimal part'ı 2 haneli yap
                if len(decimal_part) == 1:
                    decimal_part = decimal_part + '0'
                elif len(decimal_part) > 2:
                    decimal_part = decimal_part[:2]
                
                return f"{integer_part}.{decimal_part}"
        
        # Sadece nokta varsa (binlik ayıracı olabilir)
        elif '.' in price_str:
            parts = price_str.split('.')
            if len(parts) == 2:
                integer_part = parts[0]
                decimal_part = parts[1]
                
                # Eğer decimal part 3 karakter ise, binlik ayıracı olabilir
                if len(decimal_part) == 3:
                    # 7.829 → 7829.00 (binlik ayıracı)
                    return f"{integer_part}{decimal_part}.00"
                elif len(decimal_part) == 2:
                    # 7.82 → 7.82 (decimal)
                    return f"{integer_part}.{decimal_part}"
                elif len(decimal_part) == 1:
                    # 7.8 → 7.80
                    return f"{integer_part}.{decimal_part}0"
        
        # Sadece virgül varsa
        elif ',' in price_str:
            # Virgülü noktaya çevir
            return price_str.replace(',', '.')
        
        # Hiçbir ayıracı yoksa, integer olarak kabul et
        return f"{price_str}.00"

    except Exception as e:
        print(f"❌ Price parsing hatası: {price} → {e}")
        return None