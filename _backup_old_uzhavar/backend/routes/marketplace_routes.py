from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from database.db import query_db, execute_db
from backend.auth.security import login_required

marketplace_bp = Blueprint('marketplace', __name__, url_prefix='/marketplace')

@marketplace_bp.route('/')
def index():
    search = request.args.get('q', '').strip()
    category_id = request.args.get('category')
    state = request.args.get('state')
    district = request.args.get('district')
    sort_by = request.args.get('sort', 'newest')

    query = """
        SELECT p.*, c.name as category_name, c.icon as category_icon, 
               u.full_name as farmer_name, u.mobile as farmer_mobile,
               COALESCE(AVG(r.rating), 5.0) as avg_rating,
               COUNT(r.id) as review_count
        FROM products p
        JOIN product_categories c ON p.category_id = c.id
        JOIN users u ON p.seller_id = u.id
        LEFT JOIN reviews r ON p.id = r.product_id
        WHERE p.status = 'active'
    """
    params = []

    if search:
        query += " AND (p.name LIKE ? OR p.harvest_location LIKE ? OR p.description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    if category_id and category_id.isdigit():
        query += " AND p.category_id = ?"
        params.append(int(category_id))

    if state and state != 'All':
        query += " AND p.state = ?"
        params.append(state)

    if district and district != 'All':
        query += " AND p.district = ?"
        params.append(district)

    query += " GROUP BY p.id"

    if sort_by == 'price_low':
        query += " ORDER BY p.price_per_unit ASC"
    elif sort_by == 'price_high':
        query += " ORDER BY p.price_per_unit DESC"
    else:
        query += " ORDER BY p.id DESC"

    products = query_db(query, tuple(params))
    categories = query_db("SELECT * FROM product_categories ORDER BY name ASC")
    states = [r['state'] for r in query_db("SELECT DISTINCT state FROM products WHERE status = 'active' ORDER BY state ASC")]

    return render_template(
        'marketplace/index.html',
        products=products,
        categories=categories,
        states=states,
        current_category=category_id,
        current_state=state,
        current_sort=sort_by,
        search_query=search
    )

@marketplace_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = query_db(
        """SELECT p.*, c.name as category_name, 
                  u.full_name as farmer_name, u.mobile as farmer_mobile, u.email as farmer_email,
                  u.state as farmer_state, u.district as farmer_district, u.reward_points as farmer_points,
                  fp.farm_size_acres, fp.primary_crops, fp.bio as farmer_bio
           FROM products p
           JOIN product_categories c ON p.category_id = c.id
           JOIN users u ON p.seller_id = u.id
           LEFT JOIN farmer_profiles fp ON u.id = fp.user_id
           WHERE p.id = ?""",
        (product_id,),
        one=True
    )
    if not product:
        flash("Product not found.", "warning")
        return redirect(url_for('marketplace.index'))

    reviews = query_db(
        """SELECT r.*, u.full_name as reviewer_name 
           FROM reviews r
           JOIN users u ON r.buyer_id = u.id
           WHERE r.product_id = ?
           ORDER BY r.created_at DESC""",
        (product_id,)
    )

    avg_rating_row = query_db(
        "SELECT AVG(rating) as avg_r, COUNT(*) as cnt FROM reviews WHERE product_id = ?",
        (product_id,),
        one=True
    )
    avg_rating = round(avg_rating_row['avg_r'], 1) if avg_rating_row and avg_rating_row['avg_r'] else 5.0
    review_count = avg_rating_row['cnt'] if avg_rating_row else 0

    # Related products from same category
    related_products = query_db(
        """SELECT p.*, c.name as category_name, u.full_name as farmer_name
           FROM products p
           JOIN product_categories c ON p.category_id = c.id
           JOIN users u ON p.seller_id = u.id
           WHERE p.category_id = ? AND p.id != ? AND p.status = 'active'
           LIMIT 3""",
        (product['category_id'], product_id)
    )

    is_wishlisted = False
    if 'user_id' in session:
        w = query_db("SELECT id FROM wishlists WHERE user_id = ? AND product_id = ?", (session['user_id'], product_id), one=True)
        is_wishlisted = bool(w)

    return render_template(
        'marketplace/product_detail.html',
        product=product,
        reviews=reviews,
        avg_rating=avg_rating,
        review_count=review_count,
        related_products=related_products,
        is_wishlisted=is_wishlisted
    )

@marketplace_bp.route('/review/<int:product_id>', methods=['POST'])
@login_required
def submit_review(product_id):
    buyer_id = session['user_id']
    rating = int(request.form.get('rating', 5))
    comment = request.form.get('comment', '').strip()

    if rating < 1 or rating > 5:
        rating = 5

    execute_db(
        "INSERT INTO reviews (product_id, buyer_id, rating, comment) VALUES (?, ?, ?, ?)",
        (product_id, buyer_id, rating, comment)
    )

    # Award 10 reward points for contributing a helpful review
    execute_db("UPDATE users SET reward_points = reward_points + 10 WHERE id = ?", (buyer_id,))
    execute_db(
        "INSERT INTO reward_transactions (user_id, points, transaction_type, description) VALUES (?, ?, ?, ?)",
        (buyer_id, 10, 'credit', 'Product Review Reward')
    )

    flash("Thank you! Your verified review and rating have been posted (+10 reward points earned!).", "success")
    return redirect(url_for('marketplace.product_detail', product_id=product_id))

@marketplace_bp.route('/wishlist/toggle/<int:product_id>', methods=['POST'])
@login_required
def toggle_wishlist(product_id):
    user_id = session['user_id']
    existing = query_db("SELECT id FROM wishlists WHERE user_id = ? AND product_id = ?", (user_id, product_id), one=True)
    if existing:
        execute_db("DELETE FROM wishlists WHERE id = ?", (existing['id'],))
        return jsonify({'wishlisted': False, 'message': 'Removed from wishlist'})
    else:
        execute_db("INSERT INTO wishlists (user_id, product_id) VALUES (?, ?)", (user_id, product_id))
        return jsonify({'wishlisted': True, 'message': 'Added to wishlist'})
