from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from database.db import query_db, execute_db
from backend.auth.security import admin_required
from backend.services.notification_service import NotificationService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_farmers = query_db("SELECT COUNT(*) as cnt FROM users WHERE role = 'farmer'", one=True)['cnt']
    total_buyers = query_db("SELECT COUNT(*) as cnt FROM users WHERE role = 'buyer'", one=True)['cnt']
    total_products = query_db("SELECT COUNT(*) as cnt FROM products", one=True)['cnt']
    pending_approvals = query_db("SELECT COUNT(*) as cnt FROM products WHERE status = 'pending'", one=True)['cnt']
    
    sales_row = query_db(
        "SELECT COUNT(*) as total_orders, COALESCE(SUM(final_amount), 0) as total_revenue FROM orders WHERE status != 'cancelled'",
        one=True
    )
    total_orders = sales_row['total_orders']
    total_revenue = sales_row['total_revenue']

    pending_products = query_db(
        """SELECT p.*, u.full_name as farmer_name, c.name as category_name
           FROM products p
           JOIN users u ON p.seller_id = u.id
           JOIN product_categories c ON p.category_id = c.id
           WHERE p.status = 'pending'
           ORDER BY p.id DESC LIMIT 10"""
    )

    recent_orders = query_db(
        """SELECT o.*, u1.full_name as buyer_name, u2.full_name as farmer_name
           FROM orders o
           JOIN users u1 ON o.buyer_id = u1.id
           JOIN users u2 ON o.seller_id = u2.id
           ORDER BY o.created_at DESC LIMIT 8"""
    )

    # Category breakdown for chart
    category_counts = query_db(
        """SELECT c.name, COUNT(p.id) as product_count
           FROM product_categories c
           LEFT JOIN products p ON c.id = p.category_id
           GROUP BY c.id ORDER BY product_count DESC"""
    )

    return render_template(
        'admin/dashboard.html',
        stats={
            'farmers': total_farmers,
            'buyers': total_buyers,
            'products': total_products,
            'pending': pending_approvals,
            'orders': total_orders,
            'revenue': total_revenue
        },
        pending_products=pending_products,
        recent_orders=recent_orders,
        category_counts=category_counts
    )

@admin_bp.route('/users')
@admin_required
def users():
    role_filter = request.args.get('role', 'all')
    search = request.args.get('q', '').strip()

    query = "SELECT * FROM users WHERE 1=1"
    params = []

    if role_filter != 'all':
        query += " AND role = ?"
        params.append(role_filter)

    if search:
        query += " AND (full_name LIKE ? OR mobile LIKE ? OR email LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY id DESC"
    users_list = query_db(query, tuple(params))

    return render_template('admin/users.html', users=users_list, current_role=role_filter, search=search)

@admin_bp.route('/user/toggle-status/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    user = query_db("SELECT id, is_active, full_name FROM users WHERE id = ?", (user_id,), one=True)
    if user:
        new_status = 0 if user['is_active'] == 1 else 1
        execute_db("UPDATE users SET is_active = ? WHERE id = ?", (new_status, user_id))
        status_word = "Activated" if new_status == 1 else "Suspended"
        flash(f"User {user['full_name']} has been {status_word}.", "info")
    return redirect(url_for('admin.users'))

@admin_bp.route('/products')
@admin_required
def products():
    status = request.args.get('status', 'all')
    query = """
        SELECT p.*, u.full_name as farmer_name, c.name as category_name
        FROM products p
        JOIN users u ON p.seller_id = u.id
        JOIN product_categories c ON p.category_id = c.id
        WHERE 1=1
    """
    params = []
    if status != 'all':
        query += " AND p.status = ?"
        params.append(status)

    query += " ORDER BY p.id DESC"
    all_products = query_db(query, tuple(params))

    return render_template('admin/products.html', products=all_products, current_status=status)

@admin_bp.route('/product/approve/<int:product_id>', methods=['POST'])
@admin_required
def approve_product(product_id):
    product = query_db("SELECT * FROM products WHERE id = ?", (product_id,), one=True)
    if product:
        execute_db("UPDATE products SET status = 'active' WHERE id = ?", (product_id,))
        NotificationService.notify(
            product['seller_id'],
            "Product Approved!",
            f"Your crop listing '{product['name']}' has been approved by admin and is now active in the marketplace.",
            notif_type="product",
            link=f"/marketplace/product/{product_id}"
        )
        flash(f"Crop '{product['name']}' approved successfully.", "success")
    return redirect(request.referrer or url_for('admin.products'))

@admin_bp.route('/product/reject/<int:product_id>', methods=['POST'])
@admin_required
def reject_product(product_id):
    reason = request.form.get('reason', 'Listing did not meet agricultural verification standards.')
    product = query_db("SELECT * FROM products WHERE id = ?", (product_id,), one=True)
    if product:
        execute_db("UPDATE products SET status = 'rejected', rejection_reason = ? WHERE id = ?", (reason, product_id))
        NotificationService.notify(
            product['seller_id'],
            "Listing Notice",
            f"Your crop listing '{product['name']}' was not approved: {reason}",
            notif_type="product"
        )
        flash(f"Crop '{product['name']}' rejected.", "warning")
    return redirect(request.referrer or url_for('admin.products'))

@admin_bp.route('/orders')
@admin_required
def orders():
    orders_list = query_db(
        """SELECT o.*, u1.full_name as buyer_name, u2.full_name as farmer_name
           FROM orders o
           JOIN users u1 ON o.buyer_id = u1.id
           JOIN users u2 ON o.seller_id = u2.id
           ORDER BY o.created_at DESC"""
    )
    return render_template('admin/orders.html', orders=orders_list)

@admin_bp.route('/coupons', methods=['GET', 'POST'])
@admin_required
def coupons():
    if request.method == 'POST':
        code = request.form.get('code', '').strip().upper()
        dtype = request.form.get('discount_type', 'percent')
        dval = float(request.form.get('discount_value', 10.0))
        min_order = float(request.form.get('min_order_value', 0.0))
        max_discount = float(request.form.get('max_discount', 500.0)) if dtype == 'percent' else None
        
        try:
            execute_db(
                """INSERT INTO coupons (code, discount_type, discount_value, min_order_value, max_discount)
                   VALUES (?, ?, ?, ?, ?)""",
                (code, dtype, dval, min_order, max_discount)
            )
            flash(f"Coupon '{code}' created successfully!", "success")
        except Exception as e:
            flash(f"Error creating coupon: {str(e)}", "danger")

    coupons_list = query_db("SELECT * FROM coupons ORDER BY id DESC")
    return render_template('admin/coupons.html', coupons=coupons_list)

@admin_bp.route('/coupon/toggle/<int:coupon_id>', methods=['POST'])
@admin_required
def toggle_coupon(coupon_id):
    c = query_db("SELECT is_active FROM coupons WHERE id = ?", (coupon_id,), one=True)
    if c:
        execute_db("UPDATE coupons SET is_active = ? WHERE id = ?", (0 if c['is_active'] == 1 else 1, coupon_id))
    return redirect(url_for('admin.coupons'))

@admin_bp.route('/reports')
@admin_required
def reports():
    # Top Crops by Listings
    top_crops = query_db(
        """SELECT name, COUNT(*) as listings, SUM(stock_quantity) as total_volume, stock_unit
           FROM products GROUP BY name ORDER BY listings DESC LIMIT 5"""
    )
    # State distribution
    state_distribution = query_db(
        """SELECT state, COUNT(*) as count FROM products GROUP BY state ORDER BY count DESC LIMIT 8"""
    )
    # Revenue summary
    monthly_sales = query_db(
        """SELECT strftime('%Y-%m', created_at) as month, SUM(final_amount) as revenue, COUNT(*) as order_count
           FROM orders WHERE status != 'cancelled' GROUP BY month ORDER BY month DESC LIMIT 6"""
    )

    return render_template(
        'admin/reports.html',
        top_crops=top_crops,
        state_distribution=state_distribution,
        monthly_sales=monthly_sales
    )
