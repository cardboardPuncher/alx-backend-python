#!/usr/bin/env python3
"""Client module for interacting with GitHub API."""
import requests
from utils import get_json


def get_json(url):
    """Fetch JSON data from a URL."""
    response = requests.get(url)
    return response.json()


class GithubOrgClient:
    """Client for GitHub organization data."""

    ORG_URL = "https://api.github.com/orgs/{}"

    def __init__(self, org_name):
        self.org_name = org_name

    @property
    def org(self):
        """Return the organization data."""
        return get_json(self.ORG_URL.format(self.org_name))
    
    @property
    def _public_repos_url(self):
        """Returns the public repos URL from org info."""
        return self.org.get("repos_url")
    
    def public_repos(self, license=None):
        """Get list of public repo names, optionally filtered by license"""
        repos = get_json(self._public_repos_url)  # This returns list of dicts

        if license is None:
            return [repo["name"] for repo in repos]

        return [
            repo["name"]
            for repo in repos
            if repo.get("license", {}).get("key") == license
        ]

    
    @staticmethod
    def has_license(repo, license_key):
        """Checks if repo has a given license key"""
        return repo.get("license", {}).get("key") == license_key