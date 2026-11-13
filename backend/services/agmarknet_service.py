import datetime
import requests
from flask import current_app
from database.db import query_db, execute_db

class AgmarknetService:
    """
    Service for integrating and syncing daily crop prices from official
    AGMARKNET / Ministry of Agriculture & Farmers Welfare APIs.
    """

    @classmethod
    def sync_from_datagov(cls):
        """
        Fetch latest live commodity prices from data.gov.in AGMARKNET API resource.
        Updates market_prices table with fresh verified prices.
        """
        api_key = (
            current_app.config.get('DATA_GOV_IN_API_KEY') or 
            current_app.config.get('DATA_GOV_API_KEY') or 
            ''
        ).strip()
        endpoint = current_app.config.get('AGMARKNET_ENDPOINT')

        if not api_key or api_key == 'your_datagov_api_key_here':
            return {
                'success': False,
                'message': 'DATA_GOV_IN_API_KEY is not configured in .env. Showing cached verified AGMARKNET prices.',
                'records_updated': 0
            }

        try:
            params = {
                'api-key': api_key,
                'format': 'json',
                'offset': 0,
                'limit': 50
            }
            resp = requests.get(endpoint, params=params, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                records = data.get('records', [])
                count = 0
                today_str = datetime.date.today().isoformat()

                for r in records:
                    state = r.get('state', '').strip()
                    district = r.get('district', '').strip()
                    market = r.get('market', '').strip()
                    commodity = r.get('commodity', '').strip()
                    min_p = float(r.get('min_price', 0))
                    max_p = float(r.get('max_price', 0))
                    modal_p = float(r.get('modal_price', 0))
                    arrival_date = r.get('arrival_date', today_str)

                    if state and commodity and modal_p > 0:
                        execute_db(
                            """INSERT INTO market_prices 
                               (crop_name, mandi_name, state, district, min_price, max_price, modal_price, unit, price_date, data_source, is_live)
                               VALUES (?, ?, ?, ?, ?, ?, ?, '₹/Quintal', ?, 'AGMARKNET - Govt. of India (Live Sync)', 1)""",
                            (commodity, market, state, district, min_p, max_p, modal_p, arrival_date)
                        )
                        count += 1

                return {
                    'success': True,
                    'message': f'Successfully synced {count} latest live mandi records from AGMARKNET API.',
                    'records_updated': count
                }
            else:
                return {
                    'success': False,
                    'message': f'AGMARKNET API returned HTTP {resp.status_code}',
                    'records_updated': 0
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Network error contacting AGMARKNET API: {str(e)}',
                'records_updated': 0
            }

    @classmethod
    def get_prices(cls, state=None, district=None, crop_name=None, limit=50):
        """Query stored verified market prices with flexible filters."""
        query = "SELECT * FROM market_prices WHERE 1=1"
        params = []

        if state and state != 'All':
            query += " AND state = ?"
            params.append(state)

        if district and district != 'All':
            query += " AND district = ?"
            params.append(district)

        if crop_name and crop_name != 'All':
            query += " AND crop_name LIKE ?"
            params.append(f"%{crop_name}%")

        query += " ORDER BY price_date DESC, id DESC LIMIT ?"
        params.append(limit)

        return query_db(query, tuple(params))

    @classmethod
    def get_filter_options(cls):
        """Get distinct list of states, commodities, and districts available in the price dataset."""
        states = [r['state'] for r in query_db("SELECT DISTINCT state FROM market_prices ORDER BY state ASC")]
        crops = [r['crop_name'] for r in query_db("SELECT DISTINCT crop_name FROM market_prices ORDER BY crop_name ASC")]
        return {
            'states': states,
            'crops': crops
        }

    # =========================================================================
    # INDEPENDENT CONNECTION VERIFICATION
    # =========================================================================
    @classmethod
    def test_datagov_connection(cls, api_key=None, endpoint=None):
        """
        Independently tests connection to data.gov.in AGMARKNET price API.
        Returns status: 'Connected', 'Missing Credentials', or 'Connection Failed'.
        Never logs or exposes the raw API key.
        """
        key = api_key
        if not key:
            try:
                if current_app:
                    key = current_app.config.get('DATA_GOV_IN_API_KEY') or current_app.config.get('DATA_GOV_API_KEY')
            except Exception:
                pass
        if not key:
            import os
            key = os.environ.get('DATA_GOV_IN_API_KEY') or os.environ.get('DATA_GOV_API_KEY', '')
        key = (key or '').strip()

        if not key or key == 'your_datagov_api_key_here':
            return {
                'service': 'data.gov.in AGMARKNET API',
                'status': 'Missing Credentials',
                'message': 'DATA_GOV_IN_API_KEY is not configured in .env'
            }

        url = endpoint
        if not url:
            try:
                if current_app:
                    url = current_app.config.get('AGMARKNET_ENDPOINT')
            except Exception:
                pass
        if not url:
            import os
            url = os.environ.get('AGMARKNET_ENDPOINT', 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070')

        try:
            params = {
                'api-key': key,
                'format': 'json',
                'offset': 0,
                'limit': 1
            }
            resp = requests.get(url, params=params, timeout=8)

            if resp.status_code == 200:
                data = resp.json()
                if 'records' in data or 'title' in data:
                    return {
                        'service': 'data.gov.in AGMARKNET API',
                        'status': 'Connected',
                        'endpoint': url,
                        'message': 'Successfully connected to data.gov.in AGMARKNET daily commodity price API'
                    }
                else:
                    return {
                        'service': 'data.gov.in AGMARKNET API',
                        'status': 'Connection Failed',
                        'message': f'Unexpected JSON response: {list(data.keys())}'
                    }
            elif resp.status_code in (401, 403):
                return {
                    'service': 'data.gov.in AGMARKNET API',
                    'status': 'Connection Failed',
                    'message': f'Authentication failed: HTTP {resp.status_code} (Invalid or inactive API key)'
                }
            else:
                return {
                    'service': 'data.gov.in AGMARKNET API',
                    'status': 'Connection Failed',
                    'message': f'Server returned HTTP {resp.status_code}'
                }
        except requests.exceptions.Timeout:
            return {
                'service': 'data.gov.in AGMARKNET API',
                'status': 'Connection Failed',
                'message': 'Connection timed out while contacting data.gov.in'
            }
        except requests.exceptions.ConnectionError as e:
            return {
                'service': 'data.gov.in AGMARKNET API',
                'status': 'Connection Failed',
                'message': f'Cannot reach data.gov.in: {str(e)[:120]}'
            }
        except Exception as e:
            return {
                'service': 'data.gov.in AGMARKNET API',
                'status': 'Connection Failed',
                'message': f'Unexpected error: {str(e)[:120]}'
            }
