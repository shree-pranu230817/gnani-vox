from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            user_role = session.get('role')
            if user_role not in allowed_roles:
                flash(f'Access denied. This page is only available for {", ".join(allowed_roles)}.', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def farmer_required(f):
    return role_required('farmer', 'admin')(f)

def buyer_required(f):
    return role_required('buyer', 'admin')(f)

def admin_required(f):
    return role_required('admin')(f)
