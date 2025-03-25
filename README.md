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
    allow_on_multiple_devices=True,
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
    name="Employee NFC key",
    platform="apple",
    use_case="employee_badge",
    protocol="desfire",
    allow_on_multiple_devices=True,
    watch_count=2,
    iphone_count=3,
    design={
        "background_color": "#FFFFFF",
        "label_color": "#000000",
        "label_secondary_color": "#333333",
        "background_image": "[image_in_base64_encoded_format]",
        "logo_image": "[image_in_base64_encoded_format]",
        "icon_image": "[image_in_base64_encoded_format]"
    },
    support_info={
        "support_url": "https://help.yourcompany.com",
        "support_phone_number": "+1-555-123-4567",
        "support_email": "support@yourcompany.com",
        "privacy_policy_url": "https://yourcompany.com/privacy",
        "terms_and_conditions_url": "https://yourcompany.com/terms"
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
    support_info={
        "support_url": "https://help.yourcompany.com",
        "support_phone_number": "+1-555-123-4567",
        "support_email": "support@yourcompany.com",
        "privacy_policy_url": "https://yourcompany.com/privacy",
        "terms_and_conditions_url": "https://yourcompany.com/terms"
    }
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