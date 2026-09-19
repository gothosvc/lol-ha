from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import LolHaEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            LolHaRankSensor(coordinator, entry),
            LolHaLeaguePointsSensor(coordinator, entry),
            LolHaWinStreakSensor(coordinator, entry),
            LolHaGamesPlayedSensor(coordinator, entry),
            LolHaSplitsGamesPlayedSensor(coordinator, entry),
            LolHaLastMatchSensor(coordinator, entry),
        ]
    )


class LolHaRankSensor(LolHaEntity, SensorEntity):
    _attr_translation_key = "rank"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "rank")

    @property
    def native_value(self) -> str | None:
        rank = self.coordinator.data.get("rank")
        if not rank:
            return None
        division = rank.get("rank")
        return f"{rank['tier']} {division}" if division else rank["tier"]

    @property
    def extra_state_attributes(self) -> dict:
        rank = self.coordinator.data.get("rank") or {}
        return {
            "league_points": rank.get("leaguePoints"),
            "wins": rank.get("wins"),
            "losses": rank.get("losses"),
            "hot_streak": rank.get("hotStreak"),
        }


class LolHaLeaguePointsSensor(LolHaEntity, SensorEntity):
    _attr_translation_key = "league_points"
    _attr_native_unit_of_measurement = "LP"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "league_points")

    @property
    def native_value(self) -> int | None:
        rank = self.coordinator.data.get("rank")
        return rank.get("leaguePoints") if rank else None


class LolHaWinStreakSensor(LolHaEntity, SensorEntity):
    _attr_translation_key = "win_streak"
    _attr_native_unit_of_measurement = "games"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "win_streak")

    @property
    def native_value(self) -> int:
        return self.coordinator.data.get("win_streak", 0)


class LolHaGamesPlayedSensor(LolHaEntity, SensorEntity):
    _attr_translation_key = "games_played"
    _attr_native_unit_of_measurement = "games"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "games_played")

    @property
    def native_value(self) -> int:
        return self.coordinator.data.get("games_played", 0)


class LolHaSplitsGamesPlayedSensor(LolHaEntity, SensorEntity):
    _attr_translation_key = "splits_games_played"
    _attr_native_unit_of_measurement = "games"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "splits_games_played")

    @property
    def native_value(self) -> int | None:
        rank = self.coordinator.data.get("rank")
        if not rank:
            return None
        return rank.get("wins", 0) + rank.get("losses", 0)


class LolHaLastMatchSensor(LolHaEntity, SensorEntity):
    _attr_translation_key = "last_match_result"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "last_match_result")

    @property
    def native_value(self) -> str | None:
        match = self.coordinator.data.get("last_match")
        if not match:
            return None
        return "win" if match["win"] else "loss"

    @property
    def extra_state_attributes(self) -> dict:
        match = self.coordinator.data.get("last_match") or {}
        return {
            "champion": match.get("champion"),
            "kills": match.get("kills"),
            "deaths": match.get("deaths"),
            "assists": match.get("assists"),
        }
