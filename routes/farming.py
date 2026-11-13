"""
GNANI VOX – KrishiGuide AI (Intelligent Agricultural Guidance Assistant)
Backed by SQLite Persistent Storage & Continuous Multi-Turn Gemini Reasoning
"""

import time
import logging
from flask import Blueprint, request, jsonify
from services.prisma_service import PrismaService
from services.timbre_service import TimbreService
from services.gemini_service import GeminiService
from services.conversation_service import ConversationService
from services.audio_controller import AudioController
from services.languages import SUPPORTED_LANGUAGES, get_dialect_code

farming_bp = Blueprint('farming', __name__)
logger = logging.getLogger("gnanivox.farming")

# =============================================================================
# 1. CONVERSATION MANAGEMENT ENDPOINTS (SECTION 6)
# =============================================================================

@farming_bp.route('/api/conversations', methods=['POST'])
def create_conversation():
    """
    POST /api/conversations
    Creates a new persistent conversation in SQLite.
    Body (optional JSON): { "language": "kn", "title": "..." }
    """
    data = request.get_json(silent=True) or request.form or {}
    lang = data.get('language') or 'kn'
    conv = ConversationService.get_or_create_conversation(None, language=lang)
    if data.get('title'):
        conv.conversation_title = data['title'].strip()
        from models import db
        db.session.commit()

    return jsonify({
        'success': True,
        'conversation': conv.to_dict(include_messages=False)
    }), 201


@farming_bp.route('/api/conversations', methods=['GET'])
def list_conversations():
    """
    GET /api/conversations
    Returns list of all saved conversations in SQLite, sorted by updated_at desc.
    """
    convs = ConversationService.list_conversations()
    return jsonify({
        'success': True,
        'conversations': convs
    }), 200


@farming_bp.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation_details(conversation_id):
    """
    GET /api/conversations/<conversation_id>
    Retrieves full details and chronological messages for a conversation.
    """
    details = ConversationService.get_conversation_details(conversation_id)
    if not details:
        return jsonify({
            'success': False,
            'error': f'Conversation {conversation_id} not found.'
        }), 404

    return jsonify({
        'success': True,
        'conversation': details
    }), 200


@farming_bp.route('/api/conversations/<conversation_id>/messages', methods=['POST'])
def add_conversation_message(conversation_id):
    """
    POST /api/conversations/<conversation_id>/messages
    Saves an individual user or assistant message to SQLite.
    """
    data = request.get_json(silent=True) or request.form or {}
    text = (data.get('message_text') or data.get('text') or '').strip()
    sender = (data.get('sender') or 'user').lower()
    lang = data.get('language') or 'kn'
    mtype = data.get('message_type') or 'text'
    audio_ref = data.get('audio_reference')

    if not text:
        return jsonify({'success': False, 'error': 'message_text cannot be empty'}), 400

    msg = ConversationService.add_message(
        conversation_id=conversation_id,
        sender=sender,
        message_text=text,
        original_language=lang,
        message_type=mtype,
        audio_reference=audio_ref
    )

    return jsonify({
        'success': True,
        'message': msg.to_dict()
    }), 201


@farming_bp.route('/api/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """
    DELETE /api/conversations/<conversation_id>
    Permanently deletes a conversation and all its messages.
    """
    success = ConversationService.delete_conversation(conversation_id)
    if not success:
        return jsonify({
            'success': False,
            'error': f'Conversation {conversation_id} not found or could not be deleted.'
        }), 404

    return jsonify({
        'success': True,
        'message': f'Conversation {conversation_id} deleted successfully.'
    }), 200


@farming_bp.route('/api/conversations/<conversation_id>/clear', methods=['POST'])
def clear_conversation(conversation_id):
    """
    POST /api/conversations/<conversation_id>/clear
    Clears all messages in the conversation while preserving the conversation container.
    """
    success = ConversationService.clear_conversation_messages(conversation_id)
    if not success:
        return jsonify({
            'success': False,
            'error': f'Conversation {conversation_id} not found.'
        }), 404

    return jsonify({
        'success': True,
        'message': f'All messages in conversation {conversation_id} have been cleared.'
    }), 200


# =============================================================================
# 2. CONTINUOUS CONTEXT-AWARE FARMING QUESTION ENDPOINT
# =============================================================================

@farming_bp.route('/api/farming-question', methods=['POST'])
def farming_question():
    """
    POST /api/farming-question
    Processes agricultural inquiry (text or voice) using permanent SQLite history
    and continuous multi-turn Gemini reasoning.
    """
    t_start = time.perf_counter()
    t_stt = 0.0
    t_ai = 0.0
    t_tts = 0.0

    # Retrieve parameters from either form data or JSON
    data = request.get_json(silent=True) or {}
    lang = request.form.get('language') or data.get('language') or 'kn'
    conv_id = request.form.get('conversation_id') or request.form.get('session_id') or \
              data.get('conversation_id') or data.get('session_id')
    prompt = (request.form.get('prompt') or data.get('prompt') or '').strip()
    text_hint = (request.form.get('text_hint') or data.get('text_hint') or '').strip()

    engine_stt = "Direct Input"
    message_type = "text"

    # Step 1: Ensure persistent SQLite conversation exists
    conv = ConversationService.get_or_create_conversation(conv_id, language=lang)
    active_conv_id = conv.conversation_id

    # Step 2: Speech-to-Text if voice audio provided
    if 'audio' in request.files and request.files['audio'].filename != '':
        message_type = "voice"
        audio_file = request.files['audio']
        valid, err_msg = AudioController.validate_audio_file(audio_file)
        if not valid:
            return jsonify({'success': False, 'error': err_msg}), 400

        audio_bytes = audio_file.read()
        t_stt_start = time.perf_counter()
        stt_res = PrismaService.transcribe(audio_bytes, lang=lang, content_type=audio_file.content_type)
        t_stt = (time.perf_counter() - t_stt_start) * 1000.0

        if stt_res.get('success') and stt_res.get('text'):
            prompt = stt_res.get('text', '').strip()
            engine_stt = stt_res.get('engine', 'Gnani Prisma STT')
        elif text_hint:
            prompt = text_hint
            engine_stt = "Web Speech Recognition (Prisma Network Fallback)"
            logger.info(f"[STAGE: STT_FALLBACK] Utilized client speech hint: '{prompt[:50]}'")
        else:
            return jsonify({
                'success': False,
                'fallback_to_browser': stt_res.get('fallback_to_browser', False),
                'error': stt_res.get('error', 'ಧ್ವನಿ ಸ್ಪಷ್ಟವಾಗಿ ಕೇಳಲಿಲ್ಲ, ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಮಾತನಾಡಿ (Could not transcribe voice).'),
                'step': 'transcription'
            }), 400
    # Step 2b: Handle optional crop/leaf image upload for visual diagnosis
    image_bytes = None
    image_mime = "image/jpeg"
    if 'image' in request.files and request.files['image'].filename != '':
        img_file = request.files['image']
        image_bytes = img_file.read()
        image_mime = img_file.content_type or 'image/jpeg'
        if not prompt:
            prompt = "Please inspect this crop image for symptoms, diseases or pest problems, and provide safe guidance."

    elif not prompt and text_hint:
        prompt = text_hint
        engine_stt = "Web Speech Recognition"
        message_type = "voice"

    if not prompt and not image_bytes:
        return jsonify({'success': False, 'error': 'Please provide an agricultural question or upload a crop photo.'}), 400

    # Step 3: Retrieve chronological history from SQLite for Gemini
    # Note: We fetch the history BEFORE inserting the current message to build pristine turn alternation
    history = ConversationService.get_messages_for_gemini(active_conv_id, max_turns=16)
    summary = conv.conversation_summary or ""

    # Step 4: Save User Message into SQLite database
    ConversationService.add_message(
        conversation_id=active_conv_id,
        sender='user',
        message_text=prompt,
        original_language=lang,
        message_type='image' if image_bytes else message_type
    )

    # Step 5: Multi-Turn Scientific Agronomic Advisory via Gemini
    t_ai_start = time.perf_counter()
    advisory_res = GeminiService.answer_farming_question(
        prompt=prompt,
        lang=lang,
        history=history,
        summary=summary,
        image_bytes=image_bytes,
        image_mime=image_mime
    )
    t_ai = (time.perf_counter() - t_ai_start) * 1000.0
    answer = advisory_res.get('answer', '')

    # Step 6: Save Assistant Response into SQLite database
    ConversationService.add_message(
        conversation_id=active_conv_id,
        sender='assistant',
        message_text=answer,
        original_language=lang,
        message_type='text'
    )

    # Step 7: Update Persistent Rolling Context Summary in SQLite
    updated_summary = ConversationService.update_farming_summary(
        conversation_id=active_conv_id,
        prompt=prompt,
        bot_response=answer
    )

    # Refresh conversation instance to get updated title & timestamps
    conv = ConversationService.get_conversation(active_conv_id)

    # Step 8: Timbre TTS Voice Synthesis
    t_tts_start = time.perf_counter()
    tts_res = TimbreService.synthesize(answer, lang=lang)
    t_tts = (time.perf_counter() - t_tts_start) * 1000.0

    t_total_backend = (time.perf_counter() - t_start) * 1000.0
    logger.info(
        f"[PERF] conv={active_conv_id} | STT: {t_stt:.1f}ms | AI: {t_ai:.1f}ms | TTS: {t_tts:.1f}ms | Total: {t_total_backend:.1f}ms"
    )

    return jsonify({
        'success': True,
        'conversation_id': active_conv_id,
        'conversation_title': conv.conversation_title if conv else 'ಕೃಷಿ ಸಮಾಲೋಚನೆ',
        'question': prompt,
        'answer': answer,
        'language': lang,
        'memory_context': updated_summary or "ಸಂದರ್ಭ ದಾಖಲಾಗಿದೆ",
        'conversation_summary': updated_summary,
        'has_image': bool(image_bytes),
        'audio_base64': tts_res.get('audio_base64'),
        'client_speech': tts_res.get('client_speech', False),
        'engines': {
            'stt': engine_stt,
            'reasoning': advisory_res.get('engine', 'Gemini Agri-Reasoner (Persistent Context)'),
            'tts': tts_res.get('engine', 'Gnani Timbre TTS')
        },
        'timings': {
            'stt_ms': round(t_stt, 1),
            'ai_ms': round(t_ai, 1),
            'tts_ms': round(t_tts, 1),
            'backend_total_ms': round(t_total_backend, 1)
        }
    }), 200


# Backward compatibility endpoints
@farming_bp.route('/api/farming-reset', methods=['POST'])
def farming_reset():
    """Reset consultation by creating a new conversation."""
    data = request.get_json(silent=True) or request.form or {}
    lang = data.get('language') or 'kn'
    new_conv = ConversationService.get_or_create_conversation(None, language=lang)
    return jsonify({
        'success': True,
        'conversation_id': new_conv.conversation_id,
        'message': 'New consultation started.'
    })


@farming_bp.route('/api/farming-history', methods=['GET'])
def farming_history():
    """Retrieve full history of current conversation."""
    conv_id = request.args.get('conversation_id') or request.args.get('session_id')
    if not conv_id:
        return jsonify({'success': True, 'history': []})
    conv = ConversationService.get_conversation_details(conv_id)
    return jsonify({
        'success': True,
        'conversation': conv,
        'history': conv.get('messages', []) if conv else []
    })
