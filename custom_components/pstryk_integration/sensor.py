"""
Sensor platform for Pstryk Integration
"""

from homeassistant.helpers.entity import Entity
from lru import LRU
from .api import PstrykAPIClient
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Pstryk sensor platform."""
    api_key = config_entry.data.get("api_key")
    nazwainstalacji = config_entry.data.get("NazwaInstalacji", "default")
    client = PstrykAPIClient(api_key)
    cache = LRU(100)
    async_add_entities([PstrykSensor(client, cache, nazwainstalacji)])

class PstrykSensor(Entity):
    """Representation of a Pstryk sensor."""


    def __init__(self, client: PstrykAPIClient, cache: LRU, nazwainstalacji: str):
        self.client = client
        self.cache = cache
        self.nazwainstalacji = nazwainstalacji
        self._state = None
        self._attr_unique_id = f"sensor.pstrykathome_{self.nazwainstalacji}_pricing"
        self._attr_name = f"Pstrykathome {self.nazwainstalacji} Pricing"
        self._attr_unit_of_measurement = "PLN"
        self._attr_device_class = "monetary"
        self._attr_state_class = "measurement"
        self._attr_extra_state_attributes = {}



    @property
    def extra_state_attributes(self):
        return self._attr_extra_state_attributes

    @property
    def state(self):
        return self._state

    async def async_update(self):
        """Fetch new state data for the sensor."""
        import datetime
        now = datetime.datetime.utcnow()
        start = (now - datetime.timedelta(hours=24)).strftime("%Y-%m-%dT%H:00:00Z")
        end = now.strftime("%Y-%m-%dT%H:00:00Z")
        data = await self.client.async_get_pricing("hour", start, end)
        prices = data.get("prices") or []
        if not prices and "price_net_avg" in data:
            prices = [data["price_net_avg"]]
        self.cache[now.isoformat()] = prices[-1] if prices else None
        self._state = prices[-1] if prices else None
        self._attr_extra_state_attributes = {
            "prices": prices,
            "window_start": start,
            "window_end": end
        }
