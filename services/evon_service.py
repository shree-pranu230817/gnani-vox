"""
UZHAVAR AI – Kannada Voice Bridge
Gnani Evon Conversational Reasoning Service Status Checker
"""

import os
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger("uzhavar.evon")

class EvonService:
    @classmethod
    def get_endpoint(cls) -> str:
        return os.environ.get('GNANI_EVON_ENDPOINT', '').strip()

    @classmethod
    def get_api_key(cls) -> str:
        return os.environ.get('GNANI_API_KEY', '').strip()

    @classmethod
    def is_available(cls) -> bool:
        endpoint = cls.get_endpoint()
        return bool(endpoint and endpoint.startswith('http'))

    @classmethod
    def test_connection(cls) -> Dict[str, Any]:
        """Verify whether an active Evon inference endpoint is configured."""
        endpoint = cls.get_endpoint()
        if not endpoint:
            return {
                'service': 'Gnani Evon Reasoning',
                'status': 'Not Configured / Inactive',
                'message': 'GNANI_EVON_ENDPOINT is empty in .env. Falling back directly to Google Gemini for reasoning and translation.'
            }

        api_key = cls.get_api_key()
        headers = {'X-API-Key-ID': api_key} if api_key else {}
        try:
            resp = requests.get(endpoint, headers=headers, timeout=5)
            if resp.status_code == 200:
                return {
                    'service': 'Gnani Evon Reasoning',
                    'status': 'Connected',
                    'endpoint': endpoint,
                    'message': 'Gnani Evon inference endpoint is reachable.'
                }
            return {
                'service': 'Gnani Evon Reasoning',
                'status': 'Connection Failed',
                'message': f'HTTP status {resp.status_code}'
            }
        except Exception as e:
            return {
                'service': 'Gnani Evon Reasoning',
                'status': 'Connection Failed',
                'message': f'Could not reach endpoint: {str(e)[:100]}'
            }

