"""
Config flow for Pstryk Integration
"""

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .const import DOMAIN

class PstrykConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pstryk Integration."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Pstryk Integration", data=user_input)

        return self.async_show_form(step_id="user", data_schema=self._get_schema())

    async def async_step_reconfigure(self, user_input=None):
        """Handle reconfiguration step."""
        if user_input is not None:
            return self.async_create_entry(title="Pstryk Integration - Reconfigured", data=user_input)

        return self.async_show_form(step_id="reconfigure", data_schema=self._get_schema())

    def _get_schema(self):
        from homeassistant.helpers import config_validation as cv
        import voluptuous as vol

        return vol.Schema({
            vol.Required("api_key"): cv.string,
            vol.Optional("debug", default=False): cv.boolean,
        })
