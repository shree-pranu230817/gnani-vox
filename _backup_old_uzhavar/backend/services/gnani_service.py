"""
UZHAVAR AI - Complete Multilingual Agricultural Intelligence Integration
Integrates:
  1. Prisma: Speech-to-Text (ASR) via official Vachana platform
  2. AgriculturalIntentClassifier: 14 semantic categories across 10 Indian languages
  3. ConversationMemoryManager: Session-isolated multi-turn context tracking
  4. MandiPriceAssistant: Real-time official AGMARKNET commodity price retrieval
  5. AgriculturalKnowledgeEngine: Sourced agronomic intelligence (ICAR/KVK/Univ)
  6. Timbre: Text-to-Speech (TTS) via official Vachana platform / browser handoff
"""

import os
import requests
import json
import base64
import logging
from typing import Tuple, Optional, Dict, Any
from flask import current_app, session

from backend.services.agri_classifier import AgriculturalIntentClassifier
from backend.services.agri_memory import ConversationMemoryManager
from backend.services.mandi_assistant import MandiPriceAssistant
from backend.services.agri_knowledge import AgriculturalKnowledgeEngine
from backend.services.gemini_service import GeminiService

# Safely inject OS/Windows native truststore for SSL verification without disabling verification
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

logger = logging.getLogger("uzhavar.gnani")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in gnani_service: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class GnaniAIService:
    """
    Main Service orchestrating the complete Voice & Agricultural Intelligence pipeline.
    """

    # Dialect mapping for standard BCP-47 codes required by speech engines
    GNANI_LANG_MAP = {
        'en': 'en-IN',
        'ta': 'ta-IN',
        'te': 'te-IN',
        'hi': 'hi-IN',
        'kn': 'kn-IN',
        'ml': 'ml-IN',
        'bn': 'bn-IN',
        'mr': 'mr-IN',
        'gu': 'gu-IN',
        'pa': 'pa-IN'
    }

    @classmethod
    def get_dialect_code(cls, lang: str) -> str:
        """Map language code (2-letter ISO or BCP-47) to standard dialect code."""
        if not lang:
            return 'en-IN'
        clean = lang.strip().lower()
        if '-' in clean:
            return clean
        return cls.GNANI_LANG_MAP.get(clean, 'en-IN')

    @classmethod
    def resolve_language(cls, prompt: str, requested_lang: str = None) -> Tuple[str, str]:
        """
        Resolves the final language to use:
        - If requested_lang is valid, respects manual choice.
        - Automatically detects language from prompt script if unselected or default.
        Returns: (iso_code, dialect_code)
        """
        detected_iso = AgriculturalIntentClassifier.detect_language(prompt)
        
        # If user explicitly picked a non-English language, honor it
        if requested_lang and requested_lang not in ('auto', 'en'):
            final_iso = requested_lang.split('-')[0].lower()
        elif detected_iso != 'en':
            final_iso = detected_iso
        else:
            final_iso = requested_lang.split('-')[0].lower() if requested_lang else 'en'

        dialect = cls.get_dialect_code(final_iso)
        logger.info(f"[STAGE: LANG_SELECT] Prompt Detected: {detected_iso} | Manual: {requested_lang} -> Final: {final_iso} ({dialect})")
        return final_iso, dialect

    # =========================================================================
    # STEP 1: SPEECH-TO-TEXT (PRISMA)
    # =========================================================================
    @classmethod
    def speech_to_text_prisma(cls, audio_bytes, lang: str = 'en', content_type: str = 'audio/wav') -> dict:
        """
        Gnani Prisma Speech-to-Text (ASR) official REST API integration.
        Endpoint: POST https://api.vachana.ai/stt/v3
        Header: X-API-Key-ID: <GNANI_API_KEY>
        """
        api_key = current_app.config.get('GNANI_API_KEY', '').strip()
        endpoint = current_app.config.get('GNANI_PRISMA_ENDPOINT', 'https://api.vachana.ai/stt/v3')
        gnani_lang = cls.get_dialect_code(lang)

        logger.info(f"[STAGE: PRISMA_STT] Submitting {len(audio_bytes)} bytes audio for language {gnani_lang} to {endpoint}")

        if not api_key or api_key == 'your_gnani_api_key_here':
            logger.warning("[STAGE: PRISMA_STT] GNANI_API_KEY not configured in .env.")
            return {
                'success': False,
                'error': 'Gnani API Key is not configured in .env. Please configure your key from vachana.ai.',
                'language': gnani_lang,
                'engine': 'gnani_prisma_v3.0'
            }

        try:
            # Safe SSL verification: support system or custom CA bundle without disabling verification
            ca_bundle = os.environ.get('GNANI_SSL_CA') or os.environ.get('REQUESTS_CA_BUNDLE') or os.environ.get('SSL_CERT_FILE')
            ssl_verify = ca_bundle if (ca_bundle and os.path.exists(ca_bundle)) else True

            headers = {'X-API-Key-ID': api_key}
            files = {'audio_file': ('recording.wav', audio_bytes, content_type)}
            data = {'model': 'prisma-v3.0', 'language_code': gnani_lang, 'format': 'transcribe'}

            response = requests.post(endpoint, headers=headers, files=files, data=data, timeout=12, verify=ssl_verify)
            logger.info(f"[STAGE: PRISMA_STT] Prisma endpoint HTTP response code: {response.status_code}")

            if response.status_code == 200:
                resp_json = response.json()
                transcript = (
                    resp_json.get('transcript') or 
                    resp_json.get('text') or 
                    resp_json.get('data', {}).get('transcript', '')
                )
                if transcript and transcript.strip():
                    logger.info(f"[STAGE: PRISMA_STT] Transcribed: '{transcript.strip()}'")
                    return {
                        'success': True,
                        'text': transcript.strip(),
                        'language': gnani_lang,
                        'engine': 'gnani_prisma_v3.0'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Prisma STT did not detect any spoken words in the audio. Please speak clearly into your microphone.',
                        'language': gnani_lang,
                        'engine': 'gnani_prisma_v3.0'
                    }
            else:
                error_body = response.text[:200]
                logger.error(f"[STAGE: PRISMA_STT] Prisma STT failed (HTTP {response.status_code}): {error_body}")
                return {
                    'success': False,
                    'error': f'Gnani Prisma STT failed (HTTP {response.status_code}): {error_body}',
                    'language': gnani_lang,
                    'engine': 'gnani_prisma_v3.0'
                }
        except requests.exceptions.SSLError as e:
            err_msg = f"SSL Certificate Verification failed: {str(e)[:180]}"
            logger.error(f"[STAGE: PRISMA_STT] {err_msg}")
            return {
                'success': False,
                'error': f'Gnani Prisma STT SSL Error: Unable to verify certificate for {endpoint}. SSL verification strictly enforced.',
                'language': gnani_lang,
                'engine': 'gnani_prisma_v3.0'
            }
        except requests.exceptions.ConnectionError as e:
            err_msg = f"Network connection failed: {str(e)[:180]}"
            logger.error(f"[STAGE: PRISMA_STT] {err_msg}")
            return {
                'success': False,
                'error': f'Gnani Prisma STT Network Error: Cannot reach {endpoint}. Check network or firewall settings.',
                'language': gnani_lang,
                'engine': 'gnani_prisma_v3.0'
            }
        except Exception as e:
            logger.error(f"[STAGE: PRISMA_STT] Exception during Prisma STT call: {str(e)[:180]}")
            return {
                'success': False,
                'error': f'Gnani Prisma STT connection error: {str(e)[:180]}',
                'language': gnani_lang,
                'engine': 'gnani_prisma_v3.0'
            }

    # =========================================================================
    # STEPS 2-7: CLASSIFICATION, RETRIEVAL, REASONING & ANSWER GENERATION
    # =========================================================================
    @classmethod
    def ask_evon(cls, prompt: str, lang: str = 'en', session_id: Optional[str] = None) -> dict:
        """
        Comprehensive Multi-Turn Agricultural Intelligence Pipeline:
        1. Language Identification
        2. Session Memory Retrieval
        3. Short Follow-Up Detection (pure context resolution before classification)
        4. Semantic Intent Classification into 14 categories
        5. Information Retrieval (Mandi DB or Scientific Agricultural Knowledge)
        6. Reasoning & Answer Synthesis
        7. Contextual Memory Update
        """
        # Step 1: Resolve language
        iso_lang, dialect_code = cls.resolve_language(prompt, lang)

        # Step 2: Retrieve Conversation Memory
        session_key = session_id
        if not session_key:
            try:
                from flask import has_request_context
                if has_request_context():
                    session_key = session.get('session_id')
            except Exception:
                pass
        if not session_key:
            session_key = 'default_guest_session'
        session_data = ConversationMemoryManager.get_or_create_session(session_key)
        context = session_data['context']
        memory_summary = ConversationMemoryManager.get_context_summary(session_key)

        logger.info(f"[STAGE: CONVERSATION_MEMORY] Session: {session_key[:8]}... | Prior context: [{memory_summary}]")

        # Step 3: Short Follow-Up Resolution
        # When the user sends a very short message (e.g. "ತಂಜಾವೂರು" / "Thanjavur"),
        # check if we have an outstanding action_needed in context and treat it as
        # the continuation of the previous intent instead of re-classifying from scratch.
        prompt_stripped = prompt.strip()
        is_short = len(prompt_stripped.split()) <= 3

        # Update context early so detected entities are available for routing
        ConversationMemoryManager.update_context(session_key, prompt, intent=None, skip_history=True)
        # Reload context after entity extraction
        context = session_data['context']

        prior_intent = context.get('intent')
        prior_action = context.get('action_needed')

        if is_short and prior_intent and prior_action:
            logger.info(
                f"[STAGE: SHORT_FOLLOWUP] Short message detected. "
                f"Resuming prior intent='{prior_intent}', action='{prior_action}'"
            )
            category = prior_intent
            cat_info = AgriculturalIntentClassifier.CATEGORIES.get(category, {
                'name': category, 'id': 0, 'keywords': []
            })
        else:
            # Step 4: Classify Intent into 14 Categories
            category, cat_info = AgriculturalIntentClassifier.classify(prompt)
            logger.info(f"[STAGE: CLASSIFICATION] Intent: {category} ({cat_info['name']}) | Prompt: '{prompt[:70]}...'")

        # Step 5: Route according to Category
        engine_used = 'uzhavar-agri-reasoner-v2.0'
        try:
            if current_app:
                engine_used = current_app.config.get('REASONING_MODEL', engine_used)
        except Exception:
            pass
        if category == 'mandi_prices':
            logger.info("[STAGE: MANDI_ROUTER] Routing query to MandiPriceAssistant...")
            result = MandiPriceAssistant.process_query(prompt, lang=iso_lang, context=context)
        else:
            # Clear action_needed when moving to a non-mandi intent
            context.pop('action_needed', None)
            gemini_res = None
            if GeminiService.is_configured():
                logger.info(f"[STAGE: KNOWLEDGE_ROUTER] Routing query to Google Gemini for {category}...")
                gemini_res = GeminiService.generate_response(
                    prompt=prompt,
                    lang=iso_lang,
                    category=category,
                    context=context
                )
            if gemini_res and gemini_res.get('success'):
                result = gemini_res
                engine_used = gemini_res.get('engine', 'Google Gemini')
            else:
                logger.info(f"[STAGE: KNOWLEDGE_ROUTER] Routing query to AgriculturalKnowledgeEngine for {category}...")
                result = AgriculturalKnowledgeEngine.generate_advisory(
                    category=category,
                    prompt=prompt,
                    lang=iso_lang,
                    context=context
                )

        answer_text = result['answer']
        logger.info(f"[STAGE: MODEL_RESPONSE] Generated {len(answer_text)} chars in {iso_lang}. Preview: '{answer_text[:90].replace(chr(10), ' ')}...'")

        # Step 6: Update Conversation Memory with the resolved intent and action
        action_needed = result.get('action_needed')
        context['intent'] = category
        if action_needed:
            context['action_needed'] = action_needed
        elif 'action_needed' in context:
            del context['action_needed']

        # Record this turn in history (bot response added now)
        history = session_data.get('history', [])
        if history and history[-1].get('user') == prompt and not history[-1].get('bot'):
            history[-1]['bot'] = answer_text
        else:
            history.append({'user': prompt, 'bot': answer_text, 'timestamp': __import__('time').time()})
        if len(history) > 6:
            session_data['history'] = history[-6:]

        return {
            'success': True,
            'answer': answer_text,
            'category': category,
            'category_name': cat_info['name'],
            'language': dialect_code,
            'iso_language': iso_lang,
            'engine': engine_used,
            'memory_context': ConversationMemoryManager.get_context_summary(session_key),
            'action_needed': action_needed
        }

    # =========================================================================
    # STEP 8: TEXT-TO-SPEECH (TIMBRE)
    # =========================================================================
    @classmethod
    def text_to_speech_timbre(cls, text: str, lang: str = 'en', voice: str = 'female') -> dict:
        """
        Gnani Timbre Text-to-Speech (TTS) official REST API integration.
        Endpoint: POST https://api.vachana.ai/api/v1/tts/inference
        Header: X-API-Key-ID: <GNANI_API_KEY>
        """
        api_key = ''
        endpoint = 'https://api.vachana.ai/api/v1/tts/inference'
        try:
            if current_app:
                api_key = current_app.config.get('GNANI_API_KEY', '').strip()
                endpoint = current_app.config.get('GNANI_TIMBRE_ENDPOINT', endpoint)
        except Exception:
            pass
        if not api_key:
            api_key = os.environ.get('GNANI_API_KEY', '').strip()
        gnani_lang = cls.get_dialect_code(lang)

        logger.info(f"[STAGE: TIMBRE_TTS] Speech synthesis requested for {len(text)} chars in {gnani_lang} to {endpoint}")

        if api_key and api_key != 'your_gnani_api_key_here':
            try:
                ca_bundle = os.environ.get('GNANI_SSL_CA') or os.environ.get('REQUESTS_CA_BUNDLE') or os.environ.get('SSL_CERT_FILE')
                ssl_verify = ca_bundle if (ca_bundle and os.path.exists(ca_bundle)) else True

                headers = {'X-API-Key-ID': api_key, 'Content-Type': 'application/json'}
                payload = {
                    'text': text[:500],
                    'language': gnani_lang,
                    'voice': voice,
                    'model': 'timbre-v3.0',
                    'speed': 1.0,
                    'audio_config': {'sample_rate': 24000, 'container': 'wav'}
                }

                response = requests.post(endpoint, headers=headers, json=payload, timeout=8, verify=ssl_verify)
                if response.status_code == 200:
                    if 'application/json' in response.headers.get('Content-Type', ''):
                        data = response.json()
                        audio_b64 = data.get('audio_base64') or data.get('audioContent') or data.get('data')
                    else:
                        audio_b64 = base64.b64encode(response.content).decode('utf-8')

                    if audio_b64:
                        logger.info("[STAGE: TIMBRE_TTS] Timbre audio received successfully.")
                        return {
                            'success': True,
                            'audio_base64': audio_b64,
                            'format': 'wav',
                            'language': gnani_lang,
                            'engine': 'gnani_timbre_v3.0'
                        }
                else:
                    logger.warning(f"[STAGE: TIMBRE_TTS] Timbre returned HTTP {response.status_code}: {response.text[:150]}")
            except Exception as e:
                logger.warning(f"[STAGE: TIMBRE_TTS] Exception contacting Timbre endpoint: {str(e)}")

        # Fallback to browser SpeechSynthesis
        logger.info(f"[STAGE: TIMBRE_TTS] Remote Timbre unavailable. Handoff to browser speech synthesis for {gnani_lang}")
        return {
            'success': True,
            'audio_base64': None,
            'client_speech': True,
            'text': text,
            'language': gnani_lang,
            'engine': 'browser_speech_synthesis',
            'note': f'Handed off to browser SpeechSynthesis for dialect {gnani_lang}'
        }

    # =========================================================================
    # INDEPENDENT CONNECTION VERIFICATION METHODS
    # =========================================================================
    @classmethod
    def test_prisma_connection(cls, api_key: Optional[str] = None, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Independently tests connection to Gnani Prisma STT service.
        Returns status: 'Connected', 'Missing Credentials', or 'Connection Failed'.
        Never logs or exposes the raw API key.
        """
        key = api_key
        if not key:
            try:
                if current_app:
                    key = current_app.config.get('GNANI_API_KEY')
            except Exception:
                pass
        if not key:
            key = os.environ.get('GNANI_API_KEY', '')
        key = key.strip()

        if not key or key == 'your_gnani_api_key_here':
            return {
                'service': 'Gnani Prisma STT',
                'status': 'Missing Credentials',
                'message': 'GNANI_API_KEY is not configured in .env'
            }

        url = endpoint
        if not url:
            try:
                if current_app:
                    url = current_app.config.get('GNANI_PRISMA_ENDPOINT')
            except Exception:
                pass
        if not url:
            url = os.environ.get('GNANI_PRISMA_ENDPOINT', 'https://api.vachana.ai/stt/v3')

        try:
            # Safe SSL verification: support system or custom CA bundle without disabling verification
            ca_bundle = os.environ.get('GNANI_SSL_CA') or os.environ.get('REQUESTS_CA_BUNDLE') or os.environ.get('SSL_CERT_FILE')
            ssl_verify = ca_bundle if (ca_bundle and os.path.exists(ca_bundle)) else True

            # Send a minimal test probe
            headers = {'X-API-Key-ID': key}
            data = {'model': 'prisma-v3.0', 'language_code': 'en-IN', 'format': 'transcribe'}
            resp = requests.post(url, headers=headers, data=data, timeout=8, verify=ssl_verify)

            # 200 = Success, 400 = Auth accepted but missing audio payload (Valid connection)
            if resp.status_code in (200, 400):
                logger.info("[STAGE: PRISMA_TEST] Prisma STT endpoint reached and authenticated.")
                return {
                    'service': 'Gnani Prisma STT',
                    'status': 'Connected',
                    'endpoint': url,
                    'message': 'Successfully connected to Gnani Prisma STT service'
                }
            elif resp.status_code in (401, 403):
                logger.warning(f"[STAGE: PRISMA_TEST] Authentication rejected: HTTP {resp.status_code}")
                return {
                    'service': 'Gnani Prisma STT',
                    'status': 'Connection Failed',
                    'message': f'Authentication failed: HTTP {resp.status_code} (Invalid API key)'
                }
            else:
                return {
                    'service': 'Gnani Prisma STT',
                    'status': 'Connection Failed',
                    'message': f'Server returned HTTP {resp.status_code}'
                }
        except requests.exceptions.SSLError as e:
            return {
                'service': 'Gnani Prisma STT',
                'status': 'Connection Failed',
                'message': f'SSL Certificate Verification failed: {str(e)[:120]}. (SSL verification strictly enforced)'
            }
        except requests.exceptions.Timeout:
            return {
                'service': 'Gnani Prisma STT',
                'status': 'Connection Failed',
                'message': 'Connection timed out while contacting Gnani Prisma STT'
            }
        except requests.exceptions.ConnectionError as e:
            return {
                'service': 'Gnani Prisma STT',
                'status': 'Connection Failed',
                'message': f'Cannot reach endpoint: {str(e)[:120]}'
            }
        except Exception as e:
            return {
                'service': 'Gnani Prisma STT',
                'status': 'Connection Failed',
                'message': f'Unexpected error: {str(e)[:120]}'
            }

    @classmethod
    def test_timbre_connection(cls, api_key: Optional[str] = None, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Independently tests connection to Gnani Timbre TTS service.
        Returns status: 'Connected', 'Missing Credentials', or 'Connection Failed'.
        Never logs or exposes the raw API key.
        """
        key = api_key
        if not key:
            try:
                if current_app:
                    key = current_app.config.get('GNANI_API_KEY')
            except Exception:
                pass
        if not key:
            key = os.environ.get('GNANI_API_KEY', '')
        key = key.strip()

        if not key or key == 'your_gnani_api_key_here':
            return {
                'service': 'Gnani Timbre TTS',
                'status': 'Missing Credentials',
                'message': 'GNANI_API_KEY is not configured in .env'
            }

        url = endpoint
        if not url:
            try:
                if current_app:
                    url = current_app.config.get('GNANI_TIMBRE_ENDPOINT')
            except Exception:
                pass
        if not url:
            url = os.environ.get('GNANI_TIMBRE_ENDPOINT', 'https://api.vachana.ai/api/v1/tts/inference')

        try:
            ca_bundle = os.environ.get('GNANI_SSL_CA') or os.environ.get('REQUESTS_CA_BUNDLE') or os.environ.get('SSL_CERT_FILE')
            ssl_verify = ca_bundle if (ca_bundle and os.path.exists(ca_bundle)) else True

            headers = {'X-API-Key-ID': key, 'Content-Type': 'application/json'}
            payload = {'text': 'ping', 'language': 'en-IN', 'voice': 'female'}
            resp = requests.post(url, headers=headers, json=payload, timeout=8, verify=ssl_verify)

            if resp.status_code in (200, 201):
                logger.info("[STAGE: TIMBRE_TEST] Timbre TTS endpoint reached and authenticated.")
                return {
                    'service': 'Gnani Timbre TTS',
                    'status': 'Connected',
                    'endpoint': url,
                    'message': 'Successfully connected to Gnani Timbre TTS service'
                }
            elif resp.status_code in (401, 403):
                logger.warning(f"[STAGE: TIMBRE_TEST] Authentication rejected: HTTP {resp.status_code}")
                return {
                    'service': 'Gnani Timbre TTS',
                    'status': 'Connection Failed',
                    'message': f'Authentication failed: HTTP {resp.status_code} (Invalid API key)'
                }
            else:
                return {
                    'service': 'Gnani Timbre TTS',
                    'status': 'Connection Failed',
                    'message': f'Server returned HTTP {resp.status_code}'
                }
        except requests.exceptions.SSLError as e:
            return {
                'service': 'Gnani Timbre TTS',
                'status': 'Connection Failed',
                'message': f'SSL Certificate Verification failed: {str(e)[:120]}. (SSL verification strictly enforced)'
            }
        except requests.exceptions.Timeout:
            return {
                'service': 'Gnani Timbre TTS',
                'status': 'Connection Failed',
                'message': 'Connection timed out while contacting Gnani Timbre TTS'
            }
        except requests.exceptions.ConnectionError as e:
            return {
                'service': 'Gnani Timbre TTS',
                'status': 'Connection Failed',
                'message': f'Cannot reach endpoint: {str(e)[:120]}'
            }
        except Exception as e:
            return {
                'service': 'Gnani Timbre TTS',
                'status': 'Connection Failed',
                'message': f'Unexpected error: {str(e)[:120]}'
            }
