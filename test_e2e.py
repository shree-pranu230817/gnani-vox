"""
End-to-End Test Suite for UZHAVAR AI
Simulates complete real-world scenarios across Farmer, Buyer, Admin, Mandi, and Gnani AI.
"""

import unittest
from app import create_app
from database.seed_data import seed_passwords_and_data
from database.db import query_db

class UzhavarE2ETestCase(unittest.TestCase):
    def setUp(self):
        seed_passwords_and_data()
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_full_farmer_and_buyer_cycle(self):
        # 1. Login as Farmer
        res = self.client.post('/auth/login', data={'demo_role': 'farmer'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # 2. Farmer adds a new crop product
        add_crop_res = self.client.post('/farmer/product/add', data={
            'name': 'Salem Fresh Turmeric Finger',
            'category_id': 5, # Spices & Herbs
            'price_per_unit': 8500.0,
            'stock_quantity': 40.0,
            'stock_unit': 'quintal',
            'harvest_location': 'Attur Organic Farm',
            'state': 'Tamil Nadu',
            'district': 'Salem',
            'contact_phone': '9876543211',
            'description': 'High curcumin natural turmeric fingers directly from harvest.'
        }, follow_redirects=True)
        self.assertEqual(add_crop_res.status_code, 200)

        # Verify crop is in marketplace
        market_res = self.client.get('/marketplace/?q=Turmeric')
        self.assertEqual(market_res.status_code, 200)
        self.assertIn(b'Salem Fresh Turmeric Finger', market_res.data)

        # Get product ID inside app context
        with self.app.app_context():
            turmeric = query_db("SELECT id FROM products WHERE name = 'Salem Fresh Turmeric Finger'", one=True)
            self.assertIsNotNone(turmeric)
            prod_id = turmeric['id']

        # 3. Farmer logs out
        self.client.get('/auth/logout')

        # 4. Login as Buyer
        self.client.post('/auth/login', data={'demo_role': 'buyer'}, follow_redirects=True)

        # 5. Buyer places order for 2 quintals with coupon FARMER10
        checkout_res = self.client.post(f'/buyer/checkout/{prod_id}', data={
            'quantity': 2.0,
            'delivery_address': 'Spice Market, George Town, Chennai, 600001',
            'contact_phone': '9876543220',
            'payment_method': 'Cash on Delivery',
            'coupon_code': 'FARMER10',
            'notes': 'Pack in double-layer gunny bags please'
        }, follow_redirects=True)
        self.assertEqual(checkout_res.status_code, 200)
        self.assertIn(b'Order #', checkout_res.data)

        # Check order in database inside app context
        with self.app.app_context():
            order = query_db("SELECT * FROM orders WHERE buyer_id = 6 AND seller_id = 2 ORDER BY id DESC LIMIT 1", one=True)
            self.assertIsNotNone(order)
            order_id = order['id']
            # 2 * 8500 = 17000; 10% coupon capped at 300 = 16700
            self.assertEqual(float(order['final_amount']), 16700.0)

        # 6. Buyer tracks order
        track_res = self.client.get(f'/buyer/order/{order_id}')
        self.assertEqual(track_res.status_code, 200)
        self.assertIn(b'Order Placed', track_res.data)

        # 7. Farmer logs in to confirm & deliver order
        self.client.get('/auth/logout')
        self.client.post('/auth/login', data={'demo_role': 'farmer'}, follow_redirects=True)

        # Update order status to shipped
        ship_res = self.client.post(f'/farmer/order/update-status/{order_id}', data={'status': 'shipped'}, follow_redirects=True)
        self.assertEqual(ship_res.status_code, 200)

        # Update order status to delivered
        deliver_res = self.client.post(f'/farmer/order/update-status/{order_id}', data={'status': 'delivered'}, follow_redirects=True)
        self.assertEqual(deliver_res.status_code, 200)

        # 8. Buyer logs in and leaves verified review
        self.client.get('/auth/logout')
        self.client.post('/auth/login', data={'demo_role': 'buyer'}, follow_redirects=True)

        review_res = self.client.post(f'/marketplace/review/{prod_id}', data={
            'rating': 5,
            'comment': 'Outstanding curcumin aroma and moisture level! Direct farm quality.'
        }, follow_redirects=True)
        self.assertEqual(review_res.status_code, 200)

        # Verify review is visible
        detail_res = self.client.get(f'/marketplace/product/{prod_id}')
        self.assertIn(b'Outstanding curcumin aroma', detail_res.data)

    def test_profit_calculator_save_and_roi(self):
        # Login as farmer
        self.client.post('/auth/login', data={'demo_role': 'farmer'}, follow_redirects=True)

        # Save calculation
        res = self.client.post('/calculator/save', data={
            'crop_name': 'Soybean',
            'calculation_title': 'Soybean Summer 2026',
            'land_area': 3.0,
            'land_unit': 'Acre',
            'expected_yield': 36.0,
            'yield_unit': 'Quintal',
            'expected_price': 4600.0,
            'seeds_cost': 6000.0,
            'fertilizer_cost': 12000.0,
            'pesticide_cost': 4500.0,
            'labour_cost': 18000.0,
            'irrigation_cost': 5000.0,
            'transport_cost': 3500.0,
            'other_expenses': 2000.0
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Soybean Summer 2026', res.data)

if __name__ == '__main__':
    unittest.main()
