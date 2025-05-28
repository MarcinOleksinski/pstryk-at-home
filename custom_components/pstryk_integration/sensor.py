"""
Sensor platform for Pstryk Integration
"""


from homeassistant.helpers.entity import Entity
from lru import LRU
from .api import PstrykAPIClient
from .const import DOMAIN
import datetime


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Pstryk sensor platform with two sensors."""
    api_key = config_entry.data.get("api_key")
    nazwainstalacji = config_entry.data.get("NazwaInstalacji", "default")
    client = PstrykAPIClient(api_key)
    cache = LRU(100)
    sensors = [
        PstrykHourlySensor(client, cache, nazwainstalacji),
        PstrykDailyAvgSensor(client, cache, nazwainstalacji)
    ]
    async_add_entities(sensors)


# --- Hourly Sensor ---
class PstrykHourlySensor(Entity):
    """Sensor presenting hourly prices (frames) from Pstryk."""

    def __init__(self, client: PstrykAPIClient, cache: LRU, nazwainstalacji: str):
        self.client = client
        self.cache = cache
        self.nazwainstalacji = nazwainstalacji
        self._state = None
        self._attr_unique_id = f"sensor.pstrykathome_{self.nazwainstalacji}_hourly"
        self._attr_name = f"Pstrykathome {self.nazwainstalacji} Hourly"
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
        today = datetime.datetime.utcnow().date()
        end_dt = datetime.datetime.combine(today, datetime.time(22, 0, 0))
        start_dt = end_dt - datetime.timedelta(days=1)
        start = start_dt.strftime("%Y-%m-%dT%H:00:00Z")
        end = end_dt.strftime("%Y-%m-%dT%H:00:00Z")
        data = await self.client.async_get_pricing("hour", start, end)
        # Preferuj dane z frames jeśli są dostępne w odpowiedzi API
        frames = []
        if "frames" in data and isinstance(data["frames"], list):
            frames = data["frames"]
        elif "prices" in data and isinstance(data["prices"], list):
            for entry in data["prices"]:
                hour = entry.get("hour") or entry.get("timestamp")
                net = entry.get("price_net") or entry.get("price_net_avg") or entry.get("net")
                gross = entry.get("price_gross") or entry.get("price_gross_avg") or entry.get("gross")
                is_cheap = entry.get("is_cheap")
                is_expensive = entry.get("is_expensive")
                if hour and net is not None and gross is not None:
                    frames.append({
                        "hour": hour,
                        "net": net,
                        "gross": gross,
                        "is_cheap": is_cheap,
                        "is_expensive": is_expensive
                    })
        # Stan sensora: ostatnia cena netto (obsługa różnych kluczy)
        def extract_net(frame):
            return (
                frame.get("net")
                or frame.get("price_net")
                or frame.get("price_net_avg")
                or None
            )
        last_net = extract_net(frames[-1]) if frames else None
        self.cache[end_dt.isoformat()] = last_net
        self._state = last_net
        self._attr_extra_state_attributes = {
            "frames": frames,
            "window_start": start,
            "window_end": end
        }

# --- Daily Average Sensor ---
class PstrykDailyAvgSensor(Entity):
    """Sensor presenting daily average prices from Pstryk."""

    def __init__(self, client: PstrykAPIClient, cache: LRU, nazwainstalacji: str):
        self.client = client
        self.cache = cache
        self.nazwainstalacji = nazwainstalacji
        self._state = None
        self._attr_unique_id = f"sensor.pstrykathome_{self.nazwainstalacji}_daily_avg"
        self._attr_name = f"Pstrykathome {self.nazwainstalacji} Daily Avg"
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
        today = datetime.datetime.utcnow().date()
        end_dt = datetime.datetime.combine(today, datetime.time(22, 0, 0))
        start_dt = end_dt - datetime.timedelta(days=1)
        start = start_dt.strftime("%Y-%m-%dT%H:00:00Z")
        end = end_dt.strftime("%Y-%m-%dT%H:00:00Z")
        data = await self.client.async_get_pricing("hour", start, end)
        price_net_avg = data.get("price_net_avg")
        price_gross_avg = data.get("price_gross_avg")
        self._state = price_net_avg
        self._attr_extra_state_attributes = {
            "price_net_avg": price_net_avg,
            "price_gross_avg": price_gross_avg,
            "window_start": start,
            "window_end": end
        }
