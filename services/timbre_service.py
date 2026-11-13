"""
UZHAVAR AI – Kannada Voice Bridge
Gnani Timbre Text-to-Speech (TTS) Service
Official API Integration for Indian Regional Languages
"""

import os
import requests
import base64
import logging
from typing import Dict, Any, Optional
from services.languages import get_dialect_code

logger = logging.getLogger("uzhavar.timbre")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in timbre_service: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

class TimbreService:
    DEFAULT_ENDPOINT = "https://api.vachana.ai/api/v1/tts/inference"
    _cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_api_key(cls) -> str:
        return os.environ.get('GNANI_API_KEY', '').strip()

    @classmethod
    def get_endpoint(cls) -> str:
        return os.environ.get('GNANI_TIMBRE_ENDPOINT', cls.DEFAULT_ENDPOINT).strip() or cls.DEFAULT_ENDPOINT

    @classmethod
    def test_connection(cls) -> Dict[str, Any]:
        """Test connection to Gnani Timbre TTS service without leaking keys."""
        api_key = cls.get_api_key()
        if not api_key or api_key == 'your_gnani_api_key_here':
            return {
                'service': 'Gnani Timbre TTS',
                'status': 'Missing Credentials',
                'message': 'GNANI_API_KEY is not configured in .env'
            }

        endpoint = cls.get_endpoint()
        headers = {'X-API-Key-ID': api_key, 'Content-Type': 'application/json'}
        payload = {
            'text': 'ನಮಸ್ಕಾರ',
            'language': 'kn-IN',
            'voice': 'female',
            'speed': 1.0
        }

        try:
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=6)
            if resp.status_code == 200:
                return {
                    'service': 'Gnani Timbre TTS',
                    'status': 'Connected',
                    'endpoint': endpoint,
                    'message': 'Gnani Timbre TTS reachable and verified'
                }
            return {
                'service': 'Gnani Timbre TTS',
                'status': 'Connection Failed',
                'message': f'HTTP status {resp.status_code}: {resp.text[:120]}'
            }
        except requests.exceptions.SSLError as e:
            return {
                'service': 'Gnani Timbre TTS',
                'status': 'SSL Certificate Issue',
                'message': f'SSL certificate verification notice: {str(e)[:100]}'
            }
        except Exception as e:
            return {
                'service': 'Gnani Timbre TTS',
                'status': 'Connection Failed',
                'message': f'Network unreachable: {str(e)[:120]}'
            }

    @classmethod
    def synthesize(cls, text: str, lang: str = 'kn', voice: str = 'female') -> Dict[str, Any]:
        """
        Synthesize speech from text using Gnani Timbre API with caching and clean text filtering.
        Falls back seamlessly to browser SpeechSynthesis if remote endpoint is unreachable.
        """
        import re
        dialect = get_dialect_code(lang)
        api_key = cls.get_api_key()
        endpoint = cls.get_endpoint()

        raw_text = text.strip() if text else ""
        if not raw_text:
            return {
                'success': False,
                'error': 'Text is empty for speech synthesis.',
                'language': dialect
            }

        # Clean markdown symbols for natural vocal pronunciation
        clean_synth = re.sub(r'[*#_`>\[\]\(\)]', ' ', raw_text)
        clean_synth = re.sub(r'\s+', ' ', clean_synth).strip()
        synth_text = clean_synth[:450]

        # Check in-memory audio cache to avoid duplicate API requests
        cache_key = f"{dialect}:{voice}:{hash(synth_text)}"
        if cache_key in cls._cache:
            logger.info(f"[STAGE: TIMBRE_TTS] Cache hit for speech synthesis ({dialect}).")
            return cls._cache[cache_key]

        if api_key and api_key != 'your_gnani_api_key_here':
            headers = {'X-API-Key-ID': api_key, 'Content-Type': 'application/json'}
            payload = {
                'text': synth_text,
                'language': dialect,
                'voice': voice,
                'model': 'timbre-v3.0',
                'speed': 1.0,
                'audio_config': {'sample_rate': 24000, 'container': 'wav'}
            }

            try:
                logger.info(f"[STAGE: TIMBRE_TTS] Sending {len(synth_text)} chars to {endpoint} in {dialect}...")
                resp = requests.post(endpoint, headers=headers, json=payload, timeout=5)

                if resp.status_code == 200:
                    content_type = resp.headers.get('Content-Type', '')
                    if 'application/json' in content_type:
                        data = resp.json()
                        audio_b64 = data.get('audio_base64') or data.get('audioContent') or data.get('data')
                    else:
                        audio_b64 = base64.b64encode(resp.content).decode('utf-8')

                    if audio_b64:
                        logger.info(f"[STAGE: TIMBRE_TTS] Generated audio stream ({len(audio_b64)} b64 bytes).")
                        res_obj = {
                            'success': True,
                            'audio_base64': audio_b64,
                            'format': 'wav',
                            'language': dialect,
                            'engine': 'Gnani Timbre TTS (Official API)'
                        }
                        cls._cache[cache_key] = res_obj
                        return res_obj
                else:
                    logger.warning(f"[STAGE: TIMBRE_TTS] Timbre returned HTTP {resp.status_code}: {resp.text[:120]}")
            except Exception as e:
                logger.warning(f"[STAGE: TIMBRE_TTS] Remote connection error: {str(e)[:120]}")

        # Browser speech synthesis fallback
        logger.info(f"[STAGE: TIMBRE_TTS] Remote endpoint unavailable, utilizing client speech synthesis for {dialect}.")
        fallback_obj = {
            'success': True,
            'audio_base64': None,
            'client_speech': True,
            'text': synth_text,
            'language': dialect,
            'engine': 'Browser SpeechSynthesis Engine'
        }
        cls._cache[cache_key] = fallback_obj
        return fallback_obj

