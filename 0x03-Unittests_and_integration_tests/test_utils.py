#!/usr/bin/env python3
"""
Unit tests for utility functions:
access_nested_map, get_json, and memoize.
"""

import unittest
from unittest.mock import patch, Mock
from utils import access_nested_map, get_json, memoize
from parameterized import parameterized


class TestAccessNestedMap(unittest.TestCase):
    """Test cases for access_nested_map"""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test that access_nested_map returns the correct value"""
        self.assertEqual(
            access_nested_map(nested_map, path),
            expected
        )

    @parameterized.expand([
        ({}, ("a",), "'a'"),
        ({"a": 1}, ("a", "b"), "'b'"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_message):
        """Test that access_nested_map raises KeyError when path is invalid"""
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        self.assertEqual(
            str(cm.exception),
            expected_message
        )


class TestGetJson(unittest.TestCase):
    """Test cases for get_json"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url, test_payload, mock_get):
        """Test that get_json returns correct JSON from URL"""
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        result = get_json(test_url)

        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test case for the memoize decorator."""

    def test_memoize(self):
        """Test that memoize caches the result of a method call."""

        class TestClass:
            """Class to test memoization on a method."""

            def a_method(self) -> int:
                """Simulate an expensive computation."""
                return 42

            @memoize
            def a_property(self) -> int:
                """Memoized property that calls a_method."""
                return self.a_method()

        with patch.object(
            TestClass, 'a_method', return_value=42
        ) as mock_method:
            instance = TestClass()
            result1 = instance.a_property
            result2 = instance.a_property

            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            mock_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()