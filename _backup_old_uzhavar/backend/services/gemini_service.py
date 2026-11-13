"""
UZHAVAR AI - Google Gemini Agricultural Intelligence Service
Provides deep agronomic reasoning and multilingual question answering for Indian farmers
grounded in ICAR, State Agricultural Universities (TNAU/UASB/PJTSAU/PAU), and KVK recommendations.
"""

import os
import requests
import json
import logging
from typing import Dict, Any, Optional

# Safely inject OS/Windows native truststore for SSL verification
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

logger = logging.getLogger("uzhavar.gemini")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in gemini_service: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

class GeminiService:
    """
    Integrates Google Gemini / Generative Language API for multilingual agricultural reasoning.
    Uses Google Generative Language REST API with fallback models.
    """

    DEFAULT_MODEL = "gemini-3.5-flash-lite"
    CANDIDATE_MODELS = [
        "gemini-3.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.8-flash",
        "gemma-4-26b-a4b-it"
    ]
    ENDPOINT_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    @classmethod
    def get_api_key(cls) -> str:
        """Retrieve Gemini API key from environment or Flask config securely."""
        try:
            from flask import current_app
            if current_app:
                key = current_app.config.get('GEMINI_API_KEY')
                if key:
                    return key.strip()
        except Exception:
            pass
        key = os.environ.get('GEMINI_API_KEY', '').strip()
        if not key:
            try:
                from dotenv import load_dotenv
                load_dotenv()
                key = os.environ.get('GEMINI_API_KEY', '').strip()
            except Exception:
                pass
        return key

    @classmethod
    def is_configured(cls) -> bool:
        """Check if GEMINI_API_KEY is configured with a non-empty value."""
        key = cls.get_api_key()
        return bool(key and key != 'your_gemini_api_key_here')

    @classmethod
    def test_connection(cls, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Independently tests connection to Google Gemini API.
        Returns status: 'Connected', 'Missing Credentials', or 'Connection Failed'.
        Never logs or exposes the raw API key.
        """
        key = (api_key or cls.get_api_key()).strip()

        if not key or key == 'your_gemini_api_key_here':
            return {
                'service': 'Google Gemini API',
                'status': 'Missing Credentials',
                'message': 'GEMINI_API_KEY is not configured in .env'
            }

        test_payload = {
            "contents": [
                {
                    "parts": [
                        {"text": "State the single word: OK"}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 5,
                "temperature": 0.0
            }
        }

        last_error = ""
        for model in cls.CANDIDATE_MODELS:
            endpoint = f"{cls.ENDPOINT_TEMPLATE.format(model=model)}?key={key}"
            try:
                resp = requests.post(
                    endpoint,
                    headers={"Content-Type": "application/json"},
                    json=test_payload,
                    timeout=8
                )

                if resp.status_code == 200:
                    logger.info(f"[STAGE: GEMINI_TEST] Connection verified successfully with {model}.")
                    return {
                        'service': 'Google Gemini API',
                        'status': 'Connected',
                        'model': model,
                        'message': f'Successfully connected to Google Gemini ({model})'
                    }
                else:
                    error_data = {}
                    try:
                        error_data = resp.json().get('error', {})
                    except Exception:
                        pass
                    last_error = error_data.get('message', f'HTTP status {resp.status_code}')
            except requests.exceptions.Timeout:
                last_error = "Connection timed out"
            except requests.exceptions.ConnectionError as e:
                last_error = f"Network connection failed: {str(e)[:120]}"
            except Exception as e:
                last_error = f"Unexpected error: {str(e)[:120]}"

        return {
            'service': 'Google Gemini API',
            'status': 'Connection Failed',
            'message': last_error or 'Could not connect to Gemini models'
        }

    @classmethod
    def generate_response(
        cls,
        prompt: str,
        lang: str = 'en',
        category: str = 'general_agriculture',
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Executes Gemini agricultural reasoning request.
        Returns advisory dict or None if API is unavailable.
        """
        key = cls.get_api_key()
        if not key or key == 'your_gemini_api_key_here':
            return None

        lang_instructions = {
            'kn': 'Respond completely and fluently in Kannada (ಕನ್ನಡ) script with practical farmer terminology.',
            'ta': 'Respond completely and fluently in Tamil (தமிழ்) script with practical farmer terminology.',
            'te': 'Respond completely and fluently in Telugu (తెలుగు) script with practical farmer terminology.',
            'hi': 'Respond completely and fluently in Hindi (हिन्दी) Devanagari script.',
            'ml': 'Respond completely and fluently in Malayalam (മലയാളം) script.',
            'bn': 'Respond completely and fluently in Bengali (বাংলা) script.',
            'mr': 'Respond completely and fluently in Marathi (मराठी) script.',
            'gu': 'Respond completely and fluently in Gujarati (ગુજરાતી) script.',
            'pa': 'Respond completely and fluently in Punjabi (ਪੰਜਾਬੀ) Gurmukhi script.',
            'en': 'Respond in clear, accessible English for Indian farmers.'
        }
        lang_directive = lang_instructions.get(lang, lang_instructions['en'])

        context_str = ""
        if context:
            parts = []
            if context.get('crop'):
                parts.append(f"Active Crop: {context['crop']}")
            if context.get('variety'):
                parts.append(f"Variety: {context['variety']}")
            if context.get('location'):
                parts.append(f"Location/Mandi: {context['location']}")
            if context.get('soil_type'):
                parts.append(f"Soil Type: {context['soil_type']}")
            if context.get('season'):
                parts.append(f"Season: {context['season']}")
            if context.get('farming_conditions'):
                parts.append(f"Farming Conditions: {context['farming_conditions']}")
            if context.get('growth_stage'):
                parts.append(f"Growth Stage: {context['growth_stage']}")
            if context.get('problem'):
                parts.append(f"Reported Symptoms/Problem: {context['problem']}")
            if parts:
                context_str = f"Conversation Context (Current Farm Session): {', '.join(parts)}\n"

        system_instruction = (
            "You are UZHAVAR AI – AI Farming Assistant (Ask Anything About Agriculture), an authoritative, practical, "
            "and highly empathetic agricultural specialist dedicated to Indian farmers.\n\n"
            "You provide verified guidance across all 13 core agricultural domains:\n"
            "1. Crop cultivation & management\n"
            "2. Seed selection & varietal characteristics\n"
            "3. Fertilizers, nutrient deficiencies & basal/top-dressing timing\n"
            "4. Irrigation & water management (drip, furrow, sprinkler scheduling)\n"
            "5. Soil health, testing, preparation & amendments\n"
            "6. Crop diseases, fungal/bacterial/viral symptoms & management\n"
            "7. Pest identification, monitoring & integrated pest management (IPM)\n"
            "8. Organic farming (Jeevamrutha, Panchagavya, Beejamrutha, green manuring)\n"
            "9. Weed management & control methods\n"
            "10. Crop harvesting, post-harvest handling & storage protection\n"
            "11. Weather-related farming precautions, heat/frost/rain alerts\n"
            "12. Agricultural equipment, machinery & modern farming techniques\n"
            "13. Sustainable farming practices & soil conservation\n\n"
            "CRITICAL ANSWER QUALITY AND SAFETY GUIDELINES (MANDATORY):\n"
            "• UNDERSTAND CONTEXT: Fully account for the crop, location, soil type, season, and farming conditions provided.\n"
            "• ASK FOR MISSING INFORMATION: If vital information is missing (e.g. unknown crop, unspecified growth stage, ambiguous symptom description, or unknown acreage), provide sound preliminary guidance and politely ask the farmer for the missing detail instead of guessing.\n"
            "• STEP-BY-STEP RECOMMENDATIONS: Present practical instructions in clear, numbered chronological steps (Step 1, Step 2, Step 3) that are easy to follow in the field.\n"
            "• EXPLAIN THE REASON: Always explain WHY each action is recommended so the farmer understands the agronomic benefit.\n"
            "• CHEMICAL & FERTILIZER SAFETY: Never invent random fertilizer dosages, pesticide quantities, or arbitrary chemical schedules. Always instruct the farmer to check the container packaging/product label and consult their local Krishi Vigyan Kendra (KVK) or State Agricultural University / Agricultural Extension Officer for site-specific dilution rates.\n"
            "• SERIOUS CROP DISEASES: Visual symptoms alone can be misleading. For serious crop diseases, caution that diagnosis cannot be 100% certain from description alone, and request that the farmer take a physical plant sample or photograph to the nearest KVK or agri clinic.\n"
            "• DISTINGUISH GENERAL VS LOCAL: Clearly differentiate general agronomic principles from region-specific university package of practices (e.g., TNAU, UAS, PJTSAU, PAU, ICAR).\n"
            "• ZERO FABRICATION: Never fabricate government schemes, market rates, or scientific claims.\n"
            "• ACCESSIBLE TONE & LANGUAGE: Simple, clear, respectful language that farmers can easily understand and act upon.\n"
            f"• LANGUAGE DIRECTIVE: {lang_directive}\n"
        )

        full_prompt = (
            f"{system_instruction}\n"
            f"Topic Category: {category}\n"
            f"{context_str}"
            f"Farmer's Question: {prompt}\n\n"
            "Provide your structured, helpful agricultural advisory:"
        )

        payload = {
            "contents": [
                {
                    "parts": [{"text": full_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1000
            }
        }

        for model in cls.CANDIDATE_MODELS:
            endpoint = f"{cls.ENDPOINT_TEMPLATE.format(model=model)}?key={key}"
            try:
                logger.info(f"[STAGE: GEMINI_REASONING] Sending prompt to Gemini ({model}) in {lang}...")
                resp = requests.post(
                    endpoint,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=14
                )

                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get('candidates', [])
                    if candidates:
                        parts = candidates[0].get('content', {}).get('parts', [])
                        # Filter out thought parts (used in reasoning models like gemma/gemini 2.5/3.x)
                        text_parts = [p['text'] for p in parts if 'text' in p and not p.get('thought')]
                        if text_parts:
                            answer_text = '\n\n'.join(text_parts).strip()
                        elif parts and 'text' in parts[0]:
                            answer_text = parts[0]['text'].strip()
                        else:
                            answer_text = ""

                        if answer_text:
                            logger.info(f"[STAGE: GEMINI_REASONING] Received {len(answer_text)} chars from {model}.")
                            return {
                                'success': True,
                                'answer': answer_text,
                                'engine': f'Google Gemini ({model})',
                                'source': 'ICAR / State Agricultural Universities Grounded Advisory'
                            }
                else:
                    logger.warning(f"[STAGE: GEMINI_REASONING] {model} returned HTTP {resp.status_code}")
            except Exception as e:
                logger.warning(f"[STAGE: GEMINI_REASONING] Exception calling {model}: {str(e)[:120]}")

        return None

