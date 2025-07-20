#!/usr/bin/env python3
"""Unit tests for GithubOrgClient
"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class
import requests
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient"""

    @patch('client.get_json')
    def test_org(self, mock_get_json):
        expected_payload = {"login": "test_org"}
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient("test_org")
        result = client.org

        self.assertEqual(result, expected_payload)
        mock_get_json.assert_called_once_with("https://api.github.com/orgs/test_org")

    @patch.object(GithubOrgClient, 'org', new_callable=PropertyMock)
    def test_public_repos_url(self, mock_org):
        expected_url = "https://api.github.com/orgs/test_org/repos"
        mock_org.return_value = {"repos_url": expected_url}

        client = GithubOrgClient("test_org")
        self.assertEqual(client._public_repos_url, expected_url)

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos returns expected repo names from fixtures without license filter"""
        mock_get_json.return_value = repos_payload

        client = GithubOrgClient("test_org")
        with patch.object(GithubOrgClient, '_public_repos_url', new_callable=PropertyMock) as mock_repos_url:
            mock_repos_url.return_value = "https://api.github.com/orgs/test_org/repos"

            repos = client.public_repos()

            self.assertEqual(repos, expected_repos)
            mock_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with("https://api.github.com/orgs/test_org/repos")

    @patch('client.get_json')
    def test_public_repos_with_license(self, mock_get_json):
        """Test public_repos returns expected repo names filtered by license 'apache-2.0'"""
        mock_get_json.return_value = repos_payload

        client = GithubOrgClient("test_org")
        with patch.object(GithubOrgClient, '_public_repos_url', new_callable=PropertyMock) as mock_repos_url:
            mock_repos_url.return_value = "https://api.github.com/orgs/test_org/repos"

            repos = client.public_repos(license="apache-2.0")

            self.assertEqual(repos, apache2_repos)
            mock_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with("https://api.github.com/orgs/test_org/repos")


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    [
        (org_payload, repos_payload, expected_repos, apache2_repos)
    ]
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos"""

    @classmethod
    def setUpClass(cls):
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url, *args, **kwargs):
            class MockResponse:
                def __init__(self, json_data):
                    self._json = json_data
                    self.status_code = 200

                def json(self):
                    return self._json

                def raise_for_status(self):
                    pass  # For simplicity, assume always successful

            if url == f"https://api.github.com/orgs/{cls.org_payload['login']}":
                return MockResponse(cls.org_payload)
            elif url == cls.org_payload['repos_url']:
                return MockResponse(cls.repos_payload)
            return MockResponse(None)

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        cls.get_patcher.stop()

    def test_public_repos(self):
        client = GithubOrgClient(self.org_payload["login"])
        repos = client.public_repos()

        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self):
        client = GithubOrgClient(self.org_payload["login"])
        repos = client.public_repos(license="apache-2.0")

        self.assertEqual(repos, self.apache2_repos)


if __name__ == "__main__":
    unittest.main()