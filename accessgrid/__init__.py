"""
AccessGrid Python SDK
~~~~~~~~~~~~~~~~~~~~

A Python SDK for interacting with the AccessGrid.com API.

Basic usage:

    >>> from accessgrid import AccessGrid
    >>> client = AccessGrid(account_id="your_id", secret_key="your_key")
    >>> card = client.access_cards.provision(
    ...     card_template_id="template_id",
    ...     full_name="Employee Name"
    ... )
    >>> print(card.url)

For more information, see https://www.accessgrid.com/docs
"""

# Import all public components
from .client import (
    AccessGrid,
    AccessGridError,
    AuthenticationError,
    AccessCard,
    Template
)

# Version of the accessgrid package
__version__ = "0.1.8"

# List of public objects that will be exported with "from accessgrid import *"
__all__ = [
    'AccessGrid',
    'AccessGridError',
    'AuthenticationError',
    'AccessCard',
    'Template'
]