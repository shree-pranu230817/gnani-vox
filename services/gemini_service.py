"""
GNANI VOX – One Voice. Many Languages. No Barriers.
Google Gemini Multilingual Translation & KrishiGuide AI Agricultural Reasoning Service
"""

import os
import requests
import json
import base64
import logging
from typing import Dict, Any, Optional, List
from services.languages import SUPPORTED_LANGUAGES

logger = logging.getLogger("gnanivox.gemini")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in gemini_service: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

class GeminiService:
    CANDIDATE_MODELS = [
        "gemini-3.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.8-flash",
        "gemma-4-26b-a4b-it"
    ]
    ENDPOINT_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    _active_model: Optional[str] = None

    @classmethod
    def get_api_key(cls) -> str:
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
    def test_connection(cls) -> Dict[str, Any]:
        """Test connection to Gemini Generative Language REST API."""
        key = cls.get_api_key()
        if not key or key == 'your_gemini_api_key_here':
            return {
                'service': 'Google Gemini API',
                'status': 'Missing Credentials',
                'message': 'GEMINI_API_KEY is not configured in .env'
            }

        payload = {
            "contents": [{"parts": [{"text": "Reply with single word: OK"}]}],
            "generationConfig": {"maxOutputTokens": 5, "temperature": 0.0}
        }

        last_error = ""
        for model in cls.CANDIDATE_MODELS:
            endpoint = f"{cls.ENDPOINT_TEMPLATE.format(model=model)}?key={key}"
            try:
                resp = requests.post(endpoint, json=payload, timeout=7)
                if resp.status_code == 200:
                    return {
                        'service': 'Google Gemini API',
                        'status': 'Connected',
                        'model': model,
                        'message': f'Connected to Google Gemini ({model})'
                    }
                else:
                    last_error = f"HTTP {resp.status_code}: {resp.text[:100]}"
            except Exception as e:
                last_error = str(e)[:100]

        return {
            'service': 'Google Gemini API',
            'status': 'Connection Failed',
            'message': last_error or 'Could not connect to Gemini models'
        }

    @classmethod
    def _call_gemini(cls, system_instruction: str, prompt_or_contents: Any, max_tokens: int = 400) -> Optional[str]:
        """Core call to Gemini REST API across candidate models with active model caching and multi-turn support."""
        key = cls.get_api_key()
        if not key:
            return None

        # Format contents payload: either multi-turn list or single prompt object
        if isinstance(prompt_or_contents, list):
            contents_payload = prompt_or_contents
        else:
            contents_payload = [{"parts": [{"text": str(prompt_or_contents)}]}]

        payload = {
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            },
            "contents": contents_payload,
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": max_tokens
            }
        }

        # Order candidate models: prioritize cached active model
        models_to_try = list(cls.CANDIDATE_MODELS)
        if cls._active_model and cls._active_model in models_to_try:
            models_to_try.remove(cls._active_model)
            models_to_try.insert(0, cls._active_model)

        for model in models_to_try:
            endpoint = f"{cls.ENDPOINT_TEMPLATE.format(model=model)}?key={key}"
            try:
                resp = requests.post(
                    endpoint,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=8
                )
                if resp.status_code == 200:
                    cls._active_model = model
                    data = resp.json()
                    candidates = data.get('candidates', [])
                    if candidates:
                        parts = candidates[0].get('content', {}).get('parts', [])
                        text_parts = [p['text'] for p in parts if 'text' in p and not p.get('thought')]
                        if text_parts:
                            return '\n\n'.join(text_parts).strip()
                        elif parts and 'text' in parts[0]:
                            return parts[0]['text'].strip()
            except Exception as e:
                logger.warning(f"Error calling Gemini model {model}: {e}")

        return None

    # =========================================================================
    # 1. DOMAIN-AWARE MULTILINGUAL VOICE TRANSLATION
    # =========================================================================
    @classmethod
    def translate(cls, text: str, source_lang: str, target_lang: str, domain: str = 'farmer') -> Dict[str, Any]:
        """
        Translates text between Indian regional languages with specialized domain vocabulary:
        - 'farmer': Agronomic terms, crop names, seeds, fertilizers, prices, irrigation.
        - 'worker': Daily wages (₹), hours, shifts, attendance, tools, construction, safety rules.
        """
        src_info = SUPPORTED_LANGUAGES.get(source_lang, SUPPORTED_LANGUAGES['kn'])
        tgt_info = SUPPORTED_LANGUAGES.get(target_lang, SUPPORTED_LANGUAGES['en'])

        if not text or not text.strip():
            return {
                'success': False,
                'error': 'Text is empty for translation.'
            }

        domain_guide = ""
        if domain == 'farmer':
            domain_guide = (
                "CONTEXT: Indian Agricultural Conversation between farmers, traders, and agronomists.\n"
                "CRITICAL INSTRUCTIONS:\n"
                "- Accurately translate agricultural terms (crops, seeds, pests, diseases, fertilizers, irrigation).\n"
                "- Preserve crop variety names (e.g., Co 51, Sona Masuri, Ragi GPU 28).\n"
                "- Preserve prices, quintal/kg weights, dates, and measurements exactly.\n"
                "- Do NOT hallucinate or alter factual quantities.\n"
            )
        elif domain == 'worker':
            domain_guide = (
                "CONTEXT: Indian Daily-Wage Worker & Contractor/Employer Communication.\n"
                "CRITICAL INSTRUCTIONS:\n"
                "- Accurately translate wage terms (daily wage, overtime, weekly payout, advance, dues in ₹).\n"
                "- Accurately translate work instructions, hours (shift, morning, overtime), attendance, leave requests.\n"
                "- Preserve tool names (trowel, shovel, tractor, sickle), safety guidelines, accommodation, transport details.\n"
                "- Keep tone respectful, clear, and unambiguous for workers.\n"
            )
        else:
            domain_guide = "CONTEXT: Clear, natural, spoken communication for Indian regional speakers.\n"

        system_instruction = (
            "You are GNANI VOX – VoxConnect Universal Multilingual Voice Translation Engine.\n"
            f"{domain_guide}"
            f"SOURCE LANGUAGE: {src_info['name']} ({src_info['native']})\n"
            f"TARGET LANGUAGE: {tgt_info['name']} ({tgt_info['native']})\n"
            "OUTPUT REQUIREMENT: Return ONLY the direct, natural translation in the target language script. "
            "Do NOT include explanations, quotes, preambles, or conversational greetings."
        )

        translated = cls._call_gemini(system_instruction, text, max_tokens=250)
        if translated:
            return {
                'success': True,
                'original_text': text,
                'translated_text': translated,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'domain': domain,
                'engine': 'GNANI VOX – VoxConnect Gemini Translation Engine'
            }

        # Clean fallback if Gemini is unreachable
        return {
            'success': False,
            'original_text': text,
            'translated_text': text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'error': 'Translation engine temporarily unavailable. Displaying original text.'
        }

    # =========================================================================
    # 2. SCIENTIFIC & GROUNDED AI FARMING QUESTION ANSWERING
    # =========================================================================
    @classmethod
    def answer_farming_question(
        cls,
        prompt: str,
        lang: str = 'kn',
        context: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, str]]] = None,
        summary: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        image_mime: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Provides practical, scientific agricultural advisory grounded in ICAR/KVK/SAU packages of practice.
        Adheres strictly to all safety guidelines and retains continuous multi-turn consultation memory.
        Supports multimodal visual leaf/crop disease diagnosis when image_bytes is provided.
        """
        lang_info = SUPPORTED_LANGUAGES.get(lang, SUPPORTED_LANGUAGES['kn'])

        context_str = ""
        if summary:
            context_str += f"\nCONFIRMED CONSULTATION FACTS & SUMMARY:\n{summary}\n"
        elif context:
            ctx_items = []
            if context.get('crop'): ctx_items.append(f"Crop: {context['crop']}")
            if context.get('variety'): ctx_items.append(f"Variety: {context['variety']}")
            if context.get('location'): ctx_items.append(f"Location: {context['location']}")
            if context.get('soil_type'): ctx_items.append(f"Soil: {context['soil_type']}")
            if context.get('season'): ctx_items.append(f"Season: {context['season']}")
            if context.get('farming_conditions'): ctx_items.append(f"Conditions: {context['farming_conditions']}")
            if context.get('growth_stage'): ctx_items.append(f"Growth Stage: {context['growth_stage']}")
            if context.get('problem'): ctx_items.append(f"Prior Concern: {context['problem']}")
            if ctx_items:
                context_str += f"\nActive Consultation Context: {', '.join(ctx_items)}\n"

        image_instruction = ""
        if image_bytes:
            image_instruction = (
                "\nIMAGE DIAGNOSIS DIRECTIVE:\n"
                "- A crop / plant leaf photo has been provided by the farmer.\n"
                "- Carefully examine visual symptoms: color lesions, yellowing, spots, mold, wilting, or pest damage.\n"
                "- Explain observable symptoms and identify the most likely diseases (fungal, bacterial, viral) or pest infestations.\n"
                "- Provide initial organic and field management steps.\n"
                "- SAFETY DISCLAIMER: State clearly that AI photo screening is indicative; recommend consulting the local Krishi Vigyan Kendra (KVK) with a physical leaf sample for definitive confirmation.\n"
            )

        system_instruction = (
            "You are GNANI VOX – KrishiGuide AI (Intelligent Agricultural Guidance Assistant), an expert agronomist "
            "empowering Indian farmers with scientific guidance based on ICAR, Krishi Vigyan Kendras (KVK), "
            "and State Agricultural Universities (UAS Bangalore/Dharwad, TNAU, PJTSAU, PAU).\n\n"
            f"{context_str}\n"
            f"{image_instruction}\n"
            "STRICT ANSWER QUALITY AND SAFETY GUIDELINES (MANDATORY):\n"
            "1. CONTEXT UNDERSTANDING: Factor in the crop, location, soil type, season, and conditions provided.\n"
            "2. CONTINUOUS CONVERSATION MEMORY: Review all prior conversation turns. Retain all previously mentioned "
            "crops, crop ages/growth stages, symptoms, and previous advice. Correctly resolve references like 'it', "
            "'that crop', 'the same issue', 'what fertilizer should I use?'. NEVER re-ask for the crop name or crop age "
            "if the farmer has already provided it earlier in this conversation!\n"
            "3. ASK ONLY FOR GENUINELY MISSING DETAILS: If critical details are missing, give preliminary safe advice "
            "and politely ask for the missing detail.\n"
            "4. STEP-BY-STEP RECOMMENDATIONS: Present practical actions in 2-3 concise numbered steps easy to execute in the field.\n"
            "5. EXPLAIN THE REASON: Briefly explain WHY each step, nutrient, or timing is advised.\n"
            "6. CHEMICAL & FERTILIZER SAFETY: Never invent chemical pesticide quantities or arbitrary fertilizer schedules. "
            "Always include this directive: 'Check product container label and consult local Krishi Vigyan Kendra (KVK) or agri officer.'\n"
            "7. SERIOUS CROP DISEASES: Visual symptoms alone can be ambiguous. State clearly if physical sample/photo at KVK is needed.\n"
            "8. DISTINGUISH GENERAL VS LOCAL: Clearly separate general agronomic principles from region-specific practices.\n"
            "9. ZERO FABRICATION: Never fabricate government schemes, market rates, or scientific claims.\n"
            f"10. LANGUAGE REQUIREMENT: Respond completely, fluently and respectfully in {lang_info['name']} ({lang_info['native']}).\n"
            "11. CONCISE SPOKEN FORMAT: Keep the total answer crisp (under 120 words) suitable for text-to-speech listening. Avoid lengthy essays."
        )

        # Build multi-turn contents payload
        contents_payload: List[Dict[str, Any]] = []
        if history and isinstance(history, list) and len(history) > 0:
            for turn in history:
                role = turn.get('role', 'user')
                text = turn.get('text', '').strip()
                if text:
                    contents_payload.append({
                        "role": role,
                        "parts": [{"text": text}]
                    })

        # Build current user turn parts
        user_parts: List[Dict[str, Any]] = [{"text": prompt or "Please inspect this crop image and advise."}]
        if image_bytes:
            user_parts.append({
                "inlineData": {
                    "mimeType": image_mime,
                    "data": base64.b64encode(image_bytes).decode('utf-8')
                }
            })

        # Append current user question if not already in history
        if not contents_payload or contents_payload[-1]["role"] != "user" or contents_payload[-1]["parts"][0].get("text") != prompt:
            contents_payload.append({
                "role": "user",
                "parts": user_parts
            })

        answer = cls._call_gemini(system_instruction, contents_payload, max_tokens=380)
        if answer:
            return {
                'success': True,
                'question': prompt,
                'answer': answer,
                'language': lang,
                'has_image': bool(image_bytes),
                'engine': 'GNANI VOX – KrishiGuide AI (ICAR/KVK Grounded)'
            }

        # Offline / fallback agricultural advice
        fallback_msg = (
            "ಕೃಷಿ ತಜ್ಞರ ಸಲಹೆ: ನಿಮ್ಮ ಪ್ರಶ್ನೆ ಸ್ವೀಕರಿಸಲಾಗಿದೆ. ಬೆಳೆ ಮತ್ತು ರೋಗದ ಲಕ್ಷಣಗಳನ್ನು ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಲು "
            "ದಯವಿಟ್ಟು ನಿಮ್ಮ ಸಮೀಪದ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರ (KVK) ಅಥವಾ ಕೃಷಿ ಇಲಾಖಾ ಅಧಿಕಾರಿಯನ್ನು ಸಂಪರ್ಕಿಸಿ."
            if lang == 'kn' else
            "Agricultural Advisory: For verified dosages and disease diagnosis, please check the product container label "
            "and consult your nearest Krishi Vigyan Kendra (KVK) or Agriculture Extension Officer."
        )
        return {
            'success': True,
            'question': prompt,
            'answer': fallback_msg,
            'language': lang,
            'has_image': bool(image_bytes),
            'engine': 'GNANI VOX – KrishiGuide Local Advisory'
        }

