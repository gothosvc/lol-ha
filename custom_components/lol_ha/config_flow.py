from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RiotApiAuthError, RiotApiClient, RiotApiError
from .const import (
    CONF_API_KEY,
    CONF_GAME_NAME,
    CONF_IDLE_INTERVAL,
    CONF_PLATFORM_REGION,
    CONF_PUUID,
    CONF_QUEUE_FILTER,
    CONF_TAG_LINE,
    DEFAULT_IDLE_INTERVAL,
    DEFAULT_QUEUE_FILTER,
    DOMAIN,
    MIN_IDLE_INTERVAL,
    PLATFORM_TO_REGION,
    QUEUE_FILTERS,
)

_LOGGER = logging.getLogger(__name__)


class LolHaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = RiotApiClient(session, user_input[CONF_API_KEY], user_input[CONF_PLATFORM_REGION])
            try:
                account = await client.get_account_by_riot_id(
                    user_input[CONF_GAME_NAME], user_input[CONF_TAG_LINE]
                )
                if account is None:
                    errors["base"] = "account_not_found"
                else:
                    await self.async_set_unique_id(f"{user_input[CONF_PLATFORM_REGION]}:{account['puuid']}")
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"{user_input[CONF_GAME_NAME]}#{user_input[CONF_TAG_LINE]}",
                        data={
                            CONF_PLATFORM_REGION: user_input[CONF_PLATFORM_REGION],
                            CONF_GAME_NAME: user_input[CONF_GAME_NAME],
                            CONF_TAG_LINE: user_input[CONF_TAG_LINE],
                            CONF_API_KEY: user_input[CONF_API_KEY],
                            CONF_PUUID: account["puuid"],
                        },
                        options={
                            CONF_IDLE_INTERVAL: DEFAULT_IDLE_INTERVAL.total_seconds(),
                            CONF_QUEUE_FILTER: DEFAULT_QUEUE_FILTER,
                        },
                    )
            except RiotApiAuthError:
                errors["base"] = "invalid_api_key"
            except RiotApiError:
                errors["base"] = "cannot_connect"

        schema = vol.Schema(
            {
                vol.Required(CONF_PLATFORM_REGION): vol.In(sorted(PLATFORM_TO_REGION)),
                vol.Required(CONF_GAME_NAME): str,
                vol.Required(CONF_TAG_LINE): str,
                vol.Required(CONF_API_KEY): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry):
        return LolHaOptionsFlow(config_entry)


class LolHaOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_IDLE_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_IDLE_INTERVAL, DEFAULT_IDLE_INTERVAL.total_seconds()
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=int(MIN_IDLE_INTERVAL.total_seconds()))),
                vol.Required(
                    CONF_QUEUE_FILTER,
                    default=self.config_entry.options.get(CONF_QUEUE_FILTER, DEFAULT_QUEUE_FILTER),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=QUEUE_FILTERS,
                        translation_key="queue_filter",
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
