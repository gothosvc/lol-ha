from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LolDataUpdateCoordinator


class LolHaEntity(CoordinatorEntity[LolDataUpdateCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: LolDataUpdateCoordinator, entry: ConfigEntry, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Riot Games",
            model="Summoner",
        )
