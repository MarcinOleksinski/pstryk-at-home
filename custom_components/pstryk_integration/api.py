"""
API client for Pstryk Integration
"""

import requests

class PstrykAPIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.pstryk.pl/integrations/pricing/"

    def get_pricing(self, resolution: str, window_start: str, window_end: str):
        headers = {"Authorization": self.api_key, "accept": "application/json"}
        params = {"resolution": resolution, "window_start": window_start, "window_end": window_end}
        response = requests.get(self.base_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
