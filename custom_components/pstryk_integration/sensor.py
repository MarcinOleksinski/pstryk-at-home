"""
Sensor platform for Pstryk Integration
"""

from homeassistant.helpers.entity import Entity
from lru import LRU
from .api import PstrykAPIClient
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Pstryk sensor platform."""
    api_key = config_entry.data["api_key"]
    client = PstrykAPIClient(api_key)
    cache = LRU(100)
    async_add_entities([PstrykSensor(client, cache)])

class PstrykSensor(Entity):
    """Representation of a Pstryk sensor."""

    def __init__(self, client: PstrykAPIClient, cache: LRU):
        self.client = client
        self.cache = cache
        self._state = None

    @property
    def name(self):
        return "Pstryk Pricing"

    @property
    def state(self):
        return self._state

    async def async_update(self):
        """Fetch new state data for the sensor."""
        data = self.client.get_pricing("hour", "2025-05-27T22:00:00Z", "2025-05-28T22:00:00Z")
        self.cache[data.get("price_net_avg")] = data
        self._state = data.get("price_net_avg")
