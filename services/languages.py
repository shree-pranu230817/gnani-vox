"""
UZHAVAR AI – Kannada Voice Bridge
Language Configuration & Internationalization (10 Indian Languages)
"""

SUPPORTED_LANGUAGES = {
    'kn': {
        'code': 'kn',
        'name': 'Kannada',
        'native': 'ಕನ್ನಡ',
        'flag': '🌿',
        'bcp47': 'kn-IN',
        'prisma_code': 'kn-IN',
        'timbre_code': 'kn-IN',
        'prisma_supported': True,
        'timbre_supported': True,
        'default_voice': 'female'
    },
    'en': {
        'code': 'en',
        'name': 'English',
        'native': 'English',
        'flag': '🌐',
        'bcp47': 'en-IN',
        'prisma_code': 'en-IN',
        'timbre_code': 'en-IN',
        'prisma_supported': True,
        'timbre_supported': True,
        'default_voice': 'female'
    },
    'ta': {
        'code': 'ta',
        'name': 'Tamil',
        'native': 'தமிழ்',
        'flag': '🌾',
        'bcp47': 'ta-IN',
        'prisma_code': 'ta-IN',
        'timbre_code': 'ta-IN',
        'prisma_supported': True,
        'timbre_supported': True,
        'default_voice': 'female'
    },
    'te': {
        'code': 'te',
        'name': 'Telugu',
        'native': 'తెలుగు',
        'flag': '🌱',
        'bcp47': 'te-IN',
        'prisma_code': 'te-IN',
        'timbre_code': 'te-IN',
        'prisma_supported': True,
        'timbre_supported': True,
        'default_voice': 'female'
    },
    'hi': {
        'code': 'hi',
        'name': 'Hindi',
        'native': 'हिन्दी',
        'flag': '🇮🇳',
        'bcp47': 'hi-IN',
        'prisma_code': 'hi-IN',
        'timbre_code': 'hi-IN',
        'prisma_supported': True,
        'timbre_supported': True,
        'default_voice': 'female'
    },
    'ml': {
        'code': 'ml',
        'name': 'Malayalam',
        'native': 'മലയാളം',
        'flag': '🌴',
        'bcp47': 'ml-IN',
        'prisma_code': 'ml-IN',
        'timbre_code': 'ml-IN',
        'prisma_supported': True,
        'timbre_supported': True,
        'default_voice': 'female'
    },
    'bn': {
        'code': 'bn',
        'name': 'Bengali',
        'native': 'বাংলা',
        'flag': '🌾',
        'bcp47': 'bn-IN',
        'prisma_code': 'bn-IN',
        'timbre_code': 'bn-IN',
        'prisma_supported': True,
        'timbre_supported': True,
        'default_voice': 'female'
    },
    'mr': {
        'code': 'mr',
        'name': 'Marathi',
        'native': 'मराठी',
        'flag': '🌱',
        'bcp47': 'mr-IN',
        'prisma_code': 'mr-IN',
        'timbre_code': 'mr-IN',
        'prisma_supported': True,
        'timbre_supported': True,
        'default_voice': 'female'
    },
    'gu': {
        'code': 'gu',
        'name': 'Gujarati',
        'native': 'ગુજરાતી',
        'flag': '🌾',
        'bcp47': 'gu-IN',
        'prisma_code': 'gu-IN',
        'timbre_code': 'gu-IN',
        'prisma_supported': True,
        'timbre_supported': True,
        'default_voice': 'female'
    },
    'pa': {
        'code': 'pa',
        'name': 'Punjabi',
        'native': 'ਪੰਜਾਬੀ',
        'flag': '🌾',
        'bcp47': 'pa-IN',
        'prisma_code': 'pa-IN',
        'timbre_code': 'pa-IN',
        'prisma_supported': True,
        'timbre_supported': True,
        'default_voice': 'female'
    }
}

# Unicode Block Range Mapping for Fast Script-based Detection
SCRIPT_RANGES = {
    'kn': (0x0C80, 0x0CFF),  # Kannada
    'ta': (0x0B80, 0x0BFF),  # Tamil
    'te': (0x0C00, 0x0C7F),  # Telugu
    'hi': (0x0900, 0x097F),  # Devanagari (Hindi/Marathi)
    'ml': (0x0D00, 0x0D7F),  # Malayalam
    'bn': (0x0980, 0x09FF),  # Bengali
    'gu': (0x0A80, 0x0AFF),  # Gujarati
    'pa': (0x0A00, 0x0A7F),  # Gurmukhi (Punjabi)
}

def detect_language_from_text(text: str, fallback: str = 'kn') -> str:
    """Detect language code based on unicode character frequencies in text."""
    if not text:
        return fallback
    counts = {code: 0 for code in SCRIPT_RANGES}
    ascii_count = 0
    for char in text:
        cp = ord(char)
        if 0x0041 <= cp <= 0x007A:
            ascii_count += 1
            continue
        for code, (start, end) in SCRIPT_RANGES.items():
            if start <= cp <= end:
                counts[code] += 1
                break

    best_code, max_count = max(counts.items(), key=lambda item: item[1])
    if max_count > 0:
        return best_code
    if ascii_count > 0:
        return 'en'
    return fallback

def get_dialect_code(lang_code: str) -> str:
    """Return BCP-47 / Gnani dialect code (e.g. kn -> kn-IN)."""
    lang = (lang_code or 'kn').lower().strip()
    if lang in SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES[lang]['bcp47']
    if '-' in lang:
        return lang
    return 'kn-IN'

