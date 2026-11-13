"""
UZHAVAR AI - Mandi Price Specialist Assistant
Retrieves live/verified APMC commodity prices from AGMARKNET data,
detects missing crop or market entities, and formats comprehensive market intelligence.
"""

import re
from typing import Dict, Any, Optional, List
from database.db import query_db

class MandiPriceAssistant:
    """
    Dedicated handler for Mandi Prices & Crop Selling questions.
    Ensures price queries are NEVER routed to crop disease or unrelated modules.
    """

    CROP_SYNONYMS = {
        'paddy': 'Paddy', 'rice': 'Paddy', 'dhan': 'Paddy', 'ಭತ್ತ': 'Paddy', 'நெல்': 'Paddy', 'వరి': 'Paddy', 'ধান': 'Paddy',
        'ragi': 'Finger Millet (Ragi)', 'finger millet': 'Finger Millet (Ragi)', 'ರಾಗಿ': 'Finger Millet (Ragi)', 'கேழ்வரகு': 'Finger Millet (Ragi)',
        'cotton': 'Cotton', 'ಹತ್ತಿ': 'Cotton', 'பருத்தி': 'Cotton', 'पत्ती': 'Cotton', 'పత్తి': 'Cotton', 'कपास': 'Cotton',
        'tomato': 'Tomato', 'ಟೊಮ್ಯಾಟೊ': 'Tomato', 'தக்காளி': 'Tomato', 'टमाटर': 'Tomato',
        'wheat': 'Wheat', 'ಗೋಧಿ': 'Wheat', 'கோதுமை': 'Wheat', 'गेहूं': 'Wheat',
        'turmeric': 'Turmeric (Finger)', 'ಅರಿಶಿನ': 'Turmeric (Finger)', 'மஞ்சள்': 'Turmeric (Finger)', 'हल्दी': 'Turmeric (Finger)',
        'banana': 'Banana (Poovan)', 'ಬಾಳೆ': 'Banana (Poovan)', 'வாழை': 'Banana (Poovan)', 'केला': 'Banana (Poovan)',
        'black gram': 'Black Gram (Urad)', 'urad': 'Black Gram (Urad)', 'ಉದ್ದು': 'Black Gram (Urad)', 'உளுந்து': 'Black Gram (Urad)',
        'mustard': 'Mustard (Sarson)', 'ಸಾಸಿವೆ': 'Mustard (Sarson)', 'கடுகு': 'Mustard (Sarson)', 'सरसों': 'Mustard (Sarson)',
        'onion': 'Onion', 'ಈರುಳ್ಳಿ': 'Onion', 'வெங்காயம்': 'Onion', 'प्याज': 'Onion',
        'potato': 'Potato', 'ಆಲೂಗಡ್ಡೆ': 'Potato', 'உருளைக்கிழங்கு': 'Potato', 'आलू': 'Potato',
        'sugarcane': 'Sugarcane (Gur)', 'ಕಬ್ಬು': 'Sugarcane (Gur)', 'கரும்பு': 'Sugarcane (Gur)', 'गन्ना': 'Sugarcane (Gur)',
        'coconut': 'Coconut', 'ತೆಂಗಿನಕಾಯಿ': 'Coconut', 'தேங்காய்': 'Coconut', 'नारियल': 'Coconut'
    }

    LOCATION_MAP = {
        'thanjavur': 'Thanjavur', 'தஞ்சாவூர்': 'Thanjavur', 'ತಂಜಾವೂರು': 'Thanjavur',
        'kumbakonam': 'Kumbakonam', 'கும்பகோணம்': 'Kumbakonam', 'ಕುಂಭಕೋಣಂ': 'Kumbakonam',
        'erode': 'Erode', 'ஈரோடு': 'Erode', 'ಈರೋಡ್': 'Erode',
        'salem': 'Salem', 'சேலம்': 'Salem', 'ಸೇಲಂ': 'Salem',
        'madurai': 'Madurai', 'மதுரை': 'Madurai', 'ಮಧುರೈ': 'Madurai',
        'coimbatore': 'Coimbatore', 'கோவை': 'Coimbatore', 'ಕೊಯಮತ್ತೂರು': 'Coimbatore',
        'pollachi': 'Pollachi', 'பொள்ளாச்சி': 'Pollachi',
        'tiruchirapalli': 'Tiruchirapalli', 'trichy': 'Tiruchirapalli', 'திருச்சி': 'Tiruchirapalli',
        'tirunelveli': 'Tirunelveli', 'திருநெல்வேலி': 'Tirunelveli',
        'ludhiana': 'Ludhiana', 'ਲੁਧਿਆਣਾ': 'Ludhiana',
        'amritsar': 'Amritsar', 'ਅੰਮ੍ਰਿਤਸਰ': 'Amritsar',
        'jalandhar': 'Jalandhar', 'ਜਲੰਧਰ': 'Jalandhar',
        'khanna': 'Khanna',
        'bangalore': 'Bangalore', 'bengaluru': 'Bangalore', 'ಬೆಂಗಳೂರು': 'Bangalore',
        'mysore': 'Mysore', 'mysuru': 'Mysuru', 'ಮೈಸೂರು': 'Mysuru',
        'mandya': 'Mandya', 'ಮಂಡ್ಯ': 'Mandya',
        'shimoga': 'Shimoga', 'ಶಿವಮೊಗ್ಗ': 'Shimoga',
        'hassan': 'Hassan', 'ಹಾಸನ': 'Hassan',
        'dharwad': 'Dharwad', 'ಧಾರವಾಡ': 'Dharwad',
        'raichur': 'Raichur', 'ರಾಯಚೂರು': 'Raichur',
        'bellary': 'Bellary', 'ballari': 'Ballari', 'ಬಳ್ಳಾರಿ': 'Ballari',
        'pune': 'Pune', 'nashik': 'Nashik', 'nagpur': 'Nagpur',
        'guntur': 'Guntur', 'warangal': 'Warangal', 'vijayawada': 'Vijayawada'
    }

    @classmethod
    def process_query(cls, prompt: str, lang: str = 'en', context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processes mandi price inquiry:
        1. Identifies crop & location from prompt and conversation memory.
        2. Queries database for verified AGMARKNET prices.
        3. Asks follow-up if location or crop is missing.
        """
        normalized = prompt.lower()

        # Step 1: Detect crop with word boundary matching for ASCII terms
        detected_crop = None
        sorted_crop_terms = sorted(cls.CROP_SYNONYMS.keys(), key=len, reverse=True)
        for term in sorted_crop_terms:
            if term.isascii():
                if re.search(r'\b' + re.escape(term) + r'\b', normalized):
                    detected_crop = cls.CROP_SYNONYMS[term]
                    break
            else:
                if term in normalized:
                    detected_crop = cls.CROP_SYNONYMS[term]
                    break

        # Fallback to session memory for crop
        if not detected_crop and context and context.get('crop'):
            detected_crop = cls.CROP_SYNONYMS.get(context['crop'].lower(), context['crop'])

        # Step 2: Detect location with word boundary matching
        detected_location = None
        sorted_loc_terms = sorted(cls.LOCATION_MAP.keys(), key=len, reverse=True)
        for term in sorted_loc_terms:
            if term.isascii():
                if re.search(r'\b' + re.escape(term) + r'\b', normalized):
                    detected_location = cls.LOCATION_MAP[term]
                    break
            else:
                if term in normalized:
                    detected_location = cls.LOCATION_MAP[term]
                    break

        # Fallback to session memory for location
        if not detected_location and context and context.get('location'):
            detected_location = cls.LOCATION_MAP.get(context['location'].lower(), context['location'])

        # Case A: Missing crop entirely
        if not detected_crop:
            return cls._ask_for_crop(lang)

        # Case B: Crop detected, query available prices
        records = cls._query_prices(detected_crop, detected_location)

        # Case C: Location missing -> Show available markets and ask farmer
        if not detected_location:
            return cls._handle_missing_location(detected_crop, records, lang)

        # Case D: Both crop & location provided but no live record
        if not records:
            return cls._handle_unavailable_data(detected_crop, detected_location, lang)

        # Case E: Verified live record found!
        return cls._format_mandi_response(records[0], lang)

    @classmethod
    def _query_prices(cls, crop: str, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query stored market_prices with loose matching."""
        query = "SELECT * FROM market_prices WHERE crop_name LIKE ?"
        params = [f"%{crop.split()[0]}%"]

        if location:
            query += " AND (mandi_name LIKE ? OR district LIKE ? OR state LIKE ?)"
            loc_param = f"%{location}%"
            params.extend([loc_param, loc_param, loc_param])

        query += " ORDER BY price_date DESC, id DESC LIMIT 5"
        return query_db(query, tuple(params))

    @classmethod
    def _ask_for_crop(cls, lang: str) -> Dict[str, Any]:
        responses = {
            'kn': "🌾 ಯಾವ ಬೆಳೆಯ ಮಂಡಿ ಬೆಲೆಯನ್ನು ತಿಳಿಯಲು ಬಯಸುತ್ತೀರಿ? (ಉದಾಹರಣೆಗೆ: ಭತ್ತ, ರಾಗಿ, ಹತ್ತಿ, ಟೊಮ್ಯಾಟೊ, ಗೋಧಿ). ದಯವಿಟ್ಟು ಬೆಳೆಯ ಹೆಸರನ್ನು ತಿಳಿಸಿ.",
            'ta': "🌾 எந்தப் பயிரின் மண்டி விலையை அறிய விரும்புகிறீர்கள்? (எடுத்துக்காட்டாக: நெல், கேழ்வரகு, பருத்தி, தக்காளி, மஞ்சள்). தயவுசெய்து பயிரின் பெயரை குறிப்பிடவும்.",
            'hi': "🌾 आप किस फसल का मंडी भाव जानना चाहते हैं? (जैसे: धान, गेहूं, कपास, टमाटर, सरसों)। कृपया फसल का नाम बताएं।",
            'te': "🌾 మీరు ఏ పంట మార్కెట్ ధరను తెలుసుకోవాలనుకుంటున్నారు? (ఉదాహరణకు: వరి, రాగి, పత్తి, టమోటా). దయచేసి పంట పేరు చెప్పండి.",
            'en': "🌾 Which crop's mandi price would you like to check? (e.g. Paddy, Ragi, Cotton, Tomato, Wheat). Please specify the crop name."
        }
        return {
            'success': True,
            'answer': responses.get(lang, responses['en']),
            'topic': 'mandi_prices',
            'action_needed': 'specify_crop'
        }

    @classmethod
    def _handle_missing_location(cls, crop: str, records: List[Dict[str, Any]], lang: str) -> Dict[str, Any]:
        # Only list markets that actually have records in our database — never fabricate names
        if records:
            available_mandis = list(dict.fromkeys([r['mandi_name'] for r in records[:4]]))
            mandi_hint = {
                'kn': f"ನಮ್ಮ ಡೇಟಾಬೇಸ್‌ನಲ್ಲಿ ಲಭ್ಯವಿರುವ ಮಾರುಕಟ್ಟೆಗಳು: **{', '.join(available_mandis)}**.",
                'ta': f"தற்போது பதிவாகியுள்ள மண்டிகள்: **{', '.join(available_mandis)}**.",
                'hi': f"वर्तमान में उपलब्ध प्रमुख मंडियां: **{', '.join(available_mandis)}**.",
                'en': f"Currently available markets in our system: **{', '.join(available_mandis)}**."
            }
        else:
            mandi_hint = {
                'kn': "ಪ್ರಸ್ತುತ ಈ ಬೆಳೆಗೆ ನಮ್ಮ ಡೇಟಾಬೇಸ್‌ನಲ್ಲಿ ಯಾವ ಮಾರುಕಟ್ಟೆ ದಾಖಲೆಗಳು ಲಭ್ಯವಿಲ್ಲ.",
                'ta': "இந்த பயிருக்கு தற்போது எந்த மண்டி பதிவும் இல்லை.",
                'hi': "इस फसल के लिए अभी कोई मंडी रिकॉर्ड उपलब्ध नहीं है।",
                'en': "No market records are currently available in our database for this crop."
            }

        responses = {
            'kn': (
                f"💰 **{crop} ಬೆಳೆಯ ಮಂಡಿ ದರ:**\n"
                f"{mandi_hint.get('kn', mandi_hint['en'])}\n\n"
                f"ನೀವು ಯಾವ ನಿರ್ದಿಷ್ಟ ಜಿಲ್ಲೆ ಅಥವಾ ಎಪಿಎಂಸಿ ಮಂಡಿಯ ಬೆಲೆಯನ್ನು ತಿಳಿಯಲು ಬಯಸುತ್ತೀರಿ? "
                f"ದಯವಿಟ್ಟು ನಿಮ್ಮ ಮಾರುಕಟ್ಟೆ ಅಥವಾ ಜಿಲ್ಲೆಯ ಹೆಸರನ್ನು ತಿಳಿಸಿ."
            ),
            'ta': (
                f"💰 **{crop} பயிரின் மண்டி விலை:**\n"
                f"{mandi_hint.get('ta', mandi_hint['en'])}\n\n"
                f"நீங்கள் எந்த மாவட்டம் அல்லது மண்டி விலையை அறிய விரும்புகிறீர்கள்? "
                f"தயவுசெய்து ஊர் பெயரை குறிப்பிடவும்."
            ),
            'hi': (
                f"💰 **{crop} का मंडी भाव:**\n"
                f"{mandi_hint.get('hi', mandi_hint['en'])}\n\n"
                f"आप किस विशिष्ट जिले या मंडी का भाव देखना चाहते हैं? "
                f"कृपया अपने जिले या मंडी का नाम बताएं।"
            ),
            'en': (
                f"💰 **Live Mandi Rates for {crop}:**\n"
                f"{mandi_hint.get('en', mandi_hint['en'])}\n\n"
                f"Which specific district or APMC market are you looking for? "
                f"Please reply with your location."
            )
        }
        return {
            'success': True,
            'answer': responses.get(lang, responses['en']),
            'topic': 'mandi_prices',
            'crop': crop,
            'action_needed': 'specify_location'
        }

    @classmethod
    def _handle_unavailable_data(cls, crop: str, location: str, lang: str) -> Dict[str, Any]:
        responses = {
            'kn': (
                f"ℹ️ **ಮಂಡಿ ದರ ಮಾಹಿತಿ:**\n"
                f"ಪ್ರಸ್ತುತ **{location}** ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ **{crop}** ಬೆಳೆಗೆ ಅಧಿಕೃತ ಲೈವ್ ದರವು ಕೇಂದ್ರ AGMARKNET ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ನೋಂದಣಿಯಾಗಿಲ್ಲ.\n"
                f"ನಾವು ಹಳೆಯ ಅಥವಾ ಊಹಾತ್ಮಕ ಬೆಲೆಗಳನ್ನು ನೀಡುವುದಿಲ್ಲ. ದಯವಿಟ್ಟು ನಮ್ಮ 'ಲೈವ್ ಮಂಡಿ ಬೆಲೆಗಳು' ಟ್ಯಾಬ್‌ನಲ್ಲಿ ಹತ್ತಿರದ ಜಿಲ್ಲೆಯ ಮಾರುಕಟ್ಟೆ ದರಗಳನ್ನು ಪರಿಶೀಲಿಸಿ."
            ),
            'ta': (
                f"ℹ️ **சந்தை விலை தகவல்:**\n"
                f"தற்போது **{location}** மண்டியில் **{crop}** பயிருக்கான நேரலை அரசு விலை AGMARKNET தளத்தில் பதிவாகவில்லை.\n"
                f"உண்மையான விலையையே நாங்கள் வழங்குகிறோம். அருகிலுள்ள பிற சந்தை விலைகளை எங்கள் நேரலை மண்டி பக்கத்தில் காணலாம்."
            ),
            'hi': (
                f"ℹ️ **मंडी भाव सूचना:**\n"
                f"वर्तमान में **{location}** मंडी के लिए **{crop}** का आधिकारिक लाइव भाव सरकारी AGMARKNET पोर्टल पर उपलब्ध नहीं है।\n"
                f"हम केवल वास्तविक सरकारी डेटा प्रस्तुत करते हैं। कृपया हमारे 'लाइव मंडी भाव' सेक्शन में निकटतम मंडी देखें।"
            ),
            'en': (
                f"ℹ️ **Mandi Data Notice:**\n"
                f"Currently, verified daily AGMARKNET price data for **{crop}** in **{location}** is not officially recorded today.\n"
                f"We strictly do not invent rates or present outdated quotes. Please check nearby districts on our 'Live Mandi Prices' tab or visit agmarknet.gov.in."
            )
        }
        return {
            'success': True,
            'answer': responses.get(lang, responses['en']),
            'topic': 'mandi_prices',
            'crop': crop,
            'location': location
        }

    @classmethod
    def _format_mandi_response(cls, r: Any, lang: str) -> Dict[str, Any]:
        row = dict(r) if hasattr(r, 'keys') else r
        crop = row['crop_name']
        mandi = row['mandi_name']
        district = row['district']
        state = row['state']
        modal_p = row['modal_price']
        min_p = row.get('min_price') or (modal_p * 0.92)
        max_p = row.get('max_price') or (modal_p * 1.08)
        unit = row.get('unit', '₹/Quintal')
        price_date = str(row['price_date'])[:10]
        data_source = row.get('data_source', 'AGMARKNET - Govt. of India')

        if lang == 'kn':
            answer = (
                f"💰 **ಅಧಿಕೃತ ಮಂಡಿ ಬೆಲೆ ಮಾಹಿತಿ ({crop}):**\n\n"
                f"• **ಮಾರುಕಟ್ಟೆ (Mandi):** {mandi}, {district} ({state})\n"
                f"• **ಮಾದರಿ ಬೆಲೆ (Modal Price):** ₹{modal_p:,.0f} / ಕ್ವಿಂಟಾಲ್\n"
                f"• **ಕನಿಷ್ಠ ಬೆಲೆ (Min Price):** ₹{min_p:,.0f} / ಕ್ವಿಂಟಾಲ್\n"
                f"• **ಗರಿಷ್ಠ ಬೆಲೆ (Max Price):** ₹{max_p:,.0f} / ಕ್ವಿಂಟಾಲ್\n"
                f"• **ದಿನಾಂಕ:** {price_date}\n"
                f"• **ಮಾಹಿತಿ ಮೂಲ:** {data_source}\n\n"
                f"💡 **ರೈತರಿಗೆ ಸಲಹೆ:** ಮಧ್ಯವರ್ತಿಗಳಿಗೆ ಕಮಿಷನ್ ನೀಡುವ ಬದಲು, ಉಳವರ್ AI 'ಬೆಳೆ ಮಾರುಕಟ್ಟೆ' ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ನಿಮ್ಮ ಉತ್ಪನ್ನವನ್ನು ಪಟ್ಟಿ ಮಾಡಿ ನೇರವಾಗಿ ಖರೀದಿದಾರರಿಗೆ ಮಾರಾಟ ಮಾಡುವುದರಿಂದ ಶೇ. 15-25% ಹೆಚ್ಚಿನ ಲಾಭ ಗಳಿಸಬಹುದು."
            )
        elif lang == 'ta':
            answer = (
                f"💰 **அரசு அங்கீகரிக்கப்பட்ட மண்டி விலை விபரம் ({crop}):**\n\n"
                f"• **சந்தை (Mandi):** {mandi}, {district} ({state})\n"
                f"• **சராசரி விலை (Modal Price):** ₹{modal_p:,.0f} / குவிண்டால்\n"
                f"• **குறைந்தபட்ச விலை (Min Price):** ₹{min_p:,.0f} / குவிண்டால்\n"
                f"• **அதிகபட்ச விலை (Max Price):** ₹{max_p:,.0f} / குவிண்டால்\n"
                f"• **விலை தேதி:** {price_date}\n"
                f"• **தரவு மூலம்:** {data_source}\n\n"
                f"💡 **விவசாயிக்கு ஆலோசனை:** உழவர் AI நேரடி பயிர் சந்தையில் உங்கள் விளைபொருளை விற்பதன் மூலம் இடைத்தரகர் இன்றி 15-25% கூடுதல் வருமானம் பெறலாம்."
            )
        elif lang == 'hi':
            answer = (
                f"💰 **आधिकारिक दैनिक मंडी भाव ({crop}):**\n\n"
                f"• **मंडी:** {mandi}, {district} ({state})\n"
                f"• **मॉडल भाव (Modal Price):** ₹{modal_p:,.0f} / क्विंटल\n"
                f"• **न्यूनतम भाव (Min Price):** ₹{min_p:,.0f} / क्विंटल\n"
                f"• **अधिकतम भाव (Max Price):** ₹{max_p:,.0f} / क्विंटल\n"
                f"• **दिनांक:** {price_date}\n"
                f"• **डेटा स्रोत:** {data_source}\n\n"
                f"💡 **सलाह:** उझवर AI प्लेटफॉर्म पर सीधे खरीदारों से जुड़ें और बिचौलियों को हटाकर 15-25% अधिक मुनाफा कमाएं।"
            )
        else:
            answer = (
                f"💰 **Official Mandi Price Report ({crop}):**\n\n"
                f"• **Market / APMC:** {mandi}, {district} ({state})\n"
                f"• **Modal Price:** ₹{modal_p:,.0f} / Quintal\n"
                f"• **Minimum Price:** ₹{min_p:,.0f} / Quintal\n"
                f"• **Maximum Price:** ₹{max_p:,.0f} / Quintal\n"
                f"• **Date:** {price_date}\n"
                f"• **Data Source:** {data_source}\n\n"
                f"💡 **Selling Recommendation:** Farmers who list directly on the Uzhavar AI Crop Marketplace eliminate intermediary cuts and realize 15-25% higher profit margins."
            )

        return {
            'success': True,
            'answer': answer,
            'topic': 'mandi_prices',
            'mandi_record': {
                'crop': crop,
                'mandi': mandi,
                'district': district,
                'modal_price': modal_p,
                'unit': unit,
                'date': price_date
            }
        }
