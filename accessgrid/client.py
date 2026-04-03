import base64
import hashlib
import hmac
import json
from typing import Any, Dict, List, Optional, Union

import requests

try:
    from importlib.metadata import version

    __version__ = version("accessgrid")
except Exception:
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
        self.id = data.get("id")
        self.url = data.get("install_url")
        self.install_url = data.get("install_url")
        self.details = data.get("details")
        self.state = data.get("state")
        self.full_name = data.get("full_name")
        self.employee_id = data.get("employee_id")
        self.expiration_date = data.get("expiration_date")
        self.card_template_id = data.get("card_template_id")
        self.card_number = data.get("card_number")
        self.site_code = data.get("site_code")
        self.file_data = data.get("file_data")
        self.direct_install_url = data.get("direct_install_url")
        self.organization_name = data.get("organization_name")
        self.temporary = data.get("temporary")
        self.created_at = data.get("created_at")
        self.devices = data.get("devices", [])
        self.metadata = data.get("metadata", {})

    def __str__(self) -> str:
        return (
            f"AccessCard(name='{self.full_name}', id='{self.id}', "
            f"state='{self.state}', "
            f"card_template_id='{self.card_template_id}')"
        )

    def __repr__(self) -> str:
        return self.__str__()


class UnifiedAccessPass:
    def __init__(self, client, data: Dict[str, Any]):
        self._client = client
        self.id = data.get("id")
        self.url = data.get("install_url")
        self.install_url = data.get("install_url")
        self.state = data.get("state")
        self.status = data.get("status")
        self.details = [AccessCard(client, item) for item in data.get("details", [])]

    def __str__(self) -> str:
        return (
            f"UnifiedAccessPass(id='{self.id}', "
            f"state='{self.state}', cards={len(self.details)})"
        )

    def __repr__(self) -> str:
        return self.__str__()


class Template:
    def __init__(self, client, data: Dict[str, Any]):
        self._client = client
        self.id = data.get("id")
        self.name = data.get("name")
        self.platform = data.get("platform")
        self.use_case = data.get("use_case")
        self.protocol = data.get("protocol")
        self.created_at = data.get("created_at")
        self.last_published_at = data.get("last_published_at")
        self.issued_keys_count = data.get("issued_keys_count")
        self.active_keys_count = data.get("active_keys_count")
        self.allowed_device_counts = data.get("allowed_device_counts")
        self.support_settings = data.get("support_settings")
        self.terms_settings = data.get("terms_settings")
        self.style_settings = data.get("style_settings")
        self.metadata = data.get("metadata", {})


class Org:
    def __init__(self, client, data: Dict[str, Any]):
        self._client = client
        self.id = data.get("id")
        self.name = data.get("name")
        self.slug = data.get("slug")
        self.status = data.get("status")
        self.full_address = data.get("full_address")
        self.phone = data.get("phone")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.email = data.get("email")
        self.created_at = data.get("created_at")
        self.updated_at = data.get("updated_at")

    def __str__(self) -> str:
        return (
            f"Org(name='{self.name}', id='{self.id}', "
            f"slug='{self.slug}', status='{self.status}')"
        )

    def __repr__(self) -> str:
        return self.__str__()


class TemplateInfo:
    def __init__(self, client, data: Dict[str, Any]):
        self._client = client
        self._data = data
        self.id = data.get("id")
        self.name = data.get("name")
        self.platform = data.get("platform")

    def __getitem__(self, key):
        return self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __str__(self) -> str:
        return (
            f"TemplateInfo(id='{self.id}', "
            f"name='{self.name}', platform='{self.platform}')"
        )

    def __repr__(self) -> str:
        return self.__str__()


class PassTemplatePair:
    def __init__(self, client, data: Dict[str, Any]):
        self._client = client
        self._data = data
        self.id = data.get("id")
        self.name = data.get("name")
        self.created_at = data.get("created_at")
        self.android_template = (
            TemplateInfo(client, data["android_template"])
            if data.get("android_template")
            else None
        )
        self.ios_template = (
            TemplateInfo(client, data["ios_template"])
            if data.get("ios_template")
            else None
        )

    def __getitem__(self, key):
        if key in ("android_template", "ios_template"):
            return getattr(self, key)
        return self._data[key]

    def get(self, key, default=None):
        if key in ("android_template", "ios_template"):
            return getattr(self, key, default)
        return self._data.get(key, default)

    def __str__(self) -> str:
        return f"PassTemplatePair(id='{self.id}', name='{self.name}')"

    def __repr__(self) -> str:
        return self.__str__()


class LandingPage:
    def __init__(self, client, data: Dict[str, Any]):
        self._client = client
        self.id = data.get("id")
        self.name = data.get("name")
        self.created_at = data.get("created_at")
        self.kind = data.get("kind")
        self.password_protected = data.get("password_protected")
        self.logo_url = data.get("logo_url")

    def __str__(self) -> str:
        return (
            f"LandingPage(id='{self.id}', "
            f"name='{self.name}', kind='{self.kind}')"
        )

    def __repr__(self) -> str:
        return self.__str__()


class CredentialProfile:
    def __init__(self, client, data: Dict[str, Any]):
        self._client = client
        self.id = data.get("id")
        self.aid = data.get("aid")
        self.name = data.get("name")
        self.apple_id = data.get("apple_id")
        self.created_at = data.get("created_at")
        self.card_storage = data.get("card_storage")
        self.keys = data.get("keys", [])
        self.files = data.get("files", [])

    def __str__(self) -> str:
        return (
            f"CredentialProfile(id='{self.id}', "
            f"name='{self.name}', aid='{self.aid}')"
        )

    def __repr__(self) -> str:
        return self.__str__()


class IosPreflight:
    def __init__(self, client, data: Dict[str, Any]):
        self._client = client
        self.provisioningCredentialIdentifier = data.get(
            "provisioningCredentialIdentifier"
        )
        self.sharingInstanceIdentifier = data.get("sharingInstanceIdentifier")
        self.cardTemplateIdentifier = data.get("cardTemplateIdentifier")
        self.environmentIdentifier = data.get("environmentIdentifier")

    def __str__(self) -> str:
        return (
            f"IosPreflight("
            f"provisioningCredentialIdentifier="
            f"'{self.provisioningCredentialIdentifier}')"
        )

    def __repr__(self) -> str:
        return self.__str__()


class Webhook:
    def __init__(self, client, data: Dict[str, Any]):
        self._client = client
        self.id = data.get("id")
        self.name = data.get("name")
        self.url = data.get("url")
        self.auth_method = data.get("auth_method")
        self.subscribed_events = data.get("subscribed_events", [])
        self.created_at = data.get("created_at")
        self.private_key = data.get("private_key")
        self.client_cert = data.get("client_cert")
        self.cert_expires_at = data.get("cert_expires_at")

    def __str__(self) -> str:
        return f"Webhook(id='{self.id}', name='{self.name}', url='{self.url}')"

    def __repr__(self) -> str:
        return self.__str__()


class AccessCards:
    def __init__(self, client):
        self._client = client

    def issue(self, **kwargs) -> Union[AccessCard, UnifiedAccessPass]:
        """Issue a new access card or unified access pass"""
        response = self._client._post("/v1/key-cards", kwargs)
        if "details" in response:
            return UnifiedAccessPass(self._client, response)
        return AccessCard(self._client, response)

    def provision(self, **kwargs) -> Union[AccessCard, UnifiedAccessPass]:
        """Alias for issue() method to maintain backwards compatibility"""
        return self.issue(**kwargs)

    def get(self, card_id: str) -> AccessCard:
        """Get details about a specific issued Access Pass"""
        response = self._client._get(f"/v1/key-cards/{card_id}")
        return AccessCard(self._client, response)

    def update(self, card_id: str, **kwargs) -> AccessCard:
        """Update an existing access card"""
        response = self._client._patch(f"/v1/key-cards/{card_id}", kwargs)
        return AccessCard(self._client, response)

    def list(
        self, template_id: Optional[str] = None, state: Optional[str] = None
    ) -> List[AccessCard]:
        """
        List NFC keys provisioned for a particular card template.

        Args:
            template_id: The card template ID to list keys for (optional)
            state: Filter keys by state (active, suspended, unlink, deleted)

        Returns:
            List of AccessCard objects
        """
        params = {}
        if template_id:
            params["template_id"] = template_id

        if state:
            params["state"] = state

        response = self._client._get("/v1/key-cards", params=params)
        return [AccessCard(self._client, item) for item in response.get("keys", [])]

    def manage(self, card_id: str, action: str) -> AccessCard:
        """Manage card state (suspend/resume/unlink)"""
        response = self._client._post(f"/v1/key-cards/{card_id}/{action}", {})
        return AccessCard(self._client, response)

    def suspend(self, card_id: str) -> AccessCard:
        """Suspend an access card"""
        return self.manage(card_id, "suspend")

    def resume(self, card_id: str) -> AccessCard:
        """Resume a suspended access card"""
        return self.manage(card_id, "resume")

    def unlink(self, card_id: str) -> AccessCard:
        """Unlink an access card"""
        return self.manage(card_id, "unlink")

    def delete(self, card_id: str) -> AccessCard:
        """Delete an access card"""
        return self.manage(card_id, "delete")


class HIDOrgs:
    def __init__(self, client):
        self._client = client

    def activate(self, email: str, password: str) -> Org:
        """
        Complete HID org registration with credentials from HID email.

        Args:
            email: Admin email address
            password: Password from HID registration email

        Returns:
            Org object with registration details
        """
        data = {"email": email, "password": password}
        response = self._client._post("/v1/console/hid/orgs/activate", data)
        return Org(self._client, response)

    def list(self) -> List["Org"]:
        """
        List all HID organizations.

        Returns:
            List of Org objects
        """
        response = self._client._get("/v1/console/hid/orgs")
        orgs = response if isinstance(response, list) else response.get("orgs", [])
        return [Org(self._client, org) for org in orgs]

    def create(
        self, name: str, full_address: str, phone: str, first_name: str, last_name: str
    ) -> Org:
        """
        Create a new HID organization.

        Args:
            name: Organization name
            full_address: Full address of the organization
            phone: Phone number (e.g., '+1-555-0000')
            first_name: First name of the contact person
            last_name: Last name of the contact person

        Returns:
            Org object with creation details
        """
        data = {
            "name": name,
            "full_address": full_address,
            "phone": phone,
            "first_name": first_name,
            "last_name": last_name,
        }
        response = self._client._post("/v1/console/hid/orgs", data)
        return Org(self._client, response)


class HID:
    def __init__(self, client):
        self._client = client
        self.orgs = HIDOrgs(client)


class Webhooks:
    def __init__(self, client):
        self._client = client

    def create(
        self,
        name: str,
        url: str,
        subscribed_events: List[str],
        auth_method: str = "bearer_token",
    ) -> Webhook:
        """Create a new webhook."""
        data = {
            "name": name,
            "url": url,
            "subscribed_events": subscribed_events,
            "auth_method": auth_method,
        }
        response = self._client._post("/v1/console/webhooks", data)
        return Webhook(self._client, response)

    def list(self, **kwargs) -> List[Webhook]:
        """List all webhooks."""
        response = self._client._get("/v1/console/webhooks", params=kwargs)
        return [Webhook(self._client, wh) for wh in response.get("webhooks", [])]

    def delete(self, webhook_id: str) -> None:
        """Delete a webhook by ID."""
        self._client._delete(f"/v1/console/webhooks/{webhook_id}")


class CredentialProfiles:
    def __init__(self, client):
        self._client = client

    def create(
        self, name: str, app_name: str = "KEY-ID-main", keys: Optional[List[Dict]] = None, file_id: Optional[str] = None
    ) -> CredentialProfile:
        """
        Create a new credential profile.

        Args:
            name: Profile name
            app_name: Application name (default: KEY-ID-main)
            keys: List of key dicts, each with 'value' and optional 'keys_diversified', 'source_key_index'
            file_id: Optional file ID (default: "00")

        Returns:
            CredentialProfile object
        """
        data: Dict[str, Any] = {"name": name, "app_name": app_name}
        if keys is not None:
            data["keys"] = keys
        if file_id is not None:
            data["file_id"] = file_id
        response = self._client._post("/v1/console/credential-profiles", data)
        return CredentialProfile(self._client, response)

    def list(self) -> List[CredentialProfile]:
        """
        List all credential profiles.

        Returns:
            List of CredentialProfile objects
        """
        response = self._client._get("/v1/console/credential-profiles")
        profiles = response if isinstance(response, list) else response.get("credential_profiles", [])
        return [CredentialProfile(self._client, p) for p in profiles]


class Console:
    def __init__(self, client):
        self._client = client
        self.hid = HID(client)
        self.webhooks = Webhooks(client)
        self.credential_profiles = CredentialProfiles(client)

    def create_template(self, **kwargs) -> Template:
        """Create a new card template"""
        response = self._client._post("/v1/console/card-templates", kwargs)
        return Template(self._client, response)

    def update_template(self, card_template_id: str, **kwargs) -> Template:
        """Update an existing card template"""
        response = self._client._put(
            f"/v1/console/card-templates/{card_template_id}", kwargs
        )
        return Template(self._client, response)

    def read_template(self, card_template_id: str) -> Union[Template, List[Template]]:
        "Read card template by id or list the card template pairs"
        response = self._client._get(f"/v1/console/card-templates/{card_template_id}")
        if "templates" in response:
            return [Template(self._client, item) for item in response["templates"]]
        return Template(self._client, response)

    def get_logs(self, template_id: str, **kwargs) -> Dict[str, Any]:
        """Get event logs for a card template"""
        return self._client._get(
            f"/v1/console/card-templates/{template_id}/logs", params=kwargs
        )

    def event_log(self, card_template_id: str, **kwargs) -> Dict[str, Any]:
        """Alias for get_logs. Get event logs for a card template."""
        return self.get_logs(card_template_id, **kwargs)

    def ios_preflight(
        self, card_template_id: str, access_pass_ex_id: str
    ) -> IosPreflight:
        """Run iOS In-App Provisioning preflight for an access pass."""
        data = {"access_pass_ex_id": access_pass_ex_id}
        response = self._client._post(
            f"/v1/console/card-templates/{card_template_id}/ios_preflight", data
        )
        return IosPreflight(self._client, response)

    def ledger_items(self, **kwargs) -> Dict[str, Any]:
        """
        List ledger items with pagination and date filtering.

        Args:
            page: Page number for pagination (default: 1)
            per_page: Number of results per page (default: 50, max: 100)
            start_date: ISO8601 start date filter
            end_date: ISO8601 end date filter

        Returns:
            Dict containing ledger_items list and pagination info
        """
        return self._client._get("/v1/console/ledger-items", params=kwargs)

    def list_landing_pages(self) -> List[LandingPage]:
        """List all landing pages."""
        response = self._client._get("/v1/console/landing-pages")
        pages = response if isinstance(response, list) else response.get("landing_pages", [])
        return [LandingPage(self._client, lp) for lp in pages]

    def create_landing_page(self, **kwargs) -> LandingPage:
        """
        Create a new landing page.

        Args:
            name: Landing page name
            kind: Landing page kind (e.g. 'universal')
            additional_text: Optional text to display
            bg_color: Background color hex string
            allow_immediate_download: Whether to allow immediate download
            password: Optional password protection
            is_2fa_enabled: Whether 2FA is enabled
            logo: Optional base64-encoded logo image

        Returns:
            LandingPage object
        """
        response = self._client._post("/v1/console/landing-pages", kwargs)
        return LandingPage(self._client, response)

    def update_landing_page(self, landing_page_id: str, **kwargs) -> LandingPage:
        """
        Update an existing landing page.

        Args:
            landing_page_id: The landing page ID
            name: Updated name
            additional_text: Updated text
            bg_color: Updated background color
            allow_immediate_download: Updated download setting
            password: Updated password
            is_2fa_enabled: Updated 2FA setting
            logo: Updated base64-encoded logo image

        Returns:
            LandingPage object
        """
        response = self._client._put(
            f"/v1/console/landing-pages/{landing_page_id}", kwargs
        )
        return LandingPage(self._client, response)

    def list_pass_template_pairs(self, **kwargs) -> Dict[str, Any]:
        """
        List Pass Template Pairs with pagination support.

        Args:
            page: Page number for pagination (default: 1)
            per_page: Number of results per page (default: 50, max: 100)

        Returns:
            Dict containing pass_template_pairs list and pagination info
        """
        response = self._client._get("/v1/console/pass-template-pairs", params=kwargs)

        if "pass_template_pairs" in response:
            response["pass_template_pairs"] = [
                PassTemplatePair(self._client, pair)
                for pair in response["pass_template_pairs"]
            ]

        return response


class AccessGrid:
    def __init__(
        self,
        account_id: str,
        secret_key: str,
        base_url: str = "https://api.accessgrid.com",
    ):
        if not account_id:
            raise ValueError("Account ID is required")
        if not secret_key:
            raise ValueError("Secret Key is required")

        self.account_id = account_id
        self.secret_key = secret_key
        self.base_url = base_url.rstrip("/")

        # Initialize API clients
        self.access_cards = AccessCards(self)
        self.console = Console(self)

    def _generate_signature(self, payload: str) -> str:
        """
        Generate HMAC signature for the payload according to the shared secret scheme:
        SHA256.update(shared_secret + base64.encode(payload)).hexdigest()

        For requests with no payload (like GET, or actions like
        suspend/unlink/resume), caller should provide a payload
        with {"id": "{resource_id}"}
        """
        # Base64 encode the payload
        payload_bytes = payload.encode()
        encoded_payload = base64.b64encode(payload_bytes)

        # Create HMAC using the shared secret as the key
        # and the base64 encoded payload as the message
        signature = hmac.new(
            self.secret_key.encode(), encoded_payload, hashlib.sha256
        ).hexdigest()

        return signature

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API"""
        url = f"{self.base_url}{endpoint}"

        # Extract resource ID from the endpoint if needed for signature
        resource_id = None
        if method in ("GET", "DELETE") or (
            method == "POST" and (not data or data == {})
        ):
            # Extract ID from endpoint patterns like
            # /resource/{id} or /resource/{id}/action
            parts = endpoint.strip("/").split("/")
            if len(parts) >= 2:
                # For actions like unlink/suspend/resume,
                # get the card ID (second to last part)
                if parts[-1] in ["suspend", "resume", "unlink", "delete"]:
                    resource_id = parts[-2]
                else:
                    # Otherwise, the ID is typically the last part of the path
                    resource_id = parts[-1]

        # Special handling for requests with no payload:
        # 1. POST requests with empty body (like unlink/suspend/resume)
        # 2. GET requests
        if (method == "POST" and not data) or method in ("GET", "DELETE"):
            # Use {"id": "card_id"} as the signature payload
            if resource_id:
                payload = json.dumps({"id": resource_id})
            else:
                payload = "{}"
        else:
            # For normal POST/PUT/PATCH with body, use the actual payload
            payload = json.dumps(data) if data else ""

        # Generate signature — resource_id is already
        # incorporated into the payload when needed
        signature = self._generate_signature(payload)

        headers = {
            "X-ACCT-ID": self.account_id,
            "X-PAYLOAD-SIG": signature,
            "Content-Type": "application/json",
            "User-Agent": f"accessgrid.py @ v{__version__}",
        }

        # For GET requests, we don't need to add sig_payload here anymore
        # as it's handled in the request section below

        try:
            # For empty-body requests (GET or actions),
            # include the sig_payload parameter
            if method in ("GET", "DELETE") or (method == "POST" and not data):
                if not params:
                    params = {}
                # Include the ID payload in the query params
                if resource_id:
                    # The server expects the raw JSON string, not URL-encoded
                    params["sig_payload"] = json.dumps({"id": resource_id})

            # For POST/PUT/PATCH with empty body, don't include a JSON body
            # as the server uses request.raw_post which would be empty
            json_data = data if data and method != "GET" else None

            response = requests.request(
                method=method, url=url, headers=headers, json=json_data, params=params
            )

            if response.status_code == 401:
                raise AuthenticationError("Invalid credentials")
            elif response.status_code == 402:
                raise AccessGridError("Insufficient account balance")
            elif not 200 <= response.status_code < 300:
                error_data = response.json() if response.text else {}
                error_message = error_data.get("message", response.text)
                raise AccessGridError(f"API request failed: {error_message}")

            if response.status_code == 204 or not response.text:
                return {}

            return response.json()

        except requests.exceptions.RequestException as e:
            raise AccessGridError(f"Request failed: {str(e)}")

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request"""
        return self._make_request("GET", endpoint, params=params)

    def _post(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """Make a POST request"""
        return self._make_request("POST", endpoint, data=data)

    def _put(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """Make a PUT request"""
        return self._make_request("PUT", endpoint, data=data)

    def _patch(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """Make a PATCH request"""
        return self._make_request("PATCH", endpoint, data=data)

    def _delete(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make a DELETE request"""
        return self._make_request("DELETE", endpoint)
