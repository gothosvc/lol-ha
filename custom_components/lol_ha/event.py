from __future__ import annotations

from homeassistant.components.event import EventEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import LolHaEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LolHaRankChangeEvent(coordinator, entry)])


class LolHaRankChangeEvent(LolHaEntity, EventEntity):
    _attr_translation_key = "rank_change"
    _attr_event_types = ["promotion", "demotion"]
    _attr_should_poll = False

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "rank_change")
        self._last_seen: str | None = None

    def _handle_coordinator_update(self) -> None:
        change = self.coordinator.data.get("rank_change")
        if change and change["timestamp"] != self._last_seen:
            self._last_seen = change["timestamp"]
            self._trigger_event(
                change["direction"],
                {"old_tier": change["old_tier"], "new_tier": change["new_tier"]},
            )
        super()._handle_coordinator_update()
