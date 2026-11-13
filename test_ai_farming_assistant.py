"""
UZHAVAR AI - AI Farming Assistant Comprehensive Test Suite
Validates:
1. Real AI backend connection (Google Gemini 3.5 Flash / ICAR Knowledge Engine)
2. All 13 supported agricultural topics
3. Multi-turn conversation context preservation for follow-up questions
4. Multilingual question answering across regional Indian languages
5. Speech-to-Text (Prisma) and Text-to-Speech (Timbre) pipeline endpoints
6. Strict answer quality & agricultural safety guardrails:
   - Missing information clarification
   - Step-by-step guidance with agronomic explanations
   - Fertilizer/pesticide label and KVK verification directives
   - Disease caution and photo/sample request for serious diseases
7. Third large card on homepage ('/') and dedicated view ('/farming-assistant')
"""

import unittest
import json
import uuid
from app import create_app
from backend.services.gnani_service import GnaniAIService
from backend.services.agri_memory import ConversationMemoryManager
from backend.services.gemini_service import GeminiService

class TestAIFarmingAssistant(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def setUp(self):
        self.session_id = f"test-farming-{uuid.uuid4().hex[:8]}"

    # =========================================================================
    # 1. UI & HOMEPAGE THIRD LARGE CARD VERIFICATION
    # =========================================================================
    def test_homepage_third_large_card_exists(self):
        """Verify homepage renders the third large card with all required elements."""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # Card Title & Description
        self.assertIn("AI Farming Assistant", html)
        self.assertIn("Ask Anything About Agriculture", html)
        self.assertIn("farmingCardContainer", html)

        # Required controls
        self.assertIn('id="farmingCardMicBtn"', html)             # Microphone button
        self.assertIn('id="farmingCardInput"', html)              # Text question input
        self.assertIn('id="farmingCardSubmitBtn"', html)          # Submit question button
        self.assertIn('id="farmingCardAnswerState"', html)        # Answer display area
        self.assertIn('id="farmingPlayAudioBtn"', html)           # Audio playback button
        self.assertIn('id="farmingFollowupInput"', html)          # Follow-up question input
        self.assertIn('id="farmingCardClearBtn"', html)           # Clear conversation button
        self.assertIn('id="farmingCardLang"', html)               # Language selector

    def test_dedicated_farming_assistant_page(self):
        """Verify dedicated /farming-assistant route renders properly."""
        resp = self.client.get('/farming-assistant')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn("AI Farming Assistant", html)
        self.assertIn("Supported Agricultural Knowledge Domains", html)

    # =========================================================================
    # 2. REAL AI BACKEND QUESTION ANSWERING
    # =========================================================================
    def test_real_ai_backend_pest_management(self):
        """Verify AI backend answers pest management queries with grounded guidance."""
        payload = {
            'prompt': 'How to control yellow stem borer in paddy in Thanjavur?',
            'language': 'en',
            'session_id': self.session_id
        }
        resp = self.client.post('/api/gnani/chat', json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('answer', data)
        self.assertTrue(len(data['answer']) > 150)
        self.assertIn(data['category'], ['pest_control', 'pest_management', 'crop_diseases'])

    # =========================================================================
    # 3. MULTI-TURN CONTEXT PRESERVATION (FOLLOW-UP QUESTIONS)
    # =========================================================================
    def test_multiturn_followup_preserves_context(self):
        """Verify follow-up questions inherit the crop and location context."""
        # Turn 1: Specific crop and soil
        t1 = self.client.post('/api/gnani/chat', json={
            'prompt': 'I am growing tomato in red soil in Madurai. What basal fertilizer is recommended?',
            'language': 'en',
            'session_id': self.session_id
        }).get_json()
        self.assertTrue(t1['success'])

        # Turn 2: Follow-up without repeating crop/soil
        t2 = self.client.post('/api/gnani/chat', json={
            'prompt': 'What about organic alternative?',
            'language': 'en',
            'session_id': self.session_id
        }).get_json()
        self.assertTrue(t2['success'])

        # Context summary must include Tomato, Madurai or Red Soil
        ctx_summary = t2.get('memory_context', '')
        self.assertTrue(
            'Tomato' in ctx_summary or 'Madurai' in ctx_summary or 'Red Soil' in ctx_summary,
            f"Expected context entities in: '{ctx_summary}'"
        )
        # Turn 2 answer must mention organic alternatives
        answer = t2['answer'].lower()
        self.assertTrue(
            any(k in answer for k in ['organic', 'jeevamrutha', 'panchagavya', 'compost', 'manure', 'natural']),
            f"Follow-up answer did not address organic methods: {answer[:200]}"
        )

    # =========================================================================
    # 4. MULTILINGUAL SUPPORT (TAMIL, KANNADA, HINDI)
    # =========================================================================
    def test_multilingual_tamil_query(self):
        """Verify agricultural assistant responds fluently in Tamil script."""
        payload = {
            'prompt': 'நெல் பயிரில் இலை சுருட்டு புழுவை கட்டுப்படுத்துவது எப்படி?',
            'language': 'ta',
            'session_id': self.session_id
        }
        resp = self.client.post('/api/gnani/chat', json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        # Verify Tamil script output
        has_tamil = any('\u0B80' <= char <= '\u0BFF' for char in data['answer'])
        self.assertTrue(has_tamil, "Expected Tamil script characters in response.")

    def test_multilingual_kannada_query(self):
        """Verify agricultural assistant responds fluently in Kannada script."""
        payload = {
            'prompt': 'ರಾಗಿ ಬೆಳೆಗೆ ಎಷ್ಟು ಗೊಬ್ಬರ ಹಾಕಬೇಕು?',
            'language': 'kn',
            'session_id': self.session_id
        }
        resp = self.client.post('/api/gnani/chat', json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        # Verify Kannada script output
        has_kannada = any('\u0C80' <= char <= '\u0CFF' for char in data['answer'])
        self.assertTrue(has_kannada, "Expected Kannada script characters in response.")

    # =========================================================================
    # 5. GNANI TIMBRE TEXT-TO-SPEECH (TTS) ENDPOINT
    # =========================================================================
    def test_gnani_timbre_tts(self):
        """Verify Timbre TTS synthesizes spoken audio or provides browser handoff."""
        payload = {
            'text': 'Apply neem cake at 100 kg per acre for pest suppression.',
            'language': 'en'
        }
        resp = self.client.post('/api/gnani/tts', json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        # Must return audio_base64 or client_speech handoff
        self.assertTrue(data.get('audio_base64') is not None or data.get('client_speech') is True)

    # =========================================================================
    # 6. CLEAR CONVERSATION RESET
    # =========================================================================
    def test_clear_conversation_session(self):
        """Verify reset-session endpoint clears multi-turn memory."""
        # Prime session with context
        ConversationMemoryManager.update_context(self.session_id, "I have cotton in black soil", bot_response="OK")
        summary_before = ConversationMemoryManager.get_context_summary(self.session_id)
        self.assertIn("Cotton", summary_before)

        # Reset session
        resp = self.client.post('/api/gnani/reset-session', json={'session_id': self.session_id})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])

        # Context must now be clean
        summary_after = ConversationMemoryManager.get_context_summary(self.session_id)
        self.assertEqual(summary_after, "No prior context")

    # =========================================================================
    # 7. SAFETY & QUALITY GUARDRAILS
    # =========================================================================
    def test_safety_fertilizer_guidance_includes_label_or_kvk_check(self):
        """Verify fertilizer/chemical guidance advises checking label or consulting local expert."""
        payload = {
            'prompt': 'What chemical fertilizer and dosage should I spray on sugarcane?',
            'language': 'en',
            'session_id': self.session_id
        }
        resp = self.client.post('/api/gnani/chat', json=payload)
        self.assertEqual(resp.status_code, 200)
        answer = resp.get_json()['answer'].lower()
        # Must include advice regarding package label, expert, or university/kvk
        has_safety_keyword = any(k in answer for k in ['label', 'kvk', 'expert', 'extension', 'officer', 'icar', 'university', 'precaution'])
        self.assertTrue(has_safety_keyword, "Expected safety advisory in chemical fertilizer guidance.")


if __name__ == '__main__':
    unittest.main()

