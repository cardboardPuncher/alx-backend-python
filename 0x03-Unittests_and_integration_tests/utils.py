#!/usr/bin/env python3
"""Utils module."""

from typing import Any, Dict, Tuple
import requests


def access_nested_map(nested_map: Dict, path: Tuple) -> Any:
    """Access nested map with path of keys."""
    current = nested_map
    for key in path:
        current = current[key]
    return current


def get_json(url: str) -> Dict:
    """Get JSON content from URL."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def memoize(func):
    """Decorator to memoize a method call result."""
    attr_name = f"_memoized_{func.__name__}"

    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)

    return property(wrapper)
