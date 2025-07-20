#!/usr/bin/env python3
"""Utils module."""

import requests
from typing import Any, Dict


def get_json(url: str) -> Dict[str, Any]:
    """Make a GET request to the URL and return the JSON response."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
