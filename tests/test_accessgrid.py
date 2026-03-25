from unittest.mock import Mock, patch

import pytest

from accessgrid import AccessGrid, AccessGridError, AuthenticationError

MOCK_ACCOUNT_ID = "test-account-id"
MOCK_SECRET_KEY = "test-secret-key"


@pytest.fixture
def client():
    return AccessGrid(MOCK_ACCOUNT_ID, MOCK_SECRET_KEY)


@pytest.fixture
def mock_response():
    mock = Mock()
    mock.json.return_value = {"status": "success"}
    mock.status_code = 200
    mock.text = '{"status": "success"}'
    return mock


class TestAccessGrid:
    def test_constructor_missing_account_id(self):
        with pytest.raises(ValueError, match="Account ID is required"):
            AccessGrid(None, MOCK_SECRET_KEY)

    def test_constructor_missing_secret_key(self):
        with pytest.raises(ValueError, match="Secret Key is required"):
            AccessGrid(MOCK_ACCOUNT_ID, None)

    def test_constructor_with_custom_base_url(self):
        custom_url = "https://custom.api.com"
        client = AccessGrid(MOCK_ACCOUNT_ID, MOCK_SECRET_KEY, base_url=custom_url)
        assert client.base_url == custom_url.rstrip("/")


class TestAccessCards:
    @pytest.fixture
    def mock_provision_params(self):
        return {
            "card_template_id": "0xd3adb00b5",
            "employee_id": "123456789",
            "tag_id": "DDEADB33FB00B5",
            "full_name": "Employee name",
            "email": "employee@yourwebsite.com",
            "phone_number": "+19547212241",
            "classification": "full_time",
            "start_date": "2025-01-31T22:46:25.601Z",
            "expiration_date": "2025-04-30T22:46:25.601Z",
            "employee_photo": "base64photo",
        }

    @patch("requests.request")
    def test_provision_card(
        self, mock_request, client, mock_response, mock_provision_params
    ):
        mock_request.return_value = mock_response

        client.access_cards.provision(**mock_provision_params)

        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        assert call_args["method"] == "POST"
        assert call_args["url"] == f"{client.base_url}/v1/key-cards"
        assert call_args["json"] == mock_provision_params
        assert call_args["headers"]["X-ACCT-ID"] == MOCK_ACCOUNT_ID
        assert "X-PAYLOAD-SIG" in call_args["headers"]
        assert call_args["headers"]["Content-Type"] == "application/json"

    @patch("requests.request")
    def test_issue_returns_unified_access_pass(
        self, mock_request, client, mock_provision_params
    ):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": "uap-1",
            "install_url": "https://example.com/install/uap-1",
            "state": "active",
            "status": "issued",
            "details": [
                {
                    "id": "card-ios",
                    "state": "active",
                    "full_name": "John Doe",
                    "install_url": "https://example.com/install/card-ios",
                },
                {
                    "id": "card-android",
                    "state": "active",
                    "full_name": "John Doe",
                    "install_url": "https://example.com/install/card-android",
                },
            ],
        }
        mock_request.return_value = mock_resp

        result = client.access_cards.issue(**mock_provision_params)

        assert type(result).__name__ == "UnifiedAccessPass"
        assert result.id == "uap-1"
        assert result.state == "active"
        assert result.status == "issued"
        assert len(result.details) == 2
        assert result.details[0].id == "card-ios"
        assert result.details[1].id == "card-android"
        expected_str = (
            "UnifiedAccessPass(id='uap-1', state='active', cards=2)"  # noqa: E501
        )
        assert str(result) == expected_str
        assert repr(result) == expected_str

    @patch("requests.request")
    def test_provision_card_auth_error(
        self, mock_request, client, mock_provision_params
    ):
        error_response = Mock()
        error_response.status_code = 401
        error_response.text = "Unauthorized"
        mock_request.return_value = error_response

        with pytest.raises(AuthenticationError, match="Invalid credentials"):
            client.access_cards.provision(**mock_provision_params)

    @patch("requests.request")
    def test_provision_card_balance_error(
        self, mock_request, client, mock_provision_params
    ):
        error_response = Mock()
        error_response.status_code = 402
        error_response.text = "Payment required"
        mock_request.return_value = error_response

        with pytest.raises(AccessGridError, match="Insufficient account balance"):
            client.access_cards.provision(**mock_provision_params)

    @patch("requests.request")
    def test_provision_card_error(self, mock_request, client, mock_provision_params):
        error_response = Mock()
        error_response.status_code = 400
        error_response.text = '{"message": "Invalid template ID"}'
        error_response.json.return_value = {"message": "Invalid template ID"}
        mock_request.return_value = error_response

        with pytest.raises(
            AccessGridError, match="API request failed: Invalid template ID"
        ):
            client.access_cards.provision(**mock_provision_params)

    @patch("requests.request")
    def test_get_card(self, mock_request, client):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": "card-123",
            "full_name": "John Doe",
            "state": "active",
            "install_url": "https://example.com/install/card-123",
            "card_template_id": "tmpl-456",
            "expiration_date": "2025-12-31",
        }
        mock_request.return_value = mock_resp

        card = client.access_cards.get("card-123")

        call_args = mock_request.call_args[1]
        assert call_args["method"] == "GET"
        assert call_args["url"] == f"{client.base_url}/v1/key-cards/card-123"
        assert card.id == "card-123"
        assert card.full_name == "John Doe"
        assert card.state == "active"
        assert card.install_url == "https://example.com/install/card-123"
        assert card.card_template_id == "tmpl-456"
        expected_str = "AccessCard(name='John Doe', id='card-123', state='active', card_template_id='tmpl-456')"  # noqa: E501
        assert str(card) == expected_str
        assert repr(card) == expected_str

    @patch("requests.request")
    def test_update_card(self, mock_request, client, mock_response):
        mock_request.return_value = mock_response
        card_id = "0xc4rd1d"
        update_params = {
            "employee_id": "987654321",
            "full_name": "Updated Employee Name",
            "classification": "contractor",
            "expiration_date": "2025-02-22T21:04:03.664Z",
        }

        client.access_cards.update(card_id, **update_params)

        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        assert call_args["method"] == "PATCH"
        assert call_args["url"] == f"{client.base_url}/v1/key-cards/{card_id}"
        assert call_args["json"] == update_params

    @patch("requests.request")
    def test_manage_operations(self, mock_request, client, mock_response):
        mock_request.return_value = mock_response
        card_id = "0xc4rd1d"

        # Test suspend
        client.access_cards.suspend(card_id)
        call_args = mock_request.call_args[1]
        assert call_args["method"] == "POST"
        assert call_args["url"] == f"{client.base_url}/v1/key-cards/{card_id}/suspend"
        assert call_args["json"] is None

        # Test resume
        client.access_cards.resume(card_id)
        call_args = mock_request.call_args[1]
        assert call_args["method"] == "POST"
        assert call_args["url"] == f"{client.base_url}/v1/key-cards/{card_id}/resume"
        assert call_args["json"] is None

        # Test unlink
        client.access_cards.unlink(card_id)
        call_args = mock_request.call_args[1]
        assert call_args["method"] == "POST"
        assert call_args["url"] == f"{client.base_url}/v1/key-cards/{card_id}/unlink"
        assert call_args["json"] is None

        # Test delete
        client.access_cards.delete(card_id)
        call_args = mock_request.call_args[1]
        assert call_args["method"] == "POST"
        assert call_args["url"] == f"{client.base_url}/v1/key-cards/{card_id}/delete"
        assert call_args["json"] is None

    @patch("requests.request")
    def test_list_keys(self, mock_request, client, mock_response):
        mock_response.json.return_value = {
            "keys": [
                {
                    "id": "key1",
                    "state": "active",
                    "full_name": "John Doe",
                    "install_url": "https://example.com/install/key1",
                    "expiration_date": "2025-12-31",
                },
                {
                    "id": "key2",
                    "state": "suspended",
                    "full_name": "Jane Smith",
                    "install_url": "https://example.com/install/key2",
                    "expiration_date": "2025-12-31",
                },
            ]
        }
        mock_request.return_value = mock_response
        template_id = "0xd3adb00b5"

        # Test list with template_id only
        keys = client.access_cards.list(template_id=template_id)
        assert len(keys) == 2
        assert keys[0].id == "key1"
        assert keys[0].state == "active"
        assert keys[0].full_name == "John Doe"

        call_args = mock_request.call_args[1]
        assert call_args["method"] == "GET"
        assert call_args["url"] == f"{client.base_url}/v1/key-cards"
        assert call_args["params"]["template_id"] == template_id
        assert "sig_payload" in call_args["params"]

        # Test list with template_id and state
        keys = client.access_cards.list(template_id=template_id, state="active")
        call_args = mock_request.call_args[1]
        assert call_args["params"]["template_id"] == template_id
        assert call_args["params"]["state"] == "active"
        assert "sig_payload" in call_args["params"]


class TestConsole:
    @pytest.fixture
    def mock_template_params(self):
        return {
            "name": "Employee NFC key",
            "platform": "apple",
            "use_case": "employee_badge",
            "protocol": "desfire",
            "allow_on_multiple_devices": True,
            "watch_count": 2,
            "iphone_count": 3,
            "design": {
                "background_color": "#FFFFFF",
                "label_color": "#000000",
                "label_secondary_color": "#333333",
            },
            "support_info": {
                "support_url": "https://help.yourcompany.com",
                "support_phone_number": "+1-555-123-4567",
                "support_email": "support@yourcompany.com",
                "privacy_policy_url": "https://yourcompany.com/privacy",
                "terms_and_conditions_url": "https://yourcompany.com/terms",
            },
        }

    @patch("requests.request")
    def test_create_template(
        self, mock_request, client, mock_response, mock_template_params
    ):
        mock_request.return_value = mock_response

        client.console.create_template(**mock_template_params)

        call_args = mock_request.call_args[1]
        assert call_args["method"] == "POST"
        assert call_args["url"] == f"{client.base_url}/v1/console/card-templates"
        assert call_args["json"] == mock_template_params

    @patch("requests.request")
    def test_update_template(self, mock_request, client, mock_response):
        mock_request.return_value = mock_response
        template_id = "0xd3adb00b5"
        update_params = {
            "name": "Updated Template",
            "allow_on_multiple_devices": False,
            "watch_count": 1,
            "iphone_count": 2,
        }

        client.console.update_template(template_id, **update_params)

        call_args = mock_request.call_args[1]
        assert call_args["method"] == "PUT"
        assert (
            call_args["url"]
            == f"{client.base_url}/v1/console/card-templates/{template_id}"
        )
        assert call_args["json"] == update_params

    @patch("requests.request")
    def test_read_template(self, mock_request, client, mock_response):
        mock_request.return_value = mock_response
        template_id = "0xd3adb00b5"

        client.console.read_template(template_id)

        call_args = mock_request.call_args[1]
        assert call_args["method"] == "GET"
        assert (
            call_args["url"]
            == f"{client.base_url}/v1/console/card-templates/{template_id}"
        )

    @patch("requests.request")
    def test_list_pass_template_pairs(self, mock_request, client):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "pass_template_pairs": [
                {
                    "id": "pair-1",
                    "name": "Employee Badge",
                    "created_at": "2025-01-15T10:00:00Z",
                    "android_template": {
                        "id": "tmpl-android-1",
                        "name": "Android Employee Badge",
                        "platform": "google",
                    },
                    "ios_template": {
                        "id": "tmpl-ios-1",
                        "name": "iOS Employee Badge",
                        "platform": "apple",
                    },
                },
                {
                    "id": "pair-2",
                    "name": "Visitor Pass",
                    "created_at": "2025-02-01T12:00:00Z",
                    "android_template": None,
                    "ios_template": {
                        "id": "tmpl-ios-2",
                        "name": "iOS Visitor Pass",
                        "platform": "apple",
                    },
                },
            ],
            "page": 1,
            "per_page": 50,
        }
        mock_request.return_value = mock_resp

        result = client.console.list_pass_template_pairs(page=1, per_page=50)

        call_args = mock_request.call_args[1]
        assert call_args["method"] == "GET"
        assert call_args["url"] == f"{client.base_url}/v1/console/pass-template-pairs"
        assert call_args["params"]["page"] == 1
        assert call_args["params"]["per_page"] == 50

        pairs = result["pass_template_pairs"]
        assert len(pairs) == 2

        # First pair — both platforms
        assert pairs[0].id == "pair-1"
        assert pairs[0].name == "Employee Badge"
        assert pairs[0].android_template.id == "tmpl-android-1"
        assert pairs[0].android_template.platform == "google"
        expected_ti = "TemplateInfo(id='tmpl-android-1', name='Android Employee Badge', platform='google')"  # noqa: E501
        assert str(pairs[0].android_template) == expected_ti
        assert repr(pairs[0].android_template) == expected_ti
        assert pairs[0].ios_template.id == "tmpl-ios-1"
        assert pairs[0].ios_template.platform == "apple"

        # Second pair — android_template is None
        assert pairs[1].id == "pair-2"
        assert pairs[1].android_template is None
        assert pairs[1].ios_template.id == "tmpl-ios-2"


class TestHIDOrgs:
    @patch("requests.request")
    def test_create_org(self, mock_request, client):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": "org-1",
            "name": "Acme Corp",
            "slug": "acme-corp",
            "status": "pending",
            "full_address": "123 Main St",
            "phone": "+1-555-0000",
            "first_name": "Jane",
            "last_name": "Doe",
            "created_at": "2025-01-15T10:00:00Z",
        }
        mock_request.return_value = mock_resp

        org = client.console.hid.orgs.create(
            name="Acme Corp",
            full_address="123 Main St",
            phone="+1-555-0000",
            first_name="Jane",
            last_name="Doe",
        )

        call_args = mock_request.call_args[1]
        assert call_args["method"] == "POST"
        assert call_args["url"] == f"{client.base_url}/v1/console/hid/orgs"
        assert call_args["json"]["name"] == "Acme Corp"
        assert call_args["json"]["first_name"] == "Jane"
        assert org.id == "org-1"
        assert org.name == "Acme Corp"
        assert org.slug == "acme-corp"
        assert org.status == "pending"
        expected_str = "Org(name='Acme Corp', id='org-1', slug='acme-corp', status='pending')"  # noqa: E501
        assert str(org) == expected_str
        assert repr(org) == expected_str

    @patch("requests.request")
    def test_activate_org(self, mock_request, client):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": "org-1",
            "name": "Acme Corp",
            "slug": "acme-corp",
            "status": "active",
            "email": "admin@acme.com",
        }
        mock_request.return_value = mock_resp

        org = client.console.hid.orgs.activate(
            email="admin@acme.com", password="hid-registration-pw"
        )

        call_args = mock_request.call_args[1]
        assert call_args["method"] == "POST"
        assert call_args["url"] == f"{client.base_url}/v1/console/hid/orgs/activate"
        assert call_args["json"]["email"] == "admin@acme.com"
        assert call_args["json"]["password"] == "hid-registration-pw"
        assert org.id == "org-1"
        assert org.status == "active"

    @patch("requests.request")
    def test_list_orgs(self, mock_request, client):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "orgs": [
                {"id": "org-1", "name": "Acme Corp", "status": "active"},
                {"id": "org-2", "name": "Globex", "status": "pending"},
            ]
        }
        mock_request.return_value = mock_resp

        orgs = client.console.hid.orgs.list()

        call_args = mock_request.call_args[1]
        assert call_args["method"] == "GET"
        assert call_args["url"] == f"{client.base_url}/v1/console/hid/orgs"
        assert len(orgs) == 2
        assert orgs[0].id == "org-1"
        assert orgs[0].name == "Acme Corp"
        assert orgs[1].status == "pending"


class TestConsoleLogs:
    @patch("requests.request")
    def test_get_logs(self, mock_request, client, mock_response):
        mock_request.return_value = mock_response
        template_id = "0xd3adb00b5"
        filters = {
            "device": "mobile",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-02-01T00:00:00Z",
            "event_type": "install",
        }

        client.console.get_logs(template_id, **filters)

        call_args = mock_request.call_args[1]
        assert call_args["method"] == "GET"
        assert (
            call_args["url"]
            == f"{client.base_url}/v1/console/card-templates/{template_id}/logs"
        )
        assert call_args["params"]["device"] == "mobile"
        assert call_args["params"]["start_date"] == "2025-01-01T00:00:00Z"
        assert call_args["params"]["end_date"] == "2025-02-01T00:00:00Z"
        assert call_args["params"]["event_type"] == "install"

    @patch("requests.request")
    def test_event_log_alias(self, mock_request, client, mock_response):
        mock_request.return_value = mock_response
        template_id = "0xd3adb00b5"

        client.console.event_log(card_template_id=template_id, device="mobile")

        call_args = mock_request.call_args[1]
        assert call_args["method"] == "GET"
        assert (
            call_args["url"]
            == f"{client.base_url}/v1/console/card-templates/{template_id}/logs"
        )
        assert call_args["params"]["device"] == "mobile"


class TestIosPreflight:
    @patch("requests.request")
    def test_ios_preflight(self, mock_request, client):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = '{"provisioningCredentialIdentifier": "pci-123"}'
        mock_resp.json.return_value = {
            "provisioningCredentialIdentifier": "pci-123",
            "sharingInstanceIdentifier": "si-456",
            "cardTemplateIdentifier": "ct-789",
            "environmentIdentifier": "env-abc",
        }
        mock_request.return_value = mock_resp

        result = client.console.ios_preflight(
            card_template_id="0xt3mp14t3",
            access_pass_ex_id="0xp455",
        )

        call_args = mock_request.call_args[1]
        assert call_args["method"] == "POST"
        assert (
            call_args["url"]
            == f"{client.base_url}/v1/console/card-templates/0xt3mp14t3/ios_preflight"
        )
        assert call_args["json"]["access_pass_ex_id"] == "0xp455"
        assert result.provisioningCredentialIdentifier == "pci-123"
        assert result.sharingInstanceIdentifier == "si-456"
        assert result.cardTemplateIdentifier == "ct-789"
        assert result.environmentIdentifier == "env-abc"


class TestLedgerItems:
    @patch("requests.request")
    def test_ledger_items(self, mock_request, client):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = '{"ledger_items": []}'
        mock_resp.json.return_value = {
            "ledger_items": [
                {
                    "id": "li-1",
                    "amount": 100,
                    "kind": "ap_debit",
                    "event": "ag.access_pass.issued",
                    "created_at": "2025-01-15T10:00:00Z",
                    "metadata": {},
                    "access_pass": {
                        "id": "ap-1",
                        "ex_id": "ap-1",
                        "full_name": "John Doe",
                        "state": "active",
                        "pass_template": {
                            "id": "tmpl-1",
                            "ex_id": "tmpl-1",
                            "name": "Employee Badge",
                            "protocol": "desfire",
                            "platform": "apple",
                            "use_case": "employee_badge",
                        },
                    },
                }
            ],
            "pagination": {
                "current_page": 1,
                "per_page": 50,
                "total_pages": 1,
                "total_count": 1,
            },
        }
        mock_request.return_value = mock_resp

        result = client.console.ledger_items(
            page=1, per_page=50, start_date="2025-01-01T00:00:00Z"
        )

        call_args = mock_request.call_args[1]
        assert call_args["method"] == "GET"
        assert call_args["url"] == f"{client.base_url}/v1/console/ledger-items"
        assert call_args["params"]["page"] == 1
        assert call_args["params"]["per_page"] == 50
        assert call_args["params"]["start_date"] == "2025-01-01T00:00:00Z"

        items = result["ledger_items"]
        assert len(items) == 1
        assert items[0]["amount"] == 100
        assert items[0]["kind"] == "ap_debit"
        assert items[0]["access_pass"]["full_name"] == "John Doe"
        assert items[0]["access_pass"]["pass_template"]["name"] == "Employee Badge"
        assert result["pagination"]["total_count"] == 1


class TestWebhooks:
    @patch("requests.request")
    def test_create_webhook(self, mock_request, client):
        mock_resp = Mock()
        mock_resp.status_code = 201
        mock_resp.text = '{"id": "wh-1"}'
        mock_resp.json.return_value = {
            "id": "wh-1",
            "name": "Production",
            "url": "https://example.com/webhooks",
            "auth_method": "bearer_token",
            "subscribed_events": ["ag.access_pass.issued"],
            "created_at": "2025-01-15T10:00:00Z",
            "private_key": "pk-secret-123",
        }
        mock_request.return_value = mock_resp

        webhook = client.console.webhooks.create(
            name="Production",
            url="https://example.com/webhooks",
            subscribed_events=["ag.access_pass.issued"],
        )

        call_args = mock_request.call_args[1]
        assert call_args["method"] == "POST"
        assert call_args["url"] == f"{client.base_url}/v1/console/webhooks"
        assert call_args["json"]["name"] == "Production"
        assert call_args["json"]["url"] == "https://example.com/webhooks"
        assert call_args["json"]["subscribed_events"] == ["ag.access_pass.issued"]
        assert webhook.id == "wh-1"
        assert webhook.name == "Production"
        assert webhook.private_key == "pk-secret-123"
        expected_str = (
            "Webhook(id='wh-1', name='Production', "
            "url='https://example.com/webhooks')"
        )
        assert str(webhook) == expected_str

    @patch("requests.request")
    def test_list_webhooks(self, mock_request, client):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = '{"webhooks": []}'
        mock_resp.json.return_value = {
            "webhooks": [
                {
                    "id": "wh-1",
                    "name": "Production",
                    "url": "https://example.com/webhooks",
                    "auth_method": "bearer_token",
                    "subscribed_events": ["ag.access_pass.issued"],
                    "created_at": "2025-01-15T10:00:00Z",
                },
                {
                    "id": "wh-2",
                    "name": "Staging",
                    "url": "https://staging.example.com/webhooks",
                    "auth_method": "mtls",
                    "subscribed_events": ["ag.access_pass.issued"],
                    "created_at": "2025-02-01T12:00:00Z",
                    "cert_expires_at": "2026-02-01T12:00:00Z",
                },
            ]
        }
        mock_request.return_value = mock_resp

        webhooks = client.console.webhooks.list()

        call_args = mock_request.call_args[1]
        assert call_args["method"] == "GET"
        assert call_args["url"] == f"{client.base_url}/v1/console/webhooks"
        assert len(webhooks) == 2
        assert webhooks[0].id == "wh-1"
        assert webhooks[0].name == "Production"
        assert webhooks[1].id == "wh-2"
        assert webhooks[1].cert_expires_at == "2026-02-01T12:00:00Z"

    @patch("requests.request")
    def test_delete_webhook(self, mock_request, client):
        mock_resp = Mock()
        mock_resp.status_code = 204
        mock_resp.text = ""
        mock_request.return_value = mock_resp

        client.console.webhooks.delete("wh-1")

        call_args = mock_request.call_args[1]
        assert call_args["method"] == "DELETE"
        assert call_args["url"] == f"{client.base_url}/v1/console/webhooks/wh-1"


class TestPassTemplatePairDictAccess:
    def test_bracket_access(self):
        from accessgrid.client import PassTemplatePair

        data = {
            "id": "pair-1",
            "name": "Employee Badge",
            "created_at": "2025-01-15T10:00:00Z",
            "android_template": {
                "id": "tmpl-android-1",
                "name": "Android Badge",
                "platform": "google",
            },
            "ios_template": None,
        }
        pair = PassTemplatePair(None, data)

        assert pair["id"] == "pair-1"
        assert pair["name"] == "Employee Badge"
        assert pair["android_template"].id == "tmpl-android-1"
        assert pair["android_template"]["name"] == "Android Badge"
        assert pair["ios_template"] is None

    def test_get_method(self):
        from accessgrid.client import PassTemplatePair

        data = {
            "id": "pair-1",
            "name": "Test",
            "created_at": "2025-01-15T10:00:00Z",
            "android_template": None,
            "ios_template": None,
        }
        pair = PassTemplatePair(None, data)

        assert pair.get("id") == "pair-1"
        assert pair.get("missing", "default") == "default"
