"""
GNANI VOX – One Voice. Many Languages. No Barriers.
Multilingual Voice AI Platform Powered by Gnani AI
Main Flask Application Entry Point
"""

import os
import sys

# Force UTF-8 encoding on standard I/O streams for Windows compatibility
if sys.platform.startswith('win'):
    try:
        if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Force pure-Python SQLAlchemy mode to comply with Windows security policies
os.environ['DISABLE_SQLALCHEMY_CEXT'] = '1'

from flask import Flask, render_template, jsonify, request, send_from_directory
from config import Config
from models import db, Conversation, Message
from routes.translation import translation_bp
from routes.farming import farming_bp
from services.languages import SUPPORTED_LANGUAGES
from services.prisma_service import PrismaService
from services.timbre_service import TimbreService
from services.evon_service import EvonService
from services.gemini_service import GeminiService

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))

    template_candidates = [
        os.path.join(base_dir, 'templates'),
        os.path.join(base_dir, 'api', 'templates'),
        os.path.join(os.getcwd(), 'templates'),
        os.path.join(os.getcwd(), 'api', 'templates')
    ]
    template_folder = next((p for p in template_candidates if os.path.isdir(p)), template_candidates[0])

    static_candidates = [
        os.path.join(base_dir, 'static'),
        os.path.join(base_dir, 'api', 'static'),
        os.path.join(os.getcwd(), 'static'),
        os.path.join(os.getcwd(), 'api', 'static')
    ]
    static_folder = next((p for p in static_candidates if os.path.isdir(p)), static_candidates[0])

    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder,
        static_url_path='/static'
    )
    app.config.from_object(Config)

    # Initialize SQLite Database & SQLAlchemy ORM
    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.warning(f"Database initialization notice: {e}")

    # Ensure uploads directory exists
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except Exception as e:
        app.logger.warning(f"Uploads directory notice: {e}")

    # Explicit fallback route for static assets in serverless environments
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        for s_dir in static_candidates:
            target = os.path.join(s_dir, filename)
            if os.path.isfile(target):
                return send_from_directory(s_dir, filename)
        return jsonify({'error': f'Static file {filename} not found'}), 404

    # Register Blueprints
    app.register_blueprint(translation_bp)
    app.register_blueprint(farming_bp)

    # Global Template Context Processor
    @app.context_processor
    def inject_global_template_data():
        return {
            'languages': SUPPORTED_LANGUAGES,
            'default_lang': 'kn',
            'app_title': 'GNANI VOX – One Voice. Many Languages. No Barriers.',
            'app_tagline': 'One Voice. Many Languages. No Barriers.',
            'app_subtitle': 'AI-Powered Communication and Agricultural Guidance Platform',
            'brand_desc': 'GNANI VOX connects people through intelligent multilingual voice translation and provides farmers with accessible AI-powered agricultural guidance.'
        }

    # ==========================================================
    # USER-FACING APPLICATION SCREENS (MAIN FEATURES)
    # ==========================================================
    @app.route('/')
    def index():
        """
        Homepage with two main feature cards:
        1. VoxConnect – Universal Voice Translator
        2. KrishiGuide AI – Farmer Guidance Assistant
        """
        return render_template('index.html')

    @app.route('/voxconnect')
    @app.route('/farmer-translator')
    def voxconnect_screen():
        """
        Feature 1: VoxConnect – Universal Voice Translator
        Universal voice and conversation translation for all users.
        """
        return render_template('voxconnect.html')

    @app.route('/krishiguide')
    @app.route('/farming-assistant')
    def krishiguide_screen():
        """
        Feature 2: KrishiGuide AI – Farmer Guidance Assistant
        Voice-enabled agricultural intelligence with continuous memory.
        """
        return render_template('krishiguide.html')

    @app.route('/about')
    def about_screen():
        """
        About GNANI VOX – Architecture, Gnani AI Integration & Mission.
        """
        return render_template('about.html')

    # ==========================================================
    # SYSTEM STATUS & SECURE API VERIFICATION ENDPOINT
    # ==========================================================
    @app.route('/api/system/status', methods=['GET', 'POST'])
    def system_status():
        """
        Inspects real connection status of all services without leaking secrets.
        """
        gemini_stat = GeminiService.test_connection()
        prisma_stat = PrismaService.test_connection()
        timbre_stat = TimbreService.test_connection()
        evon_stat = EvonService.test_connection()

        return jsonify({
            'gemini': gemini_stat,
            'prisma': prisma_stat,
            'timbre': timbre_stat,
            'evon': evon_stat,
            'overall_status': 'Ready' if gemini_stat.get('status') == 'Connected' else 'Partial'
        })

    # ==========================================================
    # DEBUG ENDPOINT — logs all Vercel WSGI environ headers
    # ==========================================================
    @app.route('/api/debug/env', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'])
    def debug_env():
        import json as _json
        env_snapshot = {
            k: str(v) for k, v in request.environ.items()
            if isinstance(v, (str, int, float, bool, type(None)))
            and not k.startswith(('wsgi.', 'werkzeug.'))
        }
        return jsonify({
            'method': request.method,
            'path': request.path,
            'content_type': request.content_type,
            'form_keys': list(request.form.keys()),
            'json_body': request.get_json(silent=True),
            'files': list(request.files.keys()),
            'environ_headers': env_snapshot
        }), 200

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('index.html'), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        """Return JSON for API routes, HTML for page routes."""
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Method Not Allowed',
                'method': request.method,
                'path': request.path,
                'allowed': list(e.valid_methods or [])
            }), 405
        return render_template('index.html'), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal server error', 'detail': str(e)}), 500

    return app

class VercelPathFixerMiddleware:
    """
    Middleware to fix PATH_INFO and REQUEST_METHOD on Vercel serverless.
    Vercel's Python adapter routes all requests through /api/index, so we
    restore the original path and HTTP method from forwarded headers.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # 1. Restore original URL path from Vercel forwarded headers
        original_path = (
            environ.get('HTTP_X_FORWARDED_URI') or
            environ.get('HTTP_X_MATCHED_PATH') or
            environ.get('HTTP_X_NOW_ROUTE') or
            environ.get('HTTP_X_VERCEL_REWRITE_PATH') or
            environ.get('HTTP_X_ORIGINAL_URI')
        )
        if original_path:
            # Strip query string from path
            path_only = original_path.split('?')[0]
            # Also restore QUERY_STRING if present in the forwarded URI
            if '?' in original_path:
                environ['QUERY_STRING'] = original_path.split('?', 1)[1]
            environ['PATH_INFO'] = path_only
        elif environ.get('PATH_INFO') in ('/api/index', '/api', '/api/index.py', ''):
            environ['PATH_INFO'] = '/'

        # 2. Restore original HTTP method — Vercel sometimes passes method override headers
        # Also check if body has _method field for method override
        orig_method = (
            environ.get('HTTP_X_HTTP_METHOD_OVERRIDE') or
            environ.get('HTTP_X_METHOD_OVERRIDE') or
            environ.get('HTTP_X_ORIGINAL_METHOD') or
            environ.get('HTTP_ACCESS_CONTROL_REQUEST_METHOD')
        )
        # Only override GET/HEAD with the found method (never downgrade POST)
        current_method = environ.get('REQUEST_METHOD', 'GET').upper()
        if orig_method and current_method in ('GET', 'HEAD'):
            environ['REQUEST_METHOD'] = orig_method.upper()

        return self.wsgi_app(environ, start_response)

app = create_app()
app.wsgi_app = VercelPathFixerMiddleware(app.wsgi_app)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🎙️ GNANI VOX – One Voice. Many Languages. No Barriers. is running on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
