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
    tag_id="DDEADB33FB00B5",
    full_name="Employee name",
    email="employee@yourwebsite.com",
    phone_number="+19547212241",
    classification="full_time",
    department="Engineering",
    location="San Francisco",
    site_name="HQ Building A",
    workstation="4F-207",
    mail_stop="MS-401",
    company_address="123 Main St, San Francisco, CA 94105",
    start_date="2025-01-31T22:46:25.601Z",
    expiration_date="2025-04-30T22:46:25.601Z",
    employee_photo="[image_in_base64_encoded_format]",
    title="Engineering Manager",
    metadata={
        "department": "engineering",
        "badge_type": "contractor"
    }
)
```

#### Update a card

```python
card = client.access_cards.update(
    card_id="0xc4rd1d",
    employee_id="987654321",
    full_name="Updated Employee Name",
    classification="contractor",
    department="Marketing",
    location="New York",
    site_name="NYC Office",
    workstation="2F-105",
    mail_stop="MS-200",
    company_address="456 Broadway, New York, NY 10013",
    expiration_date="2025-02-22T21:04:03.664Z",
    employee_photo="[image_in_base64_encoded_format]",
    title="Senior Developer"
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
    card_template_id="0xd3adb00b5",
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

### Landing Pages

#### List landing pages

```python
landing_pages = client.console.list_landing_pages()

for page in landing_pages:
    print(f"ID: {page.id}, Name: {page.name}, Kind: {page.kind}")
    print(f"  Password Protected: {page.password_protected}")
    if page.logo_url:
        print(f"  Logo URL: {page.logo_url}")
```

#### Create a landing page

```python
landing_page = client.console.create_landing_page(
    name="Miami Office Access Pass",
    kind="universal",
    additional_text="Welcome to the Miami Office",
    bg_color="#f1f5f9",
    allow_immediate_download=True
)

print(f"Landing page created: {landing_page.id}")
print(f"Name: {landing_page.name}, Kind: {landing_page.kind}")
```

#### Update a landing page

```python
landing_page = client.console.update_landing_page(
    landing_page_id="0xlandingpage1d",
    name="Updated Miami Office Access Pass",
    additional_text="Welcome! Tap below to get your access pass.",
    bg_color="#e2e8f0"
)

print(f"Landing page updated: {landing_page.id}")
print(f"Name: {landing_page.name}")
```

### Credential Profiles

#### List credential profiles

```python
profiles = client.console.credential_profiles.list()

for profile in profiles:
    print(f"ID: {profile.id}, Name: {profile.name}, AID: {profile.aid}")
```

#### Create a credential profile

```python
profile = client.console.credential_profiles.create(
    name='Main Office Profile',
    app_name='KEY-ID-main',
    keys=[
        {'value': 'your_32_char_hex_master_key_here'},
        {'value': 'your_32_char_hex__read_key__here'}
    ]
)

print(f"Profile created: {profile.id}")
print(f"AID: {profile.aid}")
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
| GET /v1/console/card-template-pairs | `console.list_pass_template_pairs()` | Y |
| POST /v1/console/card-template-pairs | `console.create_pass_template_pair()` | Y |
| POST /v1/console/card-templates/{id}/ios_preflight | `console.ios_preflight()` | Y |
| GET /v1/console/ledger-items | `console.ledger_items()` | Y |
| GET /v1/console/landing-pages | `console.list_landing_pages()` | Y |
| POST /v1/console/landing-pages | `console.create_landing_page()` | Y |
| PUT /v1/console/landing-pages/{id} | `console.update_landing_page()` | Y |
| GET /v1/console/credential-profiles | `console.credential_profiles.list()` | Y |
| POST /v1/console/credential-profiles | `console.credential_profiles.create()` | Y |
| GET /v1/console/webhooks | `console.webhooks.list()` | Y |
| POST /v1/console/webhooks | `console.webhooks.create()` | Y |
| DELETE /v1/console/webhooks/{id} | `console.webhooks.delete()` | Y |
| POST /v1/console/hid/orgs | `console.hid.orgs.create()` | Y |
| POST /v1/console/hid/orgs/activate | `console.hid.orgs.activate()` | Y |
| GET /v1/console/hid/orgs | `console.hid.orgs.list()` | Y |
