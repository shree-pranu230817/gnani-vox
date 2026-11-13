import os
import json
import uuid
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from database.db import query_db, execute_db
from backend.services.gnani_service import GnaniAIService
from backend.services.agri_memory import ConversationMemoryManager
from backend.auth.security import login_required
from backend.utilities.i18n import LANGUAGES, TRANSLATIONS, get_text

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Featured active products
    featured_products = query_db(
        """SELECT p.*, c.name as category_name, u.full_name as farmer_name 
           FROM products p 
           JOIN product_categories c ON p.category_id = c.id
           JOIN users u ON p.seller_id = u.id
           WHERE p.status = 'active'
           ORDER BY p.id DESC LIMIT 6"""
    )
    
    # Categories
    categories = query_db("SELECT * FROM product_categories ORDER BY name ASC")
    
    # Recent live mandi ticker prices
    recent_prices = query_db(
        "SELECT * FROM market_prices ORDER BY price_date DESC, id DESC LIMIT 8"
    )

    # Summary Statistics for Trust Counters
    total_farmers = query_db("SELECT COUNT(*) as cnt FROM users WHERE role = 'farmer'", one=True)['cnt']
    total_buyers = query_db("SELECT COUNT(*) as cnt FROM users WHERE role = 'buyer'", one=True)['cnt']
    total_crops = query_db("SELECT COUNT(*) as cnt FROM products WHERE status = 'active'", one=True)['cnt']
    total_mandis = query_db("SELECT COUNT(DISTINCT mandi_name) as cnt FROM market_prices", one=True)['cnt']

    return render_template(
        'index.html',
        featured_products=featured_products,
        categories=categories,
        recent_prices=recent_prices,
        stats={
            'farmers': total_farmers,
            'buyers': total_buyers,
            'crops': total_crops,
            'mandis': total_mandis
        }
    )

@main_bp.route('/farming-assistant')
def farming_assistant():
    """
    AI Farming Assistant – Ask Anything About Agriculture
    Full-page agricultural advisory powered by Gemini, Gnani Prisma & Gnani Timbre.
    """
    return render_template('farming_assistant.html')

@main_bp.route('/notifications')
@login_required
def notifications():
    user_id = session['user_id']
    notifs = query_db(
        "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50",
        (user_id,)
    )
    # Mark as read
    execute_db("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
    return render_template('notifications.html', notifications=notifs)

@main_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def read_all_notifications():
    user_id = session['user_id']
    execute_db("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
    return jsonify({'success': True})

# ==============================================================
# GNANI AI ASSISTANT API ENDPOINTS (Prisma, Evon, Timbre)
# ==============================================================

@main_bp.route('/api/gnani/chat', methods=['POST'])
def gnani_chat():
    """
    Agricultural Conversational AI route:
    Accepts text prompt & language, returns agricultural advisory answer.
    """
    data = request.get_json(silent=True) or request.form or {}
    prompt = data.get('prompt', '').strip()
    lang = data.get('language') or session.get('lang', 'en')

    if not prompt:
        return jsonify({'success': False, 'message': 'Please provide a question for the assistant.'}), 400

    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    session_id = data.get('session_id') or session['session_id']

    result = GnaniAIService.ask_evon(prompt, lang=lang, session_id=session_id)
    status_code = 200 if result.get('success', False) else 500
    return jsonify(result), status_code

@main_bp.route('/api/gnani/reset-session', methods=['POST'])
def gnani_reset_session():
    """Reset multi-turn conversation memory for the current session."""
    data = request.get_json(silent=True) or {}
    session_id = data.get('session_id') or session.get('session_id')
    if session_id:
        ConversationMemoryManager.clear_context(session_id)
    session['session_id'] = str(uuid.uuid4())
    return jsonify({'success': True, 'message': 'Conversation memory reset successfully.'})

@main_bp.route('/api/gnani/stt', methods=['POST'])
def gnani_stt():
    """
    Prisma Speech-to-Text (ASR) route:
    Accepts audio file, sends to Prisma, returns transcribed text.
    """
    lang = request.form.get('language') or session.get('lang', 'en')
    
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'success': False, 'error': 'Empty audio file'}), 400

    audio_bytes = audio_file.read()
    if len(audio_bytes) == 0:
        return jsonify({'success': False, 'error': 'Audio recording is empty.'}), 400

    result = GnaniAIService.speech_to_text_prisma(
        audio_bytes,
        lang=lang,
        content_type=audio_file.content_type or 'audio/wav'
    )
    status_code = 200 if result.get('success', False) else 400
    return jsonify(result), status_code

@main_bp.route('/api/gnani/tts', methods=['POST'])
def gnani_tts():
    """
    Timbre Text-to-Speech (TTS) route:
    Accepts text & language, returns generated audio stream.
    """
    data = request.get_json(silent=True) or request.form or {}
    text = data.get('text', '').strip()
    lang = data.get('language') or session.get('lang', 'en')
    voice = data.get('voice', 'female')

    if not text:
        return jsonify({'success': False, 'error': 'Text is required for TTS synthesis'}), 400

    result = GnaniAIService.text_to_speech_timbre(text, lang=lang, voice=voice)
    return jsonify(result)

@main_bp.route('/api/gnani/demo-loop', methods=['POST'])
def gnani_demo_loop():
    """
    Complete Voice Assistant Pipeline Demonstration Loop:
    Farmer Speaks -> Prisma converts to text -> Reasoning Model generates agricultural answer -> Timbre speaks the answer!
    """
    lang = request.form.get('language') or session.get('lang', 'en')
    user_prompt = ""
    prisma_res = None

    # Step 1: Prisma STT (if audio was sent)
    if 'audio' in request.files and request.files['audio'].filename != '':
        audio_bytes = request.files['audio'].read()
        prisma_res = GnaniAIService.speech_to_text_prisma(audio_bytes, lang=lang)
        if not prisma_res.get('success'):
            return jsonify({
                'success': False,
                'error': prisma_res.get('error', 'STT failed during demonstration loop'),
                'step': 'step_1_prisma_stt'
            }), 400
        user_prompt = prisma_res.get('text', '')
    
    if not user_prompt:
        user_prompt = request.form.get('text_override', '').strip()

    if not user_prompt:
        return jsonify({
            'success': False,
            'error': 'Please provide an audio recording or text question for the assistant demo.'
        }), 400

    # Step 2: Reasoning Model (uzhavar-agri-reasoner or configured Evon)
    evon_res = GnaniAIService.ask_evon(user_prompt, lang=lang)
    if not evon_res.get('success'):
        return jsonify({
            'success': False,
            'error': evon_res.get('error', 'Reasoning model failed to generate response'),
            'step': 'step_2_reasoning'
        }), 500

    evon_answer = evon_res.get('answer', '')

    # Step 3: Timbre TTS
    timbre_res = GnaniAIService.text_to_speech_timbre(evon_answer, lang=lang)

    return jsonify({
        'success': True,
        'step_1_prisma_stt': {
            'transcript': user_prompt,
            'engine': prisma_res.get('engine', 'Direct Input') if prisma_res else 'Direct Input'
        },
        'step_2_evon_ai': {
            'answer': evon_answer,
            'engine': evon_res.get('engine', 'Uzhavar Agri Reasoner')
        },
        'step_3_timbre_tts': {
            'audio_base64': timbre_res.get('audio_base64'),
            'client_speech': timbre_res.get('client_speech', True),
            'engine': timbre_res.get('engine', 'Gnani Timbre')
        },
        'language': lang
    })

# ==============================================================
# SECURE API CONNECTION STATUS & VERIFICATION ENDPOINT
# ==============================================================

@main_bp.route('/api/system/connection-status', methods=['GET', 'POST'])
def system_connection_status():
    """
    Independently verifies connection status of all external services:
      1. Google Gemini API (GEMINI_API_KEY)
      2. Gnani Prisma STT (GNANI_API_KEY)
      3. Gnani Timbre TTS (GNANI_API_KEY)
      4. data.gov.in AGMARKNET Mandi API (DATA_GOV_IN_API_KEY)

    Returns: 'Connected', 'Missing Credentials', or 'Connection Failed' for each.
    Never exposes raw API keys.
    """
    from backend.services.gemini_service import GeminiService
    from backend.services.agmarknet_service import AgmarknetService

    results = {
        'gemini': GeminiService.test_connection(),
        'gnani_prisma': GnaniAIService.test_prisma_connection(),
        'gnani_timbre': GnaniAIService.test_timbre_connection(),
        'data_gov_in': AgmarknetService.test_datagov_connection(),
    }

    # Summary table
    summary = {
        'gemini_status': results['gemini']['status'],
        'gnani_prisma_status': results['gnani_prisma']['status'],
        'gnani_timbre_status': results['gnani_timbre']['status'],
        'data_gov_in_status': results['data_gov_in']['status'],
        'details': results
    }

    return jsonify(summary), 200
