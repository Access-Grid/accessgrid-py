import base64
import hmac
import hashlib
import json
import requests
from datetime import datetime, timezone
from urllib.parse import quote
from typing import Optional, Dict, Any, List, Union

try:
    from importlib.metadata import version
    __version__ = version("accessgrid")
except:
    __version__ = "unknown"

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
        self.card_number = data.get('card_number')
        self.site_code = data.get('site_code')
        self.file_data = data.get('file_data')
        self.direct_install_url = data.get('direct_install_url')
        
    def __str__(self) -> str:
        return f"AccessCard(name='{self.full_name}', id='{self.id}', state='{self.state}')"
    
    def __repr__(self) -> str:
        return self.__str__()

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
        response = self._client._patch(f'/v1/key-cards/{card_id}', kwargs)
        return AccessCard(self._client, response)

    def list(self, template_id: str, state: Optional[str] = None) -> List[AccessCard]:
        """
        List NFC keys provisioned for a particular card template.
        
        Args:
            template_id: Required. The card template ID to list keys for
            state: Filter keys by state (active, suspended, unlink, deleted)
            
        Returns:
            List of AccessCard objects
        """
        params = {'template_id': template_id}
        if state:
            params['state'] = state
            
        response = self._client._get('/v1/key-cards', params=params)
        return [AccessCard(self._client, item) for item in response.get('keys', [])]

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

    def delete(self, card_id: str) -> AccessCard:
        """Delete an access card"""
        return self.manage(card_id, 'delete')

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

    def read_template(self, template_id: str) -> Union[Template, List[Template]]:
        "Read card template by id or list the card template pairs"
        response = self._client._get(f'/v1/console/card-templates/{template_id}')
        if 'templates' in response:
            return [Template(self._client, item) for item in response['templates']]
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
        """
        Generate HMAC signature for the payload according to the shared secret scheme:
        SHA256.update(shared_secret + base64.encode(payload)).hexdigest()
        
        For requests with no payload (like GET, or actions like suspend/unlink/resume), 
        caller should provide a payload with {"id": "{resource_id}"}
        """
        # Base64 encode the payload
        payload_bytes = payload.encode()
        encoded_payload = base64.b64encode(payload_bytes)
        
        # Create HMAC using the shared secret as the key and the base64 encoded payload as the message
        signature = hmac.new(
            self.secret_key.encode(),
            encoded_payload,
            hashlib.sha256
        ).hexdigest()
        
        return signature

    def _make_request(self, method: str, endpoint: str, 
                     data: Optional[Dict] = None, 
                     params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make an HTTP request to the API"""
        url = f"{self.base_url}{endpoint}"
        
        # Extract resource ID from the endpoint if needed for signature
        resource_id = None
        if method == 'GET' or (method == 'POST' and (not data or data == {})):
            # Extract the ID from the endpoint - patterns like /resource/{id} or /resource/{id}/action
            parts = endpoint.strip('/').split('/')
            if len(parts) >= 2:
                # For actions like unlink/suspend/resume, get the card ID (second to last part)
                if parts[-1] in ['suspend', 'resume', 'unlink', 'delete']:
                    resource_id = parts[-2]
                else:
                    # Otherwise, the ID is typically the last part of the path
                    resource_id = parts[-1]
        
        # Special handling for requests with no payload:
        # 1. POST requests with empty body (like unlink/suspend/resume)
        # 2. GET requests
        if (method == 'POST' and not data) or method == 'GET':
            # For these requests, use {"id": "card_id"} as the payload for signature generation
            if resource_id:
                payload = json.dumps({"id": resource_id})
            else:
                payload = "{}"
        else:
            # For normal POST/PUT/PATCH with body, use the actual payload
            payload = json.dumps(data) if data else ""
        
        # Generate signature - we don't need to pass resource_id separately since we've already
        # incorporated it into the payload when needed
        signature = self._generate_signature(payload)
        
        headers = {
            'X-ACCT-ID': self.account_id,
            'X-PAYLOAD-SIG': signature,
            'Content-Type': 'application/json',
            'User-Agent': f'accessgrid.py @ v{__version__}'
        }

        # For GET requests, we don't need to add sig_payload here anymore 
        # as it's handled in the request section below

        try:
            # For requests with empty bodies (GET or action endpoints like unlink/suspend/resume),
            # we need to include the sig_payload parameter
            if method == 'GET' or (method == 'POST' and not data):
                if not params:
                    params = {}
                # Include the ID payload in the query params
                if resource_id:
                    # The server expects the raw JSON string, not URL-encoded
                    params['sig_payload'] = json.dumps({"id": resource_id})
            
            # For POST/PUT/PATCH with empty body, don't include a JSON body
            # as the server uses request.raw_post which would be empty
            json_data = data if data and method != 'GET' else None
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
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
