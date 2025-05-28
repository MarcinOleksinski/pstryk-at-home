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
        today = datetime.datetime.utcnow().date()
        end_dt = datetime.datetime.combine(today, datetime.time(22, 0, 0))
        start_dt = end_dt - datetime.timedelta(days=1)
        start = start_dt.strftime("%Y-%m-%dT%H:00:00Z")
        end = end_dt.strftime("%Y-%m-%dT%H:00:00Z")
        data = await self.client.async_get_pricing("hour", start, end)
        # Oczekujemy, że API zwraca listę słowników z polami: hour, price_net, price_gross
        # Jeśli nie, przemapuj dane do takiej struktury
        prices = []
        hours = []
        if "prices" in data and isinstance(data["prices"], list):
            for entry in data["prices"]:
                # Obsługa różnych formatów odpowiedzi API
                hour = entry.get("hour") or entry.get("timestamp")
                net = entry.get("price_net") or entry.get("price_net_avg") or entry.get("net")
                gross = entry.get("price_gross") or entry.get("price_gross_avg") or entry.get("gross")
                if hour and net is not None and gross is not None:
                    prices.append({"hour": hour, "net": net, "gross": gross})
                    hours.append(hour)
        # fallback: jeśli API zwraca tylko jedną wartość
        elif "price_net_avg" in data and "price_gross_avg" in data:
            prices = [{"hour": end, "net": data["price_net_avg"], "gross": data["price_gross_avg"]}]
            hours = [end]
        # Stan sensora: ostatnia cena netto
        last_net = prices[-1]["net"] if prices else None
        self.cache[end_dt.isoformat()] = last_net
        self._state = last_net
        self._attr_extra_state_attributes = {
            "prices": prices,
            "hours": hours,
            "window_start": start,
            "window_end": end
        }
