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

from flask import Flask, render_template, jsonify, request
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
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'static')
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

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('index.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🎙️ GNANI VOX – One Voice. Many Languages. No Barriers. is running on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
