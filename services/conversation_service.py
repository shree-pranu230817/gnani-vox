"""
UZHAVAR AI – Kannada Voice Bridge
Permanent Conversation Management & Context Tracking Service
Backed by SQLite Database & SQLAlchemy ORM
"""

import time
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from models import db, Conversation, Message

logger = logging.getLogger("uzhavar.conversations")

class ConversationService:
    KNOWN_CROPS = {
        'paddy': 'Paddy', 'rice': 'Paddy', 'dhan': 'Paddy', 'ಭತ್ತ': 'Paddy', 'ನೆಲ್': 'Paddy', 'వరి': 'Paddy', 'ধান': 'Paddy',
        'ragi': 'Ragi', 'finger millet': 'Ragi', 'ರಾಗಿ': 'Ragi', 'கேழ்வரகு': 'Ragi', 'रागी': 'Ragi', 'మల్లె': 'Ragi',
        'cotton': 'Cotton', 'ಹತ್ತಿ': 'Cotton', 'பருத்தி': 'Cotton', 'पत्ती': 'Cotton', 'పత్తి': 'Cotton', 'कपास': 'Cotton',
        'tomato': 'Tomato', 'ಟೊಮ್ಯಾಟೊ': 'Tomato', 'தக்காளி': 'Tomato', 'टमाटर': 'Tomato', 'టమోటా': 'Tomato',
        'sugarcane': 'Sugarcane', 'ಕಬ್ಬು': 'Sugarcane', 'கரும்பு': 'Sugarcane', 'गन्ना': 'Sugarcane', 'చెరకు': 'Sugarcane',
        'groundnut': 'Groundnut', 'peanut': 'Groundnut', 'ಕಡಲೆಕಾಯಿ': 'Groundnut', 'வேர்க்கடலை': 'Groundnut', 'मूंगफली': 'Groundnut',
        'chilli': 'Chilli', 'pepper': 'Chilli', 'ಮೆಣಸಿನಕಾಯಿ': 'Chilli', 'மிளகாய்': 'Chilli', 'मिर्च': 'Chilli',
        'maize': 'Maize', 'corn': 'Maize', 'ಮೆಕ್ಕೆಜೋಳ': 'Maize', 'மக்காச்சೋளம்': 'Maize', 'मक्का': 'Maize',
        'wheat': 'Wheat', 'ಗೋಧಿ': 'Wheat', 'கோதுமை': 'Wheat', 'गेहूं': 'Wheat', 'గోధుమ': 'Wheat',
        'onion': 'Onion', 'ಈರುಳ್ಳಿ': 'Onion', 'வெங்காயம்': 'Onion', 'प्याज': 'Onion', 'ఉల్లిపాయ': 'Onion'
    }

    KNOWN_LOCATIONS = {
        'mandya': 'Mandya', 'ಮಂಡ್ಯ': 'Mandya', 'mysuru': 'Mysuru', 'mysore': 'Mysuru', 'ಮೈಸೂರು': 'Mysuru',
        'hassan': 'Hassan', 'ಹಾಸನ': 'Hassan', 'shimoga': 'Shimoga', 'ಶಿವಮೊಗ್ಗ': 'Shimoga',
        'dharwad': 'Dharwad', 'ಧಾರವಾಡ': 'Dharwad', 'belagavi': 'Belagavi', 'ಬೆಳಗಾವಿ': 'Belagavi',
        'ballari': 'Ballari', 'ಬಳ್ಳಾರಿ': 'Ballari', 'raichur': 'Raichur', 'ರಾಯಚೂರು': 'Raichur',
        'thanjavur': 'Thanjavur', 'தஞ்சாவூர்': 'Thanjavur', 'madurai': 'Madurai', 'மதுரை': 'Madurai',
        'coimbatore': 'Coimbatore', 'கோவை': 'Coimbatore', 'salem': 'Salem', 'சேலம்': 'Salem',
        'guntur': 'Guntur', 'వరంగల్': 'Warangal', 'warangal': 'Warangal', 'pune': 'Pune', 'nashik': 'Nashik'
    }

    KNOWN_SOILS = {
        'red soil': 'Red Soil', 'ಕೆಂಪು ಮಣ್ಣು': 'Red Soil', 'செம்மண்': 'Red Soil', 'लाल मिट्टी': 'Red Soil',
        'black soil': 'Black Soil', 'ಕಪ್ಪು ಮಣ್ಣು': 'Black Soil', 'கரிசல் மண்': 'Black Soil', 'काली मिट्टी': 'Black Soil',
        'clay soil': 'Clay Soil', 'ಜೇಡಿ ಮಣ್ಣು': 'Clay Soil', 'कछारी मिट्टी': 'Clay Soil',
        'sandy soil': 'Sandy Soil', 'ಮರಳು ಮಣ್ಣು': 'Sandy Soil', 'மணல் மண்': 'Sandy Soil',
        'loamy soil': 'Loamy Soil', 'ಗೋಡು ಮಣ್ಣು': 'Loamy Soil', 'வண்டல் மண்': 'Loamy Soil'
    }

    # In-memory translation session store for Service 1 & 2
    _TRANSLATION_SESSIONS: Dict[str, Dict[str, Any]] = {}

    # =========================================================================
    # 1. SQLITE CONVERSATION CRUD OPERATIONS
    # =========================================================================
    @classmethod
    def get_or_create_conversation(cls, conversation_id: Optional[str] = None, language: str = 'kn') -> Conversation:
        """
        Retrieves an existing conversation from SQLite by ID or creates a persistent new one.
        Guarantees that a valid Conversation model instance is always returned.
        """
        if conversation_id:
            conv = Conversation.query.filter_by(conversation_id=conversation_id).first()
            if conv:
                if language and conv.selected_language != language:
                    conv.selected_language = language
                    db.session.commit()
                return conv

        # Use provided conversation ID if given, or generate unique ID
        new_id = conversation_id if conversation_id else f"conv_{uuid.uuid4().hex[:12]}"
        default_title = "ಹೊಸ ಕೃಷಿ ಸಮಾಲೋಚನೆ" if language == 'kn' else "New Farming Consultation"
        conv = Conversation(
            conversation_id=new_id,
            conversation_title=default_title,
            selected_language=language or 'kn',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(conv)
        db.session.commit()
        logger.info(f"[DB] Created new conversation: {new_id} ({language})")
        return conv

    @classmethod
    def get_conversation(cls, conversation_id: str) -> Optional[Conversation]:
        """Fetch conversation by ID."""
        if not conversation_id:
            return None
        return Conversation.query.filter_by(conversation_id=conversation_id).first()

    @classmethod
    def list_conversations(cls) -> List[Dict[str, Any]]:
        """List all conversations ordered by latest activity."""
        convs = Conversation.query.order_by(Conversation.updated_at.desc()).all()
        return [c.to_dict(include_messages=False) for c in convs]

    @classmethod
    def get_conversation_details(cls, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Fetch conversation details with all messages in chronological order."""
        conv = cls.get_conversation(conversation_id)
        if not conv:
            return None
        return conv.to_dict(include_messages=True)

    @classmethod
    def delete_conversation(cls, conversation_id: str) -> bool:
        """Permanently deletes a conversation and all its messages."""
        conv = cls.get_conversation(conversation_id)
        if not conv:
            return False
        db.session.delete(conv)
        db.session.commit()
        logger.info(f"[DB] Deleted conversation: {conversation_id}")
        return True

    @classmethod
    def clear_conversation_messages(cls, conversation_id: str) -> bool:
        """Removes all messages from a conversation while preserving the conversation row."""
        conv = cls.get_conversation(conversation_id)
        if not conv:
            return False
        Message.query.filter_by(conversation_id=conversation_id).delete()
        conv.conversation_summary = None
        conv.updated_at = datetime.utcnow()
        db.session.commit()
        logger.info(f"[DB] Cleared messages for conversation: {conversation_id}")
        return True

    # =========================================================================
    # 2. SQLITE MESSAGE STORAGE & CHRONOLOGICAL HISTORY
    # =========================================================================
    @classmethod
    def add_message(
        cls,
        conversation_id: str,
        sender: str,
        message_text: str,
        original_language: str = 'kn',
        message_type: str = 'text',
        audio_reference: Optional[str] = None
    ) -> Message:
        """
        Appends a message to the conversation in SQLite.
        Updates conversation timestamps and auto-titles the conversation on first user question.
        """
        conv = cls.get_or_create_conversation(conversation_id, original_language)

        msg = Message(
            message_id=f"msg_{uuid.uuid4().hex[:12]}",
            conversation_id=conv.conversation_id,
            sender=sender,
            message_text=message_text.strip(),
            original_language=original_language,
            message_type=message_type,
            timestamp=datetime.utcnow(),
            audio_reference=audio_reference
        )
        db.session.add(msg)

        # Auto-update conversation title from first user query if still default
        if sender == 'user' and (
            conv.conversation_title.startswith("ಹೊಸ ಕೃಷಿ") or
            conv.conversation_title.startswith("New Farming") or
            len(conv.messages) == 0
        ):
            snippet = message_text.strip()
            if len(snippet) > 45:
                snippet = snippet[:45] + "..."
            conv.conversation_title = snippet

        conv.updated_at = datetime.utcnow()
        db.session.commit()
        return msg

    @classmethod
    def get_messages_for_gemini(cls, conversation_id: str, max_turns: int = 16) -> List[Dict[str, str]]:
        """
        Retrieves previous messages in chronological order formatted for multi-turn Gemini reasoning.
        Returns a list of dicts: [{'role': 'user'|'model', 'text': ...}, ...]
        Ensures strict user/model turn alternation.
        """
        messages = Message.query.filter_by(conversation_id=conversation_id)\
            .order_by(Message.timestamp.asc()).all()

        if not messages:
            return []

        # Limit to the most recent max_turns
        if len(messages) > max_turns:
            messages = messages[-max_turns:]

        formatted_turns: List[Dict[str, str]] = []
        for m in messages:
            role = 'user' if m.sender == 'user' else 'model'
            text = m.message_text.strip()
            if not text:
                continue

            # Merge consecutive messages from same role to ensure valid alternating turns
            if formatted_turns and formatted_turns[-1]['role'] == role:
                formatted_turns[-1]['text'] += f"\n{text}"
            else:
                formatted_turns.append({'role': role, 'text': text})

        return formatted_turns

    # =========================================================================
    # 3. ROLLING FACTUAL CONTEXT SUMMARY EXTRACTION
    # =========================================================================
    @classmethod
    def update_farming_summary(cls, conversation_id: str, prompt: str, bot_response: str = "") -> str:
        """
        Extracts key agricultural entities (crop, stage, symptoms, soil, location)
        and maintains a rolling summary string stored directly in the SQLite Conversation record.
        """
        conv = cls.get_conversation(conversation_id)
        if not conv:
            return ""

        lower = prompt.lower()
        extracted: Dict[str, str] = {}

        # Parse existing summary if present
        if conv.conversation_summary:
            for item in conv.conversation_summary.split(' | '):
                if ':' in item:
                    k, v = item.split(':', 1)
                    extracted[k.strip().upper()] = v.strip()

        # Crop matching
        for term, crop_name in cls.KNOWN_CROPS.items():
            if term in lower:
                extracted['CROP'] = crop_name
                break

        # Growth stage / Age matching (e.g., "30 days", "45 ದಿನ", "ಹೂವಾಡುವ ಹಂತ", "tillering")
        import re
        age_match = re.search(r'(\d+)\s*(days?|ದಿನ|ವಾರ|months?|ತಿಂಗಳು)', lower)
        if age_match:
            extracted['AGE/STAGE'] = age_match.group(0)
        elif any(w in lower for w in ['flowering', 'ಹೂವು', 'tillering', 'ನಾಟಿ', 'harvest', 'ಕೊಯ್ಲು', 'sowing', 'ಬಿತ್ತನೆ']):
            for stage in ['flowering', 'tillering', 'harvesting', 'sowing', 'vegetative', 'ಹೂವಾಡುವ ಹಂತ', 'ನಾಟಿ ಹಂತ']:
                if stage in lower:
                    extracted['AGE/STAGE'] = stage
                    break

        # Location matching
        for term, loc_name in cls.KNOWN_LOCATIONS.items():
            if term in lower:
                extracted['LOCATION'] = loc_name
                break

        # Soil matching
        for term, soil_name in cls.KNOWN_SOILS.items():
            if term in lower:
                extracted['SOIL'] = soil_name
                break

        # Symptoms matching
        for symp in ['yellow', 'spot', 'rot', 'wilt', 'blast', 'curl', 'borer', 'drying', 'ಕಲೆ', 'ಹಳದಿ', 'ಕೊಳೆ', 'ರೋಗ', 'ಬುಡ ಕೊಳೆ', 'ಚುಕ್ಕೆ']:
            if symp in lower:
                extracted['SYMPTOM'] = symp
                break

        # Build rolling summary string
        if extracted:
            parts = [f"{k}: {v}" for k, v in extracted.items()]
            summary_str = " | ".join(parts)
            conv.conversation_summary = summary_str
            conv.updated_at = datetime.utcnow()
            db.session.commit()
            return summary_str

        return conv.conversation_summary or ""

    @classmethod
    def get_farming_context_summary(cls, conversation_id: str) -> str:
        """Return the current conversation's persistent summary."""
        conv = cls.get_conversation(conversation_id)
        if conv and conv.conversation_summary:
            return conv.conversation_summary
        return "No prior context"

    # =========================================================================
    # 4. TRANSLATION TURNS (SERVICE 1 & 2 BACKWARD COMPATIBILITY)
    # =========================================================================
    @classmethod
    def add_translation_turn(
        cls,
        session_id: str,
        source_text: str,
        translated_text: str,
        source_lang: str,
        target_lang: str,
        speaker: str = 'speaker_a'
    ):
        sid = session_id or 'default_trans'
        if sid not in cls._TRANSLATION_SESSIONS:
            cls._TRANSLATION_SESSIONS[sid] = {'history': [], 'last_active': time.time()}

        cls._TRANSLATION_SESSIONS[sid]['history'].append({
            'speaker': speaker,
            'source_text': source_text,
            'translated_text': translated_text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'timestamp': time.time()
        })
        if len(cls._TRANSLATION_SESSIONS[sid]['history']) > 20:
            cls._TRANSLATION_SESSIONS[sid]['history'] = cls._TRANSLATION_SESSIONS[sid]['history'][-20:]

    @classmethod
    def get_history(cls, session_id: str):
        sid = session_id or 'default_trans'
        return cls._TRANSLATION_SESSIONS.get(sid, {}).get('history', [])

    @classmethod
    def clear_session(cls, session_id: str):
        if session_id in cls._TRANSLATION_SESSIONS:
            del cls._TRANSLATION_SESSIONS[session_id]
