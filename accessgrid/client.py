import base64
import hmac
import hashlib
import json
import requests
from datetime import datetime, timezone
from urllib.parse import quote
from typing import Optional, Dict, Any, List

class AccessGridError(Exception):
    """Base exception for AccessGrid SDK"""
    pass

class AuthenticationError(AccessGridError):
    """Raised when authentication fails"""
    pass

class AccessCard:
    def __init__(self, client, data: Dict[str, Any]):
        self._client = client
        self.id = data.get('id')
        self.url = data.get('install_url')
        self.state = data.get('state')
        self.full_name = data.get('full_name')
        self.expiration_date = data.get('expiration_date')

class Template:
    def __init__(self, client, data: Dict[str, Any]):
        self._client = client
        self.id = data.get('id')
        self.name = data.get('name')
        self.platform = data.get('platform')
        self.use_case = data.get('use_case')
        self.protocol = data.get('protocol')
        self.created_at = data.get('created_at')
        self.last_published_at = data.get('last_published_at')
        self.issued_keys_count = data.get('issued_keys_count')
        self.active_keys_count = data.get('active_keys_count')
        self.allowed_device_counts = data.get('allowed_device_counts')
        self.support_settings = data.get('support_settings')
        self.terms_settings = data.get('terms_settings')
        self.style_settings = data.get('style_settings')

class AccessCards:
    def __init__(self, client):
        self._client = client

    def issue(self, **kwargs) -> AccessCard:
        """Issue a new access card"""
        response = self._client._post('/v1/key-cards', kwargs)
        return AccessCard(self._client, response)
        
    def provision(self, **kwargs) -> AccessCard:
        """Alias for issue() method to maintain backwards compatibility"""
        return self.issue(**kwargs)

    def update(self, card_id: str, **kwargs) -> AccessCard:
        """Update an existing access card"""
        response = self._client._put(f'/v1/key-cards/{card_id}', kwargs)
        return AccessCard(self._client, response)

    def manage(self, card_id: str, action: str) -> AccessCard:
        """Manage card state (suspend/resume/unlink)"""
        response = self._client._post(f'/v1/key-cards/{card_id}/{action}', {})
        return AccessCard(self._client, response)

    def suspend(self, card_id: str) -> AccessCard:
        """Suspend an access card"""
        return self.manage(card_id, 'suspend')

    def resume(self, card_id: str) -> AccessCard:
        """Resume a suspended access card"""
        return self.manage(card_id, 'resume')

    def unlink(self, card_id: str) -> AccessCard:
        """Unlink an access card"""
        return self.manage(card_id, 'unlink')

class Console:
    def __init__(self, client):
        self._client = client

    def create_template(self, **kwargs) -> Template:
        """Create a new card template"""
        response = self._client._post('/v1/console/card-templates', kwargs)
        return Template(self._client, response)

    def update_template(self, template_id: str, **kwargs) -> Template:
        """Update an existing card template"""
        response = self._client._put(f'/v1/console/card-templates/{template_id}', kwargs)
        return Template(self._client, response)

    def read_template(self, template_id: str) -> Template:
        """Get details of a card template"""
        response = self._client._get(f'/v1/console/card-templates/{template_id}')
        return Template(self._client, response)

    def get_logs(self, template_id: str, **kwargs) -> Dict[str, Any]:
        """Get event logs for a card template"""
        return self._client._get(f'/v1/console/card-templates/{template_id}/logs', params=kwargs)

class AccessGrid:
    def __init__(self, account_id: str, secret_key: str, base_url: str = 'https://api.accessgrid.com'):
        if not account_id:
            raise ValueError("Account ID is required")
        if not secret_key:
            raise ValueError("Secret Key is required")

        self.account_id = account_id
        self.secret_key = secret_key
        self.base_url = base_url.rstrip('/')
        
        # Initialize API clients
        self.access_cards = AccessCards(self)
        self.console = Console(self)

    def _generate_signature(self, payload: str) -> str:
        """Generate HMAC signature for the payload"""
        encoded_payload = base64.b64encode(payload.encode()).decode()
        return hmac.new(
            self.secret_key.encode(),
            encoded_payload.encode(),
            hashlib.sha256
        ).hexdigest()

    def _make_request(self, method: str, endpoint: str, 
                     data: Optional[Dict] = None, 
                     params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make an HTTP request to the API"""
        url = f"{self.base_url}{endpoint}"
        
        # Prepare payload and signature
        payload = json.dumps(data) if data else ""
        headers = {
            'X-ACCT-ID': self.account_id,
            'X-PAYLOAD-SIG': self._generate_signature(payload),
            'Content-Type': 'application/json'
        }

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data if data else None,
                params=params
            )
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid credentials")
            elif response.status_code == 402:
                raise AccessGridError("Insufficient account balance")
            elif not 200 <= response.status_code < 300:
                error_data = response.json() if response.text else {}
                error_message = error_data.get('message', response.text)
                raise AccessGridError(f"API request failed: {error_message}")

            return response.json()

        except requests.exceptions.RequestException as e:
            raise AccessGridError(f"Request failed: {str(e)}")

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request"""
        return self._make_request('GET', endpoint, params=params)

    def _post(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """Make a POST request"""
        return self._make_request('POST', endpoint, data=data)

    def _put(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """Make a PUT request"""
        return self._make_request('PUT', endpoint, data=data)

    def _patch(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """Make a PATCH request"""
        return self._make_request('PATCH', endpoint, data=data)