# AccessGrid SDK

A Python SDK for interacting with the [AccessGrid.com](https://www.accessgrid.com) API. This SDK provides a simple interface for managing NFC key cards and enterprise templates. Full docs at https://www.accessgrid.com/docs

## Installation

```bash
pip install accessgrid
```

## Quick Start

```python
from accessgrid import AccessGrid

account_id = os.environ.get('ACCOUNT_ID')
secret_key = os.environ.get('SECRET_KEY')

client = AccessGrid(account_id, secret_key)
```

## API Reference

### Access Cards

#### Provision a new card

```python
card = client.access_cards.provision(
    card_template_id="0xd3adb00b5",
    employee_id="123456789",
    full_name="Employee name",
    email="employee@yourwebsite.com",
    phone_number="+19547212241",
    classification="full_time",
    start_date="2025-01-31T22:46:25.601Z",
    expiration_date="2025-04-30T22:46:25.601Z",
    employee_photo="[image_in_base64_encoded_format]"
)
```

#### Update a card

```python
card = client.access_cards.update(
    card_id="0xc4rd1d",
    employee_id="987654321",
    full_name="Updated Employee Name",
    classification="contractor",
    expiration_date="2025-02-22T21:04:03.664Z",
    employee_photo="[image_in_base64_encoded_format]"
)
```

#### List NFC keys / Access passes

```python
# List all cards for a template
cards = client.access_cards.list(template_id="0xd3adb00b5")
for card in cards:
    print(card)  # Outputs: AccessCard(name='Employee Name', id='0xc4rd1d', state='active')

# Filter cards by state
active_cards = client.access_cards.list(template_id="0xd3adb00b5", state="active")
```

#### Manage card states

```python
# Suspend a card
client.access_cards.suspend(card_id="0xc4rd1d")

# Resume a card
client.access_cards.resume(card_id="0xc4rd1d")

# Unlink a card
client.access_cards.unlink(card_id="0xc4rd1d")

# Delete a card
client.access_cards.delete(card_id="0xc4rd1d")
```

### Enterprise Console

#### Create a template

```python
template = client.console.create_template(
    name="Employee Access Pass",
    platform="apple",
    use_case="employee_badge",
    protocol="desfire",
    allow_on_multiple_devices=True,
    watch_count=2,
    iphone_count=3,
    background_color="#FFFFFF",
    label_color="#000000",
    label_secondary_color="#333333",
    support_url="https://help.yourcompany.com",
    support_phone_number="+1-555-123-4567",
    support_email="support@yourcompany.com",
    privacy_policy_url="https://yourcompany.com/privacy",
    terms_and_conditions_url="https://yourcompany.com/terms",
    metadata={
        "version": "2.1",
        "approval_status": "approved"
    }
)
```

#### Update a template

```python
template = client.console.update_template(
    template_id="0xd3adb00b5",
    name="Updated Employee NFC key",
    allow_on_multiple_devices=True,
    watch_count=2,
    iphone_count=3,
    support_url="https://help.yourcompany.com",
    support_phone_number="+1-555-123-4567",
    support_email="support@yourcompany.com",
    privacy_policy_url="https://yourcompany.com/privacy",
    terms_and_conditions_url="https://yourcompany.com/terms"
)
```

#### Read a template

```python
template = client.console.read_template(card_template_id="0xd3adb00b5")
```

#### Get event logs

```python
from datetime import datetime, timedelta

events = client.console.event_log(
    card_template_id="0xd3adb00b5",
    filters={
        "device": "mobile",  # "mobile" or "watch"
        "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "end_date": datetime.now().isoformat(),
        "event_type": "install"
    }
)
```

#### iOS In-App Provisioning Preflight

```python
response = client.console.ios_preflight(
    card_template_id="0xt3mp14t3-3x1d",
    access_pass_ex_id="0xp455-3x1d"
)

print(f"Provisioning Credential ID: {response.provisioningCredentialIdentifier}")
print(f"Sharing Instance ID: {response.sharingInstanceIdentifier}")
print(f"Card Template ID: {response.cardTemplateIdentifier}")
print(f"Environment ID: {response.environmentIdentifier}")
```

#### List ledger items

```python
from datetime import datetime, timezone, timedelta

start_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
end_date = datetime.now(timezone.utc).isoformat()

result = client.console.ledger_items(
    page=1,
    per_page=50,
    start_date=start_date,
    end_date=end_date
)

for item in result['ledger_items']:
    print(f"Amount: {item['amount']}, Kind: {item['kind']}, Date: {item['created_at']}")
    if item.get('access_pass'):
        print(f"  Access Pass: {item['access_pass']['ex_id']}")
        if item['access_pass'].get('pass_template'):
            print(f"  Card Template: {item['access_pass']['pass_template']['ex_id']}")
```

### Webhooks

#### Create a webhook

```python
webhook = client.console.webhooks.create(
    name='Production',
    url='https://example.com/webhooks',
    subscribed_events=['ag.access_pass.issued']
)

print(f"Webhook created: {webhook.id}")
print(f"Private key: {webhook.private_key}")
```

#### List webhooks

```python
webhooks = client.console.webhooks.list()

for webhook in webhooks:
    print(f"ID: {webhook.id}, Name: {webhook.name}")
```

#### Delete a webhook

```python
client.console.webhooks.delete('abc123')
```

### HID Organizations

#### Create a HID organization

```python
org = client.console.hid.orgs.create(
    name='My Organization',
    full_address='1 Main St, NY NY',
    phone='+1-555-0000',
    first_name='Ada',
    last_name='Lovelace'
)

print(f"Created org: {org.name} (ID: {org.id})")
print(f"Slug: {org.slug}")
```

#### Complete HID org registration

After creating an organization, complete the registration with credentials from your HID email:

```python
result = client.console.hid.orgs.activate(
    email='admin@example.com',
    password='hid-password-123'
)

print(f"Completed registration for org: {result.name}")
print(f"Status: {result.status}")
```

#### List all HID organizations

```python
orgs = client.console.hid.orgs.list()

for org in orgs:
    print(f"Org ID: {org.id}, Name: {org.name}, Slug: {org.slug}")
```

## Configuration

The SDK can be configured with custom options:

```python
client = AccessGrid(
    account_id,
    secret_key
)
```

## Error Handling

The SDK throws errors for various scenarios including:
- Missing required credentials
- API request failures
- Invalid parameters
- Server errors

Example error handling:

```python
try:
    card = client.access_cards.provision(
        # ... parameters
    )
except AccessGridError as error:
    print(f'Failed to provision card: {str(error)}')
```

## Requirements

- Python 3.7 or higher
- Required packages:
  - requests
  - cryptography
  - python-dateutil

## Security

The SDK automatically handles:
- Request signing using HMAC-SHA256
- Secure payload encoding
- Authentication headers
- HTTPS communication

Never expose your `secret_key` in source code. Always use environment variables or a secure configuration management system.

## License

MIT License - See LICENSE file for details.

## Feature Matrix

| Endpoint | Method | Supported |
|---|---|:---:|
| POST /v1/key-cards | `access_cards.issue()` | Y |
| GET /v1/key-cards/{id} | `access_cards.get()` | Y |
| PATCH /v1/key-cards/{id} | `access_cards.update()` | Y |
| GET /v1/key-cards | `access_cards.list()` | Y |
| POST /v1/key-cards/{id}/suspend | `access_cards.suspend()` | Y |
| POST /v1/key-cards/{id}/resume | `access_cards.resume()` | Y |
| POST /v1/key-cards/{id}/unlink | `access_cards.unlink()` | Y |
| POST /v1/key-cards/{id}/delete | `access_cards.delete()` | Y |
| POST /v1/console/card-templates | `console.create_template()` | Y |
| PUT /v1/console/card-templates/{id} | `console.update_template()` | Y |
| GET /v1/console/card-templates/{id} | `console.read_template()` | Y |
| GET /v1/console/card-templates/{id}/logs | `console.get_logs()` / `console.event_log()` | Y |
| GET /v1/console/pass-template-pairs | `console.list_pass_template_pairs()` | Y |
| POST /v1/console/card-templates/{id}/ios_preflight | `console.ios_preflight()` | Y |
| GET /v1/console/ledger-items | `console.ledger_items()` | Y |
| GET /v1/console/webhooks | `console.webhooks.list()` | Y |
| POST /v1/console/webhooks | `console.webhooks.create()` | Y |
| DELETE /v1/console/webhooks/{id} | `console.webhooks.delete()` | Y |
| POST /v1/console/hid/orgs | `console.hid.orgs.create()` | Y |
| POST /v1/console/hid/orgs/activate | `console.hid.orgs.activate()` | Y |
| GET /v1/console/hid/orgs | `console.hid.orgs.list()` | Y |
