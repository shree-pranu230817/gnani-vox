"""
GNANI VOX – One Voice. Many Languages. No Barriers.
Configuration Module
Safely loads credentials from .env without exposing keys.
"""

import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    try:
        load_dotenv(env_path, override=True, encoding='utf-8')
    except Exception:
        load_dotenv(env_path, override=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'gnani-vox-voice-ai-platform-2026')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB max audio
    ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm', 'm4a', 'flac', 'aac'}
    DEFAULT_LANGUAGE = 'kn'  # Kannada is default

    # Core API Credentials
    GNANI_API_KEY = os.environ.get('GNANI_API_KEY', '').strip()
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()

    # Gnani AI Endpoints
    GNANI_BASE_URL = os.environ.get('GNANI_BASE_URL', 'https://api.vachana.ai').strip()
    GNANI_PRISMA_ENDPOINT = os.environ.get('GNANI_PRISMA_ENDPOINT', 'https://api.vachana.ai/stt/v3').strip()
    GNANI_TIMBRE_ENDPOINT = os.environ.get('GNANI_TIMBRE_ENDPOINT', 'https://api.vachana.ai/api/v1/tts/inference').strip()
    GNANI_EVON_ENDPOINT = os.environ.get('GNANI_EVON_ENDPOINT', '').strip()

    # Gemini Model Selection
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-3.5-flash-lite').strip()

    # Database Configuration (Persistent SQLite Storage)
    DB_PATH = os.path.join(BASE_DIR, 'uzhavar_conversations.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{DB_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
