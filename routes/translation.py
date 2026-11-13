"""
UZHAVAR AI – Kannada Voice Bridge
Voice Translation Routes (Farmer & Daily-Wage Worker Translators)
"""

import os
import time
import logging
from flask import Blueprint, request, jsonify, current_app
from services.prisma_service import PrismaService
from services.timbre_service import TimbreService
from services.gemini_service import GeminiService
from services.conversation_service import ConversationService
from services.audio_controller import AudioController
from services.languages import SUPPORTED_LANGUAGES, get_dialect_code

translation_bp = Blueprint('translation', __name__)
logger = logging.getLogger("uzhavar.perf")

@translation_bp.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """
    POST /api/transcribe
    Converts speech audio into text via Gnani Prisma STT API.
    """
    lang = request.form.get('language', 'kn')
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    valid, err_msg = AudioController.validate_audio_file(audio_file)
    if not valid:
        return jsonify({'success': False, 'error': err_msg}), 400

    audio_bytes = audio_file.read()
    content_type = audio_file.content_type or 'audio/wav'
    result = PrismaService.transcribe(audio_bytes, lang=lang, content_type=content_type)
    return jsonify(result), 200 if result.get('success') else 400

@translation_bp.route('/api/translate', methods=['POST'])
def translate_text():
    """
    POST /api/translate
    Translates text between Indian languages preserving domain terminology.
    """
    data = request.get_json(silent=True) or request.form or {}
    text = (data.get('text') or '').strip()
    source_lang = data.get('source_lang', 'kn')
    target_lang = data.get('target_lang', 'en')
    domain = data.get('domain', 'farmer')  # 'farmer' or 'worker'

    if not text:
        return jsonify({'success': False, 'error': 'Text is required for translation'}), 400

    result = GeminiService.translate(text, source_lang, target_lang, domain=domain)
    return jsonify(result), 200 if result.get('success') else 500

@translation_bp.route('/api/synthesize', methods=['POST'])
def synthesize_speech():
    """
    POST /api/synthesize
    Generates spoken audio from text via Gnani Timbre TTS API.
    """
    data = request.get_json(silent=True) or request.form or {}
    text = (data.get('text') or '').strip()
    lang = data.get('language', 'kn')
    voice = data.get('voice', 'female')

    if not text:
        return jsonify({'success': False, 'error': 'Text is required for speech synthesis'}), 400

    result = TimbreService.synthesize(text, lang=lang, voice=voice)
    return jsonify(result), 200

@translation_bp.route('/api/voice-translate', methods=['POST'])
def voice_translate_pipeline():
    """
    POST /api/voice-translate
    Complete end-to-end voice translation pipeline:
    Speech (Prisma) -> Text -> Translation (Gemini) -> Audio Speech (Timbre).
    Fully instrumented with latency breakdown.
    """
    t_start = time.perf_counter()
    t_stt = 0.0
    t_trans = 0.0
    t_tts = 0.0

    source_lang = request.form.get('source_lang', 'kn')
    target_lang = request.form.get('target_lang', 'en')
    domain = request.form.get('domain', 'farmer')
    session_id = request.form.get('session_id', 'default_trans_session')
    speaker = request.form.get('speaker', 'speaker_a')
    text_override = (request.form.get('text') or '').strip()
    text_hint = (request.form.get('text_hint') or '').strip()

    original_text = ""
    engine_stt = "Direct Input"

    # Step 1: STT if audio was uploaded
    if 'audio' in request.files and request.files['audio'].filename != '':
        audio_file = request.files['audio']
        valid, err_msg = AudioController.validate_audio_file(audio_file)
        if not valid:
            return jsonify({'success': False, 'error': err_msg}), 400

        audio_bytes = audio_file.read()
        t_stt_start = time.perf_counter()
        stt_res = PrismaService.transcribe(audio_bytes, lang=source_lang, content_type=audio_file.content_type)
        t_stt = (time.perf_counter() - t_stt_start) * 1000.0

        if stt_res.get('success') and stt_res.get('text'):
            original_text = stt_res.get('text', '')
            engine_stt = stt_res.get('engine', 'Gnani Prisma STT')
        elif text_hint:
            original_text = text_hint
            engine_stt = "Web Speech Recognition (Prisma Network Fallback)"
            logger.info(f"[STAGE: STT_FALLBACK] Utilized client speech hint: '{original_text[:50]}'")
        else:
            return jsonify({
                'success': False,
                'fallback_to_browser': stt_res.get('fallback_to_browser', False),
                'error': stt_res.get('error', 'ಧ್ವನಿ ಸ್ಪಷ್ಟವಾಗಿ ಕೇಳಲಿಲ್ಲ (Could not transcribe speech).'),
                'step': 'transcription'
            }), 400

    if not original_text and text_override:
        original_text = text_override
    elif not original_text and text_hint:
        original_text = text_hint
        engine_stt = "Web Speech Recognition"

    if not original_text:
        return jsonify({'success': False, 'error': 'No speech or text received for translation.'}), 400

    # Step 2: Translation (Gemini Domain-Aware)
    t_trans_start = time.perf_counter()
    trans_res = GeminiService.translate(original_text, source_lang, target_lang, domain=domain)
    t_trans = (time.perf_counter() - t_trans_start) * 1000.0
    translated_text = trans_res.get('translated_text') or original_text

    # Record turn in session memory
    ConversationService.add_translation_turn(
        session_id=session_id,
        source_text=original_text,
        translated_text=translated_text,
        source_lang=source_lang,
        target_lang=target_lang,
        speaker=speaker
    )

    # Step 3: TTS (Timbre)
    t_tts_start = time.perf_counter()
    tts_res = TimbreService.synthesize(translated_text, lang=target_lang)
    t_tts = (time.perf_counter() - t_tts_start) * 1000.0

    t_total_backend = (time.perf_counter() - t_start) * 1000.0
    logger.info(
        f"[PERF] /api/voice-translate -> STT: {t_stt:.1f}ms | Translate: {t_trans:.1f}ms | TTS: {t_tts:.1f}ms | Total: {t_total_backend:.1f}ms"
    )

    return jsonify({
        'success': True,
        'original_text': original_text,
        'translated_text': translated_text,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'domain': domain,
        'audio_base64': tts_res.get('audio_base64'),
        'client_speech': tts_res.get('client_speech', False),
        'engines': {
            'stt': engine_stt,
            'translation': trans_res.get('engine', 'Gemini Translator'),
            'tts': tts_res.get('engine', 'Gnani Timbre TTS')
        },
        'timings': {
            'stt_ms': round(t_stt, 1),
            'translation_ms': round(t_trans, 1),
            'tts_ms': round(t_tts, 1),
            'backend_total_ms': round(t_total_backend, 1)
        }
    }), 200

@translation_bp.route('/api/translation/history', methods=['GET'])
def get_translation_history():
    session_id = request.args.get('session_id', 'default_trans_session')
    history = ConversationService.get_history(session_id)
    return jsonify({'success': True, 'history': history})

@translation_bp.route('/api/translation/clear', methods=['POST'])
def clear_translation_history():
    data = request.get_json(silent=True) or {}
    session_id = data.get('session_id', 'default_trans_session')
    ConversationService.clear_session(session_id)
    return jsonify({'success': True, 'message': 'Translation history cleared'})

