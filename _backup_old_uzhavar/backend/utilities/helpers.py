import os
import uuid
import datetime
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed image extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_image(file_storage):
    """Securely save uploaded image to uploads folder and return relative URL path."""
    if not file_storage or file_storage.filename == '':
        return None
        
    if not allowed_file(file_storage.filename):
        return None

    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex[:12]}_{int(datetime.datetime.now().timestamp())}.{ext}"
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    save_path = os.path.join(upload_folder, unique_name)
    file_storage.save(save_path)
    
    return f"/uploads/{unique_name}"

def format_currency(amount):
    """Format decimal amount as Indian Rupees symbol string."""
    try:
        val = float(amount)
        # Indian numbering grouping format roughly or standard 2 decimals
        return f"₹{val:,.2f}"
    except (ValueError, TypeError):
        return f"₹0.00"

def format_date(dt):
    """Format date string or datetime object to readable Indian date."""
    if not dt:
        return ""
    try:
        if isinstance(dt, str):
            # Try parse ISO or YYYY-MM-DD
            dt = datetime.datetime.fromisoformat(dt.replace('Z', '+00:00'))
        return dt.strftime("%d %b %Y")
    except Exception:
        return str(dt)[:10]

def generate_order_number():
    """Generate a unique order reference code."""
    ts = datetime.datetime.now().strftime("%y%m%d")
    rnd = uuid.uuid4().hex[:5].upper()
    return f"ORD-{ts}-{rnd}"
