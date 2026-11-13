"""
UZHAVAR AI - Multi-Turn Conversation Memory Manager
Tracks session context (crop, variety, problem, location, soil type, growth stage)
to enable coherent multi-turn agricultural consultations without cross-user leakage.
"""

import time
import re
from typing import Dict, Any, Optional

class ConversationMemoryManager:
    """
    Session-isolated in-memory context store with automatic entity tracking.
    """

    # In-memory store keyed by session_id: { session_id: { 'context': {...}, 'history': [...], 'last_active': ... } }
    _SESSIONS: Dict[str, Dict[str, Any]] = {}
    SESSION_TIMEOUT_SECONDS = 3600  # 1 hour

    KNOWN_CROPS = {
        'paddy': 'Paddy', 'rice': 'Paddy', 'dhan': 'Paddy', 'ಭತ್ತ': 'Paddy', 'ನೆಲ್': 'Paddy', 'వరి': 'Paddy', 'ধান': 'Paddy',
        'ragi': 'Ragi', 'finger millet': 'Ragi', 'ರಾಗಿ': 'Ragi', 'கேழ்வரகு': 'Ragi', 'रागी': 'Ragi', 'మల్లె': 'Ragi',
        'cotton': 'Cotton', 'ಹತ್ತಿ': 'Cotton', 'பருத்தி': 'Cotton', 'पत्ती': 'Cotton', 'పత్తి': 'Cotton', 'कपास': 'Cotton',
        'tomato': 'Tomato', 'ಟೊಮ್ಯಾಟೊ': 'Tomato', 'தக்காளி': 'Tomato', 'टमाटर': 'Tomato', 'టమోటా': 'Tomato',
        'sugarcane': 'Sugarcane', 'ಕಬ್ಬು': 'Sugarcane', 'கரும்பு': 'Sugarcane', 'गन्ना': 'Sugarcane', 'చెరకు': 'Sugarcane',
        'wheat': 'Wheat', 'ಗೋಧಿ': 'Wheat', 'கோதுமை': 'Wheat', 'गेहूं': 'Wheat', 'గోధుమ': 'Wheat',
        'maize': 'Maize', 'corn': 'Maize', 'ಮೆಕ್ಕೆಜೋಳ': 'Maize', 'மக்காச்சோளம்': 'Maize', 'मक्का': 'Maize',
        'turmeric': 'Turmeric', 'ಅರಿಶಿನ': 'Turmeric', 'மஞ்சள்': 'Turmeric', 'हल्दी': 'Turmeric', 'పసుపు': 'Turmeric',
        'banana': 'Banana', 'ಬಾಳೆ': 'Banana', 'வாழை': 'Banana', 'केला': 'Banana', 'అరటి': 'Banana',
        'groundnut': 'Groundnut', 'peanut': 'Groundnut', 'ಕಡಲೆಕಾಯಿ': 'Groundnut', 'வேர்க்கடலை': 'Groundnut', 'मूंगफली': 'Groundnut',
        'chilli': 'Chilli', 'pepper': 'Chilli', 'ಮೆಣಸಿನಕಾಯಿ': 'Chilli', 'மிளகாய்': 'Chilli', 'मिर्च': 'Chilli'
    }

    KNOWN_VARIETIES = [
        'co 51', 'co51', 'adt 37', 'adt 45', 'adt 43', 'bpt 5204', 'sona masuri', 'jaya', 'basmati 1121', 'ir 64',
        'gpu 28', 'ml 365', 'kmr 301', 'indaf 8', 'mr 1', 'mr 6',
        'bt cotton', 'dch 32', 'suraj', 'rch 2',
        'shivam', 'arka rakshak', 'vaishnavi', 'arka vikas',
        'co 86032', 'coc 671'
    ]

    KNOWN_LOCATIONS = {
        'thanjavur': 'Thanjavur', 'erode': 'Erode', 'salem': 'Salem', 'madurai': 'Madurai',
        'coimbatore': 'Coimbatore', 'tiruchirappalli': 'Tiruchirappalli', 'vellore': 'Vellore', 'tirunelveli': 'Tirunelveli',
        'bangalore': 'Bangalore', 'bengaluru': 'Bangalore', 'mandya': 'Mandya', 'mysuru': 'Mysuru', 'mysore': 'Mysuru',
        'shimoga': 'Shimoga', 'dharwad': 'Dharwad', 'belagavi': 'Belagavi', 'hassan': 'Hassan', 'ballari': 'Ballari',
        'raichur': 'Raichur', 'davanagere': 'Davanagere', 'tumakuru': 'Tumakuru', 'kolar': 'Kolar', 'udupi': 'Udupi',
        'ludhiana': 'Ludhiana', 'amritsar': 'Amritsar', 'jalandhar': 'Jalandhar', 'patiala': 'Patiala', 'khanna': 'Khanna',
        'pune': 'Pune', 'nashik': 'Nashik', 'nagpur': 'Nagpur', 'aurangabad': 'Aurangabad',
        'rajkot': 'Rajkot', 'ahmedabad': 'Ahmedabad', 'surat': 'Surat', 'mehsana': 'Mehsana',
        'guntur': 'Guntur', 'khammam': 'Khammam', 'warangal': 'Warangal', 'vijayawada': 'Vijayawada',
        # Kannada script districts & mandis
        'ಮಂಡ್ಯ': 'Mandya', 'ಮೈಸೂರು': 'Mysuru', 'ಹಾಸನ': 'Hassan', 'ಶಿವಮೊಗ್ಗ': 'Shimoga',
        'ಧಾರವಾಡ': 'Dharwad', 'ಬೆಳಗಾವಿ': 'Belagavi', 'ರಾಯಚೂರು': 'Raichur', 'ಬಳ್ಳಾರಿ': 'Ballari',
        'ದಾವಣಗೆರೆ': 'Davanagere', 'ತುಮಕೂರು': 'Tumakuru', 'ಕೋಲಾರ': 'Kolar', 'ಉಡುಪಿ': 'Udupi',
        'ಬೆಂಗಳೂರು': 'Bangalore', 'ತಂಜಾವೂರು': 'Thanjavur',
        # Tamil script districts & mandis
        'தஞ்சாவூர்': 'Thanjavur', 'ஈரோடு': 'Erode', 'சேலம்': 'Salem', 'மதுரை': 'Madurai',
        'கோயம்புத்தூர்': 'Coimbatore', 'கோவை': 'Coimbatore', 'திருச்சி': 'Tiruchirappalli'
    }

    KNOWN_SOILS = {
        'red soil': 'Red Soil', 'black soil': 'Black Soil', 'loamy soil': 'Loamy Soil',
        'clay soil': 'Clay Soil', 'sandy soil': 'Sandy Soil', 'alluvial': 'Alluvial Soil',
        'saline soil': 'Saline Soil', 'laterite': 'Laterite Soil',
        'ಕೆಂಪು ಮಣ್ಣು': 'Red Soil', 'ಕಪ್ಪು ಮಣ್ಣು': 'Black Soil', 'ಗೋಡು ಮಣ್ಣು': 'Loamy Soil',
        'ಜೇಡಿ ಮಣ್ಣು': 'Clay Soil', 'ಮರಳು ಮಣ್ಣು': 'Sandy Soil',
        'செம்மண்': 'Red Soil', 'கரிசல் மண்': 'Black Soil', 'வண்டல் மண்': 'Alluvial Soil',
        'लाल मिट्टी': 'Red Soil', 'काली मिट्टी': 'Black Soil', 'दोमट मिट्टी': 'Loamy Soil'
    }

    KNOWN_SEASONS = {
        'kharif': 'Kharif', 'rabi': 'Rabi', 'zaid': 'Zaid',
        'monsoon': 'Monsoon (Kharif)', 'winter': 'Winter (Rabi)', 'summer': 'Summer (Zaid)',
        'kuruvai': 'Kuruvai Season', 'samba': 'Samba Season', 'thaladi': 'Thaladi Season',
        'ಮುಂಗಾರು': 'Kharif', 'ಹಿಂಗಾರು': 'Rabi', 'ಬೇಸಿಗೆ': 'Summer',
        'குறுவை': 'Kuruvai', 'சம்பா': 'Samba', 'தாளடி': 'Thaladi',
        'खरीफ': 'Kharif', 'रबी': 'Rabi', 'जायद': 'Zaid'
    }

    KNOWN_CONDITIONS = {
        'organic': 'Organic Farming', 'natural farming': 'Natural Farming (SPNF/ZBNF)',
        'irrigated': 'Irrigated', 'rainfed': 'Rainfed (Dryland)', 'drip': 'Drip Irrigation',
        'sprinkler': 'Sprinkler Irrigation', 'greenhouse': 'Greenhouse/Polyhouse',
        'sri method': 'System of Rice Intensification (SRI)',
        'ಸಾವಯವ': 'Organic Farming', 'ನೀರಾವರಿ': 'Irrigated', 'ಮಳೆಯಾಶ್ರಿತ': 'Rainfed',
        'இயற்கை விவசாயம்': 'Organic Farming', 'பாசனம்': 'Irrigated', 'மானாவாரி': 'Rainfed',
        'சொட்டு நீர்': 'Drip Irrigation', 'தெளிப்பு நீர்': 'Sprinkler Irrigation',
        'जैविक खेती': 'Organic Farming', 'सिंचित': 'Irrigated', 'बारानी': 'Rainfed'
    }

    @classmethod
    def get_or_create_session(cls, session_id: str) -> Dict[str, Any]:
        """Retrieve existing session context or initialize a fresh isolated context."""
        cls._cleanup_expired_sessions()
        if not session_id or session_id not in cls._SESSIONS:
            cls._SESSIONS[session_id] = {
                'context': {
                    'crop': None,
                    'variety': None,
                    'problem': None,
                    'location': None,
                    'soil_type': None,
                    'season': None,
                    'farming_conditions': None,
                    'growth_stage': None,
                    'intent': None,           # Track last classified intent across turns
                    'previous_question': None # Track last user question
                },
                'history': [],
                'last_active': time.time()
            }
        else:
            cls._SESSIONS[session_id]['last_active'] = time.time()
        return cls._SESSIONS[session_id]

    @classmethod
    def update_context(cls, session_id: str, user_prompt: str, bot_response: Optional[str] = None,
                       intent: Optional[str] = None, skip_history: bool = False):
        """Extract entities from prompt and optionally record interaction in history.

        Args:
            session_id: Unique session identifier.
            user_prompt: The user's message text.
            bot_response: The bot's reply (optional).
            intent: The classified intent category (optional). When provided,
                    it is persisted so follow-up messages can inherit the intent.
            skip_history: When True, entities are extracted but no history entry is appended.
                          Use this for the early entity-extraction pass in ask_evon so that
                          history is recorded only once (after the bot reply is known).
        """
        session_data = cls.get_or_create_session(session_id)
        ctx = session_data['context']
        lower_prompt = user_prompt.lower()

        # Persist intent so follow-up short messages can inherit it
        if intent:
            ctx['intent'] = intent

        # 1. Crop extraction with word boundary matching
        sorted_crop_terms = sorted(cls.KNOWN_CROPS.keys(), key=len, reverse=True)
        for term in sorted_crop_terms:
            if term.isascii():
                if re.search(r'\b' + re.escape(term) + r'\b', lower_prompt):
                    ctx['crop'] = cls.KNOWN_CROPS[term]
                    break
            else:
                if term in lower_prompt:
                    ctx['crop'] = cls.KNOWN_CROPS[term]
                    break

        # 2. Variety extraction
        sorted_varieties = sorted(cls.KNOWN_VARIETIES, key=len, reverse=True)
        for v in sorted_varieties:
            if re.search(r'\b' + re.escape(v) + r'\b', lower_prompt):
                ctx['variety'] = v.upper()
                break

        # 3. Location / District / Market extraction
        sorted_locs = sorted(cls.KNOWN_LOCATIONS.keys(), key=len, reverse=True)
        for loc_term in sorted_locs:
            if loc_term.isascii():
                if re.search(r'\b' + re.escape(loc_term) + r'\b', lower_prompt):
                    ctx['location'] = cls.KNOWN_LOCATIONS[loc_term]
                    break
            else:
                if loc_term in lower_prompt:
                    ctx['location'] = cls.KNOWN_LOCATIONS[loc_term]
                    break

        # 4. Soil type extraction
        sorted_soils = sorted(cls.KNOWN_SOILS.keys(), key=len, reverse=True)
        for s_term in sorted_soils:
            if s_term.isascii():
                if re.search(r'\b' + re.escape(s_term) + r'\b', lower_prompt):
                    ctx['soil_type'] = cls.KNOWN_SOILS[s_term]
                    break
            else:
                if s_term in lower_prompt:
                    ctx['soil_type'] = cls.KNOWN_SOILS[s_term]
                    break

        # 4b. Season extraction
        sorted_seasons = sorted(cls.KNOWN_SEASONS.keys(), key=len, reverse=True)
        for sea_term in sorted_seasons:
            if sea_term.isascii():
                if re.search(r'\b' + re.escape(sea_term) + r'\b', lower_prompt):
                    ctx['season'] = cls.KNOWN_SEASONS[sea_term]
                    break
            else:
                if sea_term in lower_prompt:
                    ctx['season'] = cls.KNOWN_SEASONS[sea_term]
                    break

        # 4c. Farming conditions extraction (organic, irrigated, drip, rainfed)
        sorted_conds = sorted(cls.KNOWN_CONDITIONS.keys(), key=len, reverse=True)
        for c_term in sorted_conds:
            if c_term.isascii():
                if re.search(r'\b' + re.escape(c_term) + r'\b', lower_prompt):
                    ctx['farming_conditions'] = cls.KNOWN_CONDITIONS[c_term]
                    break
            else:
                if c_term in lower_prompt:
                    ctx['farming_conditions'] = cls.KNOWN_CONDITIONS[c_term]
                    break

        # 5. Growth stage extraction
        for stage in ['nursery', 'tillering', 'flowering', 'fruiting', 'harvest', 'sowing', 'seedling',
                      'ಸಸಿಮಡಿ', 'ನಾಟಿ', 'ತೆನೆ', 'ಹೂವಾಡುವ', 'ಕಟಾವು', 'ಬಿತ್ತನೆ']:
            if stage in lower_prompt:
                ctx['growth_stage'] = stage.capitalize()
                break

        # 6. Symptom / problem extraction
        problem_markers = ['yellow', 'brown spot', 'leaf curl', 'wilt', 'blast', 'rot', 'borer', 'hole', 'stunted', 'drying',
                           'ಹಳದಿ', 'ಬೆಂಕಿ ರೋಗ', 'ಕೊಳೆ', 'ಸುರುಟು', 'ಕಲೆ', 'ಎಲೆ ಹಳದಿ', 'ಮಂಜள்', 'புள்ளி', 'வாடல்', 'பிளாஸ்ட்', 'पीला', 'सड़न']
        for p in problem_markers:
            if p in lower_prompt:
                ctx['problem'] = p
                break

        # Save previous question
        ctx['previous_question'] = user_prompt

        # Record conversation turn (skip if caller will record it separately)
        if not skip_history:
            session_data['history'].append({
                'user': user_prompt,
                'bot': bot_response or '',
                'timestamp': time.time()
            })
            # Keep maximum 6 recent turns to conserve context window
            if len(session_data['history']) > 6:
                session_data['history'] = session_data['history'][-6:]

    @classmethod
    def get_context_summary(cls, session_id: str) -> str:
        """Returns readable summary of current active context for reasoning models."""
        session_data = cls.get_or_create_session(session_id)
        ctx = session_data['context']
        parts = []
        if ctx.get('crop'):
            parts.append(f"Crop: {ctx['crop']}")
        if ctx.get('variety'):
            parts.append(f"Variety: {ctx['variety']}")
        if ctx.get('location'):
            parts.append(f"District/Market: {ctx['location']}")
        if ctx.get('soil_type'):
            parts.append(f"Soil: {ctx['soil_type']}")
        if ctx.get('season'):
            parts.append(f"Season: {ctx['season']}")
        if ctx.get('farming_conditions'):
            parts.append(f"Conditions: {ctx['farming_conditions']}")
        if ctx.get('growth_stage'):
            parts.append(f"Stage: {ctx['growth_stage']}")
        if ctx.get('problem'):
            parts.append(f"Active Concern: {ctx['problem']}")
        if ctx.get('intent'):
            parts.append(f"Last Intent: {ctx['intent']}")
        return ", ".join(parts) if parts else "No prior context"

    @classmethod
    def clear_context(cls, session_id: str):
        """Explicitly clear the conversation context for this session."""
        if session_id in cls._SESSIONS:
            del cls._SESSIONS[session_id]

    @classmethod
    def _cleanup_expired_sessions(cls):
        """Evicts sessions inactive for over 1 hour to prevent memory leaks."""
        now = time.time()
        expired = [sid for sid, data in cls._SESSIONS.items() if now - data['last_active'] > cls.SESSION_TIMEOUT_SECONDS]
        for sid in expired:
            del cls._SESSIONS[sid]
