"""
Comprehensive Automated Test Suite for UZHAVAR AI
Tests all routes, services, auth flows, and Gnani AI APIs
"""

import unittest
from app import create_app
from database.seed_data import seed_passwords_and_data

class UzhavarAITestCase(unittest.TestCase):
    def setUp(self):
        seed_passwords_and_data()
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_01_homepage(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'UZHAVAR AI', res.data)

    def test_02_multilingual_switch(self):
        # Switch to Tamil
        res = self.client.get('/auth/set-language/ta', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn('உழவர் AI'.encode('utf-8'), res.data)

        # Switch to Hindi
        res = self.client.get('/auth/set-language/hi', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn('उझवर AI'.encode('utf-8'), res.data)

        # Switch back to English
        res = self.client.get('/auth/set-language/en', follow_redirects=True)
        self.assertEqual(res.status_code, 200)

    def test_03_marketplace(self):
        res = self.client.get('/marketplace/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Paddy', res.data)

        # Product detail
        res2 = self.client.get('/marketplace/product/1')
        self.assertEqual(res2.status_code, 200)
        self.assertIn(b'Organic Ponni Paddy', res2.data)

    def test_04_mandi_prices(self):
        res = self.client.get('/mandi/prices')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'AGMARKNET', res.data)
        self.assertIn(b'Modal Price', res.data)

    def test_05_profit_calculator(self):
        res = self.client.get('/calculator/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Profit Calculator', res.data)

    def test_06_gnani_ai_evon_chat(self):
        # Test English
        res = self.client.post('/api/gnani/chat', json={
            'prompt': 'How to control paddy blast disease?',
            'language': 'en'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('blast', data['answer'].lower())

        # Test Tamil
        res_ta = self.client.post('/api/gnani/chat', json={
            'prompt': 'நெல் பயிரில் குலை நோயை கட்டுப்படுத்த என்ன செய்ய வேண்டும்?',
            'language': 'ta'
        })
        self.assertEqual(res_ta.status_code, 200)
        data_ta = res_ta.get_json()
        self.assertTrue(data_ta['success'])
        self.assertIn('ட்ரைசைக்ளசோல்', data_ta['answer'])

    def test_07_gnani_ai_demo_loop(self):
        # Full 3-step loop demonstration
        res = self.client.post('/api/gnani/demo-loop', data={
            'text_override': 'What is the best fertilizer for cotton?',
            'language': 'en'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('step_1_prisma_stt', data)
        self.assertIn('step_2_evon_ai', data)
        self.assertIn('step_3_timbre_tts', data)

    def test_08_farmer_flow(self):
        # Demo login as farmer
        login_res = self.client.post('/auth/login', data={'demo_role': 'farmer'}, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Farmer Portal', login_res.data)

        # Farmer orders page
        orders_res = self.client.get('/farmer/orders')
        self.assertEqual(orders_res.status_code, 200)

    def test_09_buyer_flow(self):
        # Demo login as buyer
        login_res = self.client.post('/auth/login', data={'demo_role': 'buyer'}, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Buyer Portal', login_res.data)

    def test_10_admin_flow(self):
        # Demo login as admin
        login_res = self.client.post('/auth/login', data={'demo_role': 'admin'}, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Admin Control Center', login_res.data)

        # Admin products & users
        users_res = self.client.get('/admin/users')
        self.assertEqual(users_res.status_code, 200)

        prods_res = self.client.get('/admin/products')
        self.assertEqual(prods_res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
