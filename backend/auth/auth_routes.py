from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import query_db, execute_db
from backend.auth.security import login_required
from backend.utilities.i18n import LANGUAGES

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect_by_role(session.get('role'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '').strip()
        demo_role = request.form.get('demo_role')

        # Fast Demo Login shortcut for competition testing
        if demo_role in ['admin', 'farmer', 'buyer']:
            user = query_db("SELECT * FROM users WHERE role = ? AND is_active = 1 LIMIT 1", (demo_role,), one=True)
            if user:
                set_user_session(user)
                flash(f"Welcome to Uzhavar AI Demo as {user['full_name']} ({user['role'].title()})!", "success")
                return redirect_by_role(user['role'])

        if not identifier or not password:
            flash("Please enter your mobile number or email and password.", "danger")
            return render_template('auth/login.html')

        user = query_db(
            "SELECT * FROM users WHERE (mobile = ? OR email = ?) AND is_active = 1",
            (identifier, identifier),
            one=True
        )

        if user and check_password_hash(user['password_hash'], password):
            set_user_session(user)
            flash(f"Welcome back, {user['full_name']}!", "success")
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect_by_role(user['role'])
        else:
            flash("Invalid mobile/email or password. Please try again.", "danger")

    return render_template('auth/login.html')

def set_user_session(user):
    session['user_id'] = user['id']
    session['full_name'] = user['full_name']
    session['role'] = user['role']
    session['mobile'] = user['mobile']
    session['state'] = user['state']
    session['district'] = user['district']
    session['reward_points'] = user['reward_points']
    session['lang'] = user['preferred_language'] or 'en'

def redirect_by_role(role):
    if role == 'farmer':
        return redirect(url_for('farmer.dashboard'))
    elif role == 'buyer':
        return redirect(url_for('buyer.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect_by_role(session.get('role'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        mobile = request.form.get('mobile', '').strip()
        email = request.form.get('email', '').strip() or None
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'farmer').strip()
        state = request.form.get('state', '').strip()
        district = request.form.get('district', '').strip()
        village = request.form.get('village', '').strip()
        preferred_lang = request.form.get('preferred_language', 'en').strip()

        # Validation
        if not full_name or not mobile or not password or not state or not district:
            flash("Please fill in all required fields (Name, Mobile, Password, State, District).", "danger")
            return render_template('auth/register.html', languages=LANGUAGES)

        if role not in ['farmer', 'buyer']:
            role = 'farmer'

        # Check existing mobile or email
        existing_user = query_db(
            "SELECT id FROM users WHERE mobile = ? OR (email IS NOT NULL AND email = ?)",
            (mobile, email),
            one=True
        )
        if existing_user:
            flash("A user with this mobile number or email already exists. Please login instead.", "warning")
            return redirect(url_for('auth.login'))

        # Hash password and insert
        hashed = generate_password_hash(password)
        try:
            user_id = execute_db(
                """INSERT INTO users 
                   (full_name, mobile, email, password_hash, role, state, district, village, preferred_language, reward_points) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 50)""",
                (full_name, mobile, email, hashed, role, state, district, village, preferred_lang)
            )

            # Insert role specific profile
            if role == 'farmer':
                farm_size = float(request.form.get('farm_size_acres', 0.0) or 0.0)
                primary_crops = request.form.get('primary_crops', '')
                upi_id = request.form.get('upi_id', '')
                execute_db(
                    "INSERT INTO farmer_profiles (user_id, farm_size_acres, primary_crops, upi_id) VALUES (?, ?, ?, ?)",
                    (user_id, farm_size, primary_crops, upi_id)
                )
            else:
                business_name = request.form.get('business_name', '')
                delivery_address = request.form.get('delivery_address', f"{village}, {district}, {state}")
                execute_db(
                    "INSERT INTO buyer_profiles (user_id, business_name, delivery_address) VALUES (?, ?, ?)",
                    (user_id, business_name, delivery_address)
                )

            # Welcome notification + 50 signup points
            execute_db(
                "INSERT INTO notifications (user_id, title, message, type, link) VALUES (?, ?, ?, ?, ?)",
                (user_id, "Welcome to Uzhavar AI!", "You have received 50 bonus reward points for joining our agricultural family.", "reward", "/auth/profile")
            )
            execute_db(
                "INSERT INTO reward_transactions (user_id, points, transaction_type, description) VALUES (?, ?, ?, ?)",
                (user_id, 50, "credit", "Welcome Bonus Points")
            )

            # Auto login
            new_user = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
            set_user_session(new_user)
            flash("Registration successful! Welcome to Uzhavar AI.", "success")
            return redirect_by_role(role)

        except Exception as e:
            flash(f"Error registering user: {str(e)}", "danger")
            return render_template('auth/register.html', languages=LANGUAGES)

    return render_template('auth/register.html', languages=LANGUAGES)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been safely logged out. See you soon!", "info")
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    user = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    
    farmer_prof = None
    buyer_prof = None
    if user['role'] == 'farmer':
        farmer_prof = query_db("SELECT * FROM farmer_profiles WHERE user_id = ?", (user_id,), one=True)
    elif user['role'] == 'buyer':
        buyer_prof = query_db("SELECT * FROM buyer_profiles WHERE user_id = ?", (user_id,), one=True)

    reward_history = query_db(
        "SELECT * FROM reward_transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
        (user_id,)
    )

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip() or None
        state = request.form.get('state', '').strip()
        district = request.form.get('district', '').strip()
        village = request.form.get('village', '').strip()
        preferred_lang = request.form.get('preferred_language', 'en')

        execute_db(
            """UPDATE users SET full_name = ?, email = ?, state = ?, district = ?, 
               village = ?, preferred_language = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?""",
            (full_name, email, state, district, village, preferred_lang, user_id)
        )

        session['full_name'] = full_name
        session['lang'] = preferred_lang

        if user['role'] == 'farmer':
            farm_size = float(request.form.get('farm_size_acres', 0.0) or 0.0)
            primary_crops = request.form.get('primary_crops', '')
            upi_id = request.form.get('upi_id', '')
            bio = request.form.get('bio', '')
            execute_db(
                "UPDATE farmer_profiles SET farm_size_acres = ?, primary_crops = ?, upi_id = ?, bio = ? WHERE user_id = ?",
                (farm_size, primary_crops, upi_id, bio, user_id)
            )
        elif user['role'] == 'buyer':
            business_name = request.form.get('business_name', '')
            delivery_address = request.form.get('delivery_address', '')
            execute_db(
                "UPDATE buyer_profiles SET business_name = ?, delivery_address = ? WHERE user_id = ?",
                (business_name, delivery_address, user_id)
            )

        flash("Your profile has been updated successfully!", "success")
        return redirect(url_for('auth.profile'))

    return render_template(
        'auth/profile.html',
        user=user,
        farmer_prof=farmer_prof,
        buyer_prof=buyer_prof,
        reward_history=reward_history,
        languages=LANGUAGES
    )

@auth_bp.route('/set-language/<lang_code>')
def set_language(lang_code):
    if lang_code in LANGUAGES:
        session['lang'] = lang_code
        if 'user_id' in session:
            execute_db("UPDATE users SET preferred_language = ? WHERE id = ?", (lang_code, session['user_id']))
    
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    return redirect(url_for('main.index'))
