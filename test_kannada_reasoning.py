"""
Dedicated test suite verifying detailed agricultural reasoning for Kannada queries:
1. ಭತ್ತ ಬೆಳೆಯುವ ವಿದ್ಯೆ. (Detailed step-by-step paddy cultivation package of practices)
2. ಭತ್ತಕ್ಕೆ ಯಾವ ಗೊಬ್ಬರ ಹಾಕಬೇಕು? (Paddy fertilizer schedule, NPK dosage, split application)
3. ಭತ್ತಕ್ಕೆ ಎಷ್ಟು ನೀರು ಬೇಕು? (Paddy water requirements, water depth, AWD method)
4. ಭತ್ತದ ಎಲೆ ಹಳದಿಯಾಗುತ್ತಿದೆ, ಏನು ಮಾಡಬೇಕು? (Paddy yellow leaves: Zinc, Nitrogen, BLB, Iron chlorosis)
"""

import unittest
from app import create_app

class KannadaAgriculturalReasoningTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_01_paddy_cultivation_step_by_step(self):
        """1. ಭತ್ತ ಬೆಳೆಯುವ ವಿದ್ಯೆ: Must provide comprehensive step-by-step package of practices."""
        res = self.client.post('/api/gnani/chat', json={
            'prompt': 'ಭತ್ತ ಬೆಳೆಯುವ ವಿದ್ಯೆ.',
            'language': 'kn'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        ans = data['answer']
        self.assertEqual(data['category'], 'crop_cultivation')

        # Verify key steps covered
        self.assertIn('ಭೂಮಿ ಸಿದ್ಧತೆ', ans)
        self.assertIn('ಬೀಜದ ಆಯ್ಕೆ', ans)
        self.assertIn('ಸಸಿಮಡಿ', ans)
        self.assertIn('ನಾಟಿ', ans)
        self.assertIn('ನೀರು ನಿರ್ವಹಣೆ', ans)
        self.assertIn('ರಸಗೊಬ್ಬರ', ans)
        self.assertIn('ಕಟಾವು', ans)
        self.assertIn('ಜಿಲ್ಲೆ', ans)

    def test_02_paddy_fertilizer_schedule(self):
        """2. ಭತ್ತಕ್ಕೆ ಯಾವ ಗೊಬ್ಬರ ಹಾಕಬೇಕು?: Must provide NPK ratio and schedule."""
        res = self.client.post('/api/gnani/chat', json={
            'prompt': 'ಭತ್ತಕ್ಕೆ ಯಾವ ಗೊಬ್ಬರ ಹಾಕಬೇಕು?',
            'language': 'kn'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        ans = data['answer']
        self.assertEqual(data['category'], 'fertilizer_soil')

        # Verify NPK dosage and zinc
        self.assertIn('40:20:20', ans)
        self.assertIn('ಯೂರಿಯಾ', ans)
        self.assertIn('ಸತು', ans)

    def test_03_paddy_water_management(self):
        """3. ಭತ್ತಕ್ಕೆ ಎಷ್ಟು ನೀರು ಬೇಕು?: Must explain AWD and water depth."""
        res = self.client.post('/api/gnani/chat', json={
            'prompt': 'ಭತ್ತಕ್ಕೆ ಎಷ್ಟು ನೀರು ಬೇಕು?',
            'language': 'kn'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        ans = data['answer']
        self.assertEqual(data['category'], 'irrigation_water')

        # Verify water depth and AWD
        self.assertIn('1200', ans)
        self.assertIn('AWD', ans)
        self.assertIn('ಸೆಂ.ಮೀ', ans)

    def test_04_paddy_yellow_leaves_diagnosis(self):
        """4. ಭತ್ತದ ಎಲೆ ಹಳದಿಯಾಗುತ್ತಿದೆ, ಏನು ಮಾಡಬೇಕು?: Must cover Zinc deficiency, Nitrogen, BLB."""
        res = self.client.post('/api/gnani/chat', json={
            'prompt': 'ಭತ್ತದ ಎಲೆ ಹಳದಿಯಾಗುತ್ತಿದೆ, ಏನು ಮಾಡಬೇಕು?',
            'language': 'kn'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        ans = data['answer']
        self.assertEqual(data['category'], 'crop_diseases')

        # Verify diagnostic causes
        self.assertIn('ಸತು (Zinc) ಕೊರತೆ', ans)
        self.assertIn('ಖೈರಾ', ans)
        self.assertIn('ಸಾರಜನಕ', ans)
        self.assertIn('ಕರಕಲು', ans)

    def test_05_multi_turn_conversation_context(self):
        """Verify context preservation across turns (Crop, Variety, District)."""
        session_id = 'test_paddy_session_kannada'
        
        # Turn 1: Farmer mentions crop
        r1 = self.client.post('/api/gnani/chat', json={
            'prompt': 'ನಾನು ಭತ್ತ ಬೆಳೆಯುತ್ತಿದ್ದೇನೆ.',
            'language': 'kn',
            'session_id': session_id
        })
        self.assertEqual(r1.status_code, 200)

        # Turn 2: Farmer mentions variety
        r2 = self.client.post('/api/gnani/chat', json={
            'prompt': 'ತಳಿ ಬಿಪಿಟಿ 5204.',
            'language': 'kn',
            'session_id': session_id
        })
        self.assertEqual(r2.status_code, 200)
        
        # Turn 3: Farmer mentions location/district
        r3 = self.client.post('/api/gnani/chat', json={
            'prompt': 'ನನ್ನ ಊರು ಮಂಡ್ಯ.',
            'language': 'kn',
            'session_id': session_id
        })
        self.assertEqual(r3.status_code, 200)
        d3 = r3.get_json()
        mem = d3.get('memory_context', '')
        self.assertIn('Paddy', mem)
        self.assertIn('Mandya', mem)

if __name__ == '__main__':
    unittest.main()

