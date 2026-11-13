"""
Comprehensive Test Suite for UZHAVAR AI Multilingual Agricultural Intelligence System
Tests:
1. All 14 Agricultural Categories semantic classification.
2. Multilingual understanding across 10 Indian Languages (English, Tamil, Kannada, Telugu, Hindi, Malayalam, Bengali, Marathi, Gujarati, Punjabi).
3. Multi-turn Conversation Memory:
   User: "I am growing paddy."
   User: "CO 51 variety."
   User: "Yellow leaves." -> verifies context includes Paddy + CO 51 + Yellow leaves.
4. Mandi Price Retrieval System:
   - Identifies crop & location.
   - Fetches modal price, min/max price, unit, date, source.
   - Proactively asks for missing location if only crop is specified.
   - Never sends price questions to crop disease system.
5. Error handling and real API feedback.
"""

import unittest
import uuid
from app import create_app
from backend.services.agri_classifier import AgriculturalIntentClassifier
from backend.services.agri_memory import ConversationMemoryManager
from backend.services.mandi_assistant import MandiPriceAssistant
from backend.services.gnani_service import GnaniAIService

class MultilingualAgriculturalIntelligenceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.test_session_id = f"test_session_{uuid.uuid4().hex[:8]}"

    def test_01_fourteen_categories_classification(self):
        """Verify semantic classification for each of the 14 agricultural categories."""
        samples = [
            ("Which crop should I grow in red soil this Kharif season?", "crop_cultivation"),
            ("What is the recommended NPK fertilizer dosage for maize?", "fertilizer_soil"),
            ("My tomato leaves have yellow curling and brown spots", "crop_diseases"),
            ("How to control pink bollworm caterpillars in cotton?", "pest_management"),
            ("How much water does drip irrigation save compared to flooding?", "irrigation_water"),
            ("How to treat seeds with Trichoderma viride before sowing?", "seeds_treatment"),
            ("What is the proper plant spacing and harvest maturity for paddy?", "sowing_harvesting"),
            ("Heavy rainfall is predicted tomorrow, what precautions to take?", "weather_climate"),
            ("What is the live mandi price of turmeric in Erode market?", "mandi_prices"),
            ("How to apply for PM-KISAN subsidy and crop insurance?", "govt_schemes"),
            ("How to prepare Jeevamrutha using cow dung and jaggery?", "organic_farming"),
            ("Is a power weeder or tractor better for weed removal?", "equipment_technology"),
            ("How to calculate net profit per acre for ragi cultivation?", "yield_profit"),
            ("Where is the nearest Krishi Vigyan Kendra KVK office?", "general_agriculture")
        ]

        for prompt, expected_cat in samples:
            cat, cat_info = AgriculturalIntentClassifier.classify(prompt)
            self.assertEqual(cat, expected_cat, f"Failed for prompt: '{prompt}' (got {cat}, expected {expected_cat})")

    def test_02_multilingual_language_detection(self):
        """Verify automatic identification across 10 Indian regional languages."""
        test_phrases = {
            'ta': 'நெல் பயிரில் குலை நோய் கட்டுப்பாடு எப்படி?',
            'kn': 'ಭತ್ತದ ಬೆಳೆಗಳಲ್ಲಿ ಬೆಂಕಿ ರೋಗಕ್ಕೆ ಯಾವ ಔಷಧಿ ಸಿಂಪಡಿಸಬೇಕು?',
            'te': 'వరి పంటలో అగ్గితెగులు నివారణకు ఎలాంటి చర్యలు తీసుకోవాలి?',
            'hi': 'धान में झुलसा रोग नियंत्रण के लिए कौन सी दवा डालें?',
            'ml': 'നെല്ലിലെ കുമിൾ രോഗത്തിന് എന്ത് ചെയ്യണം?',
            'bn': 'ধানের ব্লাস্ট রোগ প্রতিরোধের উপায় কি?',
            'mr': 'भात पिकावरील करपा रोगाचे नियंत्रण कसे करावे?',
            'gu': 'ડાંગરમાં ગેરુ અને કરપા રોગ માટે શું કરવું?',
            'pa': 'ਝੋਨੇ ਦੇ ਝੁਲਸ ਰੋਗ ਦੀ ਰੋਕਥਾਮ ਕਿਵੇਂ ਕਰੀਏ?',
            'en': 'How to control paddy blast disease organically?'
        }

        for expected_lang, phrase in test_phrases.items():
            detected = AgriculturalIntentClassifier.detect_language(phrase)
            self.assertEqual(detected, expected_lang, f"Failed detecting {expected_lang} for: {phrase}")

    def test_03_mandi_prices_retrieval(self):
        """Verify live mandi price extraction from AGMARKNET database."""
        # 1. Query with both crop and location
        res = self.client.post('/api/gnani/chat', json={
            'prompt': 'What is the market price of turmeric in Erode mandi?',
            'language': 'en'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['category'], 'mandi_prices')
        self.assertIn("Erode", data['answer'])
        self.assertIn("Turmeric", data['answer'])
        self.assertIn("Modal Price", data['answer'])
        self.assertIn("AGMARKNET", data['answer'])

        # 2. Query in Kannada for Mandi price
        res_kn = self.client.post('/api/gnani/chat', json={
            'prompt': 'ಈರೋಡ್ ಮಂಡಿಯಲ್ಲಿ ಅರಿಶಿನ ಬೆಲೆ ಎಷ್ಟು?',
            'language': 'kn'
        })
        self.assertEqual(res_kn.status_code, 200)
        data_kn = res_kn.get_json()
        self.assertEqual(data_kn['category'], 'mandi_prices')
        self.assertIn("ಮಾದರಿ ಬೆಲೆ", data_kn['answer'])

        # 3. Query with crop but missing location -> Should ask for location
        fresh_sess = f"fresh_sess_{uuid.uuid4().hex}"
        res_missing = self.client.post('/api/gnani/chat', json={
            'prompt': 'What is the current mandi price of paddy?',
            'language': 'en',
            'session_id': fresh_sess
        })
        self.assertEqual(res_missing.status_code, 200)
        data_missing = res_missing.get_json()
        self.assertEqual(data_missing['category'], 'mandi_prices')
        self.assertIn("location", data_missing['answer'].lower())

    def test_04_multi_turn_conversation_memory(self):
        """Verify session-isolated conversation context tracking across sequential turns."""
        sess_id = f"test_session_{uuid.uuid4().hex}"

        # Turn 1: Farmer mentions crop
        res1 = self.client.post('/api/gnani/chat', json={
            'prompt': 'I am growing paddy in my farm.',
            'language': 'en',
            'session_id': sess_id
        })
        self.assertEqual(res1.status_code, 200)

        # Verify context remembered Paddy
        ctx1 = ConversationMemoryManager.get_or_create_session(sess_id)['context']
        self.assertEqual(ctx1['crop'], 'Paddy')

        # Turn 2: Farmer mentions variety
        res2 = self.client.post('/api/gnani/chat', json={
            'prompt': 'The variety is CO 51.',
            'language': 'en',
            'session_id': sess_id
        })
        self.assertEqual(res2.status_code, 200)

        ctx2 = ConversationMemoryManager.get_or_create_session(sess_id)['context']
        self.assertEqual(ctx2['crop'], 'Paddy')
        self.assertEqual(ctx2['variety'], 'CO 51')

        # Turn 3: Farmer reports symptom without repeating crop name
        res3 = self.client.post('/api/gnani/chat', json={
            'prompt': 'I am noticing yellow leaves and brown spots on the leaves.',
            'language': 'en',
            'session_id': sess_id
        })
        self.assertEqual(res3.status_code, 200)
        data3 = res3.get_json()
        self.assertEqual(data3['category'], 'crop_diseases')
        # The answer should know we are dealing with Paddy / CO 51
        self.assertIn("Paddy", data3['answer'])

    def test_05_memory_session_isolation(self):
        """Verify that conversation memory is strictly isolated between different user sessions."""
        user_a = f"session_a_{uuid.uuid4().hex[:6]}"
        user_b = f"session_b_{uuid.uuid4().hex[:6]}"

        # User A discusses Cotton
        self.client.post('/api/gnani/chat', json={
            'prompt': 'I am cultivating Cotton in Salem.',
            'language': 'en',
            'session_id': user_a
        })

        # User B discusses Wheat
        self.client.post('/api/gnani/chat', json={
            'prompt': 'I have Wheat crop in Ludhiana.',
            'language': 'en',
            'session_id': user_b
        })

        ctx_a = ConversationMemoryManager.get_or_create_session(user_a)['context']
        ctx_b = ConversationMemoryManager.get_or_create_session(user_b)['context']

        self.assertEqual(ctx_a['crop'], 'Cotton')
        self.assertEqual(ctx_a['location'], 'Salem')
        self.assertEqual(ctx_b['crop'], 'Wheat')
        self.assertEqual(ctx_b['location'], 'Ludhiana')

    def test_06_reset_session(self):
        """Verify conversation memory reset endpoint."""
        sess_id = f"test_session_{uuid.uuid4().hex}"
        self.client.post('/api/gnani/chat', json={
            'prompt': 'I am growing sugarcane.',
            'session_id': sess_id
        })
        ctx = ConversationMemoryManager.get_or_create_session(sess_id)['context']
        self.assertEqual(ctx['crop'], 'Sugarcane')

        # Reset
        res_reset = self.client.post('/api/gnani/reset-session', json={'session_id': sess_id})
        self.assertEqual(res_reset.status_code, 200)
        self.assertTrue(res_reset.get_json()['success'])

if __name__ == '__main__':
    unittest.main()
