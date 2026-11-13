import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from database.db import query_db, execute_db
from backend.auth.security import farmer_required
from backend.utilities.helpers import save_uploaded_image
from backend.services.notification_service import NotificationService

farmer_bp = Blueprint('farmer', __name__, url_prefix='/farmer')

@farmer_bp.route('/dashboard')
@farmer_required
def dashboard():
    farmer_id = session['user_id']
    farmer = query_db("SELECT * FROM users WHERE id = ?", (farmer_id,), one=True)
    profile = query_db("SELECT * FROM farmer_profiles WHERE user_id = ?", (farmer_id,), one=True)

    # Products summary
    products = query_db(
        """SELECT p.*, c.name as category_name 
           FROM products p 
           JOIN product_categories c ON p.category_id = c.id
           WHERE p.seller_id = ?
           ORDER BY p.id DESC""",
        (farmer_id,)
    )

    # Orders received
    orders = query_db(
        """SELECT o.*, u.full_name as buyer_name, u.mobile as buyer_mobile
           FROM orders o
           JOIN users u ON o.buyer_id = u.id
           WHERE o.seller_id = ?
           ORDER BY o.created_at DESC LIMIT 10""",
        (farmer_id,)
    )

    # Metrics
    total_listings = len(products)
    total_sales = query_db(
        "SELECT COALESCE(SUM(final_amount), 0) as total FROM orders WHERE seller_id = ? AND status != 'cancelled'",
        (farmer_id,),
        one=True
    )['total']
    total_orders_count = query_db(
        "SELECT COUNT(*) as cnt FROM orders WHERE seller_id = ?",
        (farmer_id,),
        one=True
    )['cnt']

    return render_template(
        'farmer/dashboard.html',
        farmer=farmer,
        profile=profile,
        products=products,
        orders=orders,
        total_listings=total_listings,
        total_sales=total_sales,
        total_orders_count=total_orders_count
    )

@farmer_bp.route('/product/add', methods=['GET', 'POST'])
@farmer_required
def add_product():
    farmer_id = session['user_id']
    farmer = query_db("SELECT * FROM users WHERE id = ?", (farmer_id,), one=True)
    categories = query_db("SELECT * FROM product_categories ORDER BY name ASC")

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_id = int(request.form.get('category_id', 1))
        description = request.form.get('description', '').strip()
        price_per_unit = float(request.form.get('price_per_unit', 0))
        stock_quantity = float(request.form.get('stock_quantity', 0))
        stock_unit = request.form.get('stock_unit', 'quintal')
        harvest_location = request.form.get('harvest_location', '').strip()
        state = request.form.get('state', farmer['state']).strip()
        district = request.form.get('district', farmer['district']).strip()
        village = request.form.get('village', farmer['village'] or '').strip()
        latitude = float(request.form.get('latitude', 11.1271))
        longitude = float(request.form.get('longitude', 78.6569))
        harvest_date = request.form.get('harvest_date') or None
        expected_availability = request.form.get('expected_availability') or None
        contact_phone = request.form.get('contact_phone', farmer['mobile']).strip()

        # Handle Image Upload
        image_url = "/static/images/crops/default_crop.jpg"
        if 'image' in request.files:
            uploaded = save_uploaded_image(request.files['image'])
            if uploaded:
                image_url = uploaded

        try:
            prod_id = execute_db(
                """INSERT INTO products 
                   (seller_id, category_id, name, description, price_per_unit, stock_quantity, stock_unit,
                    image_url, harvest_location, state, district, village, latitude, longitude,
                    harvest_date, expected_availability, contact_phone, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')""",
                (farmer_id, category_id, name, description, price_per_unit, stock_quantity, stock_unit,
                 image_url, harvest_location, state, district, village, latitude, longitude,
                 harvest_date, expected_availability, contact_phone)
            )

            # Award 20 reward points to the farmer for listing farm produce
            execute_db("UPDATE users SET reward_points = reward_points + 20 WHERE id = ?", (farmer_id,))
            execute_db(
                "INSERT INTO reward_transactions (user_id, points, transaction_type, description, reference_id) VALUES (?, ?, ?, ?, ?)",
                (farmer_id, 20, 'credit', f'Crop Listing: {name}', str(prod_id))
            )

            NotificationService.notify(
                farmer_id,
                "Crop Listed Successfully!",
                f"Your crop '{name}' is now live in the marketplace. You earned +20 reward points!",
                notif_type="product",
                link=f"/marketplace/product/{prod_id}"
            )

            flash(f"Crop '{name}' has been successfully listed in the marketplace! (+20 Reward Points)", "success")
            return redirect(url_for('farmer.dashboard'))

        except Exception as e:
            flash(f"Failed to add crop: {str(e)}", "danger")

    return render_template('farmer/add_product.html', categories=categories, farmer=farmer)

@farmer_bp.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
@farmer_required
def edit_product(product_id):
    farmer_id = session['user_id']
    product = query_db("SELECT * FROM products WHERE id = ? AND seller_id = ?", (product_id, farmer_id), one=True)
    if not product:
        flash("Product not found or unauthorized.", "warning")
        return redirect(url_for('farmer.dashboard'))

    categories = query_db("SELECT * FROM product_categories ORDER BY name ASC")

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_id = int(request.form.get('category_id', 1))
        description = request.form.get('description', '').strip()
        price_per_unit = float(request.form.get('price_per_unit', 0))
        stock_quantity = float(request.form.get('stock_quantity', 0))
        stock_unit = request.form.get('stock_unit', 'quintal')
        harvest_location = request.form.get('harvest_location', '').strip()
        state = request.form.get('state', '').strip()
        district = request.form.get('district', '').strip()
        harvest_date = request.form.get('harvest_date') or None
        expected_availability = request.form.get('expected_availability') or None
        status = request.form.get('status', 'active')

        image_url = product['image_url']
        if 'image' in request.files and request.files['image'].filename != '':
            uploaded = save_uploaded_image(request.files['image'])
            if uploaded:
                image_url = uploaded

        execute_db(
            """UPDATE products 
               SET name = ?, category_id = ?, description = ?, price_per_unit = ?, stock_quantity = ?,
                   stock_unit = ?, harvest_location = ?, state = ?, district = ?, harvest_date = ?,
                   expected_availability = ?, status = ?, image_url = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ? AND seller_id = ?""",
            (name, category_id, description, price_per_unit, stock_quantity, stock_unit,
             harvest_location, state, district, harvest_date, expected_availability, status, image_url,
             product_id, farmer_id)
        )

        flash(f"Crop '{name}' updated successfully!", "success")
        return redirect(url_for('farmer.dashboard'))

    return render_template('farmer/edit_product.html', product=product, categories=categories)

@farmer_bp.route('/product/delete/<int:product_id>', methods=['POST'])
@farmer_required
def delete_product(product_id):
    farmer_id = session['user_id']
    prod = query_db("SELECT name FROM products WHERE id = ? AND seller_id = ?", (product_id, farmer_id), one=True)
    if prod:
        execute_db("DELETE FROM products WHERE id = ? AND seller_id = ?", (product_id, farmer_id))
        flash(f"Crop '{prod['name']}' has been removed.", "info")
    return redirect(url_for('farmer.dashboard'))

@farmer_bp.route('/orders')
@farmer_required
def orders():
    farmer_id = session['user_id']
    orders_list = query_db(
        """SELECT o.*, u.full_name as buyer_name, u.mobile as buyer_mobile 
           FROM orders o
           JOIN users u ON o.buyer_id = u.id
           WHERE o.seller_id = ?
           ORDER BY o.created_at DESC""",
        (farmer_id,)
    )
    return render_template('farmer/orders.html', orders=orders_list)

@farmer_bp.route('/order/update-status/<int:order_id>', methods=['POST'])
@farmer_required
def update_order_status(order_id):
    farmer_id = session['user_id']
    new_status = request.form.get('status')
    
    order = query_db("SELECT * FROM orders WHERE id = ? AND seller_id = ?", (order_id, farmer_id), one=True)
    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for('farmer.orders'))

    if new_status in ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']:
        payment_status = 'paid' if new_status == 'delivered' else order['payment_status']
        execute_db(
            "UPDATE orders SET status = ?, payment_status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_status, payment_status, order_id)
        )

        # Notify buyer
        NotificationService.notify(
            order['buyer_id'],
            f"Order Status Update: {new_status.title()}",
            f"Your order #{order['order_number']} is now {new_status.upper()}.",
            notif_type="order",
            link=f"/buyer/order/{order_id}"
        )

        # Reward farmer for delivering order
        if new_status == 'delivered':
            execute_db("UPDATE users SET reward_points = reward_points + 50 WHERE id = ?", (farmer_id,))
            execute_db(
                "INSERT INTO reward_transactions (user_id, points, transaction_type, description, reference_id) VALUES (?, ?, ?, ?, ?)",
                (farmer_id, 50, 'credit', f"Order Delivered: #{order['order_number']}", str(order_id))
            )

        flash(f"Order #{order['order_number']} updated to {new_status.title()}.", "success")

    return redirect(url_for('farmer.orders'))
