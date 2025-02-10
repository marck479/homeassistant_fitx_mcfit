from homeassistant import config_entries
from homeassistant.helpers import selector
import voluptuous as vol
from . import DOMAIN, FitnessAPI

class FitnessConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        return self.async_show_menu(
            step_id="provider",
            menu_options=["fitx", "mcfit"]
        )

    async def async_step_fitx(self, user_input=None):
        return await self._async_step_provider("fitx", user_input)

    async def async_step_mcfit(self, user_input=None):
        return await self._async_step_provider("mcfit", user_input)

    async def _async_step_provider(self, provider, user_input):
        errors = {}
        if user_input:
            try:
                api = FitnessAPI(provider, user_input["username"], user_input["password"])
                studios = await api.get_studios()
                studio = next(s for s in studios if s["id"] == user_input["studio_id"])
                
                return self.async_create_entry(
                    title=f"{provider.upper()} {studio['name']}",
                    data={
                        **user_input,
                        "provider": provider
                    }
                )
            except Exception as e:
                _LOGGER.error("Config error: %s", e)
                errors["base"] = "auth" if "401" in str(e) else "connection"

        studios = await self._fetch_studios(provider)
        
        return self.async_show_form(
            step_id=provider,
            data_schema=vol.Schema({
                vol.Required("username"): str,
                vol.Required("password"): str,
                vol.Required("studio_id"): selector({
                    "select": {
                        "options": studios,
                        "mode": "dropdown"
                    }
                })
            }),
            errors=errors
        )

    async def _fetch_studios(self, provider):
        try:
            api = FitnessAPI(provider, "", "")  # Temporary dummy auth
            data = await api.get_studios()
            return [
                {
                    "label": f"{s['name']} ({s['address']['city']})",
                    "value": s["id"]
                } for s in data["studios"] if provider == "fitx" else data
            ]
        except:
            return []
