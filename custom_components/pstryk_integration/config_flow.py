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
        from homeassistant.helpers import config_validation as cv
        import voluptuous as vol
        errors = {}
        if user_input is not None:
            # Sprawdź czy NazwaInstalacji nie zawiera spacji
            if " " in user_input["NazwaInstalacji"]:
                errors["NazwaInstalacji"] = "Nie używaj spacji w nazwie instalacji."
            else:
                return self.async_create_entry(title=f"Pstryk-at-Home [{user_input['NazwaInstalacji']}]", data=user_input)

        schema = vol.Schema({
            vol.Required("NazwaInstalacji", description={"suggested_value": "instalacja1"}): cv.string,
            vol.Required("api_key"): cv.string,
            vol.Optional("debug", default=False): cv.boolean,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    # Opcje (rekonfiguracja)
    @staticmethod
    def async_get_options_flow(config_entry):
        return PstrykOptionsFlowHandler(config_entry)


class PstrykOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        from homeassistant.helpers import config_validation as cv
        import voluptuous as vol
        if user_input is not None:
            return self.async_create_entry(title="Opcje Pstryk Integration", data=user_input)

        schema = vol.Schema({
            # NazwaInstalacji nie jest edytowalna podczas rekonfiguracji
            vol.Required("api_key", default=self.config_entry.data.get("api_key", "")): cv.string,
            vol.Optional("debug", default=self.config_entry.data.get("debug", False)): cv.boolean,
        })
        return self.async_show_form(step_id="init", data_schema=schema)
