"""
UZHAVAR AI – Kannada Voice Bridge
Gnani Prisma Speech-to-Text (ASR) Service
Official API Integration for Indian Regional Languages
"""

import os
import requests
import logging
from typing import Dict, Any, Optional
from services.languages import get_dialect_code, SUPPORTED_LANGUAGES

logger = logging.getLogger("uzhavar.prisma")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in prisma_service: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

class PrismaService:
    DEFAULT_ENDPOINT = "https://api.vachana.ai/stt/v3"

    @classmethod
    def get_api_key(cls) -> str:
        return os.environ.get('GNANI_API_KEY', '').strip()

    @classmethod
    def get_endpoint(cls) -> str:
        return os.environ.get('GNANI_PRISMA_ENDPOINT', cls.DEFAULT_ENDPOINT).strip() or cls.DEFAULT_ENDPOINT

    @classmethod
    def test_connection(cls) -> Dict[str, Any]:
        """Test connection to Gnani Prisma STT service without leaking keys."""
        api_key = cls.get_api_key()
        if not api_key or api_key == 'your_gnani_api_key_here':
            return {
                'service': 'Gnani Prisma STT',
                'status': 'Missing Credentials',
                'message': 'GNANI_API_KEY is not configured in .env'
            }

        endpoint = cls.get_endpoint()
        headers = {'X-API-Key-ID': api_key}
        dummy_wav = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'

        try:
            files = {'audio': ('probe.wav', dummy_wav, 'audio/wav')}
            data = {'language': 'kn-IN'}
            resp = requests.post(endpoint, headers=headers, files=files, data=data, timeout=6)
            if resp.status_code in (200, 400):  # 400 is expected for empty dummy audio
                return {
                    'service': 'Gnani Prisma STT',
                    'status': 'Connected',
                    'endpoint': endpoint,
                    'message': f'Gnani Prisma STT reachable (HTTP {resp.status_code})'
                }
            return {
                'service': 'Gnani Prisma STT',
                'status': 'Connection Failed',
                'message': f'HTTP status {resp.status_code}: {resp.text[:120]}'
            }
        except requests.exceptions.SSLError as e:
            return {
                'service': 'Gnani Prisma STT',
                'status': 'SSL Certificate Issue',
                'message': f'SSL certificate verification notice: {str(e)[:100]}'
            }
        except Exception as e:
            return {
                'service': 'Gnani Prisma STT',
                'status': 'Connection Failed',
                'message': f'Network unreachable: {str(e)[:120]}'
            }

    @classmethod
    def transcribe(cls, audio_bytes: bytes, lang: str = 'kn', content_type: str = 'audio/wav') -> Dict[str, Any]:
        """
        Transcribe audio bytes using Gnani Prisma STT API.
        Falls back cleanly to browser Web Speech API instruction if remote connection fails.
        """
        dialect = get_dialect_code(lang)
        api_key = cls.get_api_key()
        endpoint = cls.get_endpoint()

        if not audio_bytes or len(audio_bytes) < 64:
            return {
                'success': False,
                'error': 'Audio recording is empty or too short. Please speak clearly.',
                'language': dialect
            }

        if api_key and api_key != 'your_gnani_api_key_here':
            headers = {'X-API-Key-ID': api_key}
            files = {'audio': ('recording.wav', audio_bytes, content_type or 'audio/wav')}
            
            # Match Prisma encoding parameters with input audio container
            ct_lower = (content_type or '').lower()
            if 'webm' in ct_lower:
                payload = {'language': dialect, 'encoding': 'WEBM_OPUS'}
            elif 'ogg' in ct_lower or 'opus' in ct_lower:
                payload = {'language': dialect, 'encoding': 'OGG_OPUS'}
            elif 'mp3' in ct_lower:
                payload = {'language': dialect, 'encoding': 'MP3'}
            elif 'flac' in ct_lower:
                payload = {'language': dialect, 'encoding': 'FLAC'}
            else:
                payload = {'language': dialect, 'encoding': 'LINEAR16', 'sample_rate': 16000}

            try:
                logger.info(f"[STAGE: PRISMA_STT] Uploading {len(audio_bytes)} bytes audio ({payload.get('encoding')}) to {endpoint} in {dialect}...")
                resp = requests.post(endpoint, headers=headers, files=files, data=payload, timeout=6)

                if resp.status_code == 200:
                    data = resp.json()
                    transcript = data.get('transcript') or data.get('text') or data.get('result', '')
                    if transcript:
                        logger.info(f"[STAGE: PRISMA_STT] Transcribed: '{transcript[:70]}...'")
                        return {
                            'success': True,
                            'text': transcript.strip(),
                            'language': dialect,
                            'engine': 'Gnani Prisma STT (Official API)'
                        }
                    else:
                        logger.warning("[STAGE: PRISMA_STT] Empty transcript returned from Prisma API.")
                else:
                    logger.warning(f"[STAGE: PRISMA_STT] Prisma returned HTTP {resp.status_code}: {resp.text[:120]}")
            except Exception as e:
                logger.warning(f"[STAGE: PRISMA_STT] Remote connection error: {str(e)[:120]}")

        # Browser speech recognition fallback
        return {
            'success': False,
            'fallback_to_browser': True,
            'language': dialect,
            'message': 'Remote Prisma endpoint unreachable or returned empty. Using Web Speech recognition.'
        }

