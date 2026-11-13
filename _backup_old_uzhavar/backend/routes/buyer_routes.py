import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from database.db import query_db, execute_db
from backend.auth.security import login_required
from backend.utilities.helpers import generate_order_number
from backend.services.notification_service import NotificationService

buyer_bp = Blueprint('buyer', __name__, url_prefix='/buyer')

@buyer_bp.route('/dashboard')
@login_required
def dashboard():
    buyer_id = session['user_id']
    buyer = query_db("SELECT * FROM users WHERE id = ?", (buyer_id,), one=True)
    profile = query_db("SELECT * FROM buyer_profiles WHERE user_id = ?", (buyer_id,), one=True)

    orders = query_db(
        """SELECT o.*, u.full_name as farmer_name, u.mobile as farmer_mobile
           FROM orders o
           JOIN users u ON o.seller_id = u.id
           WHERE o.buyer_id = ?
           ORDER BY o.created_at DESC""",
        (buyer_id,)
    )

    wishlist_items = query_db(
        """SELECT p.*, c.name as category_name, u.full_name as farmer_name
           FROM wishlists w
           JOIN products p ON w.product_id = p.id
           JOIN product_categories c ON p.category_id = c.id
           JOIN users u ON p.seller_id = u.id
           WHERE w.user_id = ?""",
        (buyer_id,)
    )

    total_orders = len(orders)
    total_spent = sum(o['final_amount'] for o in orders if o['status'] != 'cancelled')
    active_deliveries = sum(1 for o in orders if o['status'] in ['pending', 'confirmed', 'shipped'])

    return render_template(
        'buyer/dashboard.html',
        buyer=buyer,
        profile=profile,
        orders=orders,
        wishlist_items=wishlist_items,
        total_orders=total_orders,
        total_spent=total_spent,
        active_deliveries=active_deliveries
    )

@buyer_bp.route('/checkout/<int:product_id>', methods=['GET', 'POST'])
@login_required
def checkout(product_id):
    buyer_id = session['user_id']
    buyer = query_db("SELECT * FROM users WHERE id = ?", (buyer_id,), one=True)
    buyer_prof = query_db("SELECT * FROM buyer_profiles WHERE user_id = ?", (buyer_id,), one=True)

    product = query_db(
        """SELECT p.*, c.name as category_name, u.full_name as farmer_name, u.mobile as farmer_mobile 
           FROM products p
           JOIN product_categories c ON p.category_id = c.id
           JOIN users u ON p.seller_id = u.id
           WHERE p.id = ? AND p.status = 'active'""",
        (product_id,),
        one=True
    )
    if not product:
        flash("Product is not currently available for purchase.", "warning")
        return redirect(url_for('marketplace.index'))

    # Available coupons
    coupons = query_db("SELECT * FROM coupons WHERE is_active = 1")

    if request.method == 'POST':
        quantity = float(request.form.get('quantity', 1.0))
        delivery_address = request.form.get('delivery_address', '').strip()
        contact_phone = request.form.get('contact_phone', buyer['mobile']).strip()
        payment_method = request.form.get('payment_method', 'Cash on Delivery')
        coupon_code = request.form.get('coupon_code', '').strip().upper()
        notes = request.form.get('notes', '').strip()

        if quantity <= 0:
            flash("Please enter a valid order quantity.", "danger")
            return redirect(url_for('buyer.checkout', product_id=product_id))

        if quantity > product['stock_quantity']:
            flash(f"Requested quantity exceeds available stock ({product['stock_quantity']} {product['stock_unit']}).", "danger")
            return redirect(url_for('buyer.checkout', product_id=product_id))

        subtotal = round(quantity * float(product['price_per_unit']), 2)
        discount = 0.0

        # Apply coupon if entered
        applied_coupon = None
        if coupon_code:
            coupon = query_db("SELECT * FROM coupons WHERE code = ? AND is_active = 1", (coupon_code,), one=True)
            if coupon and subtotal >= float(coupon['min_order_value']):
                if coupon['discount_type'] == 'percent':
                    discount = round(subtotal * (float(coupon['discount_value']) / 100.0), 2)
                    if coupon['max_discount'] and discount > float(coupon['max_discount']):
                        discount = float(coupon['max_discount'])
                else:
                    discount = float(coupon['discount_value'])
                applied_coupon = coupon['code']
                execute_db("UPDATE coupons SET times_used = times_used + 1 WHERE id = ?", (coupon['id'],))

        final_amount = max(0.0, subtotal - discount)
        order_num = generate_order_number()

        # Insert Order
        order_id = execute_db(
            """INSERT INTO orders 
               (order_number, buyer_id, seller_id, total_amount, discount_amount, final_amount,
                coupon_code, status, delivery_address, contact_phone, payment_method, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?)""",
            (order_num, buyer_id, product['seller_id'], subtotal, discount, final_amount,
             applied_coupon, delivery_address, contact_phone, payment_method, notes)
        )

        # Insert Order Item
        execute_db(
            """INSERT INTO order_items 
               (order_id, product_id, product_name, unit_price, quantity, stock_unit, subtotal)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (order_id, product_id, product['name'], product['price_per_unit'], quantity, product['stock_unit'], subtotal)
        )

        # Decrement product stock
        new_stock = product['stock_quantity'] - quantity
        new_status = 'sold_out' if new_stock <= 0 else 'active'
        execute_db(
            "UPDATE products SET stock_quantity = ?, status = ? WHERE id = ?",
            (new_stock, new_status, product_id)
        )

        # Award 20 reward points to buyer
        execute_db("UPDATE users SET reward_points = reward_points + 20 WHERE id = ?", (buyer_id,))
        execute_db(
            "INSERT INTO reward_transactions (user_id, points, transaction_type, description, reference_id) VALUES (?, ?, ?, ?, ?)",
            (buyer_id, 20, 'credit', f'Order Placed #{order_num}', str(order_id))
        )

        # Notify Seller Farmer
        NotificationService.notify(
            product['seller_id'],
            "New Order Received!",
            f"You received an order for {quantity} {product['stock_unit']} of '{product['name']}' from {buyer['full_name']}.",
            notif_type="order",
            link="/farmer/orders"
        )

        flash(f"Order #{order_num} has been placed successfully! Farmer {product['farmer_name']} has been notified.", "success")
        return redirect(url_for('buyer.order_detail', order_id=order_id))

    return render_template(
        'marketplace/checkout.html',
        product=product,
        buyer=buyer,
        buyer_prof=buyer_prof,
        coupons=coupons
    )

@buyer_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    buyer_id = session['user_id']
    order = query_db(
        """SELECT o.*, u.full_name as farmer_name, u.mobile as farmer_mobile,
                  u.state as farmer_state, u.district as farmer_district
           FROM orders o
           JOIN users u ON o.seller_id = u.id
           WHERE o.id = ? AND (o.buyer_id = ? OR ? = 1)""",
        (order_id, buyer_id, 1 if session.get('role') == 'admin' else 0),
        one=True
    )
    if not order:
        flash("Order not found or unauthorized.", "danger")
        return redirect(url_for('buyer.dashboard'))

    items = query_db("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
    
    # Check if review already submitted
    reviewed_products = [
        r['product_id'] for r in query_db(
            "SELECT product_id FROM reviews WHERE buyer_id = ? AND product_id IN (SELECT product_id FROM order_items WHERE order_id = ?)",
            (buyer_id, order_id)
        )
    ]

    return render_template(
        'buyer/order_detail.html',
        order=order,
        items=items,
        reviewed_products=reviewed_products
    )
