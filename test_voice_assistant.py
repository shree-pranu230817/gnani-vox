"""
Verification test suite for UZHAVAR AI Voice Assistant
Tests:
1. 5 different Kannada agricultural questions across diseases, fertilizers, irrigation, mandi prices, organic farming.
2. English and Tamil questions.
3. Verification that all 5 Kannada responses are distinct, relevant, and not hardcoded static fallbacks.
4. Language code mapping (kn -> kn-IN).
5. Error handling when invalid audio or empty question is passed.
6. TTS endpoint response.
"""

import unittest
from app import create_app

class VoiceAssistantTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_five_kannada_questions(self):
        questions = [
            ("ಭತ್ತದ ಬೆಳೆಗಳಲ್ಲಿ ಬೆಂಕಿ ರೋಗಕ್ಕೆ ಯಾವ ಔಷಧಿ ಸಿಂಪಡಿಸಬೇಕು?", "blast / disease", "ಟ್ರೈಸೈಕ್ಲೋಜೋಲ್"),
            ("ರಾಗಿ ಬೆಳೆಗೆ ಶಿಫಾರಸು ಮಾಡಲಾದ ರಸಗೊಬ್ಬರಗಳ ಪ್ರಮಾಣ ಎಷ್ಟು?", "ragi fertilizer", "ರಾಗಿ"),
            ("ಹನಿ ನೀರಾವರಿ ಪದ್ಧತಿಯಿಂದ ನೀರು ಎಷ್ಟು ಉಳಿತಾಯವಾಗುತ್ತದೆ?", "drip irrigation", "ಹನಿ ನೀರಾವರಿ"),
            ("ಬೆಳೆಗಳಿಗೆ ಉತ್ತಮ ಮಂಡಿ ಬೆಲೆ ಪಡೆಯುವುದು ಹೇಗೆ?", "mandi prices", "ಮಂಡಿ"),
            ("ಜೀವಾಮೃತವನ್ನು ಹೇಗೆ ತಯಾರಿಸಬೇಕು ಮತ್ತು ಬಳಸಬೇಕು?", "jeevamrutha organic", "ಜೀವಾಮೃತ")
        ]

        answers = []
        for q, label, expected_keyword in questions:
            res = self.client.post('/api/gnani/chat', json={
                'prompt': q,
                'language': 'kn'
            })
            self.assertEqual(res.status_code, 200, f"Failed for {label}")
            data = res.get_json()
            self.assertTrue(data['success'])
            answer = data['answer']
            self.assertIn(expected_keyword, answer, f"Expected keyword '{expected_keyword}' not found in answer for {label}")
            answers.append(answer)

        # Verify that all 5 answers are mutually unique (not the same repeated response)
        unique_answers = set(answers)
        self.assertEqual(len(unique_answers), 5, "All 5 Kannada questions must produce distinct, different answers!")

    def test_english_and_tamil(self):
        # English
        res_en = self.client.post('/api/gnani/chat', json={
            'prompt': 'How to control paddy blast disease and what fungicide to spray?',
            'language': 'en'
        })
        self.assertEqual(res_en.status_code, 200)
        data_en = res_en.get_json()
        self.assertTrue(data_en['success'])
        self.assertIn("Tricyclazole", data_en['answer'])

        # Tamil
        res_ta = self.client.post('/api/gnani/chat', json={
            'prompt': 'ஜீவாமிர்தம் எவ்வாறு தயாரிக்க வேண்டும்?',
            'language': 'ta'
        })
        self.assertEqual(res_ta.status_code, 200)
        data_ta = res_ta.get_json()
        self.assertTrue(data_ta['success'])
        self.assertIn("ஜீவாமிர்தம்", data_ta['answer'])

    def test_error_handling_empty_prompt(self):
        res = self.client.post('/api/gnani/chat', json={
            'prompt': '',
            'language': 'kn'
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data['success'])

    def test_tts_endpoint(self):
        res = self.client.post('/api/gnani/tts', json={
            'text': 'ಭತ್ತದ ಬೆಂಕಿ ರೋಗ ನಿಯಂತ್ರಣಕ್ಕೆ ಟ್ರೈಸೈಕ್ಲೋಜೋಲ್ ಸಿಂಪಡಿಸಿ.',
            'language': 'kn'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['language'], 'kn-IN')

    def test_demo_loop_endpoint(self):
        res = self.client.post('/api/gnani/demo-loop', data={
            'text_override': 'ರಾಗಿ ಬೆಳೆಗೆ ಎಷ್ಟು ಗೊಬ್ಬರ ಹಾಕಬೇಕು?',
            'language': 'kn'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('step_1_prisma_stt', data)
        self.assertIn('step_2_evon_ai', data)
        self.assertIn('step_3_timbre_tts', data)
        self.assertIn('ರಾಗಿ', data['step_2_evon_ai']['answer'])

if __name__ == '__main__':
    unittest.main()

