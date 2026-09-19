from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import LolHaEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LolHaInGameSensor(coordinator, entry)])


class LolHaInGameSensor(LolHaEntity, BinarySensorEntity):
    _attr_translation_key = "in_game"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "in_game")

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get("in_game"))
