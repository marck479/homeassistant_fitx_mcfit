from homeassistant.components.sensor import SensorEntity
from . import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    api = hass.data[DOMAIN][config_entry.entry_id]
    studio_id = config_entry.data["studio_id"]
    
    studios = await api.get_studios()
    studio = next(
        s for s in (studios["studios"] if config_entry.data["provider"] == "fitx" else studios)
        if s["id"] == studio_id
    )
    
    async_add_entities([
        FitnessOccupancySensor(api, studio_id, studio["name"])
    ], True)

class FitnessOccupancySensor(SensorEntity):
    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:dumbbell"

    def __init__(self, api, studio_id, studio_name):
        self.api = api
        self.studio_id = studio_id
        self._attr_name = f"{studio_name} Auslastung"
        self._attr_unique_id = f"{self.api.provider}_{studio_id}_occupancy"

    async def async_update(self):
        self._attr_native_value = await self.api.get_occupancy(self.studio_id)
        self._attr_extra_state_attributes = {
            "provider": self.api.provider,
            "studio_id": self.studio_id
        }
