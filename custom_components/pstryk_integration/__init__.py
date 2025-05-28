"""
Pstryk Integration for Home Assistant
"""

from homeassistant.core import HomeAssistant

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Pstryk integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry):
    """Set up Pstryk integration from a config entry."""
    await hass.config_entries.async_forward_entry_setup(entry, "sensor")
    return True

async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload Pstryk integration config entry."""
    return True
