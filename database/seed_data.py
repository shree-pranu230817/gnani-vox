"""
Database seed & password reset utility for Uzhavar AI.
Sets standardized test passwords:
- Admin (9876543210): admin123
- Farmer (9876543211): farmer123
- Buyer (9876543220): buyer123
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uzhavar.db')

def seed_passwords_and_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    admin_hash = generate_password_hash('admin123')
    farmer_hash = generate_password_hash('farmer123')
    buyer_hash = generate_password_hash('buyer123')

    # Update passwords
    cur.execute("UPDATE users SET password_hash = ? WHERE role = 'admin'", (admin_hash,))
    cur.execute("UPDATE users SET password_hash = ? WHERE role = 'farmer'", (farmer_hash,))
    cur.execute("UPDATE users SET password_hash = ? WHERE role = 'buyer'", (buyer_hash,))

    # Ensure demo coupons exist
    demo_coupons = [
        ('FARMER10', 'percent', 10.0, 500.0, 300.0),
        ('KISAN10', 'percent', 10.0, 1000.0, 500.0),
        ('HARVEST50', 'fixed', 50.0, 400.0, 50.0),
        ('UZHAVAR50', 'fixed', 50.0, 500.0, 50.0),
        ('UZHAVAR100', 'fixed', 100.0, 1000.0, 100.0)
    ]

    for code, dtype, val, min_order, max_disc in demo_coupons:
        cur.execute("SELECT id FROM coupons WHERE code = ?", (code,))
        if not cur.fetchone():
            cur.execute(
                """INSERT INTO coupons (code, discount_type, discount_value, min_order_value, max_discount, is_active)
                   VALUES (?, ?, ?, ?, ?, 1)""",
                (code, dtype, val, min_order, max_disc)
            )

    conn.commit()
    conn.close()
    print("✅ Passwords & test data verified successfully!")

if __name__ == '__main__':
    seed_passwords_and_data()
