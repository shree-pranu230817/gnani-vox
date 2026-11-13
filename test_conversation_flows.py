"""
UZHAVAR AI – Multi-Turn Conversation Flow Tests
Tests the four specified conversation scenarios:
  TEST A: Mandi price with follow-up location
  TEST B: Ragi cultivation + follow-up fertilizer (crop context retained)
  TEST C: English paddy price with follow-up location
  TEST D: Mandi price with no API records (no fabrication)
"""

import unittest
import uuid
from unittest.mock import patch, MagicMock

# Bootstrap Flask app context
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from backend.services.agri_memory import ConversationMemoryManager
from backend.services.gnani_service import GnaniAIService
from backend.services.agri_classifier import AgriculturalIntentClassifier


class TestConversationFlows(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.session_id = str(uuid.uuid4())

    def tearDown(self):
        ConversationMemoryManager.clear_context(self.session_id)
        self.ctx.pop()

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    def _ask(self, prompt, lang='kn'):
        return GnaniAIService.ask_evon(prompt, lang=lang, session_id=self.session_id)

    # ------------------------------------------------------------------
    # TEST A: Kannada mandi price → location follow-up
    # ------------------------------------------------------------------
    def test_A_paddy_price_then_location_followup(self):
        """
        Turn 1: "ಭತ್ತದ ಬೆಲೆ ಎಷ್ಟು?" → should ask for location
        Turn 2: "ತಂಜಾವೂರು" (bare location, 1 word) → should RESUME mandi intent,
                NOT classify as general_agriculture
        """
        print("\n\n=== TEST A: Paddy price + Thanjavur follow-up ===")

        # Turn 1
        r1 = self._ask("ಭತ್ತದ ಬೆಲೆ ಎಷ್ಟು?", lang='kn')
        print(f"T1 intent={r1['category']} | action={r1.get('action_needed')}")
        print(f"T1 answer preview: {r1['answer'][:120]}")
        self.assertEqual(r1['category'], 'mandi_prices', "Turn 1 must classify as mandi_prices")

        # Turn 2: bare location
        r2 = self._ask("ತಂಜಾವೂರು", lang='kn')
        print(f"T2 intent={r2['category']} | action={r2.get('action_needed')}")
        print(f"T2 answer preview: {r2['answer'][:200]}")
        self.assertEqual(r2['category'], 'mandi_prices',
                         "Turn 2 follow-up location must stay on mandi_prices intent")
        # Answer must NOT be the generic agriculture fallback
        self.assertNotIn("ಕಿಸಾನ್ ಕಾಲ್ ಸೆಂಟರ್", r2['answer'],
                         "Should not return generic fallback for a mandi location follow-up")
        # Answer must reference the location or explain unavailability
        answer_lower = r2['answer'].lower()
        has_location = 'ತಂಜಾವೂರು' in r2['answer'] or 'thanjavur' in answer_lower
        has_unavailable = 'ಲಭ್ಯವಿಲ್ಲ' in r2['answer'] or 'not' in answer_lower
        self.assertTrue(has_location or has_unavailable,
                        f"Answer must reference Thanjavur or state unavailability. Got: {r2['answer'][:200]}")
        print("TEST A PASSED ✅")

    # ------------------------------------------------------------------
    # TEST B: Ragi cultivation → fertilizer follow-up
    # ------------------------------------------------------------------
    def test_B_ragi_cultivation_then_fertilizer_followup(self):
        """
        Turn 1: "ರಾಗಿ ಬೆಳೆಯುವ ವಿಧಾನ" → detailed Ragi cultivation
        Turn 2: "ಯಾವ ಗೊಬ್ಬರ ಹಾಕಬೇಕು?" → must KNOW crop is Ragi
        """
        print("\n\n=== TEST B: Ragi cultivation + fertilizer follow-up ===")

        r1 = self._ask("ರಾಗಿ ಬೆಳೆಯುವ ವಿಧಾನ", lang='kn')
        print(f"T1 intent={r1['category']}")
        print(f"T1 answer preview: {r1['answer'][:200]}")
        self.assertEqual(r1['category'], 'crop_cultivation')
        # Ragi-specific content expected
        self.assertTrue(
            'GPU-28' in r1['answer'] or 'KMR-301' in r1['answer'] or 'ರಾಗಿ' in r1['answer'],
            f"Ragi cultivation answer must contain variety names. Got: {r1['answer'][:200]}"
        )

        # Turn 2: short follow-up without mentioning ragi explicitly
        r2 = self._ask("ಯಾವ ಗೊಬ್ಬರ ಹಾಕಬೇಕು?", lang='kn')
        print(f"T2 intent={r2['category']} | context={r2['memory_context']}")
        print(f"T2 answer preview: {r2['answer'][:200]}")
        self.assertEqual(r2['category'], 'fertilizer_soil')
        # Must reference ragi-specific NPK
        self.assertTrue(
            'ರಾಗಿ' in r2['answer'] or '20:16' in r2['answer'] or '40:20' in r2['answer'],
            f"Fertilizer follow-up must reference Ragi NPK. Got: {r2['answer'][:200]}"
        )
        print("TEST B PASSED ✅")

    # ------------------------------------------------------------------
    # TEST C: English paddy price → English location follow-up
    # ------------------------------------------------------------------
    def test_C_english_paddy_price_then_kumbakonam(self):
        """
        Turn 1: "What is the paddy price?" → ask for location
        Turn 2: "Kumbakonam" → resume mandi intent, search for Kumbakonam
        """
        print("\n\n=== TEST C: English paddy price + Kumbakonam follow-up ===")

        r1 = self._ask("What is the paddy price?", lang='en')
        print(f"T1 intent={r1['category']} | action={r1.get('action_needed')}")
        print(f"T1 answer preview: {r1['answer'][:120]}")
        self.assertEqual(r1['category'], 'mandi_prices')

        r2 = self._ask("Kumbakonam", lang='en')
        print(f"T2 intent={r2['category']}")
        print(f"T2 answer preview: {r2['answer'][:200]}")
        self.assertEqual(r2['category'], 'mandi_prices',
                         "English location follow-up must stay on mandi_prices intent")
        self.assertNotIn("1800-180-1551", r2['answer'],
                         "Generic Kisan helpline should not appear in a mandi follow-up")
        answer_lower = r2['answer'].lower()
        self.assertTrue(
            'kumbakonam' in answer_lower or 'not' in answer_lower or 'unavailable' in answer_lower,
            f"Answer must reference Kumbakonam or state unavailability. Got: {r2['answer'][:200]}"
        )
        print("TEST C PASSED ✅")

    # ------------------------------------------------------------------
    # TEST D: No fabricated prices when API has no records
    # ------------------------------------------------------------------
    def test_D_no_fabricated_prices_when_no_records(self):
        """
        "ಭತ್ತದ ಬೆಲೆ ಎಷ್ಟು?" when database has no matching records must NOT
        invent prices or market names like Amritsar/Thanjavur/Kumbakonam.
        """
        print("\n\n=== TEST D: No fabricated prices ===")

        # Patch _query_prices to return empty list
        with patch.object(
            __import__('backend.services.mandi_assistant', fromlist=['MandiPriceAssistant'])
            .MandiPriceAssistant,
            '_query_prices',
            return_value=[]
        ):
            r = self._ask("ಭತ್ತದ ಬೆಲೆ ಎಷ್ಟು?", lang='kn')
            print(f"intent={r['category']}")
            print(f"answer: {r['answer']}")

        self.assertEqual(r['category'], 'mandi_prices')
        # Must NOT contain invented price numbers like ₹1800, ₹2100 etc.
        import re
        fake_price_pattern = re.compile(r'₹\s*\d{3,5}\s*/\s*(ಕ್ವಿಂಟಾಲ್|Quintal|quintal)', re.IGNORECASE)
        self.assertIsNone(
            fake_price_pattern.search(r['answer']),
            f"Response must not contain fabricated prices. Got: {r['answer']}"
        )
        # Must NOT list 'Amritsar' or 'Ludhiana' as available for paddy when no records returned
        fabricated_mandis = ['Amritsar', 'Ludhiana', 'Madurai', 'Erode']
        for m in fabricated_mandis:
            self.assertNotIn(
                m, r['answer'],
                f"Response must not fabricate '{m}' as an available market. Got: {r['answer']}"
            )
        print("TEST D PASSED ✅")

    # ------------------------------------------------------------------
    # TEST E: Intent classification edge cases
    # ------------------------------------------------------------------
    def test_E_intent_classification(self):
        """Verify classifier routes key Kannada phrases correctly."""
        print("\n\n=== TEST E: Intent classification ===")

        cases = [
            ("ಭತ್ತದ ಬೆಲೆ ಎಷ್ಟು?",          'mandi_prices'),
            ("ರಾಗಿ ಬೆಳೆಯುವ ವಿಧಾನ",         'crop_cultivation'),
            ("ರಾಗಿ ಬೆಳೆಯುವ ವಿದ್ಯೆ",         'crop_cultivation'),
            ("ಭತ್ತಕ್ಕೆ ಯಾವ ಗೊಬ್ಬರ ಹಾಕಬೇಕು?", 'fertilizer_soil'),
            ("ರಾಗಿ ಬೆಲೆಯೆಷ್ಟು?",             'mandi_prices'),
        ]
        for prompt, expected in cases:
            cat, _ = AgriculturalIntentClassifier.classify(prompt)
            print(f"  '{prompt[:40]}' → {cat} (expected {expected})")
            self.assertEqual(cat, expected, f"'{prompt}' should be '{expected}', got '{cat}'")
        print("TEST E PASSED ✅")


if __name__ == '__main__':
    unittest.main(verbosity=2)

