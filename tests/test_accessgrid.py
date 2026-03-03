import pytest
from unittest.mock import patch, Mock
from accessgrid import AccessGrid, AccessGridError, AuthenticationError

MOCK_ACCOUNT_ID = 'test-account-id'
MOCK_SECRET_KEY = 'test-secret-key'

@pytest.fixture
def client():
    return AccessGrid(MOCK_ACCOUNT_ID, MOCK_SECRET_KEY)

@pytest.fixture
def mock_response():
    mock = Mock()
    mock.json.return_value = {'status': 'success'}
    mock.status_code = 200
    mock.text = '{"status": "success"}'
    return mock

class TestAccessGrid:
    def test_constructor_missing_account_id(self):
        with pytest.raises(ValueError, match='Account ID is required'):
            AccessGrid(None, MOCK_SECRET_KEY)

    def test_constructor_missing_secret_key(self):
        with pytest.raises(ValueError, match='Secret Key is required'):
            AccessGrid(MOCK_ACCOUNT_ID, None)

    def test_constructor_with_custom_base_url(self):
        custom_url = 'https://custom.api.com'
        client = AccessGrid(MOCK_ACCOUNT_ID, MOCK_SECRET_KEY, base_url=custom_url)
        assert client.base_url == custom_url.rstrip('/')

class TestAccessCards:
    @pytest.fixture
    def mock_provision_params(self):
        return {
            'card_template_id': '0xd3adb00b5',
            'employee_id': '123456789',
            'tag_id': 'DDEADB33FB00B5',
            'full_name': 'Employee name',
            'email': 'employee@yourwebsite.com',
            'phone_number': '+19547212241',
            'classification': 'full_time',
            'start_date': '2025-01-31T22:46:25.601Z',
            'expiration_date': '2025-04-30T22:46:25.601Z',
            'employee_photo': 'base64photo'
        }

    @patch('requests.request')
    def test_provision_card(self, mock_request, client, mock_response, mock_provision_params):
        mock_request.return_value = mock_response

        card = client.access_cards.provision(**mock_provision_params)

        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        assert call_args['method'] == 'POST'
        assert call_args['url'] == f"{client.base_url}/v1/key-cards"
        assert call_args['json'] == mock_provision_params
        assert call_args['headers']['X-ACCT-ID'] == MOCK_ACCOUNT_ID
        assert 'X-PAYLOAD-SIG' in call_args['headers']
        assert call_args['headers']['Content-Type'] == 'application/json'

    @patch('requests.request')
    def test_provision_card_error(self, mock_request, client, mock_provision_params):
        error_response = Mock()
        error_response.status_code = 400
        error_response.text = '{"message": "Invalid template ID"}'
        error_response.json.return_value = {"message": "Invalid template ID"}
        mock_request.return_value = error_response

        with pytest.raises(AccessGridError, match='API request failed: Invalid template ID'):
            client.access_cards.provision(**mock_provision_params)

    @patch('requests.request')
    def test_get_card(self, mock_request, client):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            'id': 'card-123',
            'full_name': 'John Doe',
            'state': 'active',
            'install_url': 'https://example.com/install/card-123',
            'card_template_id': 'tmpl-456',
            'expiration_date': '2025-12-31'
        }
        mock_request.return_value = mock_resp

        card = client.access_cards.get('card-123')

        call_args = mock_request.call_args[1]
        assert call_args['method'] == 'GET'
        assert call_args['url'] == f"{client.base_url}/v1/key-cards/card-123"
        assert card.id == 'card-123'
        assert card.full_name == 'John Doe'
        assert card.state == 'active'
        assert card.install_url == 'https://example.com/install/card-123'
        assert card.card_template_id == 'tmpl-456'

    @patch('requests.request')
    def test_update_card(self, mock_request, client, mock_response):
        mock_request.return_value = mock_response
        card_id = '0xc4rd1d'
        update_params = {
            'employee_id': '987654321',
            'full_name': 'Updated Employee Name',
            'classification': 'contractor',
            'expiration_date': '2025-02-22T21:04:03.664Z'
        }

        card = client.access_cards.update(card_id, **update_params)

        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        assert call_args['method'] == 'PATCH'
        assert call_args['url'] == f"{client.base_url}/v1/key-cards/{card_id}"
        assert call_args['json'] == update_params

    @patch('requests.request')
    def test_manage_operations(self, mock_request, client, mock_response):
        mock_request.return_value = mock_response
        card_id = '0xc4rd1d'

        # Test suspend
        client.access_cards.suspend(card_id)
        call_args = mock_request.call_args[1]
        assert call_args['method'] == 'POST'
        assert call_args['url'] == f"{client.base_url}/v1/key-cards/{card_id}/suspend"
        assert call_args['json'] is None

        # Test resume
        client.access_cards.resume(card_id)
        call_args = mock_request.call_args[1]
        assert call_args['method'] == 'POST'
        assert call_args['url'] == f"{client.base_url}/v1/key-cards/{card_id}/resume"
        assert call_args['json'] is None

        # Test unlink
        client.access_cards.unlink(card_id)
        call_args = mock_request.call_args[1]
        assert call_args['method'] == 'POST'
        assert call_args['url'] == f"{client.base_url}/v1/key-cards/{card_id}/unlink"
        assert call_args['json'] is None
    
    @patch('requests.request')
    def test_list_keys(self, mock_request, client, mock_response):
        mock_response.json.return_value = {
            'keys': [
                {
                    'id': 'key1',
                    'state': 'active',
                    'full_name': 'John Doe',
                    'install_url': 'https://example.com/install/key1',
                    'expiration_date': '2025-12-31'
                },
                {
                    'id': 'key2',
                    'state': 'suspended',
                    'full_name': 'Jane Smith',
                    'install_url': 'https://example.com/install/key2',
                    'expiration_date': '2025-12-31'
                }
            ]
        }
        mock_request.return_value = mock_response
        template_id = '0xd3adb00b5'

        # Test list with template_id only
        keys = client.access_cards.list(template_id=template_id)
        assert len(keys) == 2
        assert keys[0].id == 'key1'
        assert keys[0].state == 'active'
        assert keys[0].full_name == 'John Doe'

        call_args = mock_request.call_args[1]
        assert call_args['method'] == 'GET'
        assert call_args['url'] == f"{client.base_url}/v1/key-cards"
        assert call_args['params']['template_id'] == template_id
        assert 'sig_payload' in call_args['params']

        # Test list with template_id and state
        keys = client.access_cards.list(template_id=template_id, state='active')
        call_args = mock_request.call_args[1]
        assert call_args['params']['template_id'] == template_id
        assert call_args['params']['state'] == 'active'
        assert 'sig_payload' in call_args['params']

class TestConsole:
    @pytest.fixture
    def mock_template_params(self):
        return {
            'name': 'Employee NFC key',
            'platform': 'apple',
            'use_case': 'employee_badge',
            'protocol': 'desfire',
            'allow_on_multiple_devices': True,
            'watch_count': 2,
            'iphone_count': 3,
            'design': {
                'background_color': '#FFFFFF',
                'label_color': '#000000',
                'label_secondary_color': '#333333'
            },
            'support_info': {
                'support_url': 'https://help.yourcompany.com',
                'support_phone_number': '+1-555-123-4567',
                'support_email': 'support@yourcompany.com',
                'privacy_policy_url': 'https://yourcompany.com/privacy',
                'terms_and_conditions_url': 'https://yourcompany.com/terms'
            }
        }

    @patch('requests.request')
    def test_create_template(self, mock_request, client, mock_response, mock_template_params):
        mock_request.return_value = mock_response
        
        template = client.console.create_template(**mock_template_params)
        
        call_args = mock_request.call_args[1]
        assert call_args['method'] == 'POST'
        assert call_args['url'] == f"{client.base_url}/v1/console/card-templates"
        assert call_args['json'] == mock_template_params

    @patch('requests.request')
    def test_read_template(self, mock_request, client, mock_response):
        mock_request.return_value = mock_response
        template_id = '0xd3adb00b5'
        
        template = client.console.read_template(template_id)
        
        call_args = mock_request.call_args[1]
        assert call_args['method'] == 'GET'
        assert call_args['url'] == f"{client.base_url}/v1/console/card-templates/{template_id}"

    @patch('requests.request')
    def test_get_logs(self, mock_request, client, mock_response):
        mock_request.return_value = mock_response
        template_id = '0xd3adb00b5'
        filters = {
            'device': 'mobile',
            'start_date': '2025-01-01T00:00:00Z',
            'end_date': '2025-02-01T00:00:00Z',
            'event_type': 'install'
        }

        events = client.console.get_logs(template_id, **filters)

        call_args = mock_request.call_args[1]
        assert call_args['method'] == 'GET'
        assert call_args['url'] == f"{client.base_url}/v1/console/card-templates/{template_id}/logs"
        assert call_args['params']['device'] == 'mobile'
        assert call_args['params']['start_date'] == '2025-01-01T00:00:00Z'
        assert call_args['params']['end_date'] == '2025-02-01T00:00:00Z'
        assert call_args['params']['event_type'] == 'install'
