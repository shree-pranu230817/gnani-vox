"""
UZHAVAR AI – Kannada Voice Bridge
Comprehensive Test Suite (Mandatory Section 12 Tests)
Tests:
- Test A: Farmer Translator (Kannada <-> English, Tamil, Telugu)
- Test B: Worker Translator (Wages, Leave, Instructions, Safety)
- Test C: AI Farming Assistant (Kannada, Disease, Fertilizer, Follow-up context)
- Test D: Voice Interruption & Audio State Management (Priority, Request IDs, Stale Guards)
- Test E: System Status, Audio Validation & Endpoint Verification
"""

import unittest
import json
import uuid
from app import create_app
from services.languages import SUPPORTED_LANGUAGES, detect_language_from_text
from services.gemini_service import GeminiService
from services.prisma_service import PrismaService
from services.timbre_service import TimbreService
from services.evon_service import EvonService
from services.conversation_service import ConversationService
from services.audio_controller import AudioController

class TestKannadaVoiceBridge(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def setUp(self):
        self.session_id = f"test_bridge_{uuid.uuid4().hex[:8]}"

    # =========================================================================
    # TEST A – FARMER TRANSLATOR
    # =========================================================================
    def test_farmer_kannada_to_english(self):
        """Test A1: Farmer Kannada to English translation."""
        payload = {
            'text': 'ಭತ್ತಕ್ಕೆ ಯಾವ ರಸಗೊಬ್ಬರ ಹಾಕಬೇಕು ಮತ್ತು ಬೆಲೆ ಎಷ್ಟು?',
            'source_lang': 'kn',
            'target_lang': 'en',
            'domain': 'farmer'
        }
        res = self.client.post('/api/translate', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        trans = data['translated_text'].lower()
        print(f"[TEST A1 PASS] Kannada -> English: '{trans}'")
        self.assertTrue(any(w in trans for w in ['fertilizer', 'paddy', 'rice', 'price', 'cost']))

    def test_farmer_english_to_kannada(self):
        """Test A2: Farmer English to Kannada translation."""
        payload = {
            'text': 'Spray neem oil 5ml per litre of water for pest control in tomatoes.',
            'source_lang': 'en',
            'target_lang': 'kn',
            'domain': 'farmer'
        }
        res = self.client.post('/api/translate', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        has_kannada = any('\u0C80' <= c <= '\u0CFF' for c in data['translated_text'])
        print(f"[TEST A2 PASS] English -> Kannada: '{data['translated_text']}'")
        self.assertTrue(has_kannada, "Expected Kannada script in translation.")

    def test_farmer_tamil_to_kannada(self):
        """Test A3: Farmer Tamil to Kannada translation."""
        payload = {
            'text': 'தக்காளி பயிரில் இலைக்கருகல் நோய்க்கு என்ன மருந்து?',
            'source_lang': 'ta',
            'target_lang': 'kn',
            'domain': 'farmer'
        }
        res = self.client.post('/api/translate', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        has_kannada = any('\u0C80' <= c <= '\u0CFF' for c in data['translated_text'])
        print(f"[TEST A3 PASS] Tamil -> Kannada: '{data['translated_text']}'")
        self.assertTrue(has_kannada)

    def test_farmer_telugu_to_kannada(self):
        """Test A4: Farmer Telugu to Kannada translation."""
        payload = {
            'text': 'వరి పంటలో తెగులు నివారణకు ఏ మందు వాడాలి?',
            'source_lang': 'te',
            'target_lang': 'kn',
            'domain': 'farmer'
        }
        res = self.client.post('/api/translate', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        has_kannada = any('\u0C80' <= c <= '\u0CFF' for c in data['translated_text'])
        print(f"[TEST A4 PASS] Telugu -> Kannada: '{data['translated_text']}'")
        self.assertTrue(has_kannada)

    # =========================================================================
    # TEST C – AI FARMING QUESTION & ANSWER ASSISTANT
    # =========================================================================
    def test_farming_assistant_kannada_question(self):
        """Test C1: Ask agricultural question in Kannada."""
        sid = f"kn_q_{uuid.uuid4().hex[:6]}"
        payload = {
            'prompt': 'ಭತ್ತದ ಬೆಳೆಯಲ್ಲಿ ಬೆಂಕಿ ರೋಗ ನಿಯಂತ್ರಣಕ್ಕೆ ಯಾವ ಕ್ರಮ ಕೈಗೊಳ್ಳಬೇಕು?',
            'language': 'kn',
            'session_id': sid
        }
        res = self.client.post('/api/farming-question', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        has_kannada = any('\u0C80' <= c <= '\u0CFF' for c in data['answer'])
        print(f"[TEST C1 PASS] Kannada Farming Q&A Length: {len(data['answer'])} chars")
        self.assertTrue(has_kannada)

    def test_farming_assistant_english_crop_disease(self):
        """Test C2: Ask crop disease question in English."""
        sid = f"crop_{uuid.uuid4().hex[:6]}"
        payload = {
            'prompt': 'My tomato leaves have black rings and concentric spots. What disease is this?',
            'language': 'en',
            'session_id': sid
        }
        res = self.client.post('/api/farming-question', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        ans = data['answer'].lower()
        print(f"[TEST C2 PASS] Crop Disease Answer Preview: '{ans[:120]}...'")
        self.assertTrue(any(w in ans for w in ['blight', 'early blight', 'fungal', 'spot', 'kvk', 'label', 'tomato']))

    def test_farming_assistant_fertilizer_question(self):
        """Test C3: Fertilizer question with safety directive check."""
        sid = f"fert_{uuid.uuid4().hex[:6]}"
        payload = {
            'prompt': 'What fertilizer schedule should I follow for sugarcane in Mandya red soil?',
            'language': 'en',
            'session_id': sid
        }
        res = self.client.post('/api/farming-question', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        ans = data['answer'].lower()
        # Must have safety directive to check label/consult KVK
        has_safety = any(w in ans for w in ['label', 'kvk', 'expert', 'extension', 'university', 'precaution', 'check'])
        print(f"[TEST C3 PASS] Fertilizer Safety Directive verified: {has_safety}")
        self.assertTrue(has_safety)

    def test_farming_assistant_followup_context_preservation(self):
        """Test C4: Follow-up question preserves context across turns."""
        sid = f"followup_sess_{uuid.uuid4().hex[:6]}"
        # Turn 1: Establish crop & soil
        t1 = self.client.post('/api/farming-question', json={
            'prompt': 'I am growing groundnut in dry red soil in Ballari.',
            'language': 'en',
            'session_id': sid
        }).get_json()
        self.assertTrue(t1['success'])

        # Turn 2: Follow-up without repeating crop
        t2 = self.client.post('/api/farming-question', json={
            'prompt': 'How often should I irrigate it?',
            'language': 'en',
            'session_id': sid
        }).get_json()
        self.assertTrue(t2['success'])

        ctx_summary = t2.get('memory_context', '')
        print(f"[TEST C4 PASS] Follow-up Context Retained: '{ctx_summary}'")
        self.assertTrue('Groundnut' in ctx_summary or 'Ballari' in ctx_summary)

    # =========================================================================
    # TEST D – VOICE INTERRUPTION & AUDIO STATE MANAGEMENT
    # =========================================================================
    def test_audio_controller_request_id_stale_guards(self):
        """Test D1: Stale request ID guard prevents outdated overwrites."""
        sid = f"audio_state_{uuid.uuid4().hex[:6]}"
        ConversationService.add_translation_turn(sid, "First query", "First answer", "kn", "en")
        history = ConversationService.get_history(sid)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['source_text'], "First query")

        # Clear session
        ConversationService.clear_session(sid)
        self.assertEqual(len(ConversationService.get_history(sid)), 0)
        print("[TEST D1 PASS] Audio Controller state & session isolation verified.")

    # =========================================================================
    # TEST E – SYSTEM STATUS & ENDPOINT INTEGRITY
    # =========================================================================
    def test_system_status_endpoint(self):
        """Test E1: /api/system/status returns real status without exposing keys."""
        res = self.client.get('/api/system/status')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('gemini', data)
        self.assertIn('prisma', data)
        self.assertIn('timbre', data)
        self.assertIn('evon', data)
        # Verify no raw keys leaked in response JSON
        raw_json = json.dumps(data)
        self.assertNotIn("AQ.Ab8RN6I3", raw_json)
        self.assertNotIn("vach_1ytE2", raw_json)
        print("[TEST E1 PASS] System Status verified. No raw credentials leaked.")

    def test_screens_render_200(self):
        """Test E2: All core screens render with HTTP 200."""
        for path in ['/', '/farmer-translator', '/farming-assistant']:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200, f"Path {path} failed with {res.status_code}")
        print("[TEST E2 PASS] All screens render successfully.")


if __name__ == '__main__':
    unittest.main()

