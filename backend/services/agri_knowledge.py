"""
UZHAVAR AI - Scientific Agricultural Knowledge & Advisory Engine
Built on validated recommendations from ICAR institutes, State Agricultural Universities
(TNAU, UASB, PJTSAU, PAU, IARI), Krishi Vigyan Kendras (KVKs), and Ministry of Agriculture.
"""

from typing import Dict, Any, Optional

class AgriculturalKnowledgeEngine:
    """
    Knowledge and advisory synthesizer for 14 agricultural categories
    supporting 10 Indian regional languages + English.
    """

    SOURCES_ATTRIBUTION = "ICAR & State Agricultural Universities (TNAU / UASB / PJTSAU / PAU / KVK Guidelines)"

    # Native-script crop display names keyed by internal English crop name → lang code
    CROP_DISPLAY_NAMES: Dict[str, Dict[str, str]] = {
        'Paddy':     {'kn': 'ಭತ್ತ',       'ta': 'நெல்',        'te': 'వరి',      'hi': 'धान',    'en': 'Paddy'},
        'Ragi':      {'kn': 'ರಾಗಿ',       'ta': 'கேழ்வரகு',   'te': 'రాగి',     'hi': 'रागी',   'en': 'Ragi'},
        'Cotton':    {'kn': 'ಹತ್ತಿ',      'ta': 'பருத்தி',    'te': 'పత్తి',    'hi': 'कपास',   'en': 'Cotton'},
        'Wheat':     {'kn': 'ಗೋಧಿ',       'ta': 'கோதுமை',     'te': 'గోధుమ',    'hi': 'गेहूं',  'en': 'Wheat'},
        'Tomato':    {'kn': 'ಟೊಮ್ಯಾಟೊ',   'ta': 'தக்காளி',    'te': 'టమాట',     'hi': 'टमाटर',  'en': 'Tomato'},
        'Sugarcane': {'kn': 'ಕಬ್ಬು',      'ta': 'கரும்பு',    'te': 'చెరకు',    'hi': 'गन्ना',  'en': 'Sugarcane'},
        'Maize':     {'kn': 'ಮೆಕ್ಕೆಜೋಳ',  'ta': 'மக்காச்சோளம்', 'te': 'మొక్కజొన్న', 'hi': 'मक्का', 'en': 'Maize'},
        'Turmeric':  {'kn': 'ಅರಿಶಿನ',     'ta': 'மஞ்சள்',     'te': 'పసుపు',    'hi': 'हल्दी',  'en': 'Turmeric'},
        'Banana':    {'kn': 'ಬಾಳೆ',       'ta': 'வாழை',       'te': 'అరటి',     'hi': 'केला',   'en': 'Banana'},
        'Groundnut': {'kn': 'ಕಡಲೆಕಾಯಿ',  'ta': 'வேர்க்கடலை', 'te': 'వేరుశెనగ',  'hi': 'मूंगफली', 'en': 'Groundnut'},
        'Chilli':    {'kn': 'ಮೆಣಸಿನಕಾಯಿ', 'ta': 'மிளகாய்',    'te': 'మిర్చి',   'hi': 'मिर्च',  'en': 'Chilli'},
    }

    @classmethod
    def get_crop_display(cls, crop: Optional[str], lang: str) -> str:
        """Return native-script crop name for the given language code."""
        if not crop:
            return 'ಬೆಳೆ' if lang == 'kn' else ('பயிர்' if lang == 'ta' else 'crops')
        lang_key = lang[:2] if lang else 'en'
        names = cls.CROP_DISPLAY_NAMES.get(crop, {})
        return names.get(lang_key, names.get('en', crop))

    @classmethod
    def generate_advisory(
        cls,
        category: str,
        prompt: str,
        lang: str = 'en',
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes structured agronomic advice combining:
          1. Classified intent category
          2. Multi-turn conversation context (crop, variety, growth stage, location)
          3. Sourced scientific recommendations (ICAR/KVK)
          4. Structured farmer-friendly markdown format

        Priority: prompt-extracted crop ALWAYS overrides session context crop
        to avoid session bleeding when user explicitly asks about a different crop.
        """
        # Prompt-extracted crop takes priority over session context crop
        prompt_crop = cls._extract_crop_mention(prompt)
        context_crop = (context.get('crop') if context else None)
        crop = prompt_crop or context_crop

        variety = (context.get('variety') if context else None)
        stage = (context.get('growth_stage') if context else None)
        problem = (context.get('problem') if context else None)
        location = (context.get('location') if context else None)

        handler_map = {
            'crop_cultivation': cls._handle_crop_cultivation,
            'fertilizer_soil': cls._handle_fertilizer_soil,
            'crop_diseases': cls._handle_crop_diseases,
            'pest_management': cls._handle_pest_management,
            'irrigation_water': cls._handle_irrigation_water,
            'seeds_treatment': cls._handle_seeds_treatment,
            'sowing_harvesting': cls._handle_sowing_harvesting,
            'weather_climate': cls._handle_weather_climate,
            'govt_schemes': cls._handle_govt_schemes,
            'organic_farming': cls._handle_organic_farming,
            'equipment_technology': cls._handle_equipment_technology,
            'yield_profit': cls._handle_yield_profit,
            'general_agriculture': cls._handle_general_agriculture
        }

        handler = handler_map.get(category, cls._handle_general_agriculture)
        advisory_data = handler(crop, variety, stage, problem, location, prompt, lang)

        return {
            'success': True,
            'answer': advisory_data['answer'],
            'category': category,
            'crop': crop,
            'variety': variety,
            'source': cls.SOURCES_ATTRIBUTION,
            'clarification_prompt': advisory_data.get('clarification')
        }

    @classmethod
    def _extract_crop_mention(cls, text: str) -> Optional[str]:
        lower = text.lower()
        crops = {
            'paddy': 'Paddy', 'rice': 'Paddy', 'dhan': 'Paddy', 'ಭತ್ತ': 'Paddy', 'நெல்': 'Paddy', 'వరి': 'Paddy',
            'ragi': 'Ragi', 'ರಾಗಿ': 'Ragi', 'கேழ்வரகு': 'Ragi', 'finger millet': 'Ragi',
            'cotton': 'Cotton', 'ಹತ್ತಿ': 'Cotton', 'பருத்தி': 'Cotton', 'कपास': 'Cotton', 'పత్తి': 'Cotton',
            'tomato': 'Tomato', 'ಟೊಮ್ಯಾಟೊ': 'Tomato', 'தக்காளி': 'Tomato', 'टमाटर': 'Tomato',
            'sugarcane': 'Sugarcane', 'ಕಬ್ಬು': 'Sugarcane', 'கரும்பு': 'Sugarcane', 'गन्ना': 'Sugarcane',
            'wheat': 'Wheat', 'ಗೋಧಿ': 'Wheat', 'கோதுமை': 'Wheat', 'गेहूं': 'Wheat',
            'maize': 'Maize', 'ಮೆಕ್ಕೆಜೋಳ': 'Maize', 'மக்காச்சೋளம்': 'Maize', 'मक्का': 'Maize',
            'turmeric': 'Turmeric', 'ಅರಿಶಿನ': 'Turmeric', 'மஞ்சள்': 'Turmeric', 'हल्दी': 'Turmeric',
            'banana': 'Banana', 'ಬಾಳೆ': 'Banana', 'வாழை': 'Banana', 'केला': 'Banana',
            'groundnut': 'Groundnut', 'ಕಡಲೆಕಾಯಿ': 'Groundnut', 'வேர்க்கடலை': 'Groundnut',
            'chilli': 'Chilli', 'ಮೆಣಸಿನಕಾಯಿ': 'Chilli', 'மிளகாய்': 'Chilli'
        }
        for k, v in crops.items():
            if k in lower:
                return v
        return None

    # =========================================================================
    # 1. CROP CULTIVATION & SELECTION
    # =========================================================================
    @classmethod
    def _handle_crop_cultivation(cls, crop, variety, stage, problem, location, prompt, lang):
        crop_name = cls.get_crop_display(crop, lang)
        var_text = f" (Variety: {variety})" if variety else ""

        if crop == 'Ragi' and lang == 'kn':
            answer = (
                "🌾 **ರಾಗಿ ಬೆಳೆಯುವ ಸಮಗ್ರ ಕೃಷಿ ಪದ್ಧತಿ (ICAR / UAS ಬೆಂಗಳೂರು & ಧಾರವಾಡ ಶಿಫಾರಸು):**\n\n"
                "1. **ಹವಾಮಾನ ಮತ್ತು ಮಣ್ಣು (Climate & Soil):**\n"
                "   • ರಾಗಿ ಖಾರೀಫ್ ಮತ್ತು ರಬಿ ಎರಡೂ ಹಂಗಾಮುಗಳಲ್ಲಿ ಬೆಳೆಯಬಹುದು.\n"
                "   • ಕೆಂಪು ಮರಳು ಮಿಶ್ರಿತ ಮಣ್ಣು ಮತ್ತು ನೀರು ನಿಲ್ಲದ ಕಪ್ಪು ಮಣ್ಣಿನಲ್ಲಿ ಚೆನ್ನಾಗಿ ಬೆಳೆಯುತ್ತದೆ.\n"
                "   • ಮಣ್ಣಿನ pH 5.5 - 7.5; ಮಳೆಪ್ರಮಾಣ 500 - 900 ಮಿ.ಮೀ ಸಾಕಾಗುತ್ತದೆ.\n\n"
                "2. **ಶಿಫಾರಸು ತಳಿಗಳು (Recommended Varieties):**\n"
                "   • **ಖಾರೀಫ್:** GPU-28, ML-365, KMR-301 (ಬ್ಲಾಸ್ಟ್ ನಿರೋಧಕ), Indaf-8\n"
                "   • **ರಬಿ:** MR-1, MR-6, GPU-67\n"
                "   • ಕರ್ನಾಟಕದ ಒಣ ಭೂಮಿಗೆ: GPU-28 ಮತ್ತು KMR-301 ಅತ್ಯಂತ ಸೂಕ್ತ.\n\n"
                "3. **ಬೀಜದ ಪ್ರಮಾಣ ಮತ್ತು ಬಿತ್ತನೆ ವಿಧಾನ (Seed Rate & Sowing):**\n"
                "   • ನೇರ ಬಿತ್ತನೆ: ಎಕರೆಗೆ 4-5 ಕೆಜಿ ಬೀಜ. ಬೀಜ ತೆಳ್ಳಗೆ ಬಿತ್ತಿ ಮೇಲೆ ಮಣ್ಣು ಮುಚ್ಚಿ.\n"
                "   • ನಾಟಿ ಪದ್ಧತಿ: 20-25 ದಿನಗಳ ಸಸಿಗಳನ್ನು 22.5×10 ಸೆಂ.ಮೀ ಅಂತರದಲ್ಲಿ ನಾಟಿ ಮಾಡಿ (2-3 ಕೆಜಿ ಬೀಜ/ಎಕರೆ).\n"
                "   • ಬೀಜೋಪಚಾರ: ಪ್ರತಿ ಕೆಜಿ ಬೀಜಕ್ಕೆ 4 ಗ್ರಾಂ ಟ್ರೈಕೋಡರ್ಮಾ ವಿರಿಡೆ ಅಥವಾ 2 ಗ್ರಾಂ ಕಾರ್ಬೆಂಡಾಜಿಮ್ ಬಳಸಿ.\n\n"
                "4. **ಭೂಮಿ ಸಿದ್ಧತೆ (Land Preparation):**\n"
                "   • 2-3 ಬಾರಿ ಆಳವಾಗಿ ಉಳುಮೆ ಮಾಡಿ, ಹೆಂಟೆಗಳನ್ನು ಪುಡಿಮಾಡಿ ಸಮಮಟ್ಟ ಮಾಡಿ.\n"
                "   • ಕೊನೆಯ ಉಳುಮೆಯಲ್ಲಿ ಎಕರೆಗೆ 4-5 ಟನ್ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಬೆರೆಸಿ.\n\n"
                "5. **ರಸಗೊಬ್ಬರ ನಿರ್ವಹಣೆ (Fertilizer – NPK):**\n"
                "   • ಮಳೆ ಆಧಾರಿತ (Rainfed): N:P:K = 20:16:10 ಕೆಜಿ/ಎಕರೆ\n"
                "   • ನೀರಾವರಿ (Irrigated): N:P:K = 40:20:20 ಕೆಜಿ/ಎಕರೆ\n"
                "   • ರಂಜಕ ಮತ್ತು ಪೊಟ್ಯಾಶ್ ಸಂಪೂರ್ಣ ಅಡಿಯುರ; ಸಾರಜನಕ 2 ಕಂತಿನಲ್ಲಿ (ಬಿತ್ತನೆ ಮತ್ತು 25-30 DAT).\n"
                "   • ಸತು ಕೊರತೆಗೆ 10 ಕೆಜಿ ಜಿಂಕ್ ಸಲ್ಫೇಟ್/ಎಕರೆ ಅಡಿಯುರ ಹಾಕಿ.\n\n"
                "6. **ನೀರಾವರಿ (Irrigation):**\n"
                "   • ನಿರ್ಣಾಯಕ ಹಂತಗಳು: ಮೊಳಕೆ ಒಡೆಯುವ ಸಮಯ, ತೆನೆ ಒಡೆಯುವ ಸಮಯ ಮತ್ತು ಕಾಳು ತುಂಬುವ ಸಮಯ.\n"
                "   • ಮಳೆ ಆಧಾರಿತ ಬೇಸಾಯದಲ್ಲಿ ಮಳೆ ಸಾಲದಿದ್ದಾಗ ಮಾತ್ರ ಹನಿ ನೀರಾವರಿ ನೀಡಿ.\n\n"
                "7. **ಕಳೆ ನಿರ್ವಹಣೆ (Weed Management):**\n"
                "   • ಬಿತ್ತಿದ 20 ಮತ್ತು 40 ದಿನಗಳಲ್ಲಿ ಕಳೆ ತೆಗೆಯಿರಿ.\n"
                "   • ಪ್ರಿ-ಎಮರ್ಜೆಂಟ್ ಕಳೆನಾಶಕ: ಪೆಂಡಿಮೆಥಲಿನ್ 30% EC (1 ಕೆಜಿ AI/ಎಕರೆ) ಬಿತ್ತಿದ 2 ದಿನದಲ್ಲಿ ಸಿಂಪಡಿಸಿ.\n\n"
                "8. **ಕೀಟ ಮತ್ತು ರೋಗ ನಿರ್ವಹಣೆ (Pest & Disease):**\n"
                "   • ಬ್ಲಾಸ್ಟ್ ರೋಗ: ಟ್ರೈಸೈಕ್ಲೋಜೋಲ್ 75% WP (0.6 ಗ್ರಾಂ/ಲೀ) ಅಥವಾ ಕಾರ್ಬೆಂಡಾಜಿಮ್ (1 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ.\n"
                "   • ಮಿಡ್ತೆ / ಹಿಟ್ಟು ತಿಗಣೆ: ಡಿಮೆಥೋಯೇಟ್ 30% EC (2 ಮಿ.ಲೀ/ಲೀ) ಸಿಂಪಡಿಸಿ.\n\n"
                "9. **ಕಟಾವು ಮತ್ತು ಬೆಳೆಯ ಅವಧಿ (Harvesting & Duration):**\n"
                "   • ಬೆಳೆ ಅವಧಿ: 100 ರಿಂದ 120 ದಿನಗಳು.\n"
                "   • ತೆನೆಗಳ ಕಾಳು ಗಟ್ಟಿಯಾಗಿ ಕಂದು ಬಣ್ಣ ತಿರುಗಿದಾಗ ಕಟಾವು ಮಾಡಿ. 2-3 ದಿನ ಒಣಗಿಸಿ ಕಣದಲ್ಲಿ ಮಾಡಿ.\n"
                "   • ಇಳುವರಿ: ಮಳೆ ಆಧಾರಿತ 10-14 ಕ್ವಿಂಟಾಲ್/ಎಕರೆ; ನೀರಾವರಿ 16-20 ಕ್ವಿಂಟಾಲ್/ಎಕರೆ.\n\n"
                "❓ *ಸಲಹೆ:* ನೀವು ಯಾವ ಜಿಲ್ಲೆಯಲ್ಲಿ ರಾಗಿ ಬೆಳೆಯುತ್ತಿದ್ದೀರಿ ಮತ್ತು ಮಳೆ ಆಧಾರಿತವೇ ಅಥವಾ ನೀರಾವರಿಯೇ? "
                "ತಿಳಿಸಿದರೆ ನಿಮ್ಮ ಹಂಗಾಮಿಗೆ ಸೂಕ್ತ ತಳಿ ಮತ್ತು ನಿಖರ ದಿನಾಂಕ ನೀಡಬಹುದು."
            )
        elif crop == 'Paddy' and lang == 'kn':
            answer = (
                f"🌾 **ಭತ್ತ ಬೆಳೆಯುವ ಸಮಗ್ರ ಕೃಷಿ ಪದ್ಧತಿ ಮತ್ತು ಮಾರ್ಗದರ್ಶಿ (ICAR / UAS ಬೆಂಗಳೂರು & ಧಾರವಾಡ ಶಿಫಾರಸು):**\n\n"
                f"1. **ಭೂಮಿ ಸಿದ್ಧತೆ (Land Preparation):**\n"
                f"   • ಜಮೀನನ್ನು 2-3 ಬಾರಿ ಆಳವಾಗಿ ಉಳುಮೆ ಮಾಡಿ ಹೆಂಟೆಗಳನ್ನು ಪುಡಿಮಾಡಿ.\n"
                f"   • ನೀರು ಕಟ್ಟಿ ಗದ್ದೆಯನ್ನು 2 ಬಾರಿ ಚೆನ್ನಾಗಿ ಕೆಸರು ಮಾಡಿ (Puddling) ಮರಮುಟ್ಟು ಅಥವಾ ಲೆವೆಲರ್‌ನಿಂದ ಸಮತಟ್ಟಾಗಿಸಿ.\n"
                f"   • ಕೊನೆಯ ಕೆಸರು ಮಾಡುವಾಗ ಎಕರೆಗೆ 4-5 ಟನ್ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರವನ್ನು ಮಣ್ಣಿಗೆ ಬೆರೆಸಿ.\n\n"
                f"2. **ಬೀಜದ ಆಯ್ಕೆ ಮತ್ತು ಬೀಜೋಪಚಾರ (Seed Selection & Treatment):**\n"
                f"   • ಶಿಫಾರಸು ತಳಿಗಳು: ಬಿಪಿಟಿ 5204 (ಸೋನಾ ಮಸೂರಿ), ಜಯ, ಐಆರ್ 64, ತನು, ಗಂಗಾವತಿ ಸೋನಾ, ಎಂ.ಟಿ.ಯು 1010.\n"
                f"   • ಬೀಜೋಪಚಾರ: ಪ್ರತಿ ಕೆಜಿ ಬೀಜಕ್ಕೆ 2 ಗ್ರಾಂ ಕಾರ್ಬೆಂಡಾಜಿಮ್ ಅಥವಾ 4 ಗ್ರಾಂ ಟ್ರೈಕೋಡರ್ಮಾ ವಿರಿಡೆ ಬೆರೆಸಿ 24 ಗಂಟೆ ನೀರಿನಲ್ಲಿ ನೆನೆಸಿ, ನಂತರ ನೆರಳಿನಲ್ಲಿ ಮೊಳಕೆ ಬರಿಸಿರಿ.\n\n"
                f"3. **ಸಸಿಮಡಿ ನಿರ್ವಹಣೆ (Nursery):**\n"
                f"   • 1 ಎಕರೆ ನಾಟಿಗೆ 5-6 ಗುಂಟೆ (250 ಚ.ಮೀ) ಸಸಿಮಡಿ ಬೇಕು.\n"
                f"   • 20-25 ದಿನಗಳ ಉತ್ತಮ ಆರೋಗ್ಯವಂತ ಸಸಿಗಳನ್ನು ನಾಟಿಗೆ ಬಳಸಿ.\n\n"
                f"4. **ನಾಟಿ ಅಥವಾ ನೇರ ಬಿತ್ತನೆ (Transplanting / DSR):**\n"
                f"   • ಸಾಲಿನಿಂದ ಸಾಲಿಗೆ 20 ಸೆಂ.ಮೀ ಮತ್ತು ಗಿಡದಿಂದ ಗಿಡಕ್ಕೆ 10-15 ಸೆಂ.ಮೀ ಅಂತರದಲ್ಲಿ ಪ್ರತಿ ಬುಡಕ್ಕೆ 2-3 ಸಸಿಗಳನ್ನು 2-3 ಸೆಂ.ಮೀ ಆಳಕ್ಕೆ ನಾಟಿ ಮಾಡಿ.\n"
                f"   • ಶ್ರೀ (SRI) ಪದ್ಧತಿಯಲ್ಲಿ 25x25 ಸೆಂ.ಮೀ ಅಂತರದಲ್ಲಿ ಒಂದೊಂದೇ ಸಸಿ ನಾಟಿ ಮಾಡಿ.\n\n"
                f"5. **ನೀರು ನಿರ್ವಹಣೆ (Irrigation / AWD):**\n"
                f"   • ನಾಟಿ ವೇಳೆ 2 ಸೆಂ.ಮೀ ನೀರು ನಿಲ್ಲಿಸಿ. ತೆನೆ ಬರುವವರೆಗೆ 5 ಸೆಂ.ಮೀ ನೀರು ಸಾಕು.\n"
                f"   • ಸತತ ನೀರು ನಿಲ್ಲಿಸದೆ ಪರ್ಯಾಯ ತೇವ ಮತ್ತು ಒಣಗಿಸುವ (AWD) ಪದ್ಧತಿ ಅಳವಡಿಸಿ.\n"
                f"   • ಕಟಾವಿಗೆ 10-15 ದಿನ ಮುಂಚಿತವಾಗಿ ಸಂಪೂರ್ಣ ನೀರು ಬಸಿದು ತೆಗೆಯಿರಿ.\n\n"
                f"6. **ರಸಗೊಬ್ಬರ ನಿರ್ವಹಣೆ (Fertilizer Dosage & NPK):**\n"
                f"   • ಎಕರೆಗೆ ಶಿಫಾರಸು N:P:K = 40:20:20 ಕೆಜಿ.\n"
                f"   • ಸಂಪೂರ್ಣ ರಂಜಕ (DAP/SSP) ಮತ್ತು ಶೇ. 50% ಪೊಟ್ಯಾಶ್ ನಾಟಿ ವೇಳೆ ಅಡಿಯುರವಾಗಿ ಕೊಡಿ.\n"
                f"   • ಸಾರಜನಕವನ್ನು (ಯೂರಿಯಾ) ಮೂರು ಕಂತುಗಳಲ್ಲಿ (ನಾಟಿ ವೇಳೆ 50%, ತೆನೆ ಹೊಡೆಯುವಾಗ 25%, ಹೂವಾಡುವ ಮುನ್ನ 25%) ನೀಡಿ.\n"
                f"   • ಜೊತೆಗೆ ಎಕರೆಗೆ 10 ಕೆಜಿ ಜಿಂಕ್ ಸಲ್ಫೇಟ್ ಹಾಕಿ.\n\n"
                f"7. **ಕೀಟ ಮತ್ತು ರೋಗ ನಿರ್ವಹಣೆ (Pest & Disease):**\n"
                f"   • ಕಾಂಡ ಕೊರೆಯುವ ಹುಳು: ಕ್ಲೋರಾಂಟ್ರಾನಿಲಿಪ್ರೋಲ್ 18.5% SC (0.3 ಮಿ.ಲೀ/ಲೀ) ಸಿಂಪಡಿಸಿ.\n"
                f"   • ಬೆಂಕಿ ರೋಗ (Blast): ಟ್ರೈಸೈಕ್ಲೋಜೋಲ್ 75% WP (0.6 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ.\n\n"
                f"8. **ಕಟಾವು ಮತ್ತು ಬೆಳೆಯ ಅವಧಿ (Harvesting & Duration):**\n"
                f"   • ಬೆಳೆಯ ಅವಧಿ 120 ರಿಂದ 145 ದಿನಗಳು (ತಳಿ ಆಧಾರಿತ).\n"
                f"   • ತೆನೆಯ ಶೇ. 85 ರಷ್ಟು ಕಾಳುಗಳು ಚಿನ್ನದ ಬಣ್ಣಕ್ಕೆ ತಿರುಗಿದಾಗ ಕಟಾವು ಮಾಡಿ 2-3 ದಿನ ಒಣಗಿಸಿ.\n\n"
                f"❓ *ಸಲಹೆ:* ನೀವು ಯಾವ ಜಿಲ್ಲೆಯಲ್ಲಿ ಕೃಷಿ ಮಾಡುತ್ತಿದ್ದೀರಿ, ನಿಮ್ಮ ಮಣ್ಣಿನ ಪ್ರಕಾರ (ಕೆಂಪು/ಕಪ್ಪು/ಗೋಡು) ಮತ್ತು ಯಾವ ತಳಿ ಬೆಳೆಯಲು ಇಚ್ಚಿಸುತ್ತೀರಿ? ತಿಳಿಸಿದರೆ ನಿಮ್ಮ ಜಿಲ್ಲೆಗೆ ಸೂಕ್ತವಾದ ನಿಖರ ಮಾಹಿತಿ ನೀಡಬಹುದು."
            )
        elif lang == 'kn':
            answer = (
                f"🌾 **{crop_name}{var_text} ಬೇಸಾಯ ಮತ್ತು ಬೆಳೆ ಆಯ್ಕೆ ಮಾರ್ಗಸೂಚಿ (ICAR / KVK ಶಿಫಾರಸು):**\n\n"
                f"1. **ಸೂಕ್ತ ಹವಾಗುಣ ಮತ್ತು ಮಣ್ಣು:** ಉತ್ತಮ ಬಸಿದು ಹೋಗುವ ಕೆಂಪು ಗೋಡು ಅಥವಾ ಕಪ್ಪು ಮಣ್ಣು ಸೂಕ್ತ. ಮಣ್ಣಿನ ರಸಸಾರ (pH) 6.0 ರಿಂದ 7.5 ಇರಬೇಕು.\n"
                f"2. **ಉತ್ತಮ ತಳಿಗಳ ಆಯ್ಕೆ:** ಅಧಿಕ ಇಳುವರಿ ಮತ್ತು ರೋಗ ನಿರೋಧಕ ಪ್ರಮಾಣೀಕೃತ ಬೀಜಗಳನ್ನು ಮಾತ್ರ ಬಳಸಿ (ಸ್ಥಳೀಯ KVK ಕಚೇರಿಯಿಂದ ಪಡೆಯಿರಿ).\n"
                f"3. **ಮುಖ್ಯ ಕೃಷಿ ಕ್ರಮಗಳು:** ಜಮೀನನ್ನು 2-3 ಬಾರಿ ಆಳವಾಗಿ ಉಳುಮೆ ಮಾಡಿ, ಕಳೆ ಮುಕ್ತಗೊಳಿಸಿ ಹೆಂಟೆಗಳನ್ನು ಪುಡಿಮಾಡಿ ಬಸಿಗಾಲುವೆಗಳನ್ನು ನಿರ್ಮಿಸಿ.\n"
                f"4. **ಸಾವಯವ ತಳಹದಿ:** ಕೊನೆಯ ಉಳುಮೆಯ ಸಮಯದಲ್ಲಿ ಎಕರೆಗೆ 4-5 ಟನ್ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರವನ್ನು ಮಣ್ಣಿಗೆ ಬೆರೆಸಿ.\n\n"
                f"❓ *ಸಲಹೆ:* ನೀವು ಯಾವ ಜಿಲ್ಲೆಯಲ್ಲಿ ಅಥವಾ ಯಾವ ಹಂಗಾಮಿನಲ್ಲಿ (ಖಾರೀಫ್ / ರಬಿ) ಈ ಬೆಳೆ ಬೆಳೆಯಲು ಯೋಜಿಸುತ್ತಿದ್ದೀರಿ? ತಿಳಿಸಿದರೆ ನಿಖರವಾದ ದಿನಾಂಕಗಳನ್ನು ನೀಡಬಹುದು."
            )
        elif lang == 'ta':
            answer = (
                f"🌾 **{crop_name}{var_text} சாகுபடி மற்றும் பயிர் தேர்வு வழிகாட்டுதல் (ICAR / TNAU):**\n\n"
                f"1. **மண் மற்றும் பருவம்:** நல்ல வடிகால் வசதியுள்ள செம்மண் அல்லது வண்டல் மண் சிறந்தது. உகந்த கார-அமிலத்தன்மை pH 6.0 - 7.5.\n"
                f"2. **ரகத் தேர்வு:** உங்கள் பகுதிக்கு ஏற்ற பூச்சி-நோய் எதிர்ப்பு திறன் கொண்ட சான்று பெற்ற விதைகளைத் தேர்ந்தெடுக்கவும்.\n"
                f"3. **நில தயாரிப்பு:** நிலத்தை 2-3 முறை நன்கு உழுது, கட்டிகளை உடைத்து சமன் செய்து வடிகால் வாய்க்கால்களை அமைக்கவும்.\n"
                f"4. **அடியுரம்:** கடைசி உழவின் போது ஏக்கருக்கு 4-5 டன் மக்கிய தொழுஉரத்தை சீராக பரப்பி இடவும்.\n\n"
                f"❓ *கேள்வி:* நீங்கள் எந்த மாவட்டத்தில் பயிரிட திட்டமிட்டுள்ளீர்கள்? மண்ணின் வகை என்ன?"
            )
        elif lang == 'hi':
            answer = (
                f"🌾 **{crop_name}{var_text} की उन्नत खेती एवं फसल चयन (ICAR / KVK संस्तुति):**\n\n"
                f"1. **उपयुक्त मिट्टी व जलवायु:** उचित जल निकास वाली दोमट अथवा बलुई दोमट मिट्टी सर्वोत्तम है। मिट्टी का pH मान 6.5 से 7.5 होना चाहिए।\n"
                f"2. **उन्नत किस्में:** प्रमाणित एवं रोगरोधी किस्मों का ही चयन करें।\n"
                f"3. **खेत की तैयारी:** 2-3 बार गहरी जुताई करके पाटा लगाएं और जल निकासी हेतु नालियां बनाएं।\n"
                f"4. **जैविक खाद:** अंतिम जुताई के समय 4-5 टन सड़ी गोबर की खाद प्रति एकड़ अवश्य मिलाएं।\n\n"
                f"❓ *सलाह:* आप किस जिले में खेती कर रहे हैं और सिंचाई का क्या साधन है?"
            )
        else:
            answer = (
                f"🌾 **{crop_name}{var_text} Cultivation & Agronomic Practices (ICAR / Agricultural Univ):**\n\n"
                f"1. **Soil & Climate Requirements:** Well-drained loamy or clay loam soil with pH 6.0 to 7.5 is ideal. Avoid waterlogged fields.\n"
                f"2. **Certified Seed Selection:** Procure high-yielding, pest-resistant certified seed varieties from accredited KVKs or university seed banks.\n"
                f"3. **Field Preparation:** Plough 2-3 times to a fine tilth, level the field, and form drainage channels to avoid root rot.\n"
                f"4. **Basal Organic Manuring:** Incorporate 4-5 tonnes/acre of well-decomposed FYM or compost during final land preparation.\n\n"
                f"❓ *Follow-up:* Which district and season (Kharif, Rabi, or Summer) are you planning for?"
            )
        return {'answer': answer}

    # =========================================================================
    # 2. FERTILIZERS, NUTRIENTS & SOIL HEALTH
    # =========================================================================
    @classmethod
    def _handle_fertilizer_soil(cls, crop, variety, stage, problem, location, prompt, lang):
        crop_name = cls.get_crop_display(crop, lang)

        if lang == 'kn':
            # Crop-specific detailed NPK blocks
            crop_specific_block = ""
            if crop == 'Ragi':
                crop_specific_block = (
                    f"\n📌 **ರಾಗಿ ಬೆಳೆಗೆ ICAR / UASB ಶಿಫಾರಸು ರಸಗೊಬ್ಬರ ಪ್ರಮಾಣ:**\n"
                    f"   • ಖುಷ್ಕಿ ಬೇಸಾಯ (Rainfed): N:P:K = 20:16:10 ಕೆಜಿ/ಎಕರೆ\n"
                    f"   • ನೀರಾವರಿ ಬೇಸಾಯ (Irrigated): N:P:K = 40:20:20 ಕೆಜಿ/ಎಕರೆ\n"
                    f"   • ರಂಜಕ (P) ಮತ್ತು ಪೊಟ್ಯಾಶ್ (K) ಸಂಪೂರ್ಣ ಪ್ರಮಾಣವನ್ನು ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿ ಬೆರೆಸಿ. ಸಾರಜನಕ (N) ಅನ್ನು ಎರಡು ಕಂತಿನಲ್ಲಿ ನೀಡಿ.\n"
                )
            elif crop == 'Paddy':
                crop_specific_block = (
                    f"\n📌 **ಭತ್ತದ ಬೆಳೆಗೆ ICAR / ಕೃಷಿ ವಿವಿ ಶಿಫಾರಸು ರಸಗೊಬ್ಬರ ವೇಳಾಪಟ್ಟಿ:**\n"
                    f"   • **ಶಿಫಾರಸು ಪ್ರಮಾಣ (ಪ್ರತಿ ಎಕರೆಗೆ):** N:P:K = 40:20:20 ಕೆಜಿ (ಸಾರಜನಕ: 40 ಕೆಜಿ, ರಂಜಕ: 20 ಕೆಜಿ, ಪೊಟ್ಯಾಶ್: 20 ಕೆಜಿ).\n"
                    f"   • **ಅಡಿಯುರ (Basal Dose):** ಕೊನೆಯ ಉಳುಮೆ ವೇಳೆ 4-5 ಟನ್ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ. ನಾಟಿ ಸಮಯದಲ್ಲಿ ಸಂಪೂರ್ಣ ರಂಜಕ (100 ಕೆಜಿ SSP ಅಥವಾ 45 ಕೆಜಿ DAP), ಶೇ. 50% ಪೊಟ್ಯಾಶ್ (17 ಕೆಜಿ MOP) ಮತ್ತು ಶೇ. 25-50% ಸಾರಜನಕ (22 ಕೆಜಿ ಯೂರಿಯಾ) ಹಾಕಿ.\n"
                    f"   • **ಮೇಲುಗೊಬ್ಬರ (Top Dressing):** ನಾಟಿ ಮಾಡಿದ 25-30 ದಿನಗಳ ನಂತರ (ತೆನೆ ಒಡೆಯುವ ಹಂತ) 22 ಕೆಜಿ ಯೂರಿಯಾ, ಮತ್ತು 50-55 ದಿನಗಳ ನಂತರ (ಹೂವಾಡುವ ಮುನ್ನ) ಉಳಿದ 22 ಕೆಜಿ ಯೂರಿಯಾ ಹಾಗೂ 17 ಕೆಜಿ ಪೊಟ್ಯಾಶ್ ನೀಡಿ.\n"
                    f"   • **ಸತು (Zinc):** ಸತುವಿನ ಕೊರತೆ ತಡೆಯಲು ಎಕರೆಗೆ 10 ಕೆಜಿ ಜಿಂಕ್ ಸಲ್ಫೇಟ್ ಅನ್ನು ನಾಟಿ ಸಮಯದಲ್ಲಿ ಮಣ್ಣಿಗೆ ಬೆರೆಸಿ (ಡಿಎಪಿ ಜೊತೆ ನೇರ ಬೆರೆಸಬೇಡಿ).\n"
                )
            answer = (
                f"🌱 **{crop_name} ಪೋಷಕಾಂಶ ಮತ್ತು ರಸಗೊಬ್ಬರ ನಿರ್ವಹಣೆ (ICAR ವಿಜ್ಞಾನಿಗಳ ಶಿಫಾರಸು):**\n\n"
                f"1. **ಮಣ್ಣು ಪರೀಕ್ಷೆ ಆದ್ಯತೆ:** ಮಣ್ಣು ಆರೋಗ್ಯ ಕಾರ್ಡ್ (Soil Health Card) ಆಧಾರದ ಮೇಲೆ ಮಾತ್ರ ರಸಗೊಬ್ಬರ ನೀಡಿ. ಅಗತ್ಯಕ್ಕಿಂತ ಹೆಚ್ಚು ಯೂರಿಯಾ ಹಾಕಬೇಡಿ.\n"
                f"2. **ಸಾಮಾನ್ಯ N:P:K ಅನುಪಾತ:** ಧಾನ್ಯ ಬೆಳೆಗಳಿಗೆ 4:2:1 (ಸಾರಜನಕ:ರಂಜಕ:ಪೊಟ್ಯಾಶ್), ದ್ವಿದಳ ಧಾನ್ಯಗಳಿಗೆ 1:2:1 ಅಥವಾ 1:2:2 ಸೂಕ್ತ.{crop_specific_block}\n"
                f"3. **ಮೇಲುಗೊಬ್ಬರ ನೀಡುವಿಕೆ:** ಸಾರಜನಕವನ್ನು ಒಂದೇ ಬಾರಿ ಹಾಕದೆ, ಬಿತ್ತನೆ ವೇಳೆ 50% ಹಾಗೂ ಉಳಿದ 50% ಬೆಳವಣಿಗೆಯ ನಿರ್ಣಾಯಕ ಹಂತಗಳಲ್ಲಿ (ಕಳೆ ತೆಗೆದ ನಂತರ) 2 ಕಂತುಗಳಲ್ಲಿ ನೀಡಿ.\n"
                f"4. **ಸೂಕ್ಷ್ಮ ಪೋಷಕಾಂಶಗಳ ಕೊರತೆ:** ಸತು (Zinc) ಕೊರತೆ ನಿವಾರಣೆಗೆ ಎಕರೆಗೆ 10 ಕೆಜಿ ಜಿಂಕ್ ಸಲ್ಫೇಟ್ ಬಿತ್ತನೆ ವೇಳೆ ಮಣ್ಣಿಗೆ ಬೆರೆಸಿ.\n"
                f"5. **ಜೈವಿಕ ಗೊಬ್ಬರಗಳು:** ಅಜೋಸ್ಪೈರಿಲಂ ಮತ್ತು ರಂಜಕ ಕರಗಿಸುವ ಬ್ಯಾಕ್ಟೀರಿಯಾ (PSB) ಬಳಸಿ 20-25% ರಾಸಾಯನಿಕ ಗೊಬ್ಬರ ಉಳಿಸಿ.\n\n"
                f"⚠️ *ಸುರಕ್ಷತಾ ಕ್ರಮ:* ರಸಗೊಬ್ಬರವನ್ನು ತೇವವಿರುವ ಮಣ್ಣಿನಲ್ಲಿ ಮಾತ್ರ ಅನ್ವಯಿಸಿ; ಅತಿಯಾದ ಸಾರಜನಕ ಕೀಟ ಮತ್ತು ರೋಗಗಳಿಗೆ ಆಹ್ವಾನ ನೀಡುತ್ತದೆ."
            )
        elif lang == 'ta':
            answer = (
                f"🌱 **{crop_name} உர மேலாண்மை மற்றும் மண் வளம் (ICAR / TNAU பரிந்துரை):**\n\n"
                f"1. **மண் பரிசோதனை:** மண் வள அட்டையின்படி பரிந்துரைக்கப்பட்ட உரங்களை மட்டுமே இடவும். அளவுக்கு அதிகமான யூரியாவை தவிர்க்கவும்.\n"
                f"2. **சமச்சீர் N:P:K விகிதம்:** தானிய பயிர்களுக்கு 4:2:1 மற்றும் பயறு வகைகளுக்கு 1:2:1 என்ற விகிதம் சிறந்தது.\n"
                f"3. **மேலுரமிடும் முறை:** தழைச்சத்தை (யூரியா) ஒரே தவணையாக இடாமல், 50% அடியுரமாகவும், மீதியை தூர் கட்டும் பருவம் மற்றும் பூக்கும் பருவத்தில் 2-3 முறை பிரித்து இடவும்.\n"
                f"4. **நுண்ணூட்டச் சத்து:** துத்தநாக குறைபாட்டை போக்க ஏக்கருக்கு 10 கிலோ ஜிங்க் சல்பேட் அடியுரமாக இடவும்.\n"
                f"5. **உயிர் உரம்:** அசோஸ்பைரில்லம் மற்றும் பாஸ்போபாக்டீரியா இடுவதால் ரசாயன உரத்தேவை 25% வரை குறையும்.\n\n"
                f"⚠️ *எச்சரிக்கை:* உரமிடும் போது நிலத்தில் போதுமான ஈரப்பதம் இருப்பதை உறுதி செய்யவும்."
            )
        elif lang == 'hi':
            answer = (
                f"🌱 **{crop_name} हेतु संतुलित उर्वरक एवं मृदा पोषण (ICAR संस्तुति):**\n\n"
                f"1. **मृदा परीक्षण:** सॉयल हेल्थ कार्ड के आधार पर ही संतुलित रासायनिक उर्वरक डालें। यूरिया का अंधाधुंध उपयोग न करें।\n"
                f"2. **NPK अनुपात:** खाद्यान्न फसलों में 4:2:1 तथा दलहनी फसलों में 1:2:1 (N:P:K) का अनुपात रखें।\n"
                f"3. **टॉप ड्रेसिंग:** नाइट्रोजन को 2-3 किस्तों में दें - 50% बुवाई के समय, तथा शेष कल्ले फूटते व फूल आते समय।\n"
                f"4. **जिंक का प्रयोग:** जिंक की कमी से खैरा रोग होता है; बुवाई के समय 10 किग्रा जिंक सल्फेट प्रति एकड़ डालें।\n"
                f"5. **जैव उर्वरक:** एजोटोबैक्टर व पीएसबी का उपयोग करें, इससे 20-25% रासायनिक खाद की बचत होती है।"
            )
        else:
            answer = (
                f"🌱 **Balanced Fertilizer & Nutrient Management for {crop_name} (ICAR/KVK Guidelines):**\n\n"
                f"1. **Soil Test-Based Application:** Base chemical fertilizer usage strictly on your Soil Health Card test report. Avoid excess nitrogen.\n"
                f"2. **Recommended NPK Ratios:** Maintain 4:2:1 for cereals and 1:2:1 for pulses. Full Phosphorus (P) and Potash (K) should be applied basally.\n"
                f"3. **Split Nitrogen Application:** Apply 50% Nitrogen basally and split the remaining 50% into two top-dressings at active tillering/branching and panicle/flower initiation.\n"
                f"4. **Micronutrient Correction:** Basally apply 10 kg/acre Zinc Sulphate (ZnSO4) to prevent widespread zinc deficiency chlorosis.\n"
                f"5. **Bio-fertilizers:** Seed treatment or soil inoculation with Azospirillum / Rhizobium and PSB cuts synthetic fertilizer requirement by 20-25%."
            )
        return {'answer': answer}

    # =========================================================================
    # 3. CROP DISEASES & SYMPTOMS
    # =========================================================================
    @classmethod
    def _handle_crop_diseases(cls, crop, variety, stage, problem, location, prompt, lang):
        crop_name = cls.get_crop_display(crop, lang)
        symptom_detail = problem or "ರೋಗ ಲಕ್ಷಣಗಳು"

        if lang == 'kn':
            if crop == 'Paddy' and ('ಹಳದಿ' in prompt or problem == 'ಹಳದಿ' or 'yellow' in prompt.lower()):
                answer = (
                    f"🔬 **ಭತ್ತದ ಎಲೆ ಹಳದಿಯಾಗಲು ಪ್ರಮುಖ ಕಾರಣಗಳು ಮತ್ತು ನಿಖರ ಪರಿಹಾರ ಕ್ರಮಗಳು (ICAR ವಿಜ್ಞಾನಿಗಳ ಶಿಫಾರಸು):**\n\n"
                    f"ಭತ್ತದಲ್ಲಿ ಎಲೆ ಹಳದಿಯಾಗಲು 4 ಪ್ರಮುಖ ಕಾರಣಗಳಿರಬಹುದು. ನಿಮ್ಮ ಗದ್ದೆಯ ಲಕ್ಷಣಗಳನ್ನು ನೋಡಿ ಸೂಕ್ತ ಕ್ರಮ ಕೈಗೊಳ್ಳಿ:\n\n"
                    f"1. **ಸತು (Zinc) ಕೊರತೆ - ಖೈರಾ ರೋಗ (Khaira Disease):**\n"
                    f"   • **ಲಕ್ಷಣ:** ಎಳೆಯ ಎಲೆಗಳ ನರಗಳ ಮಧ್ಯೆ ಹಳದಿಯಾಗಿ ನಂತರ ತುಕ್ಕು ಬಣ್ಣದ ಕಂದು ಚುಕ್ಕೆಗಳಾಗುತ್ತವೆ. ಸಸಿಗಳ ಬೆಳವಣಿಗೆ ಕುಂಠಿತವಾಗುತ್ತದೆ.\n"
                    f"   • **ಪರಿಹಾರ:** 1 ಲೀಟರ್ ನೀರಿಗೆ 5 ಗ್ರಾಂ ಜಿಂಕ್ ಸಲ್ಫೇಟ್ (ZnSO4) + 2.5 ಗ್ರಾಂ ಸುಣ್ಣದ ತಿಳಿನೀರು ಬೆರೆಸಿ ಎಲೆಗಳ ಮೇಲೆ ಸಿಂಪಡಿಸಿ. ಅಥವಾ ಎಕರೆಗೆ 10 ಕೆಜಿ ಜಿಂಕ್ ಸಲ್ಫೇಟ್ ಮಣ್ಣಿಗೆ ಹಾಕಿ.\n\n"
                    f"2. **ಸಾರಜನಕ (Nitrogen) ಕೊರತೆ:**\n"
                    f"   • **ಲಕ್ಷಣ:** ಗಿಡದ ಕೆಳಗಿನ ಹಳೆಯ ಎಲೆಗಳು ಮೊದಲು ತಿಳಿ ಹಳದಿ ಬಣ್ಣಕ್ಕೆ ತಿರುಗಿ ಕ್ರಮೇಣ ಒಣಗುತ್ತವೆ.\n"
                    f"   • **ಪರಿಹಾರ:** ಎಕರೆಗೆ 15-20 ಕೆಜಿ ಯೂರಿಯಾ ಮೇಲುಗೊಬ್ಬರವಾಗಿ ನೀಡಿ ಅಥವಾ 1 ಲೀಟರ್ ನೀರಿಗೆ 20 ಗ್ರಾಂ (2%) ಯೂರಿಯಾ ಬೆರೆಸಿ ಎಲೆಗಳ ಮೇಲೆ ಸಿಂಪಡಿಸಿ.\n\n"
                    f"3. **ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಎಲೆ ಕರಕಲು ರೋಗ (Bacterial Leaf Blight - BLB):**\n"
                    f"   • **ಲಕ್ಷಣ:** ಎಲೆಯ ತುದಿಯಿಂದ ಅಂಚಿನುದ್ದಕ್ಕೂ ಹಳದಿ ಅಲೆಗಳಂತಹ ಪಟ್ಟಿಗಳು ಕಂಡುಬಂದು ನಂತರ ಒಣಗಿ ಒಣಹುಲ್ಲಿನ ಬಣ್ಣಕ್ಕೆ ತಿರುಗುತ್ತವೆ.\n"
                    f"   • **ಪರಿಹಾರ:** ಯೂರಿಯಾ ಗೊಬ್ಬರ ನೀಡುವುದನ್ನು ತಕ್ಷಣ ನಿಲ್ಲಿಸಿ. 1 ಲೀಟರ್ ನೀರಿಗೆ 0.1 ಗ್ರಾಂ ಸ್ಟ್ರೆಪ್ಟೋಸೈಕ್ಲಿನ್ + 2.5 ಗ್ರಾಂ ತಾಮ್ರದ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ (COC) ಬೆರೆಸಿ ಸಿಂಪಡಿಸಿ.\n\n"
                    f"4. **ಕಬ್ಬಿಣದ (Iron) ಕೊರತೆ:**\n"
                    f"   • **ಲಕ್ಷಣ:** ಸುಣ್ಣದ ಅಂಶ ಹೆಚ್ಚಿರುವ ಮಣ್ಣಿನಲ್ಲಿ ಎಳೆಯ ಎಲೆಗಳ ನರಗಳು ಹಸಿರಾಗಿದ್ದು ಉಳಿದ ಭಾಗ ಹಳದಿಯಾಗುತ್ತದೆ.\n"
                    f"   • **ಪರಿಹಾರ:** 1 ಲೀಟರ್ ನೀರಿಗೆ 10 ಗ್ರಾಂ ಫೆರಸ್ ಸಲ್ಫೇಟ್ (Ferrous Sulphate 1%) ಬೆರೆಸಿ 1 ವಾರದ ಅಂತರದಲ್ಲಿ 2 ಬಾರಿ ಸಿಂಪಡಿಸಿ.\n\n"
                    f"⚠️ *ಸುರಕ್ಷತಾ ಕ್ರಮ:* ಸಿಂಪಡಿಸುವಾಗ ಶುದ್ಧ ನೀರು ಬಳಸಿ ಮತ್ತು ಮಣ್ಣಿನಲ್ಲಿ ತೇವಾಂಶವಿರುವಂತೆ ನೋಡಿಕೊಳ್ಳಿ. ನಿಮ್ಮ ಜಿಲ್ಲೆ ಮತ್ತು ಭತ್ತ ನಾಟಿ ಮಾಡಿ ಎಷ್ಟು ದಿನಗಳಾಗಿವೆ ಎಂದು ತಿಳಿಸಿದರೆ ಮತ್ತಷ್ಟು ನಿಖರ ಸಲಹೆ ನೀಡಬಹುದು."
                )
            else:
                answer = (
                    f"🔬 **{crop_name} ರೋಗ ನಿರ್ವಹಣೆ ಮತ್ತು ರಕ್ಷಣಾ ಕ್ರಮಗಳು (ICAR ವಿಜ್ಞಾನಿಗಳ ಶಿಫಾರಸು):**\n\n"
                    f"1. **ಸಂಭಾವ್ಯ ರೋಗ ಮತ್ತು ಲಕ್ಷಣಗಳು:** ನೀವು ತಿಳಿಸಿದ '{symptom_detail}' ಲಕ್ಷಣಗಳು ಶಿಲೀಂಧ್ರ ಅಥವಾ ವೈರಸ್ ಬಾಧೆಯನ್ನು ಸೂಚಿಸುತ್ತವೆ. (ಉದಾಹರಣೆಗೆ: ಎಲೆ ಚುಕ್ಕೆ, ಬೆಂಕಿ ರೋಗ ಅಥವಾ ಎಲೆ ಸುರುಟು).\n"
                    f"2. **ಪ್ರಾಥಮಿಕ ಜೈವಿಕ ನಿಯಂತ್ರಣ:** ಆರಂಭಿಕ ಹಂತದಲ್ಲಿ ಟ್ರೈಕೋಡರ್ಮಾ ವಿರಿಡೆ (Trichoderma viride @ 5g/L) ಅಥವಾ ಸ್ಯೂಡೋಮೊನಾಸ್ ಫ್ಲೋರೊಸೆಂಟ್ (Pseudomonas @ 5g/L) ಸಿಂಪಡಿಸಿ.\n"
                    f"3. **ಶಿಫಾರಸು ಮಾಡಿದ ಔಷಧಗಳು:**\n"
                    f"   • ಎಲೆ ಚುಕ್ಕೆ / ಬೆಂಕಿ ರೋಗಕ್ಕೆ: ಟ್ರೈಸೈಕ್ಲೋಜೋಲ್ 75% WP (0.6g/L) ಅಥವಾ ಮ್ಯಾಂಕೋಜೆಬ್ 75% WP (2g/L) ಸಿಂಪಡಿಸಿ.\n"
                    f"   • ಎಲೆ ಸುರುಟು ವೈರಸ್ ಹರಡುವ ಬಿಳಿ ನೊಣಕ್ಕೆ: ಇಮಿಡಾಕ್ಲೋಪ್ರಿಡ್ 17.8% SL (0.3ml/L) ಸಿಂಪಡಿಸಿ.\n"
                    f"4. **ಕೃಷಿ ನೈರ್ಮಲ್ಯ:** ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ಕಿತ್ತು ಸುಟ್ಟುಹಾಕಿ; ಗದ್ದೆಯಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ಬಸಿಗಾಲುವೆಗಳನ್ನು ತೆರವುಗೊಳಿಸಿ.\n\n"
                    f"⚠️ *ಗಮನಿಸಿ:* ಯಾವುದೇ ಕೀಟನಾಶಕ ಸಿಂಪಡಿಸುವಾಗ ರಕ್ಷಣಾ ಮುಖಗವಸು ಧರಿಸಿ. ಖಚಿತ ರೋಗ ಪರೀಕ್ಷೆಗಾಗಿ ಸ್ಥಳೀಯ ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರ ಅಥವಾ KVK ವಿಜ್ಞಾನಿಗಳನ್ನು ಸಂಪರ್ಕಿಸಿ."
                )
        elif lang == 'ta':
            answer = (
                f"🔬 **{crop_name} நோய் கட்டுப்பாடு மற்றும் சிகிச்சை வழிகாட்டுதல் (ICAR / TNAU):**\n\n"
                f"1. **அறிகுறிகள்:** நீங்கள் குறிப்பிட்ட '{symptom_detail}' பூஞ்சான அல்லது வைரஸ் நோய்க்கான சாத்தியத்தை காட்டுகிறது (எ.கா: குலை நோய், இலைப்புள்ளி அல்லது இலைச்சுருள்).\n"
                f"2. **உயிர் பூஞ்சானக்கொல்லி:** ஆரம்ப நிலையில் சூடோமோனாஸ் புளோரசன்ஸ் 5 கிராம்/லிட்டர் அல்லது ட்ரைக்கோடெர்மா விரிடி 5 கிராம்/லிட்டர் தெளிக்கவும்.\n"
                f"3. **பரிந்துரைக்கப்படும் மருந்துகள்:**\n"
                f"   • இலைக்கருகல் / குலை நோய்க்கு: ட்ரைசைக்ளசோல் 75% WP (0.6 கிராம்/லிட்டர்) அல்லது மேன்கோசெப் (2 கிராம்/லிட்டர்).\n"
                f"   • இலைச்சுருள் வைரஸ் பரப்பும் பூச்சிகளுக்கு: இமிடாக்குளோபிரிட் 17.8% SL (0.3 மி.லி/லிட்டர்).\n"
                f"4. **வயல் பராமரிப்பு:** பாதிக்கப்பட்ட பயிர்களை அப்புறப்படுத்தி அழிக்கவும். தழைச்சத்து உரங்களை குறைக்கவும்.\n\n"
                f"⚠️ *பாதுகாப்பு குறிப்பு:* பூச்சிக்கொல்லி தெளிக்கும் போது கையுறை மற்றும் முகக்கவசம் அணியவும்."
            )
        elif lang == 'hi':
            answer = (
                f"🔬 **{crop_name} फसल रोग प्रबंधन एवं वैज्ञानिक उपचार (ICAR संस्तुति):**\n\n"
                f"1. **रोग के संभावित लक्षण:** '{symptom_detail}' कवक (फफूंद) अथवा विषाणु संक्रमण के लक्षण हो सकते हैं (जैसे झुलसा, टिक्का, अंगमारी अथवा पत्ती मरोड़)।\n"
                f"2. **जैविक रोकथाम:** स्यूडोमोनास फ्लोरोसेंस (5 ग्राम/लीटर) अथवा ट्राइकोडर्मा विरिडी का प्रारंभिक छिड़काव करें।\n"
                f"3. **रासायनिक दवाएं (अनुमोदित मात्रा):**\n"
                f"   • झुलसा/ब्लास्ट हेतु: ट्राइसाइक्लाजोल 75% WP (0.6 ग्राम/लीटर) या मैंकोजेब (2 ग्राम/लीटर)।\n"
                f"   • पत्ती मरोड़ (सफेद मक्खी नियंत्रण): इमिडाक्लोप्रिड 17.8% SL (0.3 मिली/लीटर)।\n"
                f"4. **खेत की स्वच्छता:** रोगग्रस्त पौधों को उखाड़कर नष्ट करें और जलभराव न होने दें।"
            )
        else:
            answer = (
                f"🔬 **Disease Diagnosis & Management for {crop_name} (ICAR/KVK Research):**\n\n"
                f"1. **Symptom Analysis:** Stated concern '{symptom_detail}' indicates fungal or viral pathogens (e.g. blast, blight, leaf spot, or leaf curl virus).\n"
                f"2. **Biological First Line:** Spray Pseudomonas fluorescens @ 5g/L or Trichoderma viride @ 5g/L at first appearance of lesions.\n"
                f"3. **Targeted Approved Fungicides:**\n"
                f"   • For Fungal Blast / Blight: Tricyclazole 75% WP @ 0.6g/L or Mancozeb 75% WP @ 2g/L.\n"
                f"   • For Viral Vector (Whiteflies/Aphids): Imidacloprid 17.8% SL @ 0.3ml/L.\n"
                f"4. **Sanitation & Drainage:** Rogue out severely infected plants, reduce nitrogen top-dressing, and maintain field drainage.\n\n"
                f"⚠️ *Important Notice:* Always observe pre-harvest intervals and wear protective gear. Consult your local KVK for microscopic tissue confirmation before aggressive spraying."
            )
        return {'answer': answer}

    # =========================================================================
    # 4. PEST & INSECT MANAGEMENT
    # =========================================================================
    @classmethod
    def _handle_pest_management(cls, crop, variety, stage, problem, location, prompt, lang):
        crop_name = cls.get_crop_display(crop, lang)

        if lang == 'kn':
            answer = (
                f"🐛 **{crop_name} ಸಮಗ್ರ ಕೀಟ ನಿರ್ವಹಣೆ (IPM - ICAR ಮಾರ್ಗಸೂಚಿ):**\n\n"
                f"1. **ಪ್ರಾಕೃತಿಕ ಮತ್ತು ಬಲೆಗಳ ಬಳಕೆ:** ಎಕರೆಗೆ 5-8 ಲಿಂಗಾಕರ್ಷಕ ಬಲೆಗಳು (Pheromone traps) ಮತ್ತು 15 ಹಳದಿ/ನೀಲಿ ಜಿಗುಟು ಬಲೆಗಳನ್ನು ಅಳವಡಿಸಿ ಕೀಟಗಳನ್ನು ಆಕರ್ಷಿಸಿ ನಾಶಮಾಡಿ.\n"
                f"2. **ಬೇವಿನ ಕಷಾಯ (ಜೈವಿಕ):** 5% ಬೇವಿನ ಬೀಜದ ಕಷಾಯ (NSKE) ಅಥವಾ 10,000 ppm ಬೇವಿನ ಎಣ್ಣೆ (2 ಮಿ.ಲೀ/ಲೀ) ಸಿಂಪಡಿಸಿ ಕೀಟಗಳ ಮೊಟ್ಟೆ ಒಡೆಯುವುದನ್ನು ತಡೆಯಿರಿ.\n"
                f"3. **ರಾಸಾಯನಿಕ ಸಿಂಪಡಣೆ (ಬಾಧೆ ತೀವ್ರವಾಗಿದ್ದರೆ):**\n"
                f"   • ಕಾಂಡ ಕೊರೆಯುವ ಹುಳು: ಕ್ಲೋರಾಂಟ್ರಾನಿಲಿಪ್ರೋಲ್ 18.5% SC (0.3 ಮಿ.ಲೀ/ಲೀ) ಅಥವಾ ಕಾರ್ಟಾಪ್ ಹೈಡ್ರೋಕ್ಲೋರೈಡ್ 50% SP (2g/L).\n"
                f"   • ಕಾಯಿ ಕೊರೆಯುವ / ಗುಲಾಬಿ ಹುಳು: ಎಮಾಮೆಕ್ಟಿನ್ ಬೆಂಜೋಯೇಟ್ 5% SG (0.4g/L).\n"
                f"   • ರಸಹೀರುವ ಕೀಟಗಳು (ನುಸಿ/ಜಿಗಿಹುಳು): ಫಿಪ್ರೋನಿಲ್ 5% SC (2 ಮಿ.ಲೀ/ಲೀ).\n\n"
                f"⚠️ *ಸುರಕ್ಷತೆ:* ಸಂಜೆ ವೇಳೆಯಲ್ಲಿ ಗಾಳಿ ಇಲ್ಲದ ಸಮಯದಲ್ಲಿ ಸಿಂಪಡಣೆ ಮಾಡಿ, ಜೇನುನೊಣಗಳಿಗೆ ಹಾನಿಯಾಗದಂತೆ ಎಚ್ಚರವಹಿಸಿ."
            )
        elif lang == 'ta':
            answer = (
                f"🐛 **{crop_name} ஒருங்கிணைந்த பூச்சி மேலாண்மை (IPM - TNAU / ICAR):**\n\n"
                f"1. **பொறிகள் அமைத்தல்:** ஏக்கருக்கு 5-8 இனக்கவர்ச்சி பொறிகள் மற்றும் 15 மஞ்சள் ஒட்டும் பொறிகளை பயிர் மட்டத்தில் வைக்கவும்.\n"
                f"2. **இயற்கை முறை:** 5% வேப்பங்கொட்டை சாறு (NSKE) அல்லது வேப்பெண்ணெய் 10,000 ppm (2 மி.லி/லிட்டர்) தெளிக்கவும்.\n"
                f"3. **இரசாயன கட்டுப்பாடு (பொருளாதார சேத நிலை தாண்டினால்):**\n"
                f"   • தண்டு துளைப்பான்: குளோரான்ட்ரானிலிப்ரோல் 18.5% SC (0.3 மி.லி/லிட்டர்) அல்லது கார்டாப் 50% SP (2 கிராம்/லிட்டர்).\n"
                f"   • காய்ப்புழு: எமாமெக்டின் பென்சோயேட் 5% SG (0.4 கிராம்/லிட்டர்).\n"
                f"   • சாறு உறிஞ்சும் பூச்சிகள்: பிப்ரோனில் 5% SC (2 மி.லி/லிட்டர்).\n\n"
                f"⚠️ *முன்னெச்சரிக்கை:* பூக்கள் மலரும் பருவத்தில் பூச்சிகொல்லி தெளிப்பதைத் தவிர்க்கவும்."
            )
        else:
            answer = (
                f"🐛 **Integrated Pest Management (IPM) for {crop_name} (ICAR/KVK Protocol):**\n\n"
                f"1. **Monitoring & Traps:** Install 5-8 species-specific pheromone traps per acre and 15 yellow/blue sticky traps to monitor Economic Threshold Levels (ETL).\n"
                f"2. **Botanical Repellents:** Spray Neem Seed Kernel Extract (NSKE 5%) or Azadirachtin 10,000 ppm @ 2ml/L to inhibit pest oviposition.\n"
                f"3. **Approved Label Chemistries:**\n"
                f"   • Borers (Stem/Fruit): Chlorantraniliprole 18.5% SC @ 0.3ml/L or Cartap Hydrochloride 50% SP @ 2g/L.\n"
                f"   • Bollworms / Defoliators: Emamectin Benzoate 5% SG @ 0.4g/L.\n"
                f"   • Sucking Pests (Aphids/Thrips): Fipronil 5% SC @ 2ml/L or Thiamethoxam 25% WG @ 0.3g/L.\n\n"
                f"⚠️ *Safety:* Spray during calm late afternoon hours. Strictly avoid spraying during peak honeybee foraging."
            )
        return {'answer': answer}

    # =========================================================================
    # 5. IRRIGATION & WATER MANAGEMENT
    # =========================================================================
    @classmethod
    def _handle_irrigation_water(cls, crop, variety, stage, problem, location, prompt, lang):
        crop_name = cls.get_crop_display(crop, lang)

        if crop == 'Ragi' and lang == 'kn':
            answer = (
                "🌾 **ರಾಗಿ ಬೆಳೆಯುವ ಸಮಗ್ರ ಕೃಷಿ ಪದ್ಧತಿ (ICAR / UAS ಬೆಂಗಳೂರು & ಧಾರವಾಡ ಶಿಫಾರಸು):**\n\n"
                "1. **ಹವಾಮಾನ ಮತ್ತು ಮಣ್ಣು (Climate & Soil):**\n"
                "   • ರಾಗಿ ಖಾರೀಫ್ ಮತ್ತು ರಬಿ ಎರಡೂ ಹಂಗಾಮುಗಳಲ್ಲಿ ಬೆಳೆಯಬಹುದು.\n"
                "   • ಕೆಂಪು ಮರಳು ಮಿಶ್ರಿತ ಮಣ್ಣು ಮತ್ತು ನೀರು ನಿಲ್ಲದ ಕಪ್ಪು ಮಣ್ಣಿನಲ್ಲಿ ಚೆನ್ನಾಗಿ ಬೆಳೆಯುತ್ತದೆ.\n"
                "   • ಮಣ್ಣಿನ pH 5.5 - 7.5; ಮಳೆಪ್ರಮಾಣ 500 - 900 ಮಿ.ಮೀ ಸಾಕಾಗುತ್ತದೆ.\n\n"
                "2. **ಶಿಫಾರಸು ತಳಿಗಳು (Recommended Varieties):**\n"
                "   • **ಖಾರೀಫ್:** GPU-28, ML-365, KMR-301 (ಬ್ಲಾಸ್ಟ್ ನಿರೋಧಕ), Indaf-8\n"
                "   • **ರಬಿ:** MR-1, MR-6, GPU-67\n"
                "   • ಕರ್ನಾಟಕದ ಒಣ ಭೂಮಿಗೆ: GPU-28 ಮತ್ತು KMR-301 ಅತ್ಯಂತ ಸೂಕ್ತ.\n\n"
                "3. **ಬೀಜದ ಪ್ರಮಾಣ ಮತ್ತು ಬಿತ್ತನೆ ವಿಧಾನ (Seed Rate & Sowing):**\n"
                "   • ನೇರ ಬಿತ್ತನೆ: ಎಕರೆಗೆ 4-5 ಕೆಜಿ ಬೀಜ. ಬೀಜ ತೆಳ್ಳಗೆ ಬಿತ್ತಿ ಮೇಲೆ ಮಣ್ಣು ಮುಚ್ಚಿ.\n"
                "   • ನಾಟಿ ಪದ್ಧತಿ: 20-25 ದಿನಗಳ ಸಸಿಗಳನ್ನು 22.5×10 ಸೆಂ.ಮೀ ಅಂತರದಲ್ಲಿ ನಾಟಿ ಮಾಡಿ (2-3 ಕೆಜಿ ಬೀಜ/ಎಕರೆ).\n"
                "   • ಬೀಜೋಪಚಾರ: ಪ್ರತಿ ಕೆಜಿ ಬೀಜಕ್ಕೆ 4 ಗ್ರಾಂ ಟ್ರೈಕೋಡರ್ಮಾ ವಿರಿಡೆ ಅಥವಾ 2 ಗ್ರಾಂ ಕಾರ್ಬೆಂಡಾಜಿಮ್ ಬಳಸಿ.\n\n"
                "4. **ಭೂಮಿ ಸಿದ್ಧತೆ (Land Preparation):**\n"
                "   • 2-3 ಬಾರಿ ಆಳವಾಗಿ ಉಳುಮೆ ಮಾಡಿ, ಹೆಂಟೆಗಳನ್ನು ಪುಡಿಮಾಡಿ ಸಮಮಟ್ಟ ಮಾಡಿ.\n"
                "   • ಕೊನೆಯ ಉಳುಮೆಯಲ್ಲಿ ಎಕರೆಗೆ 4-5 ಟನ್ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಬೆರೆಸಿ.\n\n"
                "5. **ರಸಗೊಬ್ಬರ ನಿರ್ವಹಣೆ (Fertilizer – NPK):**\n"
                "   • ಮಳೆ ಆಧಾರಿತ (Rainfed): N:P:K = 20:16:10 ಕೆಜಿ/ಎಕರೆ\n"
                "   • ನೀರಾವರಿ (Irrigated): N:P:K = 40:20:20 ಕೆಜಿ/ಎಕರೆ\n"
                "   • ರಂಜಕ ಮತ್ತು ಪೊಟ್ಯಾಶ್ ಸಂಪೂರ್ಣ ಅಡಿಯುರ; ಸಾರಜನಕ 2 ಕಂತಿನಲ್ಲಿ (ಬಿತ್ತನೆ ಮತ್ತು 25-30 DAT).\n"
                "   • ಸತು ಕೊರತೆಗೆ 10 ಕೆಜಿ ಜಿಂಕ್ ಸಲ್ಫೇಟ್/ಎಕರೆ ಅಡಿಯುರ ಹಾಕಿ.\n\n"
                "6. **ನೀರಾವರಿ (Irrigation):**\n"
                "   • ನಿರ್ಣಾಯಕ ಹಂತಗಳು: ಮೊಳಕೆ ಒಡೆಯುವ ಸಮಯ, ತೆನೆ ಒಡೆಯುವ ಸಮಯ ಮತ್ತು ಕಾಳು ತುಂಬುವ ಸಮಯ.\n"
                "   • ಮಳೆ ಆಧಾರಿತ ಬೇಸಾಯದಲ್ಲಿ ಮಳೆ ಸಾಲದಿದ್ದಾಗ ಮಾತ್ರ ಹನಿ ನೀರಾವರಿ ನೀಡಿ.\n\n"
                "7. **ಕಳೆ ನಿರ್ವಹಣೆ (Weed Management):**\n"
                "   • ಬಿತ್ತಿದ 20 ಮತ್ತು 40 ದಿನಗಳಲ್ಲಿ ಕಳೆ ತೆಗೆಯಿರಿ.\n"
                "   • ಪ್ರಿ-ಎಮರ್ಜೆಂಟ್ ಕಳೆನಾಶಕ: ಪೆಂಡಿಮೆಥಲಿನ್ 30% EC (1 ಕೆಜಿ AI/ಎಕರೆ) ಬಿತ್ತಿದ 2 ದಿನದಲ್ಲಿ ಸಿಂಪಡಿಸಿ.\n\n"
                "8. **ಕೀಟ ಮತ್ತು ರೋಗ ನಿರ್ವಹಣೆ (Pest & Disease):**\n"
                "   • ಬ್ಲಾಸ್ಟ್ ರೋಗ: ಟ್ರೈಸೈಕ್ಲೋಜೋಲ್ 75% WP (0.6 ಗ್ರಾಂ/ಲೀ) ಅಥವಾ ಕಾರ್ಬೆಂಡಾಜಿಮ್ (1 ಗ್ರಾಂ/ಲೀ) ಸಿಂಪಡಿಸಿ.\n"
                "   • ಮಿಡ್ತೆ / ಹಿಟ್ಟು ತಿಗಣೆ: ಡಿಮೆಥೋಯೇಟ್ 30% EC (2 ಮಿ.ಲೀ/ಲೀ) ಸಿಂಪಡಿಸಿ.\n\n"
                "9. **ಕಟಾವು ಮತ್ತು ಬೆಳೆಯ ಅವಧಿ (Harvesting & Duration):**\n"
                "   • ಬೆಳೆ ಅವಧಿ: 100 ರಿಂದ 120 ದಿನಗಳು.\n"
                "   • ತೆನೆಗಳ ಕಾಳು ಗಟ್ಟಿಯಾಗಿ ಕಂದು ಬಣ್ಣ ತಿರುಗಿದಾಗ ಕಟಾವು ಮಾಡಿ. 2-3 ದಿನ ಒಣಗಿಸಿ ಕಣದಲ್ಲಿ ಮಾಡಿ.\n"
                "   • ಇಳುವರಿ: ಮಳೆ ಆಧಾರಿತ 10-14 ಕ್ವಿಂಟಾಲ್/ಎಕರೆ; ನೀರಾವರಿ 16-20 ಕ್ವಿಂಟಾಲ್/ಎಕರೆ.\n\n"
                "❓ *ಸಲಹೆ:* ನೀವು ಯಾವ ಜಿಲ್ಲೆಯಲ್ಲಿ ರಾಗಿ ಬೆಳೆಯುತ್ತಿದ್ದೀರಿ ಮತ್ತು ಮಳೆ ಆಧಾರಿತವೇ ಅಥವಾ ನೀರಾವರಿಯೇ? "
                "ತಿಳಿಸಿದರೆ ನಿಮ್ಮ ಹಂಗಾಮಿಗೆ ಸೂಕ್ತ ತಳಿ ಮತ್ತು ನಿಖರ ದಿನಾಂಕ ನೀಡಬಹುದು."
            )
        elif crop == 'Paddy' and lang == 'kn':
            answer = (
                f"💧 **ಭತ್ತದ ಬೆಳೆಯ ನೀರು ನಿರ್ವಹಣೆ ಮತ್ತು ನೀರಿನ ಅವಶ್ಯಕತೆ (ICAR / KVK ಮಾರ್ಗಸೂಚಿ):**\n\n"
                f"1. **ಒಟ್ಟು ನೀರಿನ ಅವಶ್ಯಕತೆ:** ಭತ್ತದ ಬೆಳೆಗೆ ಸಂಪೂರ್ಣ ಜೀವಿತಾವಧಿಯಲ್ಲಿ ಸುಮಾರು 1200 ರಿಂದ 1400 ಮಿ.ಮೀ (ಸುಮಾರು 30-35 ಲಕ್ಷ ಲೀಟರ್/ಎಕರೆ) ನೀರು ಬೇಕಾಗುತ್ತದೆ. ಸದಾ ಅತಿಯಾದ ನೀರು ನಿಲ್ಲಿಸುವುದು ಅನಗತ್ಯ ಮತ್ತು ಹಾನಿಕಾರಕ.\n"
                f"2. **ನಾಟಿ ಹಂತ:** ನಾಟಿ ಮಾಡುವಾಗ ಮತ್ತು ನಂತರದ 7-10 ದಿನಗಳವರೆಗೆ ಗದ್ದೆಯಲ್ಲಿ ಕೇವಲ 2 ರಿಂದ 3 ಸೆಂ.ಮೀ ಆಳದ ತಿಳಿ ನೀರು ನಿಲ್ಲಿಸಿ, ಸಸಿಗಳು ಬೇಗ ಬೇರು ಬಿಡಲು ಅನುಕೂಲವಾಗುತ್ತದೆ.\n"
                f"3. **ತೆನೆ ಒಡೆಯುವ ಮತ್ತು ಹೂವಾಡುವ ಹಂತ (ನಿರ್ಣಾಯಕ ಘಟ್ಟ):** ತೆನೆ ಹೊಡೆಯುವ ಮತ್ತು ಕಾಳು ತುಂಬುವ ಸಮಯದಲ್ಲಿ ಗದ್ದೆಯಲ್ಲಿ 4 ರಿಂದ 5 ಸೆಂ.ಮೀ ನೀರನ್ನು ನಿರ್ವಹಿಸಿ. ಈ ಸಮಯದಲ್ಲಿ ನೀರಿನ ಕೊರತೆಯಾದರೆ ಕಾಳು ಜೊಳ್ಳಾಗುತ್ತದೆ.\n"
                f"4. **ಪರ್ಯಾಯ ತೇವ ಮತ್ತು ಒಣಗಿಸುವ ಪದ್ಧತಿ (AWD - Alternate Wetting & Drying):** ನೀರು ಕಟ್ಟಿದ ನಂತರ ನೀರು ಸಂಪೂರ್ಣ ಇಂಗಿ ಮಣ್ಣಿನ ಮೇಲೆ ಸಣ್ಣ ಬಿರುಕು ಕಾಣಿಸಿಕೊಳ್ಳುವ ಮುನ್ನ (2-3 ದಿನಗಳ ನಂತರ) ಮರು ನೀರು ಕಟ್ಟಿ. ಈ ಪದ್ಧತಿಯಿಂದ ಶೇ. 30% ನೀರು ಉಳಿತಾಯವಾಗುವುದಲ್ಲದೆ ಭತ್ತದ ಇಳುವರಿ ಶೇ. 15% ಹೆಚ್ಚುತ್ತದೆ.\n"
                f"5. **ಕಟಾವಿಗೆ ಮುನ್ನ ಬಸಿದು ತೆಗೆಯುವುದು:** ಕಟಾವು ಮಾಡುವ 10 ರಿಂದ 15 ದಿನಗಳ ಮುಂಚಿತವಾಗಿ ಗದ್ದೆಯಲ್ಲಿರುವ ನೀರನ್ನು ಸಂಪೂರ್ಣವಾಗಿ ಹೊರಹಾಕಿ ಒಣಗಲು ಬಿಡಿ. ಇದರಿಂದ ಕಾಳು ಗಟ್ಟಿಯಾಗಿ ಕೊಯ್ಲಿಗೆ ಅನುಕೂಲವಾಗುತ್ತದೆ.\n\n"
                f"❓ *ಸಲಹೆ:* ನಿಮ್ಮ ಜಮೀನು ಕಾಲುವೆ ಆಶ್ರಯದಲ್ಲಿದೆಯೇ ಅಥವಾ ಬೋರ್‌ವೆಲ್ ನೀರಾವರಿಯೇ? ನಿಮ್ಮ ಜಿಲ್ಲೆಯ ಹೆಸರನ್ನು ತಿಳಿಸಿ."
            )
        elif lang == 'kn':
            answer = (
                f"💧 **{crop_name} ನೀರಾವರಿ ಮತ್ತು ಜಲ ಸಂರಕ್ಷಣೆ (ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರದ ಸಲಹೆ):**\n\n"
                f"1. **ಹನಿ ನೀರಾವರಿ ಪ್ರಯೋಜನಗಳು:** ಹನಿ ನೀರಾವರಿ ಪದ್ಧತಿಯಿಂದ 40% ರಿಂದ 60% ನೀರು ಉಳಿತಾಯವಾಗುತ್ತದೆ ಮತ್ತು ಇಳುವರಿ 25-30% ವೃದ್ಧಿಯಾಗುತ್ತದೆ.\n"
                f"2. **ಫರ್ಟಿಗೇಷನ್ (ನೀರಿನಲ್ಲೇ ಗೊಬ್ಬರ):** ನೀರಿನ ಮೂಲಕವೇ ರಸಗೊಬ್ಬರ ನೀಡಿದರೆ ಶೇ. 30% ಗೊಬ್ಬರ ಉಳಿತಾಯವಾಗಿ ಬೇರುಗಳಿಗೆ ನೇರವಾಗಿ ತಲುಪುತ್ತದೆ.\n"
                f"3. **ಭತ್ತಕ್ಕೆ AWD ಪದ್ಧತಿ:** ಭತ್ತದ ಗದ್ದೆಯಲ್ಲಿ ಸದಾ ನೀರು ನಿಲ್ಲಿಸದೆ 2-3 ದಿನ ಒಣಗಿಸಿ ನೀರು ಕೊಡುವ ಪದ್ಧತಿ (Alternate Wetting and Drying) ಅಳವಡಿಸಿ 25% ನೀರು ಉಳಿಸಿ.\n"
                f"4. **ಸರ್ಕಾರಿ ಸಹಾಯಧನ:** ಪ್ರಧಾನ ಮಂತ್ರಿ ಕೃಷಿ ಸಿಂಚಾಯಿ ಯೋಜನೆ (PMKSY) ಅಡಿಯಲ್ಲಿ ಸಣ್ಣ ಮತ್ತು ಅತಿಸಣ್ಣ ರೈತರಿಗೆ ಶೇ. 90% ವರೆಗೆ ಸಬ್ಸಿಡಿ ಲಭ್ಯವಿದೆ.\n"
                f"5. **ಹೊದಿಕೆ (Mulching):** ಒಣ ತ್ಯಾಜ್ಯ ಅಥವಾ ರಾಗಿ ಕಡ್ಡಿಯ ಹೊದಿಕೆ ಮಾಡುವುದರಿಂದ ಮಣ್ಣಿನ ತೇವಾಂಶ ದೀರ್ಘಕಾಲ ಉಳಿಯುತ್ತದೆ."
            )
        elif lang == 'ta':
            answer = (
                f"💧 **{crop_name} பாசன நீர் மேலாண்மை மற்றும் சேமிப்பு (TNAU / ICAR):**\n\n"
                f"1. **சொட்டு நீர் பாசனம்:** 40-60% பாசன நீர் சேமிப்புடன், பயிர் மகசூலை 25% வரை அதிகரிக்கிறது.\n"
                f"2. **நீர்வழி உரமிடுதல்:** நீரில் கரையும் உரங்களை பாசனக் குழாய்கள் மூலம் வேர்ப்பகுதிக்கு செலுத்துவதால் உரச் செலவு 30% குறைகிறது.\n"
                f"3. **காய்ச்சலும் பாய்ச்சலும்:** நெல் வயலில் எப்போதும் நீர் தேக்காமல் 'காய்ச்சலும் பாய்ச்சலும்' முறையில் 25% தண்ணீரை சேமிக்கலாம்.\n"
                f"4. **அரசு மானியம்:** PMKSY திட்டத்தின் கீழ் சிறு, குறு விவசாயிகளுக்கு 100% வரை சொட்டு நீர் பாசன மானியம் வழங்கப்படுகிறது.\n"
                f"5. **நிலப்போர்வை:** வைக்கோல் கொண்டு நிலப்போர்வை அமைப்பதால் நீர் ஆவியாதல் தடுக்கப்படுகிறது."
            )
        else:
            answer = (
                f"💧 **Water Management & Micro-Irrigation for {crop_name} (ICAR Guidelines):**\n\n"
                f"1. **Drip Irrigation Efficiency:** Delivers 40-60% water savings and boosts productivity by 20-30% by eliminating runoff and deep percolation.\n"
                f"2. **Fertigation:** Soluble fertilizers injected via venturi directly to the root zone achieve 90% uptake efficiency vs 40% with broadcast method.\n"
                f"3. **AWD for Paddy:** Implementing Alternate Wetting & Drying saves 25% water and significantly reduces methane emissions without yield loss.\n"
                f"4. **Government Subsidies:** Under PMKSY (Per Drop More Crop), small and marginal farmers qualify for up to 90% capital subsidy.\n"
                f"5. **Mulching:** Organic crop residue mulching retains soil moisture and lowers root zone temperature by 3-5°C."
            )
        return {'answer': answer}

    # =========================================================================
    # 6. SEEDS & SEED TREATMENT
    # =========================================================================
    @classmethod
    def _handle_seeds_treatment(cls, crop, variety, stage, problem, location, prompt, lang):
        crop_name = cls.get_crop_display(crop, lang)

        if lang == 'kn':
            answer = (
                f"🌱 **{crop_name} ಬೀಜೋಪಚಾರ ಮತ್ತು ಗುಣಮಟ್ಟದ ಬೀಜಗಳ ಆಯ್ಕೆ (KVK ಶಿಫಾರಸು):**\n\n"
                f"1. **ಬೀಜೋಪಚಾರದ ಮಹತ್ವ:** ಬಿತ್ತನೆಗೆ ಮುನ್ನ ಬೀಜೋಪಚಾರ ಮಾಡುವುದರಿಂದ ಶೇ. 80% ಮಣ್ಣಿನ ಮತ್ತು ಬೀಜದ ಮೂಲಕ ಹರಡುವ ರೋಗಗಳನ್ನು ಆರಂಭದಲ್ಲೇ ತಡೆಯಬಹುದು.\n"
                f"2. **ಜೈವಿಕ ಬೀಜೋಪಚಾರ:**\n"
                f"   • ಪ್ರತಿ ಕೆಜಿ ಬೀಜಕ್ಕೆ ಟ್ರೈಕೋಡರ್ಮಾ ವಿರಿಡೆ 4 ಗ್ರಾಂ ಅಥವಾ ಸ್ಯೂಡೋಮೊನಾಸ್ 10 ಗ್ರಾಂ ಬೆರೆಸಿ ನೆರಳಿನಲ್ಲಿ ಒಣಗಿಸಿ.\n"
                f"   • ದ್ವಿದಳ ಧಾನ್ಯಗಳಿಗೆ ರೈಜೋಬಿಯಂ (Rhizobium @ 200g/acre seed) ಜೈವಿಕ ಗೊಬ್ಬರ ಬೆರೆಸಿ.\n"
                f"3. **ರಾಸಾಯನಿಕ ಬೀಜೋಪಚಾರ:** ಕಾರ್ಬೆಂಡಾಜಿಮ್ 50% WP (2g/kg seed) ಅಥವಾ ಥೈರಾಮ್ 75% WP ಬೆರೆಸಿ.\n"
                f"4. **ಮೊಳಕೆ ಪರೀಕ್ಷೆ:** 100 ಬೀಜಗಳನ್ನು ಒದ್ದೆ ಬಟ್ಟೆಯಲ್ಲಿ ಇಟ್ಟು 3-4 ದಿನಗಳ ನಂತರ ಕನಿಷ್ಠ 85 ಬೀಜಗಳು ಮೊಳಕೆಯೊಡೆದಿರುವುದನ್ನು ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ."
            )
        elif lang == 'ta':
            answer = (
                f"🌱 **{crop_name} விதை நேர்த்தி முறைகள் (TNAU / ICAR):**\n\n"
                f"1. **முக்கியத்துவம்:** விதை நேர்த்தி செய்வதன் மூலம் வேர் அழுகல், நாற்று அழுகல் போன்ற மண் மற்றும் விதை மூலம் பரவும் நோய்களை 80% தடுக்கலாம்.\n"
                f"2. **உயிரியல் விதை நேர்த்தி:**\n"
                f"   • ஒரு கிலோ விதைக்கு ட்ரைக்கோடெர்மா விரிடி 4 கிராம் அல்லது சூடோமோனாஸ் 10 கிராம் கலந்து நிழலில் உலர்த்தவும்.\n"
                f"   • பயறு வகைகளுக்கு ரைசோபியம் நுண்ணுயிர் உரம் கலக்கவும்.\n"
                f"3. **இரசாயன விதை நேர்த்தி:** கார்பெண்டாசிம் 2 கிராம்/கிலோ விதைக்கு என்ற அளவில் நேர்த்தி செய்யவும்.\n"
                f"4. **முளைப்புத்திறன் சோதனை:** விதைப்பதற்கு முன் முளைப்புத்திறன் 85% மேல் இருப்பதை உறுதி செய்யவும்."
            )
        else:
            answer = (
                f"🌱 **Scientific Seed Treatment Protocols for {crop_name} (ICAR/KVK Guidelines):**\n\n"
                f"1. **Objective:** Prevents up to 80% of damping-off, collar rot, and seed-borne fungal infections during the vulnerable first 21 days.\n"
                f"2. **Biological Inoculation:**\n"
                f"   • Coat seeds with Trichoderma viride @ 4g/kg seed or Pseudomonas fluorescens @ 10g/kg.\n"
                f"   • For pulses/legumes, inoculate with crop-specific Rhizobium culture (200g per 10 kg seed) using rice starch paste.\n"
                f"3. **Chemical Seed Dressing:** Treat with Carbendazim 50% WP @ 2g/kg seed or Thiram 75% WP @ 2.5g/kg seed before sowing.\n"
                f"4. **Germination Verification:** Test sample 100 seeds in moist gunny paper; ensure germination is $\\ge$ 85% before field broadcasting."
            )
        return {'answer': answer}

    # =========================================================================
    # 7. SOWING & HARVESTING METHODS
    # =========================================================================
    @classmethod
    def _handle_sowing_harvesting(cls, crop, variety, stage, problem, location, prompt, lang):
        crop_name = cls.get_crop_display(crop, lang)

        if lang == 'kn':
            answer = (
                f"🌾 **{crop_name} ಬಿತ್ತನೆ ಮತ್ತು ಕಟಾವು ವಿಧಾನಗಳು (ICAR ವಿಜ್ಞಾನಿಗಳ ಶಿಫಾರಸು):**\n\n"
                f"1. **ಸಾಲು ಬಿತ್ತನೆ ಮತ್ತು ಅಂತರ:** ಚೆಲ್ಲಾಪಿಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡುವ ಬದಲು ಸಾಲು ಬಿತ್ತನೆ ಯಂತ್ರ (Seed Drill) ಬಳಸಿ ಶಿಫಾರಸು ಮಾಡಿದ ಸಾಲುಗಳ ಅಂತರ ಕಾಪಾಡಿ.\n"
                f"2. **ಶ್ರೀ (SRI) ಪದ್ಧತಿ (ಭತ್ತಕ್ಕೆ):** ಭತ್ತದಲ್ಲಿ 12-14 ದಿನಗಳ ಎಳೆಯ ಸಸಿಯನ್ನು 25x25 ಸೆಂ.ಮೀ ಅಂತರದಲ್ಲಿ ಒಂದೊಂದೇ ನಾಟಿ ಮಾಡುವುದರಿಂದ ಅಧಿಕ ತೆನೆಗಳು ಬರುತ್ತವೆ.\n"
                f"3. **ಕಟಾವಿನ ಪ್ರಬುದ್ಧತೆಯ ಲಕ್ಷಣಗಳು:** ತೆನೆಯ ಶೇ. 80-85 ರಷ್ಟು ಕಾಳುಗಳು ಬಂಗಾರದ ಬಣ್ಣಕ್ಕೆ ತಿರುಗಿದಾಗ ಕೊಯ್ಲು ಮಾಡಬೇಕು.\n"
                f"4. **ಕೊಯ್ಲಿನ ನಂತರದ ಶೇಖರಣೆ:** ಕಟಾವಿನ ನಂತರ ಕಾಳುಗಳನ್ನು ಕಣದಲ್ಲಿ 3-4 ದಿನ ಒಣಗಿಸಿ, ಕಾಳಿನ ತೇವಾಂಶವನ್ನು ಶೇ. 12-14ಕ್ಕೆ ಇಳಿಸಿ ಗೋದಾಮಿನಲ್ಲಿ ಶೇಖರಿಸಿ."
            )
        else:
            answer = (
                f"🌾 **Sowing, Spacing & Harvest Management for {crop_name} (ICAR Package of Practices):**\n\n"
                f"1. **Line Sowing vs Broadcasting:** Always prefer line sowing with a seed-cum-fertilizer drill. It saves 30% seed and permits mechanized weeding.\n"
                f"2. **System of Rice Intensification (SRI):** Transplant young 12-14 day single seedlings with 25x25 cm wider square spacing to multiply tillering by 40%.\n"
                f"3. **Harvest Physiological Maturity:** Harvest when 80-85% of grain panicles have turned golden straw color; avoid over-drying on field which causes grain shattering.\n"
                f"4. **Post-Harvest Drying:** Sun-dry harvested grains to reduce moisture content to safe storage limit (12-14%) to avoid storage fungal aflatoxins."
            )
        return {'answer': answer}

    # =========================================================================
    # 8. WEATHER & CLIMATE ADVICE
    # =========================================================================
    @classmethod
    def _handle_weather_climate(cls, crop, variety, stage, problem, location, prompt, lang):
        if lang == 'kn':
            answer = (
                "🌦️ **ಹವಾಮಾನ ಮತ್ತು ಮುಂಜಾಗ್ರತಾ ಕೃಷಿ ಸಲಹೆ (IMD & KVK Agro-Met Advisory):**\n\n"
                "1. **ಭಾರೀ ಮಳೆಯ ಮುನ್ಸೂಚನೆ:** ತೋಟ ಮತ್ತು ಗದ್ದೆಗಳಲ್ಲಿ ನೀರು ಸರಾಗವಾಗಿ ಹರಿದುಹೋಗಲು ಒಳಚರಂಡಿಗಳನ್ನು ತೆರವುಗೊಳಿಸಿ. ಕೀಟನಾಶಕ ಸಿಂಪಡಣೆಯನ್ನು ಮುಂದೂಡಿ.\n"
                "2. **ಹೆಚ್ಚಿನ ತೇವಾಂಶ ಮತ್ತು ಶಿಲೀಂಧ್ರ:** ಮಳೆಯ ನಂತರ ಬಿಸಿಲು ಬಿದ್ದಾಗ ಶಿಲೀಂಧ್ರ ರೋಗಗಳು ವೇಗವಾಗಿ ಹರಡುತ್ತವೆ; ಮುನ್ನೆಚ್ಚರಿಕೆಯಾಗಿ ತಾಮ್ರದ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ (COC 2.5g/L) ಸಿಂಪಡಿಸಿ.\n"
                "3. **ಬೇಸಿಗೆ ತಾಪಮಾನ ನಿರ್ವಹಣೆ:** ಒಣ ತ್ಯಾಜ್ಯ/ರಾಗಿ ಕಡ್ಡಿಗಳಿಂದ ಹೊದಿಕೆ (Mulching) ಮಾಡಿ ಬೇರಿನ ತೇವಾಂಶವನ್ನು ಕಾಪಾಡಿ.\n"
                "4. **ಕೊಯ್ಲು ಮಾಡಿದ ಬೆಳೆಗಳ ರಕ್ಷಣೆ:** ಕಟಾವು ಮಾಡಿದ ಕಾಳುಗಳನ್ನು ಟಾರ್ಪಲಿನ್ ಹೊದಿಸಿ ಸುರಕ್ಷಿತ ಎತ್ತರದ ಸ್ಥಳದಲ್ಲಿ ಸಂಗ್ರಹಿಸಿ."
            )
        else:
            answer = (
                "🌦️ **Agro-Meteorological Advisory & Climate Resilience (IMD / ICAR):**\n\n"
                "1. **Heavy Rainfall Advisory:** Clear field drainage channels immediately to eliminate standing surface water. Suspend all pesticide and foliar fertilizer sprays.\n"
                "2. **High Humidity Fungal Protection:** Warm humid conditions following precipitation trigger late blight and rots; apply prophylactic Copper Oxychloride (COC) @ 2.5g/L.\n"
                "3. **Heatwave Mitigation:** Provide light frequent irrigations during early morning or evening hours and apply straw mulching to buffer soil temperatures.\n"
                "4. **Produce Protection:** Shift harvested threshing floor heaps onto elevated platforms covered with waterproof HDPE tarpaulins."
            )
        return {'answer': answer}

    # =========================================================================
    # 10. GOVERNMENT SCHEMES & SUBSIDIES
    # =========================================================================
    @classmethod
    def _handle_govt_schemes(cls, crop, variety, stage, problem, location, prompt, lang):
        if lang == 'kn':
            answer = (
                "🏛️ **ರೈತರಿಗಾಗಿ ಪ್ರಮುಖ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಮತ್ತು ಸಹಾಯಧನ (Govt. Schemes):**\n\n"
                "1. **ಪಿಎಂ-ಕಿಸಾನ್ (PM-KISAN):** ಅರ್ಹ ಭೂಮಾಲೀಕ ರೈತರಿಗೆ ವಾರ್ಷಿಕ ₹6,000 ನೇರ ಬ್ಯಾಂಕ್ ವರ್ಗಾವಣೆ (ವರ್ಷಕ್ಕೆ 3 ಕಂತುಗಳಲ್ಲಿ ತಲಾ ₹2,000).\n"
                "2. **ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ (PMFBY):** ಅತಿವೃಷ್ಟಿ, ಅನಾವೃಷ್ಟಿ ಮತ್ತು ಬೆಳೆ ಹಾನಿಗೆ ಅತಿ ಕಡಿಮೆ ಪ್ರೀಮಿಯಂ ದರದಲ್ಲಿ ಬೆಳೆ ವಿಮೆ ಪರಿಹಾರ (ಖಾರೀಫ್ ಬೆಳೆಗಳಿಗೆ ಕೇವಲ 2%, ರಬಿಗೆ 1.5%).\n"
                "3. **ಹನಿ ನೀರಾವರಿ ಸಬ್ಸಿಡಿ (PMKSY):** ಸಣ್ಣ ಮತ್ತು ಅತಿಸಣ್ಣ ರೈತರಿಗೆ ಹನಿ/ತುಂತುರು ನೀರಾವರಿ ಸ್ಥಾಪಿಸಲು ಶೇ. 90% ವರೆಗೆ ಸರ್ಕಾರಿ ಸಹಾಯಧನ.\n"
                "4. **ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (KCC):** ಕೇವಲ ಶೇ. 4% ಬಡ್ಡಿದರದಲ್ಲಿ ಬೆಳೆ ಸಾಲ ಸೌಲಭ್ಯ.\n"
                "5. **ಕೃಷಿ ಯಂತ್ರೋಪಕರಣ ಸಬ್ಸಿಡಿ (SMAM):** ಟ್ರಾಕ್ಟರ್, ಕಳೆ ಕೀಳುವ ಯಂತ್ರ, ಪವರ್ ಟಿಲ್ಲರ್‌ಗಳಿಗೆ ಶೇ. 40-50% ಸಹಾಯಧನ.\n\n"
                "📌 *ಅರ್ಜಿ ಸಲ್ಲಿಸಲು:* ಹತ್ತಿರದ ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರ (RSK) ಅಥವಾ ಸೇವಾ ಸಿಂಧು / ಕೃಷಿ ಇಲಾಖೆ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ನೋಂದಾಯಿಸಿ."
            )
        elif lang == 'ta':
            answer = (
                "🏛️ **விவசாயிகளுக்கான முக்கிய அரசு திட்டங்கள் & மானியங்கள் (Govt. of India / TN):**\n\n"
                "1. **பி.எம் கிசான் (PM-KISAN):** விவசாயிகளுக்கு ஆண்டுக்கு ₹6,000 நிதியுதவி (மூன்று தவணைகளாக ₹2,000 வங்கி கணக்கில் செலுத்தப்படுகிறது).\n"
                "2. **பயிர் காப்பீட்டு திட்டம் (PMFBY):** இயற்கை பேரிடரால் பயிர் சேதம் அடைந்தால் உரிய இழப்பீடு (காரீப் 2%, ரபி 1.5% குறைந்த பிரீமியம்).\n"
                "3. **சொட்டு நீர் பாசன மானியம்:** சிறு, குறு விவசாயிகளுக்கு 100% வரை அரசு மானியம்.\n"
                "4. **கிசான் கிரெடிட் கார்டு (KCC):** வெறும் 4% குறைந்த வட்டியில் பயிர் கடன்.\n"
                "5. **வேளாண் இயந்திர மானியம் (SMAM):** டிராக்டர், பவர் டில்லர் போன்ற கருவிகளுக்கு 40-50% மானியம்.\n\n"
                "📌 *விண்ணப்பிக்க:* உழவன் செயலி (Uzhavan App) அல்லது வட்டார வேளாண்மை விரிவாக்க மையத்தை அணுகவும்."
            )
        else:
            answer = (
                "🏛️ **Key Government Schemes & Agricultural Subsidies (Govt. of India):**\n\n"
                "1. **PM-KISAN:** Direct income support of ₹6,000 per year in 3 equal four-monthly installments directly to farmers' bank accounts.\n"
                "2. **PM Fasal Bima Yojana (PMFBY):** Comprehensive crop loss insurance against non-preventable natural risks at minimal premium (2% Kharif, 1.5% Rabi).\n"
                "3. **Micro-Irrigation Subsidy (PMKSY):** Up to 90% capital subsidy for drip and sprinkler installations for small and marginal landholders.\n"
                "4. **Kisan Credit Card (KCC):** Concessional crop loans up to ₹3 Lakh at an effective interest rate of 4% with timely repayments.\n"
                "5. **Agricultural Mechanization (SMAM):** 40-50% financial assistance for purchasing tractors, power tillers, rotavators, and seed drills."
            )
        return {'answer': answer}

    # =========================================================================
    # 11. ORGANIC & NATURAL FARMING
    # =========================================================================
    @classmethod
    def _handle_organic_farming(cls, crop, variety, stage, problem, location, prompt, lang):
        if lang == 'kn':
            answer = (
                "🌿 **ಜೀವಾಮೃತ ತಯಾರಿಕೆ ಮತ್ತು ನೈಸರ್ಗಿಕ ಕೃಷಿ ವಿಧಾನ (Subhash Palekar Natural Farming):**\n\n"
                "1. **ಅಗತ್ಯ ಸಾಮಗ್ರಿಗಳು (200 ಲೀಟರ್ ಜೀವಾಮೃತಕ್ಕೆ / 1 ಎಕರೆಗೆ):**\n"
                "   • ದೇಶಿ ಹಸುವಿನ ಹಸಿ ಸಗಣಿ 10 ಕೆಜಿ\n"
                "   • ದೇಶಿ ಹಸುವಿನ ಗೋಮೂತ್ರ 10 ಲೀಟರ್\n"
                "   • ಕಪ್ಪು ಬೆಲ್ಲ 2 ಕೆಜಿ\n"
                "   • ದ್ವಿದಳ ಧಾನ್ಯದ ಹಿಟ್ಟು (ಕಡಲೆ/ಹುರುಳಿ) 2 ಕೆಜಿ\n"
                "   • ಬದುವಿನ ಫಲವತ್ತಾದ ಮಣ್ಣು 1 ಹಿಡಿ\n"
                "2. **ತಯಾರಿಸುವ ವಿಧಾನ:** 200 ಲೀಟರ್ ನೀರಿನ ಪ್ಲಾಸ್ಟಿಕ್ ಡ್ರಮ್ಮಿನಲ್ಲಿ ಇವೆಲ್ಲವನ್ನು ಬೆರೆಸಿ, ದಿನಕ್ಕೆ 2 ಬಾರಿ ಬೇವಿನ ಕೋಲಿನಿಂದ ಬಲಗಡೆಗೆ ತಿರುಗಿಸಿ. ನೆರಳಿನಲ್ಲಿ 48 ರಿಂದ 72 ಗಂಟೆಗಳ ಕಾಲ ಹುದುಗಲು ಬಿಡಿ.\n"
                "3. **ಬಳಕೆಯ ಪ್ರಮಾಣ:** ಪ್ರತಿ ಎಕರೆಗೆ 200 ಲೀಟರ್ ಜೀವಾಮೃತವನ್ನು ನೀರಾವರಿ ನೀರಿನ ಜೊತೆ ಅಥವಾ ನೇರವಾಗಿ ಬೆಳೆಗಳ ಸಾಲಿಗೆ 15-21 ದಿನಗಳಿಗೊಮ್ಮೆ ನೀಡಿ.\n"
                "4. **ಪಂಚಗವ್ಯ ಬಳಕೆ:** 5 ಗೋ ಉತ್ಪನ್ನಗಳಿಂದ ತಯಾರಿಸಿದ ಪಂಚಗವ್ಯವನ್ನು ಶೇ. 3% (30 ಮಿ.ಲೀ/ಲೀಟರ್) ಸಿಂಪಡಿಸುವುದರಿಂದ ಬೆಳೆಗಳು ಸಮೃದ್ಧವಾಗಿ ಬೆಳೆದು ರೋಗನಿರೋಧಕ ಶಕ್ತಿ ಹೆಚ್ಚುತ್ತದೆ."
            )
        elif lang == 'ta':
            answer = (
                "🌿 **ஜீவாமிர்தம் தயாரிப்பு மற்றும் இயற்கை வேளாண்மை வழிகாட்டி:**\n\n"
                "1. **தேவையான பொருட்கள் (200 லிட்டருக்கு - 1 ஏக்கர்):**\n"
                "   • நாட்டு மாட்டு சாணம் 10 கிலோ\n"
                "   • நாட்டு மாட்டு கோமியம் 10 லிட்டர்\n"
                "   • நாட்டு வெல்லம் 2 கிலோ\n"
                "   • பயறு மாவு (கடலை அல்லது உளுந்து மாவு) 2 கிலோ\n"
                "   • வரப்பு மண் ஒரு கைப்பிடி\n"
                "2. **தயாரிக்கும் முறை:** 200 லிட்டர் நீரில் இவற்றை கலந்து மரக்குச்சியால் கடிகார சுற்றில் தினமும் 2 முறை கலக்கி 48 மணி நேரம் நிழலில் நொதிக்க வைக்கவும்.\n"
                "3. **பயன்பாடு:** ஏக்கருக்கு 200 லிட்டர் ஜீவாமிர்தத்தை பாசன நீருடன் கலந்து 15-20 நாட்களுக்கு ஒருமுறை பாய்ச்சவும்.\n"
                "4. **பஞ்சகாவ்யா:** வளர்ச்சி ஊக்கியாக 3% பஞ்சகாவ்யா கரைசலை பயிர்களில் தெளிக்கவும்."
            )
        else:
            answer = (
                "🌿 **Jeevamrutha Preparation & Natural Farming (ICAR / NNF Guidelines):**\n\n"
                "1. **Core Ingredients (For 200 Liters / 1 Acre application):**\n"
                "   • Fresh Indigenous (Desi) Cow Dung: 10 kg\n"
                "   • Desi Cow Urine: 10 Liters\n"
                "   • Organic Jaggery: 2 kg\n"
                "   • Pulse Flour (Gram/Besan): 2 kg\n"
                "   • Virgin Forest / Bund Topsoil: 1 handful (microbial inoculant)\n"
                "2. **Preparation Protocol:** Dissolve completely in a 200-liter shaded drum. Stir clockwise with a wooden stick twice daily for 48 to 72 hours.\n"
                "3. **Application Mode:** Apply 200 L/acre with irrigation water every 15-21 days or drench along crop rows.\n"
                "4. **Panchagavya Foliar Booster:** Spray 3% Panchagavya (30ml/liter water) at vegetative, flowering, and pod/grain filling stages."
            )
        return {'answer': answer}

    # =========================================================================
    # 12. FARM EQUIPMENT & TECHNOLOGY
    # =========================================================================
    @classmethod
    def _handle_equipment_technology(cls, crop, variety, stage, problem, location, prompt, lang):
        if lang == 'kn':
            answer = (
                "🚜 **ಕೃಷಿ ಯಂತ್ರೋಪಕರಣಗಳು ಮತ್ತು ಆಧುನಿಕ ತಂತ್ರಜ್ಞಾನ (Agri-Mechanization):**\n\n"
                "1. **ಪವರ್ ವೀಡರ್ (ಕಳೆ ಕೀಳುವ ಯಂತ್ರ):** ಕೂಲಿ ಆಳುಗಳ ಕೊರತೆಯಿರುವಾಗ ಸಾಲು ಬೆಳೆಗಳಲ್ಲಿ (ಹತ್ತಿ, ಮೆಕ್ಕೆಜೋಳ, ಕಬ್ಬು) ಕಳೆ ತೆಗೆಯಲು ಪವರ್ ವೀಡರ್ ಶೇ. 70% ಖರ್ಚು ಉಳಿಸುತ್ತದೆ.\n"
                "2. **ಡ್ರೋನ್ ಸಿಂಪಡಣೆ:** ಕೃಷಿ ಡ್ರೋನ್ ಮೂಲಕ ಕೇವಲ 10-15 ನಿಮಿಷಗಳಲ್ಲಿ 1 ಎಕರೆಗೆ ಸಮನಾಗಿ ಕೀಟನಾಶಕ ಅಥವಾ ನ್ಯಾನೋ ಯೂರಿಯಾ ಸಿಂಪಡಿಸಬಹುದು (ನೀರಿನ ಉಳಿತಾಯ ಶೇ. 80%).\n"
                "3. **ಸೋಲಾರ್ ಪಂಪ್ (PM-KUSUM):** ವಿದ್ಯುತ್ ಅವಲಂಬನೆ ಇಲ್ಲದೆ ಕೃಷಿ ಪಂಪ್‌ಸೆಟ್‌ಗಳಿಗೆ ಶೇ. 60-70% ಸಬ್ಸಿಡಿಯೊಂದಿಗೆ ಸೋಲಾರ್ ಪಂಪ್ ಅಳವಡಿಸಬಹುದು.\n"
                "4. **ಬಾಡಿಗೆ ಆಧಾರದ ಸೇವೆ (CHCs):** ಕಸ್ಟಮ್ ಹೈರಿಂಗ್ ಕೇಂದ್ರಗಳ ಮೂಲಕ ದುಬಾರಿ ಟ್ರಾಕ್ಟರ್ ಮತ್ತು ಹಾರ್ವೆಸ್ಟರ್‌ಗಳನ್ನು ಗಂಟೆಯ ಬಾಡಿಗೆ ದರದಲ್ಲಿ ಪಡೆಯಿರಿ."
            )
        else:
            answer = (
                "🚜 **Farm Machinery & Modern Agri-Technology (ICAR-CIAE Bhopal):**\n\n"
                "1. **Power Weeders & Cultivators:** Mechanized weeding in wide-row crops (cotton, sugarcane, maize) slashes labor costs by 70% and aerates root zones.\n"
                "2. **Agri-Drones:** Spray 1 acre in 10-15 minutes using precision ultra-low volume (ULV) nozzles, saving 80% water and ensuring uniform canopy penetration.\n"
                "3. **Solar Pumps (PM-KUSUM):** Off-grid solar pumps with 60% government subsidy eliminate diesel costs and daytime grid unreliability.\n"
                "4. **Custom Hiring Centers (CHCs):** Access combine harvesters, laser land levellers, and rotavators on nominal hourly rentals without capital debt."
            )
        return {'answer': answer}

    # =========================================================================
    # 13. CROP YIELD & PROFIT CALCULATIONS
    # =========================================================================
    @classmethod
    def _handle_yield_profit(cls, crop, variety, stage, problem, location, prompt, lang):
        crop_name = cls.get_crop_display(crop, lang)

        if lang == 'kn':
            answer = (
                f"📊 **{crop_name} ಇಳುವರಿ ಮತ್ತು ಲಾಭದ ಲೆಕ್ಕಾಚಾರ (Economics & Cost of Cultivation):**\n\n"
                f"1. **ಇಳುವರಿ ಮಾನದಂಡ (ಪ್ರತಿ ಎಕರೆಗೆ):**\n"
                f"   • ಭತ್ತ: 22 ರಿಂದ 28 ಕ್ವಿಂಟಾಲ್/ಎಕರೆ\n"
                f"   • ರಾಗಿ: 12 ರಿಂದ 16 ಕ್ವಿಂಟಾಲ್/ಎಕರೆ\n"
                f"   • ಹತ್ತಿ: 8 ರಿಂದ 12 ಕ್ವಿಂಟಾಲ್/ಎಕರೆ\n"
                f"2. **ಬೇಸಾಯ ವೆಚ್ಚ (Cost of Cultivation):** ಬೀಜ, ಉಳುಮೆ, ರಸಗೊಬ್ಬರ, ಕೀಟನಾಶಕ ಮತ್ತು ಕಟಾವು ಸೇರಿ ಎಕರೆಗೆ ಅಂದಾಜು ₹18,000 - ₹25,000.\n"
                f"3. **ನಿವ್ವಳ ಲಾಭ ಸೂತ್ರ:**\n"
                f"   `ನಿವ್ವಳ ಲಾಭ = (ಒಟ್ಟು ಇಳುವರಿ × ಮಂಡಿ ಬೆಲೆ) - ಬೇಸಾಯ ವೆಚ್ಚ`\n"
                f"4. **ಲಾಭ ಹೆಚ್ಚಿಸುವ ತಂತ್ರ:** ಸ್ಥಳೀಯ ದಲ್ಲಾಳಿಗಳಿಗೆ ಮಾರುವ ಬದಲು ನಮ್ಮ 'ಉಳವರ್ AI ಮಾರುಕಟ್ಟೆ' ಮೂಲಕ ನೇರವಾಗಿ ಮಾರಾಟ ಮಾಡಿ 15-25% ಹೆಚ್ಚಿನ ದರ ಪಡೆಯಿರಿ."
            )
        else:
            answer = (
                f"📊 **Yield Benchmarks & Profit Calculations for {crop_name} (Agro-Economic Research):**\n\n"
                f"1. **Standard Yield Benchmarks (Per Acre under good management):**\n"
                f"   • Paddy: 22 - 28 Quintals/acre\n"
                f"   • Finger Millet (Ragi): 12 - 16 Quintals/acre\n"
                f"   • Cotton: 8 - 12 Quintals/acre\n"
                f"   • Wheat: 18 - 22 Quintals/acre\n"
                f"2. **Cost of Cultivation:** Input costs (seeds, ploughing, fertilizers, labor, harvesting) range between ₹18,000 and ₹26,000 per acre.\n"
                f"3. **Net Profit Formula:**\n"
                f"   $$\\text{{Net Profit}} = (\\text{{Yield in Quintals}} \\times \\text{{Mandi Rate}}) - \\text{{Total Production Cost}}$$\n"
                f"4. **Direct Marketplace Advantage:** Eliminating local middleman brokerage through Uzhavar AI buyer contracts secures an additional ₹200-₹400/quintal."
            )
        return {'answer': answer}

    # =========================================================================
    # 14. GENERAL AGRICULTURE
    # =========================================================================
    @classmethod
    def _handle_general_agriculture(cls, crop, variety, stage, problem, location, prompt, lang):
        """
        Context-aware general handler.
        If we have a crop in context, provide crop-specific guidance instead of a fully generic message.
        """
        crop_name = cls.get_crop_display(crop, lang) if crop else None

        if crop and lang == 'kn':
            answer = (
                f"🌾 **{crop_name} ಕೃಷಿ ಮಾಹಿತಿ (ICAR / KVK ಆಧಾರಿತ):**\n\n"
                f"ನೀವು **{crop_name}** ಬಗ್ಗೆ ಕೇಳುತ್ತಿದ್ದೀರಿ. ನಾನು ನಿಮಗೆ ಸಹಾಯ ಮಾಡಬಹುದು! ದಯವಿಟ್ಟು ನಿಮ್ಮ ನಿರ್ದಿಷ್ಟ ಪ್ರಶ್ನೆಯನ್ನು ತಿಳಿಸಿ:\n\n"
                f"• 🌱 **ಬೇಸಾಯ ವಿಧಾನ** – ಹೇಗೆ ಬೆಳೆಯುವುದು?\n"
                f"• 🧪 **ಗೊಬ್ಬರ ಮಾಹಿತಿ** – ಎಂತಹ ರಸಗೊಬ್ಬರ ಹಾಕಬೇಕು?\n"
                f"• 💧 **ನೀರಾವರಿ** – ಎಷ್ಟು ನೀರು ಬೇಕು?\n"
                f"• 🔬 **ರೋಗ ನಿರ್ವಹಣೆ** – ಯಾವ ರೋಗ ಬರುತ್ತದೆ, ಏನು ಮಾಡಬೇಕು?\n"
                f"• 🐛 **ಕೀಟ ನಿಯಂತ್ರಣ** – ಯಾವ ಕೀಟನಾಶಕ ಬಳಸಬೇಕು?\n"
                f"• 💰 **ಮಂಡಿ ಬೆಲೆ** – ಇಂದಿನ ಮಾರುಕಟ್ಟೆ ದರ ಎಷ್ಟು?\n\n"
                f"ನಿಮ್ಮ ಜಿಲ್ಲೆ ಮತ್ತು ಮಣ್ಣಿನ ವಿಧ ತಿಳಿಸಿದರೆ ಇನ್ನಷ್ಟು ನಿಖರ ಸಲಹೆ ನೀಡಬಹುದು."
            )
        elif crop and lang == 'ta':
            answer = (
                f"🌾 **{crop_name} பயிர் வழிகாட்டுதல் (ICAR / KVK):**\n\n"
                f"**{crop_name}** பற்றி மேலும் உதவ தயாராக இருக்கிறேன். உங்கள் கேள்வியை தெளிவுபடுத்தவும்:\n\n"
                f"• 🌱 சாகுபடி முறை • 🧪 உர மேலாண்மை • 💧 நீர்ப்பாசனம்\n"
                f"• 🔬 நோய் மேலாண்மை • 🐛 பூச்சி கட்டுப்பாடு • 💰 சந்தை விலை\n\n"
                f"உங்கள் மாவட்டம் மற்றும் மண் வகை தெரிவித்தால் துல்லியமான ஆலோசனை வழங்கலாம்."
            )
        elif crop and lang == 'hi':
            answer = (
                f"🌾 **{crop_name} कृषि मार्गदर्शन (ICAR / KVK):**\n\n"
                f"**{crop_name}** के बारे में मैं आपकी सहायता के लिए तैयार हूं। कृपया अपना विशिष्ट प्रश्न बताएं:\n\n"
                f"• 🌱 खेती की विधि • 🧪 उर्वरक प्रबंधन • 💧 सिंचाई\n"
                f"• 🔬 रोग प्रबंधन • 🐛 कीट नियंत्रण • 💰 मंडी भाव\n\n"
                f"अपना जिला और मिट्टी का प्रकार बताएं तो और सटीक जानकारी दे सकते हैं।"
            )
        elif crop:
            answer = (
                f"🌾 **{crop_name} Agricultural Guidance (ICAR / KVK):**\n\n"
                f"I can help you with **{crop_name}** farming. Please specify your question:\n\n"
                f"• 🌱 Cultivation method • 🧪 Fertilizer management • 💧 Irrigation\n"
                f"• 🔬 Disease management • 🐛 Pest control • 💰 Mandi prices\n\n"
                f"Share your district and soil type for more precise recommendations."
            )
        elif lang == 'kn':
            answer = (
                "🌾 **ಉಳವರ್ AI ಕೃಷಿ ಮಾರ್ಗದರ್ಶನ:**\n\n"
                "ನಾನು ನಿಮ್ಮ ಕೃಷಿ ಸಹಾಯಕ. ನಿಮ್ಮ ಬೆಳೆ, ಸಮಸ್ಯೆ ಅಥವಾ ಪ್ರಶ್ನೆಯನ್ನು ನಿರ್ದಿಷ್ಟವಾಗಿ ತಿಳಿಸಿ. ಉದಾಹರಣೆಗೆ:\n\n"
                "• 'ಭತ್ತ ಬೆಳೆಯುವ ವಿಧಾನ ಹೇಳಿ'\n"
                "• 'ರಾಗಿಗೆ ಯಾವ ಗೊಬ್ಬರ ಹಾಕಬೇಕು?'\n"
                "• 'ಭತ್ತದ ಎಲೆ ಹಳದಿಯಾಗುತ್ತಿದೆ, ಏನು ಮಾಡಬೇಕು?'\n"
                "• 'ತಂಜಾವೂರಿನಲ್ಲಿ ಭತ್ತದ ಬೆಲೆ ಎಷ್ಟು?'\n\n"
                "• **ಲೈವ್ ಮಂಡಿ ಬೆಲೆಗಳು:** ಲೈವ್ ಮಂಡಿ ಬೆಲೆಗಳು ಟ್ಯಾಬ್ ನೋಡಿ.\n"
                "• **ನೇರ ಬೆಳೆ ಮಾರುಕಟ್ಟೆ:** ಕಮಿಷನ್ ಇಲ್ಲದೆ ನೇರ ಮಾರಾಟ ಮಾಡಿ.\n"
                "• **ಕಿಸಾನ್ ಕಾಲ್ ಸೆಂಟರ್:** ಉಚಿತ ಸಹಾಯಕ್ಕೆ 1800-180-1551 ಕರೆ ಮಾಡಿ."
            )
        else:
            answer = (
                "🌾 **Uzhavar AI Agricultural Assistant:**\n\n"
                "I can help with any farming question. Please mention your crop and specific question. Examples:\n\n"
                "• 'How to grow paddy?'\n"
                "• 'What fertilizer for ragi?'\n"
                "• 'Paddy leaf yellowing — what to do?'\n"
                "• 'Paddy price in Thanjavur today?'\n\n"
                "• **Live Mandi Prices:** Check official daily APMC rates on our Mandi Prices tab.\n"
                "• **Crop Marketplace:** Sell directly to bulk buyers without middlemen.\n"
                "• **Kisan Call Center:** Dial 1800-180-1551 for free agronomist help."
            )
        return {'answer': answer}

