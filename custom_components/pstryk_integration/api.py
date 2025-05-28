"""
API client for Pstryk Integration
"""


import aiohttp
import asyncio

class PstrykAPIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.pstryk.pl/integrations/pricing/"

    async def async_get_pricing(self, resolution: str, window_start: str, window_end: str):
        headers = {"Authorization": self.api_key, "accept": "application/json"}
        params = {"resolution": resolution, "window_start": window_start, "window_end": window_end}
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, headers=headers, params=params) as response:
                response.raise_for_status()
                return await response.json()
