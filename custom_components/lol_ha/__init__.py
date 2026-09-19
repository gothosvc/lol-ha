from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RiotApiClient
from .const import (
    CONF_API_KEY,
    CONF_IDLE_INTERVAL,
    CONF_PLATFORM_REGION,
    CONF_PUUID,
    CONF_QUEUE_FILTER,
    DEFAULT_IDLE_INTERVAL,
    DEFAULT_QUEUE_FILTER,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import LolDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    client = RiotApiClient(session, entry.data[CONF_API_KEY], entry.data[CONF_PLATFORM_REGION])
    idle_interval = timedelta(seconds=entry.options.get(CONF_IDLE_INTERVAL, DEFAULT_IDLE_INTERVAL.total_seconds()))
    queue_filter = entry.options.get(CONF_QUEUE_FILTER, DEFAULT_QUEUE_FILTER)

    coordinator = LolDataUpdateCoordinator(
        hass, client, entry.data[CONF_PUUID], idle_interval, queue_filter, entry.entry_id
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
