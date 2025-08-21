def get_currency_symbol(currency_code: str) -> str:
    """Maps a currency code to its symbol, defaulting to the code itself."""
    symbols = {
        'USD': '$', 'EUR': '€', 'JPY': '¥', 'GBP': '£',
        'AUD': 'A$', 'CAD': 'C$', 'CHF': 'Fr', 'CNY': '¥',
        'HKD': 'HK$', 'NZD': 'NZ$', 'SEK': 'kr', 'KRW': '₩',
        'SGD': 'S$', 'NOK': 'kr', 'MXN': '$', 'INR': '₹',
        'RUB': '₽', 'BRL': 'R$', 'TRY': '₺', 'ZAR': 'R'
    }
    return symbols.get(currency_code, f'{currency_code} ')
